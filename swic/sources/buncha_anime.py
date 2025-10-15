from typing import List, Dict

import os
import re

from .base import BaseSourceParser
from .common import SimpleTextParser


class BunchaAnimeParser(BaseSourceParser):
    """
    Placeholder parser for Buncha Anime CSV files.
    Currently inherits the simple text behavior.
    """

    def __init__(self):
        self._delegate = SimpleTextParser()

    def parse(self, content: str, current_source: str) -> List[Dict]:
        """
        For Anime source:
        - Treat each original text line as a separate sentence.
        - A header line is any single line that is exactly a quoted label,
          e.g., "Bleach - 215_1" or "Bleach - 215_1_dialogue".
        - Use that label to mark subsequent lines until the next header.
        - Metadata for each sentence is a single element list: [anime_name],
          where anime_name is the substring before ' - ' if present,
          otherwise the whole label.
        - Returns one document with 'sentences' and 'sentence_meta'.
        """

        text = (content or "")
        norm = text.replace("\r\n", "\n").replace("\r", "\n")
        raw_lines = [ln.strip() for ln in norm.split("\n")]

        # Detect lines that are exactly a quoted label
        header_re = re.compile(r'^"([^"]+)"$')

        current_anime_name = None
        sentences: List[str] = []
        sentence_meta: List[List[str]] = []

        for ln in raw_lines:
            if not ln:
                continue

            # Header detection: a line that is just a quoted label
            # e.g., "Bleach - 215_1_dialogue" or "Bleach - 215_1"
            m = header_re.match(ln)
            if m:
                label = m.group(1).strip()
                anime_name = label
                current_anime_name = anime_name or label
                # Do not store header as a sentence
                continue

            # Regular content line: use the most recent header as metadata
            if current_anime_name:
                sentences.append(ln)
                sentence_meta.append([current_anime_name])
            else:
                # If no header seen yet, skip or attach a generic label
                # Here we skip to avoid incorrect attribution
                continue

        # If nothing parsed, fall back to simple behavior
        if not sentences:
            filename_base = os.path.basename(current_source).replace('.csv', '')
            fallback_meta = [
                "0",
                "N/A",
                f"Source: {filename_base}",
                f"Corpus: {filename_base}",
            ]
            return [{
                'metadata': fallback_meta,
                'sentences': [ln for ln in raw_lines if ln],
            }]

        return [{
            'sentences': sentences,
            'sentence_meta': sentence_meta,
        }]
