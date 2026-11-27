/**
 * web_numerology_sdk.js — Isomorphic Zero-Dependency Numerology SDK cho Dự Án Web (Next.js / React / Vue / Node / Edge)
 * Đồng bộ thuật toán 1:1 với engine_numerology.py của kb-tuvi v3.0:
 *   - Chuẩn hóa tiếng Việt NFD + Đ->D + Phân loại chữ Y theo ngữ cảnh âm tiết Việt/Quốc tế
 *   - Song hệ Pythagoras Việt Nam (giữ số 10, 11, 22/4) & Pythagoras Quốc tế (3 trụ bảo toàn 11/2, 22/4, 33/6)
 *   - Chaldean Babylon cổ đại (1..8 & Số Kép Huyền Bí 10..52) + Ma trận Định mệnh 22 Arcana
 *   - Biểu đồ 3x3 (Ngày sinh, Họ tên, Tổ hợp), 8 Mũi tên Đầy, 7 Mũi tên Trống, Kim tự tháp 4 Đỉnh cao & Chu kỳ 9 Năm
 *
 * Cách dùng trong Next.js / React / TypeScript:
 *   import { computeNumerologyProfile } from './web_numerology_sdk.js';
 *   const profile = computeNumerologyProfile({ birthDate: '1992-08-16', fullName: 'Nguyễn Minh Quân', targetYear: 2026 });
 */

const PYTHAGOREAN_MAP = {
  A:1, J:1, S:1, B:2, K:2, T:2, C:3, L:3, U:3,
  D:4, M:4, V:4, E:5, N:5, W:5, F:6, O:6, X:6,
  G:7, P:7, Y:7, H:8, Q:8, Z:8, I:9, R:9
};

const CHALDEAN_MAP = {
  A:1, I:1, J:1, Q:1, Y:1, B:2, K:2, R:2, C:3, G:3, L:3, S:3,
  D:4, M:4, T:4, E:5, H:5, N:5, X:5, U:6, V:6, W:6, O:7, Z:7, F:8, P:8
};

const CORE_VOWELS = new Set(["A", "E", "I", "O", "U"]);
const KARMIC_DEBTS = new Set([13, 14, 16, 19]);

const ARROWS_DEF = [
  [[1,2,3], "Mũi tên Kế Hoạch (1-2-3)", "Mũi tên Hỗn Độ (Trống 1-2-3)"],
  [[4,5,6], "Mũi tên Ý Chí (4-5-6)", "Mũi tên Nhạy Cảm / Dễ Nản (Trống 4-5-6)"],
  [[7,8,9], "Mũi tên Hoạt Động (7-8-9)", "Mũi tên Thụ Động / Trì Hoãn (Trống 7-8-9)"],
  [[1,4,7], "Mũi tên Thực Tế (1-4-7)", "Mũi tên Thiếu Thực Tế (Trống 1-4-7)"],
  [[2,5,8], "Mũi tên Cân Bằng Cảm Xúc (2-5-8)", "Mũi tên Nhạy Cảm Nội Tâm (Trống 2-5-8)"],
  [[3,6,9], "Mũi tên Trí Nhớ & Sáng Tạo (3-6-9)", "Mũi tên Đãng Trí Ngắn Hạn (Trống 3-6-9)"],
  [[1,5,9], "Mũi tên Quyết Tâm (1-5-9)", "Mũi tên Trì Hoãn Quyết Định (Trống 1-5-9)"],
  [[3,5,7], "Mũi tên Tâm Linh / Nhạy Bén (3-5-7)", "Mũi tên Hoài Nghi Thực Chứng (Trống 3-5-7)"]
];

export function stripVnAccents(text = "") {
  return String(text)
    .replace(/Đ/g, "D")
    .replace(/đ/g, "d")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toUpperCase();
}

export function tokenizeCleanWords(text = "") {
  return stripVnAccents(text).match(/[A-Z]+/g) || [];
}

