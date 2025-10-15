"""
Source-specific parser registry.

Provides `get_parser_for_filename` which selects the appropriate
parser implementation based on the CSV filename. Parsers currently
share placeholder logic (except Aozora), but are split for future
customization per source.
"""

from .base import BaseSourceParser
from .common import SimpleTextParser
from .aozora_corpus import AozoraCorpusParser
from .buncha_anime import BunchaAnimeParser
from .japanese_news import JapaneseNewsParser
from .monogatari_collection import MonogatariCollectionParser


def get_parser_for_filename(filename: str) -> BaseSourceParser:
    name = (filename or "").lower()

    if "aozora" in name:
        return AozoraCorpusParser()
    if "buncha" in name:
        return BunchaAnimeParser()
    if "news" in name:
        return JapaneseNewsParser()
    if "monogatari" in name:
        return MonogatariCollectionParser()

    # Fallback to a simple text parser
    return SimpleTextParser()

