// Clean frontend script with kuromoji-based readings and existing features

let currentWord = "";
let readingsEnabled = false;
let kuromojiTokenizer = null;
let kuromojiReady = false;
let lastBaseHtml = ""; // highlighted HTML without ruby (source of truth)
let lastBlockText = ""; // raw block text from backend (with <br>), before highlight

// Helper: display metadata list below the context
function displayMetadata(metadata) {
  const container = document.getElementById("metadataArea");
  container.innerHTML = "";
  if (!metadata || metadata.length === 0) {
    container.classList.add("hidden");
    return;
  }
  container.classList.remove("hidden");
  const ul = document.createElement("ul");
  metadata.forEach((item, i) => {
    const li = document.createElement("li");
    if (typeof item === "string" && item.startsWith("http")) {
      const a = document.createElement("a");
      a.href = item;
      a.textContent = item;
      a.target = "_blank";
      li.appendChild(a);
    } else {
      li.textContent = item;
    }
    if (i === 2) li.classList.add("metadata-author");
    ul.appendChild(li);
  });
  container.appendChild(ul);
}

// Writing mode toggle
function setWritingMode(mode) {
  const contextArea = document.getElementById("contextArea");
  const tategakiBtn = document.getElementById("tategakiBtn");
  const yokogakiBtn = document.getElementById("yokogakiBtn");
  if (mode === "yokogaki") {
    contextArea.classList.add("yokogaki");
    yokogakiBtn.classList.add("active");
    tategakiBtn.classList.remove("active");
  } else {
    contextArea.classList.remove("yokogaki");
    tategakiBtn.classList.add("active");
    yokogakiBtn.classList.remove("active");
  }
}

// Font selection for context area only
const FONT_MAP = {
  "Hina Mincho": "'Hina Mincho', 'Noto Serif JP', serif",
  "Noto Serif JP": "'Noto Serif JP', serif",
  "Noto Sans JP": "'Noto Sans JP', sans-serif",
  "Shippori Mincho": "'Shippori Mincho', serif",
  "Kosugi Maru": "'Kosugi Maru', sans-serif",
  "M PLUS Rounded 1c": "'M PLUS Rounded 1c', sans-serif",
  "Sawarabi Mincho": "'Sawarabi Mincho', serif",
  "Yuji Syuku": "'Yuji Syuku', serif",
};
function setFont(name) {
  const fam = FONT_MAP[name] || FONT_MAP["Hina Mincho"];
  document.documentElement.style.setProperty("--context-font", fam);
}

// ---- Ruby (furigana) support ----
const CJK_RE = /[\u4E00-\u9FFF\u3400-\u4DBF\uF900-\uFAFF\u3005\u3007]/;

function katakanaToHiragana(text) {
  if (!text) return text;
  return text.replace(/[\u30A1-\u30F6]/g, (ch) =>
    String.fromCharCode(ch.charCodeAt(0) - 0x60)
  );
}

function initKuromoji() {
  try {
    if (!window.kuromoji) return;
    window.kuromoji
      .builder({ dicPath: "kuromoji/dict" })
      .build((err, tokenizer) => {
        if (err) {
          console.error("kuromoji build error:", err);
          return;
        }
        kuromojiTokenizer = tokenizer;
        kuromojiReady = true;
        console.log("kuromoji ready");
      });
  } catch (e) {
    console.warn("kuromoji init failed:", e);
  }
}

function annotateWithRuby(text) {
  if (!text) return text;
  if (!kuromojiReady || !kuromojiTokenizer) return text; // do not fake readings
  const tokens = kuromojiTokenizer.tokenize(text);
  let out = "";
  for (const t of tokens) {
    const surface = t.surface_form || "";
    const reading = katakanaToHiragana(t.reading || "");
    if (!surface) continue;
    if (!reading || !CJK_RE.test(surface)) {
      out += surface;
      continue;
    }
    out += annotateKanjiOnly(surface, reading);
  }
  return out;
}

function isKanaChar(ch) {
  return /[\u3041-\u3096\u30A1-\u30FA\u30FC]/.test(ch);
}

