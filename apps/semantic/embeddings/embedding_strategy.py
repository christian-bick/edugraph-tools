from typing import Dict


class EmbeddingStrategy:

    def embed_entry(self, entry) -> list:
        pass

    def embed_entries(self, entries) -> Dict:
        pass
