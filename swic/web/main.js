let currentWord = "";

// main.js

// Helper function to display metadata
function displayMetadata(metadata) {
  const container = document.getElementById("metadataArea");
  container.innerHTML = ""; // Clear previous content

  if (!metadata || metadata.length === 0) {
    container.classList.add("hidden");
    return;
  }

  container.classList.remove("hidden");

  const ul = document.createElement("ul");
  // Change: Use index (i) when iterating
  metadata.forEach((item, i) => {
    const li = document.createElement("li");

    // Check if item is a URL to make it a link
    if (item.startsWith("http")) {
      const a = document.createElement("a");
      a.href = item;
      a.textContent = item;
      a.target = "_blank"; // Open link in new tab
      li.appendChild(a);
    } else {
      li.textContent = item;
    }

    // New: Add class to the second field (Author), which is index 1
    if (i === 2) {
      li.classList.add("metadata-author");
    }

    ul.appendChild(li);
  });
  container.appendChild(ul);
}

function setWritingMode(mode) {
  const contextArea = document.getElementById("contextArea");
  const tategakiBtn = document.getElementById("tategakiBtn");
  const yokogakiBtn = document.getElementById("yokogakiBtn");

  if (mode === "yokogaki") {
    contextArea.classList.add("yokogaki");
    yokogakiBtn.classList.add("active");
    tategakiBtn.classList.remove("active");
  } else {
    // Default is Tategaki
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
  // Expecting a result object: {text: string, count: number, metadata: string[]}
  const result = await eel.search_word(word)();

  // Check if the result is the expected object structure
  if (
    typeof result === "object" &&
    result !== null &&
    "text" in result &&
    "count" in result &&
    "metadata" in result
  ) {
    contextArea.innerHTML = highlight(result.text, currentWord);
    displayMetadata(result.metadata); // Display metadata
    // Show current/total after initial search
    setTimeout(async () => {
      const state = await eel.get_current_state()();
      if (
        state &&
        typeof state.current === 'number' &&
        typeof state.total === 'number' &&
        state.total > 0
      ) {
        status.innerText = `Results for '${word}': ${state.current + 1}/${state.total}`;
      }
    }, 0);

    if (result.count > 0) {
      // Display the total count
      status.innerText = `Results for “${word}”: ${result.count} entries found.`;
    } else {
      // Display the error message (e.g., "No results found...")
      status.innerText = result.text;
    }
  } else {
    // Fallback for unexpected results (e.g., if the backend failed to return JSON)
    contextArea.innerHTML = "";
    status.innerText = "An unknown search error occurred.";
    metadataArea.classList.add("hidden");
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
  // Expecting a result object: {text: string, count: number, metadata: string[]}
  const result = await eel.search_word(word)();

  // Check if the result is the expected object structure
  if (
    typeof result === "object" &&
    result !== null &&
    "text" in result &&
    "count" in result &&
    "metadata" in result
  ) {
    contextArea.innerHTML = highlight(result.text, currentWord);
    displayMetadata(result.metadata); // Display metadata
    // Show current/total after initial search
    setTimeout(async () => {
      const state = await eel.get_current_state()();
      if (
        state &&
        typeof state.current === 'number' &&
        typeof state.total === 'number' &&
        state.total > 0
      ) {
        status.innerText = `Results for '${word}': ${state.current + 1}/${state.total}`;
      }
    }, 0);

    if (result.count > 0) {
      // Display the total count
      status.innerText = `Results for “${word}”: ${result.count} entries found.`;
    } else {
      // Display the error message (e.g., "No results found...")
      status.innerText = result.text;
    }
  } else {
    // Fallback for unexpected results (e.g., if the backend failed to return JSON)
    contextArea.innerHTML = "";
    status.innerText = "An unknown search error occurred.";
    metadataArea.classList.add("hidden");
  }
}

async function prev() {
  // Expecting a result object: {text: string, metadata: string[]}
  const result = await eel.prev_result()();
  if (
    typeof result === "object" &&
    result !== null &&
    "text" in result &&
    "metadata" in result
  ) {
    document.getElementById("contextArea").innerHTML = highlight(
      result.text,
      currentWord
    );
    displayMetadata(result.metadata); // Update metadata
    // Update status with current/total
    const statePrev = await eel.get_current_state()();
    if (
      statePrev &&
      typeof statePrev.current === 'number' &&
      typeof statePrev.total === 'number' &&
      statePrev.total > 0
    ) {
      const status = document.getElementById("status");
      status.innerText = `Results for '${currentWord}': ${statePrev.current + 1}/${statePrev.total}`;
    }
  }
}

async function next() {
  // Expecting a result object: {text: string, metadata: string[]}
  const result = await eel.next_result()();
  if (
    typeof result === "object" &&
    result !== null &&
    "text" in result &&
    "metadata" in result
  ) {
    document.getElementById("contextArea").innerHTML = highlight(
      result.text,
      currentWord
    );
    displayMetadata(result.metadata); // Update metadata
    // Update status with current/total
    const stateNext = await eel.get_current_state()();
    if (
      stateNext &&
      typeof stateNext.current === 'number' &&
      typeof stateNext.total === 'number' &&
      stateNext.total > 0
    ) {
      const status = document.getElementById("status");
      status.innerText = `Results for '${currentWord}': ${stateNext.current + 1}/${stateNext.total}`;
    }
  }
}

function readAloud() {
  eel.read_context()();
}

function highlight(text, word) {
  if (!word || !text) return text || "";
  // The python backend is responsible for wrapping the word in <strong>
  // This client-side function just ensures no old bolding is missed.
  return text.split(word).join(`<strong>${word}</strong>`);
}

window.onload = async function () {
  const select = document.getElementById("sourceSelect");
  // Initialize font selector
  const fontSelect = document.getElementById("fontSelect");
  if (fontSelect) {
    fontSelect.addEventListener("change", () => setFont(fontSelect.value));
    // Default to Hina Mincho
    setFont(fontSelect.value || "Hina Mincho");
  }
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

  // When user changes source
  select.addEventListener("change", async () => {
    const file = select.value;
    const status = document.getElementById("status");
    status.innerText = "Switching source...";
    const msg = await eel.set_source(file)();
    status.innerText = msg;

    // Clear display after source switch
    document.getElementById("contextArea").innerHTML = "";
    document.getElementById("metadataArea").classList.add("hidden");
  });
};