// Split hiragana into mora units: keep small kana/long mark with previous, sokuon with next
function splitMora(hira) {
  const out = [];
  const small = /[ゃゅょぁぃぅぇぉゎ]/;
  let pendingSokuon = false;
  for (let i = 0; i < hira.length; i++) {
    const ch = hira[i];
    if (ch === "っ") {
      pendingSokuon = true;
      continue;
    }
    if (small.test(ch) || ch === "ー") {
      if (out.length) out[out.length - 1] += ch;
      else out.push(ch);
      continue;
    }
    let unit = ch;
    if (pendingSokuon) {
      unit = "っ" + unit;
      pendingSokuon = false;
    }
    out.push(unit);
  }
  if (pendingSokuon) out.push("っ");
  return out;
}

function annotateKanjiOnly(surface, readingHira) {
  const runs = [];
  let i = 0;
  const pushRun = (type, text) => {
    if (text) runs.push({ type, text });
  };
  while (i < surface.length) {
    const ch = surface[i];
    if (CJK_RE.test(ch)) {
      let j = i + 1;
      while (j < surface.length && CJK_RE.test(surface[j])) j++;
      pushRun("kanji", surface.slice(i, j));
      i = j;
      continue;
    }
    if (isKanaChar(ch)) {
      let j = i + 1;
      while (j < surface.length && isKanaChar(surface[j])) j++;
      pushRun("kana", katakanaToHiragana(surface.slice(i, j)));
      i = j;
      continue;
    }
    let j = i + 1;
    while (
      j < surface.length &&
      !CJK_RE.test(surface[j]) &&
      !isKanaChar(surface[j])
    )
      j++;
    pushRun("other", surface.slice(i, j));
    i = j;
  }

  let reading = readingHira;
  for (const r of runs) {
    if (r.type === "kana") {
      if (reading.startsWith(r.text)) reading = reading.slice(r.text.length);
    }
  }
  for (let idx = runs.length - 1; idx >= 0; idx--) {
    const r = runs[idx];
    if (r.type === "kana") {
      if (reading.endsWith(r.text))
        reading = reading.slice(0, reading.length - r.text.length);
    } else if (r.type === "kanji") {
      break;
    }
  }

  const kanjiRuns = runs.filter((r) => r.type === "kanji");
  if (kanjiRuns.length === 0 || reading.length === 0) return surface;

  // Allocate readings by mora, not raw characters
  const mora = splitMora(reading);
  const totalMora = mora.length;
  const totalKanji = kanjiRuns.reduce((s, r) => s + r.text.length, 0);
  const allocated = [];
  let used = 0;
  for (let idx = 0; idx < kanjiRuns.length; idx++) {
    const r = kanjiRuns[idx];
    let share;
    if (idx === kanjiRuns.length - 1) {
      share = Math.max(1, totalMora - used);
    } else {
      share = Math.max(1, Math.round((r.text.length / totalKanji) * totalMora));
      const remainingRuns = kanjiRuns.length - 1 - idx;
      if (used + share + remainingRuns > totalMora) {
        share = Math.max(1, totalMora - used - remainingRuns);
      }
    }
    allocated.push(mora.slice(used, used + share).join(""));
    used += share;
  }

  let ki = 0;
  let out = "";
  for (const r of runs) {
    if (r.type === "kanji") {
      const rt = allocated[ki++] || "";
      out += rt ? `<ruby><rb>${r.text}</rb><rt>${rt}</rt></ruby>` : r.text;
    } else {
      out += r.text;
    }
  }
  return out || surface;
}

function applyRubyToNode(node) {
  if (!node) return;
  if (node.nodeType === Node.ELEMENT_NODE) {
    const tag = node.tagName && node.tagName.toLowerCase();
    if (tag === "ruby" || tag === "rt" || tag === "script" || tag === "style")
      return;
  }
  if (node.nodeType === Node.TEXT_NODE) {
    const parent = node.parentNode;
    const html = annotateWithRuby(node.nodeValue);
    if (html !== node.nodeValue) {
      const span = document.createElement("span");
      span.innerHTML = html;
      parent.replaceChild(span, node);
      return;
    }
  }
  const children = Array.from(node.childNodes);
  for (const child of children) applyRubyToNode(child);
}

function annotateBlockHtml(blockHtml) {
  const withNewlines = (blockHtml || "").replace(/<br\s*\/?>/gi, "\n");
  const plain = withNewlines.replace(/<[^>]+>/g, "");
  const annotated = annotateWithRuby(plain);
  return annotated.replace(/\n/g, "<br>");
}

function renderContext(text) {
  const contextArea = document.getElementById("contextArea");
  lastBlockText = text || "";
  lastBaseHtml = highlight(lastBlockText, currentWord);
  if (readingsEnabled && kuromojiReady) {
    const annotatedBlock = annotateBlockHtml(lastBlockText);
    contextArea.innerHTML = highlight(annotatedBlock, currentWord);
  } else {
    contextArea.innerHTML = lastBaseHtml;
  }
}

