# main.py - Japanese Context Finder (Eel hybrid version)

import os
import re
import threading
import tempfile
import time
import urllib.request

# ---- Kivy parts kept (for reference or reuse later) ----
from kivy.core.text import LabelBase
from kivy.core.audio import SoundLoader
from gtts import gTTS

# ---- New import for web interface ----
import eel

# Import configuration settings
from config import (
    RESOURCES_DIR, DEFAULT_SOURCE_FILE, FONT_FILE, FONT_DIR, FONT_URL,
    DEFAULT_CONTEXT_SENTENCES
)


# --- Utility Functions (unchanged) ---
def ensure_font_downloaded():
    """Ensures the custom Japanese font is downloaded and available."""
    if not os.path.exists(FONT_DIR):
        os.makedirs(FONT_DIR)
        print(f"Created font directory: {FONT_DIR}")

    if not os.path.exists(FONT_FILE):
        try:
            print(f"Downloading font from {FONT_URL}...")
            urllib.request.urlretrieve(FONT_URL, FONT_FILE)
            print(f"Successfully downloaded font to: {FONT_FILE}")
        except Exception as e:
            print(f"Error downloading font: {e}")
            pass


ensure_font_downloaded()
LabelBase.register(name='HinaMincho', fn_regular=FONT_FILE)


# --- Core Logic (adapted for Eel) ---
def split_text_into_sentences(text_content):
    """
    Splits Japanese text content into sentences based only on true terminators 
    (。！？.!?), ensuring punctuation stays attached and commas (、) are ignored.
    """
    text_content = text_content.replace('\r', ' ').replace('\n', ' ')

    # Split AFTER terminal punctuation, keeping the punctuation attached.
    delimiters = r'(?<=[。！？\.!\?])\s*'
    
    sentences = re.split(delimiters, text_content)

    return [s.strip() for s in sentences if s.strip()]


