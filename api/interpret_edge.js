/**
 * Vercel Edge Runtime Streaming Endpoint: POST /api/interpret_edge
 * - Chạy trên V8 Edge Runtime (khởi động < 50ms, stream SSE lên tới 300s trên gói Hobby Free, KHÔNG BAO GIỜ bị lỗi 10s/60s FUNCTION_INVOCATION_TIMEOUT của Python Serverless).
 * - Bảo mật 100%: GEMINI_API_KEY nằm kín trên Server, xác thực chữ ký HMAC-SHA256 từ bước prepare để chống lạm dụng.
 * - Tự động fallback qua danh sách model Free Tier tối ưu nhất (gemini-4-hydrogen -> gemini-3.8-flash -> gemini-3.6-flash -> gemini-3.5-flash-lite) với thinkingLevel="LOW" để vừa nhanh vừa viết tiếng Việt tự nhiên, mạch lạc!
 */
export const config = {
  runtime: "edge",
};

const enc = new TextEncoder();
const dec = new TextDecoder();

function getServerApiKey() {
  const raw =
    process.env.GEMINI_API_KEY ||
    process.env.GOOGLE_API_KEY ||
    process.env.GEMINI_KEY ||
    "";
  return raw.trim().replace(/^["']+|["']+$/g, "");
}

async function sha256Hex(str) {
  const buf = await crypto.subtle.digest("SHA-256", enc.encode(str));
  return Array.from(new Uint8Array(buf))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}

async function hmacSha256Hex(secret, message) {
  const key = await crypto.subtle.importKey(
    "raw",
    enc.encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"]
  );
  const sigBuf = await crypto.subtle.sign("HMAC", key, enc.encode(message));
  return Array.from(new Uint8Array(sigBuf))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}

function buildGenerationConfig(modelId) {
  const cfg = { maxOutputTokens: 16384 };
  const id = String(modelId || "");
  if (id.startsWith("gemini-4") || id.startsWith("gemini-3")) {
    cfg.thinkingConfig = { thinkingLevel: "LOW" };
  } else if (id.startsWith("gemini-2.5")) {
    cfg.temperature = 0.7;
    cfg.thinkingConfig = { thinkingBudget: 0 };
  } else {
    cfg.temperature = 0.7;
  }
  return cfg;
}

export default async function handler(req) {
  const corsHeaders = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, X-Gemini-Api-Key",
  };

  if (req.method === "OPTIONS") {
    return new Response(null, { status: 204, headers: corsHeaders });
  }
  if (req.method !== "POST") {
    return new Response(JSON.stringify({ ok: false, error: "Method Not Allowed" }), {
      status: 405,
      headers: { ...corsHeaders, "Content-Type": "application/json; charset=utf-8" },
    });
  }

  let body;
  try {
    body = await req.json();
  } catch (e) {
    return new Response(JSON.stringify({ ok: false, error: "JSON không hợp lệ." }), {
      status: 400,
      headers: { ...corsHeaders, "Content-Type": "application/json; charset=utf-8" },
    });
  }

  const headerKey = (req.headers.get("x-gemini-api-key") || "").trim().replace(/^["']+|["']+$/g, "");
  const usingByok = Boolean(headerKey);
  const apiKey = usingByok ? headerKey : getServerApiKey();

  if (!apiKey) {
    return new Response(
      JSON.stringify({ ok: false, error: "Máy chủ chưa cấu hình GEMINI_API_KEY." }),
      { status: 401, headers: { ...corsHeaders, "Content-Type": "application/json; charset=utf-8" } }
    );
  }

  const systemInstruction = String(body.system_instruction || "");
  const userPrompt = String(body.user_prompt || "");
  const mode = String(body.mode || "full");
  const ts = Number(body.ts || 0);
  const sig = String(body.sig || "");
  const primaryModel = String(body.primary_model || "gemini-4-hydrogen");
  const modelsToTry = Array.isArray(body.models_to_try) && body.models_to_try.length
    ? body.models_to_try
    : [primaryModel, "gemini-3.8-flash", "gemini-3.6-flash", "gemini-3.5-flash-lite"];

  if (!systemInstruction || !userPrompt) {
    return new Response(
      JSON.stringify({ ok: false, error: "Thiếu dữ liệu prompt đã chuẩn bị." }),
      { status: 400, headers: { ...corsHeaders, "Content-Type": "application/json; charset=utf-8" } }
    );
  }

  // Xác thực chữ ký HMAC-SHA256 khi dùng Key chung của Server
  if (!usingByok) {
    const nowSec = Math.floor(Date.now() / 1000);
    if (!ts || Math.abs(nowSec - ts) > 300) {
      return new Response(
        JSON.stringify({ ok: false, error: "Phiên chuẩn bị AI đã hết hạn, vui lòng bấm lại." }),
        { status: 401, headers: { ...corsHeaders, "Content-Type": "application/json; charset=utf-8" } }
      );
    }
    const sysH = await sha256Hex(systemInstruction);
    const usrH = await sha256Hex(userPrompt);
    const expectedSig = await hmacSha256Hex(apiKey, `${ts}:${mode}:${sysH}:${usrH}`);
    if (!sig || sig !== expectedSig) {
      return new Response(
        JSON.stringify({ ok: false, error: "Chữ ký xác thực phiên AI không hợp lệ." }),
        { status: 401, headers: { ...corsHeaders, "Content-Type": "application/json; charset=utf-8" } }
      );
    }
  }

  const startMs = Date.now();

  const stream = new ReadableStream({
    async start(controller) {
      const sendEvent = (obj) => {
        controller.enqueue(enc.encode(`data: ${JSON.stringify(obj)}\n\n`));
      };

      // Gửi ngay heartbeat đầu tiên (< 50ms) để giữ kết nối Edge mở mượt mà
      controller.enqueue(enc.encode(": connected\n\n"));

      let lastErr = "";
      let succeeded = false;

      for (const modelId of modelsToTry) {
        try {
          const geminiUrl = `https://generativelanguage.googleapis.com/v1beta/models/${encodeURIComponent(
            modelId
          )}:streamGenerateContent?alt=sse&key=${encodeURIComponent(apiKey)}`;

          const geminiPayload = {
            system_instruction: { parts: [{ text: systemInstruction }] },
            contents: [{ role: "user", parts: [{ text: userPrompt }] }],
            generationConfig: buildGenerationConfig(modelId),
          };

          const gRes = await fetch(geminiUrl, {
            method: "POST",
            headers: { "Content-Type": "application/json; charset=utf-8" },
            body: JSON.stringify(geminiPayload),
          });

          if (!gRes.ok || !gRes.body) {
            const errTxt = await gRes.text();
            let errMsg = errTxt.slice(0, 260);
            try {
              const ej = JSON.parse(errTxt);
              if (ej && ej.error && ej.error.message) errMsg = ej.error.message;
            } catch (_) {}

            lastErr = `[${modelId}] HTTP ${gRes.status}: ${errMsg}`;
            if (
              gRes.status === 401 ||
              gRes.status === 403 ||
              errMsg.includes("API key not valid") ||
              errMsg.includes("API_KEY_INVALID")
            ) {
              sendEvent({
                type: "error",
                error: `Gemini API Key không hợp lệ hoặc chưa được kích hoạt: ${errMsg}`,
              });
              controller.close();
              return;
            }
            if ([400, 404, 429, 500, 503].includes(gRes.status)) {
              continue;
            }
            sendEvent({ type: "error", error: lastErr });
            controller.close();
            return;
          }

          sendEvent({
            type: "meta",
            model_used: modelId,
            fallback_used: modelId !== primaryModel,
            key_source: usingByok ? "user_byok" : "server_free",
          });

          const reader = gRes.body.getReader();
          let buffer = "";
          let emittedChars = 0;
          let usageMeta = {};

          while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            buffer += dec.decode(value, { stream: true });
            const lines = buffer.split(/\r?\n/);
            buffer = lines.pop() || "";

            for (const line of lines) {
              const trimmed = line.trim();
              if (!trimmed.startsWith("data:")) continue;
              const dataStr = trimmed.slice(5).trim();
              if (!dataStr || dataStr === "[DONE]") continue;
              try {
                const pkt = JSON.parse(dataStr);
                if (pkt.usageMetadata) usageMeta = pkt.usageMetadata;
                const parts = pkt?.candidates?.[0]?.content?.parts || [];
                for (const p of parts) {
                  if (p && !p.thought && typeof p.text === "string" && p.text.length > 0) {
                    emittedChars += p.text.length;
                    sendEvent({ type: "chunk", text: p.text });
                  }
                }
              } catch (_) {}
            }
          }

          if (emittedChars > 0) {
            const elapsedSec = Math.round(((Date.now() - startMs) / 1000) * 10) / 10;
            sendEvent({
              type: "done",
              elapsed_sec: elapsedSec,
              usage: usageMeta,
            });
            succeeded = true;
            break;
          } else {
            lastErr = `[${modelId}] Phản hồi rỗng từ Gemini.`;
          }
        } catch (err) {
          lastErr = `[${modelId}] ${err && err.message ? err.message : String(err)}`;
        }
      }

      if (!succeeded) {
        sendEvent({
          type: "error",
          error: `Tất cả các model Gemini Free hiện đều đang bận hoặc hết hạn mức tạm thời. Chi tiết: ${lastErr}`,
        });
      }
      controller.close();
    },
  });

  return new Response(stream, {
    status: 200,
    headers: {
      ...corsHeaders,
      "Content-Type": "text/event-stream; charset=utf-8",
      "Cache-Control": "no-cache, no-transform",
      Connection: "keep-alive",
    },
  });
}