export function classifyWordLetters(word, yMode = "contextual") {
  const chars = [...word];
  return chars.map((ch, idx) => {
    let role = "C";
    if (CORE_VOWELS.has(ch)) {
      role = "V";
    } else if (ch === "Y") {
      if (yMode === "always_vowel") role = "V";
      else if (yMode === "always_consonant") role = "C";
      else {
        const prevV = idx > 0 && CORE_VOWELS.has(chars[idx - 1]);
        const nextV = idx < chars.length - 1 && CORE_VOWELS.has(chars[idx + 1]);
        role = (prevV || nextV) ? "C" : "V";
      }
    }
    return {
      char: ch,
      role,
      pythagorean: PYTHAGOREAN_MAP[ch] || 0,
      chaldean: CHALDEAN_MAP[ch] || 0
    };
  });
}

export function sumDigits(n) {
  return [...String(Math.abs(Math.trunc(n)))].reduce((acc, d) => acc + Number(d), 0);
}

export function reduceNumber(n, { keepMasters = [11, 22, 33], keepTen = false } = {}) {
  let curr = Math.abs(Math.trunc(n));
  const steps = [curr];
  let karmic = KARMIC_DEBTS.has(curr) ? curr : null;
  const masterSet = new Set(keepMasters);

  while (curr > 9) {
    if (masterSet.has(curr)) break;
    if (keepTen && curr === 10) break;
    curr = sumDigits(curr);
    steps.push(curr);
    if (karmic === null && KARMIC_DEBTS.has(curr)) karmic = curr;
  }

  let base = curr;
  while (base > 9) base = sumDigits(base);
  const code = (curr === 11 || curr === 22 || curr === 33) ? `${curr}/${base}` : String(curr);
  return { display: curr, base, code, steps, karmic };
}

export function reduceArcana22(n) {
  let curr = Math.abs(Math.trunc(n));
  if (curr === 0) return 22;
  while (curr > 22) curr = sumDigits(curr);
  return curr || 22;
}

export function build3x3Grid(digits = []) {
  const counts = { 1:0, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0, 8:0, 9:0 };
  for (const d of digits) {
    if (d >= 1 && d <= 9) counts[d] += 1;
  }
  const presentArrows = [];
  const emptyArrows = [];
  for (const [combo, fullTitle, emptyTitle] of ARROWS_DEF) {
    const [a, b, c] = combo;
    if (counts[a] > 0 && counts[b] > 0 && counts[c] > 0) presentArrows.push({ digits: combo, name: fullTitle });
    else if (counts[a] === 0 && counts[b] === 0 && counts[c] === 0) emptyArrows.push({ digits: combo, name: emptyTitle });
  }
  return {
    counts,
    rowsTopToBottom: [
      [3, 6, 9].map(d => ({ digit: d, count: counts[d], text: String(d).repeat(counts[d]) })),
      [2, 5, 8].map(d => ({ digit: d, count: counts[d], text: String(d).repeat(counts[d]) })),
      [1, 4, 7].map(d => ({ digit: d, count: counts[d], text: String(d).repeat(counts[d]) }))
    ],
    presentArrows,
    emptyArrows
  };
}

