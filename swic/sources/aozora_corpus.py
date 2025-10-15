from typing import List, Dict

from .base import BaseSourceParser
from .common import parse_aozora_content


class AozoraCorpusParser(BaseSourceParser):
    """Parser for Aozora Corpus CSV files."""

    def parse(self, content: str, current_source: str) -> List[Dict]:
        return parse_aozora_content(content or "")

