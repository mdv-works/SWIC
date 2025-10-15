# config.py

import os

# --- File Paths ---
RESOURCES_DIR = os.path.join(os.path.dirname(__file__), 'resources')

# Default file (fallback)
DEFAULT_SOURCE_FILE = os.path.join(RESOURCES_DIR, 'Aozora Corpus.csv')


# Kivy Language (KV) file (kept for reference)
KV_FILE = 'context_finder.kv'

# --- Application Settings ---

# Default number of sentences to show before and after the matching sentence
DEFAULT_CONTEXT_SENTENCES = 2

# Font size list (used in original app, kept for reference/future use)
FONT_SIZE_LIST = [16, 18, 20, 24, 28] 