async function search() {
  const word = document.getElementById("wordInput").value.trim();
  const size = document.getElementById("contextSelect").value;
  const contextArea = document.getElementById("contextArea");
  const status = document.getElementById("status");
  const metadataArea = document.getElementById("metadataArea");

  if (!word) {
    status.innerText = "Please enter a word.";
    metadataArea.classList.add("hidden");
    return;
  }

  currentWord = word;
  status.innerText = "Searching...";
  contextArea.innerHTML = "";
  metadataArea.classList.add("hidden");

  await eel.set_context_size(size)();
  const result = await eel.search_word(word)();

  if (
    typeof result === "object" &&
    result !== null &&
    "text" in result &&
    "count" in result &&
    "metadata" in result
  ) {
    renderContext(result.text);
    displayMetadata(result.metadata);
    const state = await eel.get_current_state()();
    if (
      state &&
      typeof state.current === "number" &&
      typeof state.total === "number" &&
      state.total > 0
    ) {
      status.innerText = `Results for '${word}': ${state.current + 1}/${
        state.total
      }`;
    } else {
      status.innerText = result.text;
    }
  } else {
    contextArea.innerHTML = "";
    status.innerText = "An unknown search error occurred.";
    metadataArea.classList.add("hidden");
  }
}

async function prev() {
  const result = await eel.prev_result()();
  if (
    typeof result === "object" &&
    result !== null &&
    "text" in result &&
    "metadata" in result
  ) {
    renderContext(result.text);
    displayMetadata(result.metadata);
    const statePrev = await eel.get_current_state()();
    if (
      statePrev &&
      typeof statePrev.current === "number" &&
      typeof statePrev.total === "number" &&
      statePrev.total > 0
    ) {
      const status = document.getElementById("status");
      status.innerText = `Results for '${currentWord}': ${
        statePrev.current + 1
      }/${statePrev.total}`;
    }
  }
}

async function next() {
  const result = await eel.next_result()();
  if (
    typeof result === "object" &&
    result !== null &&
    "text" in result &&
    "metadata" in result
  ) {
    renderContext(result.text);
    displayMetadata(result.metadata);
    const stateNext = await eel.get_current_state()();
    if (
      stateNext &&
      typeof stateNext.current === "number" &&
      typeof stateNext.total === "number" &&
      stateNext.total > 0
    ) {
      const status = document.getElementById("status");
      status.innerText = `Results for '${currentWord}': ${
        stateNext.current + 1
      }/${stateNext.total}`;
    }
  }
}

function readAloud() {
  eel.read_context()();
}

function highlight(text, word) {
  if (!word || !text) return text || "";
  return text.split(word).join(`<strong>${word}</strong>`);
}

window.onload = async function () {
  // Init kuromoji (non-blocking)
  initKuromoji();

  const select = document.getElementById("sourceSelect");
  const readingToggle = document.getElementById("readingToggle");
  if (readingToggle) {
    readingToggle.addEventListener("change", () => {
      readingsEnabled = readingToggle.checked;
      const area = document.getElementById("contextArea");
      // Always restore the base HTML, then optionally apply ruby
      area.innerHTML = lastBaseHtml;
      if (readingsEnabled && kuromojiReady) {
        applyRubyToNode(area);
      }
    });
  }

  // Initialize font selector
  const fontSelect = document.getElementById("fontSelect");
  if (fontSelect) {
    fontSelect.addEventListener("change", () => setFont(fontSelect.value));
    setFont(fontSelect.value || "Hina Mincho");
  }

  // Populate sources
  const sources = await eel.get_sources()();
  if (sources && sources.length > 0) {
    sources.forEach((s) => {
      const opt = document.createElement("option");
      opt.value = s;
      opt.textContent = s.replace(".csv", "");
      select.appendChild(opt);
    });
  } else {
    const opt = document.createElement("option");
    opt.textContent = "No sources found";
    select.appendChild(opt);
  }

  // Source change handler
  select.addEventListener("change", async () => {
    const file = select.value;
    const status = document.getElementById("status");
    status.innerText = "Switching source...";
    const msg = await eel.set_source(file)();
    status.innerText = msg;
    document.getElementById("contextArea").innerHTML = "";
    document.getElementById("metadataArea").classList.add("hidden");
  });
};