export function computeNumerologyProfile({
  birthDate,
  fullName = "",
  nickname = "",
  targetYear = new Date().getFullYear(),
  targetMonth = new Date().getMonth() + 1,
  targetDay = new Date().getDate(),
  school = "vn",
  yMode = "contextual"
} = {}) {
  const [by, bm, bd] = String(birthDate).split("-").map(Number);
  const allBirthDigits = [...`${String(by).padStart(4, "0")}${String(bm).padStart(2, "0")}${String(bd).padStart(2, "0")}`].map(Number);

  const yRed = reduceNumber(sumDigits(by));
  const mRed = reduceNumber(bm);
  const dRed = reduceNumber(bd);

  const lpIntl = reduceNumber(yRed.display + mRed.display + dRed.display);
  const lpVn = reduceNumber(allBirthDigits.reduce((a, b) => a + b, 0), { keepMasters: [11, 22, 33], keepTen: true });
  const lp = school === "vn" ? lpVn : lpIntl;

  const words = tokenizeCleanWords(fullName);
  const wordDetails = words.map(w => {
    const letters = classifyWordLetters(w, yMode);
    const pythSum = letters.reduce((s, x) => s + x.pythagorean, 0);
    const vowelSum = letters.filter(x => x.role === "V").reduce((s, x) => s + x.pythagorean, 0);
    const consSum = letters.filter(x => x.role === "C").reduce((s, x) => s + x.pythagorean, 0);
    const chaldeanSum = letters.reduce((s, x) => s + x.chaldean, 0);
    return {
      word: w,
      letters,
      pythReduced: reduceNumber(pythSum),
      vowelReduced: vowelSum > 0 ? reduceNumber(vowelSum) : { display: 0, base: 0 },
      consReduced: consSum > 0 ? reduceNumber(consSum) : { display: 0, base: 0 },
      chaldeanSum
    };
  });

  const allNameDigits = wordDetails.flatMap(w => w.letters.map(l => l.pythagorean));
  const expression = words.length ? reduceNumber(wordDetails.reduce((s, w) => s + w.pythReduced.display, 0)) : null;
  const soulUrge = words.length ? reduceNumber(wordDetails.reduce((s, w) => s + w.vowelReduced.display, 0)) : null;
  const personality = words.length ? reduceNumber(wordDetails.reduce((s, w) => s + w.consReduced.display, 0)) : null;
  const maturity = expression ? reduceNumber(lp.base + expression.base) : null;
  const chaldeanTotal = wordDetails.reduce((s, w) => s + w.chaldeanSum, 0);

  const p1End = 36 - lp.base;
  const p1 = reduceNumber(mRed.base + dRed.base, { keepMasters: [11, 22] });
  const p2 = reduceNumber(dRed.base + yRed.base, { keepMasters: [11, 22] });
  const p3 = reduceNumber(p1.display + p2.display, { keepMasters: [11, 22] });
  const p4 = reduceNumber(mRed.base + yRed.base, { keepMasters: [11, 22] });
  const c1 = Math.abs(mRed.base - dRed.base);
  const c2 = Math.abs(dRed.base - yRed.base);
  const c3 = Math.abs(c1 - c2);
  const c4 = Math.abs(mRed.base - yRed.base);

  const personalYear = reduceNumber(dRed.base + mRed.base + sumDigits(targetYear), { keepMasters: [] }).base;
  const personalMonth = reduceNumber(personalYear + targetMonth, { keepMasters: [] }).base;
  const personalDay = reduceNumber(personalMonth + targetDay, { keepMasters: [] }).base;

  const dmPortrait = reduceArcana22(bd);
  const dmHeaven = reduceArcana22(bm);
  const dmEarth = reduceArcana22(sumDigits(by));
  const dmKarmic = reduceArcana22(dmPortrait + dmHeaven + dmEarth);
  const dmCenter = reduceArcana22(dmPortrait + dmHeaven + dmEarth + dmKarmic);

  return {
    meta: { birthDate, fullName, cleanName: words.join(" "), nickname, school, yMode, targetYear },
    lifePath: { ...lp, vnCode: lpVn.code, intlCode: lpIntl.code },
    birthday: dRed,
    attitude: reduceNumber(bd + bm, { keepMasters: [11, 22] }),
    expression,
    soulUrge,
    personality,
    maturity,
    chaldean: words.length ? { compound: chaldeanTotal, single: reduceNumber(chaldeanTotal, { keepMasters: [] }).base } : null,
    grids: {
      birth: build3x3Grid(allBirthDigits.filter(d => d > 0)),
      name: words.length ? build3x3Grid(allNameDigits) : null,
      composite: build3x3Grid([...allBirthDigits.filter(d => d > 0), ...allNameDigits])
    },
    pinnacles: [
      { stage: 1, code: p1.code, challenge: c1, endAge: p1End, year: by + p1End },
      { stage: 2, code: p2.code, challenge: c2, endAge: p1End + 9, year: by + p1End + 9 },
      { stage: 3, code: p3.code, challenge: c3, endAge: p1End + 18, year: by + p1End + 18 },
      { stage: 4, code: p4.code, challenge: c4, endAge: 99, year: by + p1End + 27 }
    ],
    cycles: { personalYear, personalMonth, personalDay },
    destinyMatrix22: { portrait: dmPortrait, heaven: dmHeaven, earth: dmEarth, karmicTail: dmKarmic, comfortCenter: dmCenter },
    words: wordDetails
  };
}
