from typing import List, Dict

from .base import BaseSourceParser
from .common import SimpleTextParser


class MonogatariCollectionParser(BaseSourceParser):
    """
    Placeholder parser for Monogatari Collection CSV files.
    Currently inherits the simple text behavior.
    """

    def __init__(self):
        self._delegate = SimpleTextParser()

    def parse(self, content: str, current_source: str) -> List[Dict]:
        return self._delegate.parse(content, current_source)

