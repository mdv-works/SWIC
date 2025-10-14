let currentWord = "";

// main.js

async function search() {
  const word = document.getElementById("wordInput").value.trim();
  const size = document.getElementById("contextSelect").value;
  const contextArea = document.getElementById("contextArea");
  const status = document.getElementById("status");

  if (!word) {
    status.innerText = "Please enter a word.";
    return;
  }

  currentWord = word;
  status.innerText = "Searching...";
  contextArea.innerHTML = "";

  await eel.set_context_size(size)();
  // Expecting a result object: {text: string, count: number}
  const result = await eel.search_word(word)();

  // Check if the result is the expected object structure
  if (
    typeof result === "object" &&
    result !== null &&
    "text" in result &&
    "count" in result
  ) {
    contextArea.innerHTML = highlight(result.text, currentWord);

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
  }
}
// ... (rest of main.js remains the same)

async function prev() {
  const result = await eel.prev_result()();
  if (typeof result === "string") {
    document.getElementById("contextArea").innerHTML = highlight(
      result,
      currentWord
    );
  }
}

async function next() {
  const result = await eel.next_result()();
  if (typeof result === "string") {
    document.getElementById("contextArea").innerHTML = highlight(
      result,
      currentWord
    );
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
  const select = document.getElementById("sourceSelect");
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
  });
};
