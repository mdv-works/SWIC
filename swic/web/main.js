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
