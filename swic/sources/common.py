import os
import re
from typing import List, Dict

from .base import BaseSourceParser


def parse_aozora_content(content: str) -> List[Dict]:
    """
    Parse content using strict Aozora format:
    [ID, URL, AUTHOR, TITLE],"[TEXT_CONTENT]"
    Returns list of documents with metadata list and text.
    """
    documents: List[Dict] = []

    doc_pattern = re.compile(
        r"\n?\s*\d+,([^,]+,[^,]+,[^,]+),\"([^\"]*)\"",
        re.DOTALL,
    )

    matches = doc_pattern.findall(content)
    for metadata_string, text_content in matches:
        metadata_fields = [f.strip() for f in metadata_string.split(',')]
        clean_text = text_content.strip()
        if clean_text:
            documents.append({
                'metadata': metadata_fields,
                'text': clean_text,
            })
    return documents


class SimpleTextParser(BaseSourceParser):
    """
    Treats the entire file as a single document with placeholder metadata.
    """

    def parse(self, content: str, current_source: str) -> List[Dict]:
        documents: List[Dict] = []
        filename_base = os.path.basename(current_source).replace('.csv', '')
        metadata_fields = [
            "0",
            "N/A",
            f"Source: {filename_base}",
            f"Corpus: {filename_base}",
        ]

        clean_text = (content or "").strip()
        if clean_text:
            documents.append({
                'metadata': metadata_fields,
                'text': clean_text,
            })
        return documents

