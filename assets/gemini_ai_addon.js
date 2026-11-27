/**
 * gemini_ai_addon.js — Plugin Trạm Luận Giải Gemini AI độc lập cho KB-TUVI v3.0
 * Thiết kế kiểu Non-Intrusive Add-on:
 * - Tự động gắn nút "✨ Luận Giải AI (Gemini)" vào Sidebar, Toolbar và Tab "🤖 Đông-Tây & AI Giải".
 * - Cho phép bạn tự do chỉnh sửa giao diện studio_gui.html ở thư mục gốc mà KHÔNG BAO GIỜ bị mất tính năng AI!
 */
(function () {
  if (window.__KB_TUVI_AI_ADDON_LOADED__) return;
  window.__KB_TUVI_AI_ADDON_LOADED__ = true;

  const SERVER_CFG = {
    server_has_key: false,
    requires_access_code: false,
    default_model: "gemini-3.8-flash",
    available_models: [
      { id: "gemini-3.8-flash", label: "Gemini 3.8 Flash (Mặc định — Mạnh nhất, Free Tier)" },
      { id: "gemini-3.6-flash", label: "Gemini 3.6 Flash (Ổn định — Free Tier)" },
      { id: "gemini-3.5-flash-lite", label: "Gemini 3.5 Flash-Lite (Siêu nhanh — Tiết kiệm quota)" },
      { id: "gemini-2.5-flash", label: "Gemini 2.5 Flash (Dự phòng cho Key cũ)" }
    ]
  };

  const AI_STATE = {
    loading: false,
    error: "",
    markdown: "",
    metaInfo: null,
    mode: "full",
    focusQuestion: "",
    model: "gemini-3.8-flash",
    elapsed: 0
  };
  let timerHandle = null;

  function escHtml(s) {
    if (s === null || s === undefined) return "";
    return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }

  function getStudioState() {
    try {
      if (typeof STATE !== "undefined" && STATE) return STATE;
    } catch (e) {}
    return window.STATE || null;
  }

  function injectStyles() {
    if (document.getElementById("kb-ai-addon-style")) return;
    const style = document.createElement("style");
    style.id = "kb-ai-addon-style";
    style.textContent = `
      .btn-ai-cta {
        width: 100%; padding: 11px 12px; border: 1px solid #d4a448; border-radius: 8px; cursor: pointer;
        background: linear-gradient(135deg, #c6912d, #8d5d12); color: #fff;
        font-weight: 800; font-size: 13.5px; letter-spacing: 0.3px; margin-top: 8px;
        box-shadow: 0 3px 10px rgba(194,142,44,0.32); transition: transform 0.1s;
      }
      .btn-ai-cta:hover { filter: brightness(1.08); transform: translateY(-1px); }
      .btn-ai-cta:disabled { opacity: 0.65; cursor: not-allowed; transform: none; }
      .ai-controls {
        background: #faf6ee; border: 1px solid var(--border, #dcd1bf); border-radius: 10px;
        padding: 15px 16px; margin-bottom: 14px;
      }
      .ai-grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 10px; }
      @media (max-width: 780px) { .ai-grid-2 { grid-template-columns: 1fr; } }
      .ai-field label { display: block; font-size: 12px; font-weight: 700; color: #4f4438; margin-bottom: 4px; }
      .ai-field input, .ai-field select {
        width: 100%; padding: 8.5px 10px; border: 1px solid #cfc2ae; border-radius: 6px;
        background: #fff; color: var(--ink, #1e1a17); font-size: 13px; font-family: inherit;
      }
      .ai-status-pill {
        display: inline-flex; align-items: center; gap: 6px; padding: 4px 11px;
        border-radius: 99px; font-size: 12px; font-weight: 700; margin-bottom: 11px;
      }
      .ai-status-ok { background: #e8f6f0; color: #16694f; border: 1px solid #b5e0cf; }
      .ai-status-warn { background: #fff3cd; color: #855a00; border: 1px solid #f0d58c; }
      .ai-byok-box {
        margin-top: 10px; padding: 10px 12px; background: #fff; border: 1px dashed #c8b89d;
        border-radius: 7px; font-size: 12.5px;
      }
      .ai-byok-box summary { cursor: pointer; font-weight: 700; color: var(--navy, #1d4675); }
      .ai-loader {
        display: flex; align-items: center; gap: 12px; padding: 16px;
        background: #fcf6e8; border: 1px solid #e7d1a0; border-radius: 8px;
        font-weight: 700; color: #6e4c10; margin: 12px 0;
      }
      .ai-spinner {
        width: 22px; height: 22px; border: 3px solid #e7d1a0; border-top-color: #8f1d1d;
        border-radius: 50%; animation: kbAiSpin 0.8s linear infinite; flex-shrink: 0;
      }
      @keyframes kbAiSpin { to { transform: rotate(360deg); } }
      .ai-error {
        padding: 12px 14px; background: #fdf2f0; border: 1px solid #ebb7b2;
        border-left: 4px solid #8f1d1d; border-radius: 7px; color: #7e1515;
        font-size: 13px; margin: 10px 0; line-height: 1.5;
      }
      .ai-report-header {
        display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 8px;
        padding: 10px 14px; background: linear-gradient(135deg, #251f1a, #3a2d24);
        color: #f3dcab; border-radius: 8px 8px 0 0; font-size: 12.5px;
      }
      .ai-report-body {
        background: #fffefc; border: 1px solid var(--border, #dcd1bf); border-top: none;
        border-radius: 0 0 8px 8px; padding: 20px 24px; line-height: 1.75; font-size: 14.2px;
        color: #241f1b;
      }
      .ai-report-body h1, .ai-report-body h2 {
        color: #8f1d1d; border-bottom: 1.5px solid #eee4d3; padding-bottom: 5px;
        margin: 22px 0 10px; font-size: 17.5px;
      }
      .ai-report-body h1:first-child, .ai-report-body h2:first-child { margin-top: 2px; }
      .ai-report-body h3 { color: #1d4675; margin: 16px 0 7px; font-size: 15.2px; }
      .ai-report-body h4 { color: #a87928; margin: 12px 0 5px; font-size: 14px; }
      .ai-report-body ul, .ai-report-body ol { padding-left: 22px; margin: 6px 0 12px; }
      .ai-report-body li { margin-bottom: 5px; }
      .ai-report-body blockquote {
        margin: 12px 0; padding: 10px 14px; background: #fcf6e8;
        border-left: 4px solid #a87928; border-radius: 0 6px 6px 0; color: #4a3714;
      }
      .ai-report-body table { width: 100%; border-collapse: collapse; margin: 12px 0; font-size: 13px; }
      .ai-report-body th, .ai-report-body td { border: 1px solid #dcd1bf; padding: 8px 10px; text-align: left; }
      .ai-report-body th { background: #f2eadc; }
      .ai-report-body code { background: #f2ebe0; padding: 1px 5px; border-radius: 4px; font-size: 12.5px; }
      .ai-report-body hr { border: none; border-top: 1px dashed #dcd1bf; margin: 16px 0; }
      .cv-tag-high { display:inline-block; padding:1px 7px; border-radius:4px; background:#e8f6f0; color:#16694f; font-weight:800; font-size:12px; }
      .cv-tag-mid { display:inline-block; padding:1px 7px; border-radius:4px; background:#fff3cd; color:#855a00; font-weight:800; font-size:12px; }
      .cv-tag-low { display:inline-block; padding:1px 7px; border-radius:4px; background:#fdf2f0; color:#8f1d1d; font-weight:800; font-size:12px; }
      @media (max-width: 960px) {
        .tuvi-wrapper { overflow-x: auto; padding-bottom: 6px; }
        .tuvi-board { min-width: 780px; }
        .welcome-steps { grid-template-columns: 1fr !important; }
        .elem-bars { grid-template-columns: repeat(2, 1fr) !important; }
        .dayun-grid { grid-template-columns: repeat(3, 1fr) !important; }
        .qm-board { grid-template-columns: 1fr !important; }
        .toolbar-right { margin-left: 0 !important; width: 100%; flex-wrap: wrap; }
      }
      @media print {
        .sidebar, .tabs, .ai-controls, .ai-report-header button { display: none !important; }
      }
    `;
    document.head.appendChild(style);
  }

  function renderMarkdownToHtml(md) {
    if (!md) return "";
    const lines = md.replace(/\r\n/g, "\n").split("\n");
    let html = "";
    let inUl = false;
    let inOl = false;
    let inTable = false;

    function closeLists() {
      if (inUl) { html += "</ul>"; inUl = false; }
      if (inOl) { html += "</ol>"; inOl = false; }
    }
    function closeTable() {
      if (inTable) { html += "</tbody></table>"; inTable = false; }
    }
    function inlineFmt(str) {
      let s = escHtml(str);
      s = s.replace(/`([^`]+)`/g, "<code>$1</code>");
      s = s.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
      s = s.replace(/(^|[^*])\*([^*\n]+)\*/g, "$1<em>$2</em>");
      s = s.replace(/🟢\s*ĐỒNG THUẬN CAO/g, '<span class="cv-tag-high">🟢 ĐỒNG THUẬN CAO</span>');
      s = s.replace(/🟡\s*BÁN ĐỒNG THUẬN/g, '<span class="cv-tag-mid">🟡 BÁN ĐỒNG THUẬN</span>');
      s = s.replace(/🔴\s*PHÂN KỲ/g, '<span class="cv-tag-low">🔴 PHÂN KỲ</span>');
      return s;
    }

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].trim();
      if (!line) { closeLists(); closeTable(); continue; }

      if (line.startsWith("|") && line.endsWith("|")) {
        closeLists();
        const cells = line.slice(1, -1).split("|").map(c => c.trim());
        if (cells.every(c => /^:?-{2,}:?$/.test(c))) continue;
        if (!inTable) {
          inTable = true;
          html += "<table><thead><tr>" + cells.map(c => `<th>${inlineFmt(c)}</th>`).join("") + "</tr></thead><tbody>";
        } else {
          html += "<tr>" + cells.map(c => `<td>${inlineFmt(c)}</td>`).join("") + "</tr>";
        }
        continue;
      } else {
        closeTable();
      }

      if (/^-{3,}$/.test(line) || /^\*{3,}$/.test(line)) { closeLists(); html += "<hr>"; continue; }
      if (line.startsWith("#### ")) { closeLists(); html += `<h4>${inlineFmt(line.slice(5))}</h4>`; continue; }
      if (line.startsWith("### ")) { closeLists(); html += `<h3>${inlineFmt(line.slice(4))}</h3>`; continue; }
      if (line.startsWith("## ")) { closeLists(); html += `<h2>${inlineFmt(line.slice(3))}</h2>`; continue; }
      if (line.startsWith("# ")) { closeLists(); html += `<h1>${inlineFmt(line.slice(2))}</h1>`; continue; }
      if (line.startsWith("> ")) { closeLists(); html += `<blockquote>${inlineFmt(line.slice(2))}</blockquote>`; continue; }

      const ulM = line.match(/^[-*•]\s+(.*)$/);
      if (ulM) {
        if (inOl) { html += "</ol>"; inOl = false; }
        if (!inUl) { html += "<ul>"; inUl = true; }
        html += `<li>${inlineFmt(ulM[1])}</li>`;
        continue;
      }
      const olM = line.match(/^\d+\.\s+(.*)$/);
      if (olM) {
        if (inUl) { html += "</ul>"; inUl = false; }
        if (!inOl) { html += "<ol>"; inOl = true; }
        html += `<li>${inlineFmt(olM[1])}</li>`;
        continue;
      }
      closeLists();
      html += `<p>${inlineFmt(line)}</p>`;
    }
    closeLists();
    closeTable();
    return html;
  }

  function saveAiPrefs() {
    const keyEl = document.getElementById("inp-user-apikey");
    const codeEl = document.getElementById("inp-access-code");
    const modeEl = document.getElementById("inp-ai-mode");
    const modelEl = document.getElementById("inp-ai-model");
    const focusEl = document.getElementById("inp-ai-focus");
    if (keyEl) localStorage.setItem("kb_tuvi_user_api_key", keyEl.value.trim());
    if (codeEl) localStorage.setItem("kb_tuvi_access_code", codeEl.value.trim());
    if (modeEl) AI_STATE.mode = modeEl.value;
    if (modelEl) AI_STATE.model = modelEl.value;
    if (focusEl) AI_STATE.focusQuestion = focusEl.value;
  }

  function openAiTab() {
    const tabBtns = Array.from(document.querySelectorAll(".tab-btn"));
    const aiBtn = tabBtns.find(b => (b.getAttribute("onclick") || "").includes("'ai'"));
    if (aiBtn && typeof window.switchTab === "function") {
      window.switchTab("ai", aiBtn);
    }
  }

  async function runGeminiInterpret() {
    const curState = getStudioState();
    if (!curState) {
      alert("Bạn hãy bấm 'Xem Lá Số Ngay' ở khung bên trái trước khi luận giải AI nhé!");
      return;
    }
    saveAiPrefs();

    const userApiKey = (localStorage.getItem("kb_tuvi_user_api_key") || "").trim();
    const accessCode = (localStorage.getItem("kb_tuvi_access_code") || "").trim();
    const sidebarQ = (document.getElementById("inp-question")?.value || "").trim();
    const focusQuestion = (AI_STATE.focusQuestion || sidebarQ).trim();

    if (!SERVER_CFG.server_has_key && !userApiKey) {
      AI_STATE.error = "Máy chủ chưa cấu hình GEMINI_API_KEY chung. Vui lòng mở mục '🔑 Dùng Gemini API Key riêng' bên trên và dán Key miễn phí từ Google AI Studio!";
      mountGeminiCard();
      return;
    }
    if (SERVER_CFG.requires_access_code && !userApiKey && !accessCode) {
      AI_STATE.error = "Vui lòng nhập Mã mời (Access Code) từ chủ web, hoặc dán Gemini API Key miễn phí của riêng bạn ở mục bên dưới.";
      mountGeminiCard();
      return;
    }

    AI_STATE.loading = true;
    AI_STATE.error = "";
    AI_STATE.elapsed = 0;
    mountGeminiCard();

    if (timerHandle) clearInterval(timerHandle);
    const startMs = Date.now();
    timerHandle = setInterval(() => {
      AI_STATE.elapsed = Math.floor((Date.now() - startMs) / 1000);
      const tEl = document.getElementById("kb-ai-timer-sec");
      if (tEl) tEl.textContent = AI_STATE.elapsed + "s";
    }, 1000);

    try {
      const cleanPayload = Object.assign({}, curState);
      delete cleanPayload.export_html;

      const headers = { "Content-Type": "application/json" };
      if (userApiKey) headers["X-Gemini-Api-Key"] = userApiKey;

      const res = await fetch("/api/interpret", {
        method: "POST",
        headers,
        body: JSON.stringify({
          payload: cleanPayload,
          mode: AI_STATE.mode,
          focus_question: focusQuestion,
          model: AI_STATE.model,
          access_code: accessCode
        })
      });
      const json = await res.json();
      if (!json.ok) {
        AI_STATE.error = json.error || "Có lỗi xảy ra khi gọi Gemini API.";
      } else {
        AI_STATE.markdown = json.data.markdown || "";
        AI_STATE.metaInfo = json.data;
      }
    } catch (err) {
      AI_STATE.error = "Lỗi kết nối máy chủ AI: " + err.message;
    } finally {
      AI_STATE.loading = false;
      if (timerHandle) { clearInterval(timerHandle); timerHandle = null; }
      mountGeminiCard();
    }
  }

  function buildGeminiCardHtml() {
    const savedKey = localStorage.getItem("kb_tuvi_user_api_key") || "";
    const savedCode = localStorage.getItem("kb_tuvi_access_code") || "";

    const statusHtml = SERVER_CFG.server_has_key
      ? `<span class="ai-status-pill ai-status-ok">🟢 Đã kết nối Gemini API Free${SERVER_CFG.requires_access_code ? " (Cần Mã mời)" : " — Sẵn sàng luận giải"}</span>`
      : `<span class="ai-status-pill ai-status-warn">🟡 Chế độ BYOK — Dán Gemini API Key miễn phí của bạn bên dưới</span>`;

    const modelOpts = (SERVER_CFG.available_models || []).map(m =>
      `<option value="${escHtml(m.id)}" ${AI_STATE.model === m.id ? "selected" : ""}>${escHtml(m.label)}</option>`
    ).join("");

    const codeHtml = SERVER_CFG.requires_access_code ? `
      <div class="ai-field" style="margin-bottom:10px;">
        <label>🔐 Mã mời luận giải AI (Access Code)</label>
        <input type="password" id="inp-access-code" value="${escHtml(savedCode)}" onchange="window.__kbSaveAiPrefs()" placeholder="Nhập mã mời từ chủ web để dùng miễn phí...">
      </div>` : "";

    let resultHtml = "";
    if (AI_STATE.loading) {
      resultHtml = `
        <div class="ai-loader">
          <div class="ai-spinner"></div>
          <div>
            Đang luận giải chuyên sâu theo cổ pháp Đông – Tây bằng <code>${escHtml(AI_STATE.model)}</code>...
            <span id="kb-ai-timer-sec">${AI_STATE.elapsed}s</span>
            <div style="font-size:12px;font-weight:400;color:#7a6235;margin-top:2px;">Thường mất 8–20 giây để đối chiếu cổ thư & kiểm chứng chéo 5 hệ.</div>
          </div>
        </div>`;
    } else if (AI_STATE.error) {
      resultHtml = `<div class="ai-error"><strong>⚠️ Không thể luận giải:</strong> ${escHtml(AI_STATE.error)}</div>`;
    }

    if (AI_STATE.markdown) {
      const info = AI_STATE.metaInfo || {};
      const srcLbl = info.key_source === "user_byok" ? "Key cá nhân" : "Key Free máy chủ";
      const fbTxt = info.fallback_used ? " (Auto-fallback)" : "";
      const curState = getStudioState();
      const personName = (curState && curState.meta && curState.meta.name) ? curState.meta.name : "ĐƯƠNG SỐ";
      resultHtml += `
        <div style="margin-top:12px;">
          <div class="ai-report-header">
            <div>✨ <strong>BÀI LUẬN MỆNH THƯ AI — ${escHtml(personName.toUpperCase())}</strong> &nbsp;|&nbsp; <code>${escHtml(info.model_used || AI_STATE.model)}</code>${fbTxt} • ${info.elapsed_sec || 0}s • ${srcLbl}</div>
            <div style="display:flex;gap:6px;">
              <button type="button" class="btn-sec" onclick="window.__kbCopyAiReport()">📋 Copy Bài Luận</button>
              <button type="button" class="btn-sec" onclick="downloadHtmlReport()">💾 Tải Hồ Sơ + AI</button>
            </div>
          </div>
          <div class="ai-report-body">${renderMarkdownToHtml(AI_STATE.markdown)}</div>
        </div>`;
    }

    return `
      <h3>✨ Luận Giải Trực Tiếp Bằng AI Gemini (Miễn Phí — Chuẩn Cổ Pháp)</h3>
      ${statusHtml}
      <div class="ai-controls">
        <div class="ai-grid-2">
          <div class="ai-field">
            <label>Chế độ luận giải chuyên sâu</label>
            <select id="inp-ai-mode" onchange="window.__kbSaveAiPrefs()">
              <option value="full" ${AI_STATE.mode === "full" ? "selected" : ""}>⚖️ Đông – Tây Tổng Hợp (Tử Vi × Bát Tự × Thần Số Học — Khuyên dùng)</option>
              <option value="tuvi" ${AI_STATE.mode === "tuvi" ? "selected" : ""}>🌌 Thuần Tử Vi Đẩu Số (12 Cung, Tuần Triệt, Phi Tinh)</option>
              <option value="bazi" ${AI_STATE.mode === "bazi" ? "selected" : ""}>📜 Thuần Bát Tự Tứ Trụ (Dụng Thần, Điều Hầu, Đại Vận)</option>
              <option value="numerology" ${AI_STATE.mode === "numerology" ? "selected" : ""}>🔢 Thuần Thần Số Học (Pythagoras, Chaldean, 22 Arcana)</option>
              <option value="iching" ${AI_STATE.mode === "iching" ? "selected" : ""}>☯️ Giải Quẻ Kinh Dịch Lục Hào + Mai Hoa</option>
              <option value="qimen" ${AI_STATE.mode === "qimen" ? "selected" : ""}>🧭 Giải Bàn Kỳ Môn Độn Giáp (Hướng & Giờ Tốt)</option>
              <option value="all" ${AI_STATE.mode === "all" ? "selected" : ""}>🏛️ Hồ Sơ Đại Toàn Thư (Tổng hợp cả 5 Hệ)</option>
            </select>
          </div>
          <div class="ai-field">
            <label>Model Gemini Free Tier (Tự chuyển dự phòng nếu bận)</label>
            <select id="inp-ai-model" onchange="window.__kbSaveAiPrefs()">${modelOpts}</select>
          </div>
        </div>

        <div class="ai-field" style="margin-bottom:10px;">
          <label>Câu hỏi cụ thể / Chủ đề muốn AI phân tích kỹ (Tùy chọn)</label>
          <input id="inp-ai-focus" value="${escHtml(AI_STATE.focusQuestion)}" onchange="window.__kbSaveAiPrefs()" placeholder="VD: Năm nay có nên đổi việc/đầu tư không? Đường tình duyên và tài lộc thế nào?">
        </div>

        ${codeHtml}

        <button type="button" class="btn-ai-cta" style="margin-top:4px;font-size:14px;padding:11px;" onclick="window.__kbRunGemini()" ${AI_STATE.loading ? "disabled" : ""}>
          ${AI_STATE.loading ? "⏳ ĐANG LUẬN GIẢI..." : "✨ BẮT ĐẦU LUẬN GIẢI TRỰC TIẾP BẰNG AI"}
        </button>

        <details class="ai-byok-box" ${!SERVER_CFG.server_has_key ? "open" : ""}>
          <summary>🔑 Dùng Gemini API Key riêng của bạn (BYOK — Miễn phí 100%, không giới hạn lượt)</summary>
          <div style="margin-top:8px;color:#6c6257;line-height:1.5;">
            Key chỉ lưu trên trình duyệt của bạn (<code>localStorage</code>), không bao giờ gửi lưu về máy chủ.
            Lấy key miễn phí tại <a href="https://aistudio.google.com/apikey" target="_blank" rel="noopener" style="color:#8f1d1d;font-weight:700;">Google AI Studio ↗</a>.
          </div>
          <div class="ai-field" style="margin-top:8px;">
            <input type="password" id="inp-user-apikey" value="${escHtml(savedKey)}" onchange="window.__kbSaveAiPrefs()" placeholder="Dán chuỗi AIzaSy... vào đây (để trống nếu dùng Key chung của web)">
          </div>
        </details>
      </div>
      ${resultHtml}
    `;
  }

  function mountGeminiCard() {
    const paneAi = document.getElementById("pane-ai");
    if (!paneAi || !getStudioState()) return;
    let card = document.getElementById("kb-gemini-live-card");
    if (!card) {
      card = document.createElement("div");
      card.id = "kb-gemini-live-card";
      card.className = "card";
      paneAi.prepend(card);
    }
    card.innerHTML = buildGeminiCardHtml();
  }

  function injectShortcutButtons() {
    // 1. Nút tắt trên Sidebar (ngay sau nút Xem Lá Số Ngay)
    const primaryBtn = document.querySelector(".sidebar .btn-primary");
    if (primaryBtn && !document.getElementById("kb-sidebar-ai-btn")) {
      const aiBtn = document.createElement("button");
      aiBtn.type = "button";
      aiBtn.id = "kb-sidebar-ai-btn";
      aiBtn.className = "btn-ai-cta";
      aiBtn.textContent = "✨ LUẬN GIẢI AI (GEMINI)";
      aiBtn.onclick = async function () {
        if (!getStudioState() && typeof window.runAnalyze === "function") {
          await window.runAnalyze();
        }
        if (getStudioState()) {
          openAiTab();
          runGeminiInterpret();
        }
      };
      primaryBtn.insertAdjacentElement("afterend", aiBtn);
    }

    // 2. Nút tắt trên thanh công cụ kết quả
    const toolbar = document.querySelector(".toolbar-right");
    if (toolbar && !document.getElementById("kb-toolbar-ai-btn")) {
      const tbBtn = document.createElement("button");
      tbBtn.type = "button";
      tbBtn.id = "kb-toolbar-ai-btn";
      tbBtn.className = "action-btn";
      tbBtn.style.cssText = "background:#fcf6e8;border-color:#a87928;color:#7a4e0b;";
      tbBtn.textContent = "✨ Luận AI Ngay";
      tbBtn.onclick = function () {
        openAiTab();
        if (!AI_STATE.markdown && !AI_STATE.loading) runGeminiInterpret();
      };
      toolbar.prepend(tbBtn);
    }
  }

  function hookStudioFunctions() {
    // Hook renderAiPane để luôn giữ Trạm Gemini AI ở đầu Tab 6 dù giao diện gốc có cập nhật
    if (typeof window.renderAiPane === "function" && !window.__kbOrigRenderAiPane) {
      window.__kbOrigRenderAiPane = window.renderAiPane;
      window.renderAiPane = function () {
        window.__kbOrigRenderAiPane.apply(this, arguments);
        mountGeminiCard();
      };
    }

    // Hook downloadHtmlReport để nhúng kèm bài luận AI vào file HTML xuất về máy
    if (typeof window.downloadHtmlReport === "function" && !window.__kbOrigDownloadHtml) {
      window.__kbOrigDownloadHtml = window.downloadHtmlReport;
      window.downloadHtmlReport = function () {
        const curState = getStudioState();
        if (!curState || !curState.export_html) return;
        if (!AI_STATE.markdown) {
          return window.__kbOrigDownloadHtml.apply(this, arguments);
        }
        const aiSection = `
          <section style="max-width:1100px;margin:24px auto;padding:24px 28px;background:#fffefc;border:1.5px solid #d4c4a8;border-radius:10px;line-height:1.75;font-family:'Segoe UI',sans-serif;">
            <h2 style="color:#8f1d1d;border-bottom:2px solid #efe4d2;padding-bottom:8px;margin-top:0;">✨ PHẦN LUẬN GIẢI CHUYÊN SÂU BẰNG AI (KB-TUVI × GEMINI)</h2>
            ${renderMarkdownToHtml(AI_STATE.markdown)}
          </section></body>`;
        const merged = curState.export_html.replace("</body>", aiSection);
        const blob = new Blob([merged], { type: "text/html;charset=utf-8" });
        const a = document.createElement("a");
        a.href = URL.createObjectURL(blob);
        a.download = `HoSoTuVi_AI_${(curState.meta.name || "LaSo").replace(/\s+/g, "_")}.html`;
        a.click();
      };
    }
  }

  async function loadServerConfig() {
    try {
      const res = await fetch("/api/config");
      const json = await res.json();
      if (json.ok && json.config) {
        Object.assign(SERVER_CFG, json.config);
        AI_STATE.model = SERVER_CFG.default_model || "gemini-3.8-flash";
        mountGeminiCard();
      }
    } catch (e) {
      console.warn("[KB-TUVI AI] Không tải được /api/config:", e);
    }
  }

  window.__kbSaveAiPrefs = saveAiPrefs;
  window.__kbRunGemini = runGeminiInterpret;
  window.__kbSetPreferredMode = function (mode, focusQuestion) {
    if (mode) AI_STATE.mode = mode;
    if (typeof focusQuestion === "string") AI_STATE.focusQuestion = focusQuestion;
    const modeEl = document.getElementById("inp-ai-mode");
    if (modeEl && mode) modeEl.value = mode;
    const focusEl = document.getElementById("inp-ai-focus");
    if (focusEl && typeof focusQuestion === "string") focusEl.value = focusQuestion;
  };
  window.__kbRunGeminiMode = function (mode) {
    AI_STATE.mode = mode || "full";
    openAiTab();
    mountGeminiCard();
    runGeminiInterpret();
  };
  window.__kbCopyAiReport = function () {
    if (!AI_STATE.markdown) return;
    navigator.clipboard.writeText(AI_STATE.markdown);
    alert("Đã copy toàn bộ bài luận AI vào Clipboard!");
  };

  function boot() {
    injectStyles();
    injectShortcutButtons();
    hookStudioFunctions();
    loadServerConfig();
    if (getStudioState()) mountGeminiCard();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
