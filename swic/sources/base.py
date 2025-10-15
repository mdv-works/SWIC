from typing import List, Dict


class BaseSourceParser:
    """
    Interface for source-specific parsers. Implement `parse` to return a list
    of documents, each as { 'metadata': List[str], 'text': str }.
    """

    def parse(self, content: str, current_source: str) -> List[Dict]:
        raise NotImplementedError