class ContextFinderLayout:
    
    """
    Core logic class for Japanese context search, reused for both
    Kivy and Eel interfaces.
    """

    def __init__(self):
        self.context_size = DEFAULT_CONTEXT_SENTENCES
        self.all_sentences = []
        self.match_indices = []
        self.current_match_index = -1
        self.current_word = ''
        self.current_source = DEFAULT_SOURCE_FILE
        self.sources = self.detect_sources()
        self.load_data()

    def detect_sources(self):
        """Detect all CSV sources in both the app folder and the resources folder."""
        detected = []
        # 1) resources dir (if exists)
        if os.path.isdir(RESOURCES_DIR):
            for f in os.listdir(RESOURCES_DIR):
                if f.lower().endswith('.csv'):
                    detected.append(('resources', f))
        # 2) app folder (same folder as this file)
        app_dir = os.path.dirname(__file__)
        for f in os.listdir(app_dir):
            if f.lower().endswith('.csv'):
                detected.append(('.', f))

        # De-duplicate by filename, prefer resources/ over root
        seen = set()
        ordered = []
        for folder, fname in detected:
            if fname not in seen:
                seen.add(fname)
                ordered.append((folder, fname))

        files = [fname for _, fname in ordered]
        files.sort()
        print(f"Detected sources (resources/ and app dir): {files}")
        return files


    def set_source(self, filename):
        """Change current source and reload (checks resources/ then app folder)."""
        # Try resources/
        candidate_paths = [
            os.path.join(RESOURCES_DIR, filename),
            os.path.join(os.path.dirname(__file__), filename),
        ]
        new_path = None
        for p in candidate_paths:
            if os.path.exists(p):
                new_path = p
                break

        if new_path:
            self.current_source = new_path
            print(f"Switching source to: {self.current_source}")
            self.load_data()
            # Reset search state
            self.match_indices = []
            self.current_match_index = -1
            self.current_word = ''
            return f"Source switched to {filename} ({len(self.all_sentences)} sentences)"
        else:
            return f"File not found: {filename}"


    def load_data(self):
        """Loads Japanese text corpus into memory."""
        print(f"Loading text database from {self.current_source}...")
        try:
            with open(self.current_source, 'r', encoding='utf-8') as f:
                content = f.read().replace('\n', ' ')
            self.all_sentences = split_text_into_sentences(content)
            print(f"Loaded {len(self.all_sentences)} sentences.")
        except Exception as e:
            print(f"Failed to load data: {e}")
            self.all_sentences = []

    # --- Context handling logic ---
    def search_word_js(self, word):
        """
        Search wrapper for the Eel interface.
        Returns a dictionary with 'text' and 'count'.
        """
        word = word.strip()
        if not word:
            return {"text": "Please enter a word.", "count": 0}

        if not self.all_sentences:
            return {"text": "Data not loaded.", "count": 0}

        self.current_word = word
        self.match_indices = [
            i for i, s in enumerate(self.all_sentences) if word in s
        ]

        total_count = len(self.match_indices)

        if not self.match_indices:
            # No results found, return the message and 0 count
            return {"text": f"No results found for '{word}'.", "count": 0}

        self.current_match_index = 0
        
        # Success case: Return the first context text and the total count
        return {
            "text": self._get_context_text(),
            "count": total_count
        }

    def _get_context_text(self):
        """Return the current context text as string."""
        if self.current_match_index == -1 or not self.match_indices:
            return ""

        target_index = self.match_indices[self.current_match_index]

        # interpret context_size as total window size (1 = only target)
        half_window = max(0, (self.context_size - 1) // 2)
        start = max(0, target_index - half_window)
        end = min(len(self.all_sentences), target_index + half_window + 1)

        context_sentences = self.all_sentences[start:end]

        output_lines = []
        for i, s in enumerate(context_sentences):
            idx = start + i
            if idx == target_index:
                highlighted = s.replace(self.current_word, f"{self.current_word}")
                output_lines.append(highlighted)
            else:
                output_lines.append(s)

        formatted = "".join(output_lines)
        return formatted

    def next_result(self):
        if self.current_match_index < len(self.match_indices) - 1:
            self.current_match_index += 1
        return self._get_context_text()

    def prev_result(self):
        if self.current_match_index > 0:
            self.current_match_index -= 1
        return self._get_context_text()

    def read_context(self):
        """Play the current text aloud."""
        text = self._get_context_text()
        text = re.sub(r'\\*\\*(.*?)\\*\\*', r'\\1', text)
        if not text:
            return "Nothing to read."

        threading.Thread(target=self._tts_playback, args=(text,)).start()
        return "Reading aloud..."

    def _tts_playback(self, text):
        """Internal TTS playback."""
        temp_file = None
        try:
            tts = gTTS(text=text, lang='ja')
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp:
                temp_file = tmp.name
            tts.save(temp_file)

            sound = SoundLoader.load(temp_file)
            if sound:
                sound.play()
                while sound.state == 'play':
                    time.sleep(0.1)
                sound.unload()
        except Exception as e:
            print(f"TTS error: {e}")
        finally:
            if temp_file and os.path.exists(temp_file):
                os.remove(temp_file)


# --- Eel Web App Bridge ---
app_logic = ContextFinderLayout()
eel.init('web')


@eel.expose
def search_word(word):
    return app_logic.search_word_js(word)


@eel.expose
def set_context_size(size):
    try:
        app_logic.context_size = int(size)
    except ValueError:
        app_logic.context_size = 1


@eel.expose
def next_result():
    return app_logic.next_result()


@eel.expose
def prev_result():
    return app_logic.prev_result()


@eel.expose
def read_context():
    return app_logic.read_context()


@eel.expose
def get_sources():
    """Return list of detected CSV sources (filenames only)."""
    return app_logic.detect_sources()

@eel.expose
def set_source(filename):
    """Switch the active source file by filename (in RESOURCES_DIR)."""
    return app_logic.set_source(filename)

# --- Start Web UI ---
if __name__ == '__main__':
    print("Starting Eel web interface...")
    eel.init('web')
    eel.start('index.html', size=(1000, 700), mode=None)

