import typing

from google import genai
from google.genai import types

from semantic.embeddings.embedding_strategy import EmbeddingStrategy


class GeminiEmbeddingStrategy(EmbeddingStrategy):
    def __init__(self):
        self.client = genai.Client()

    def embed_entry(self, entry) -> list:

        response = self.client.models.embed_content(
            model="gemini-embedding-exp-03-07",
            contents=entry,
            config=types.EmbedContentConfig(task_type="CLASSIFICATION")
        )

        return response.embeddings[0].values

    def embed_entries(self, entry_map: typing.Dict) -> typing.Dict:

        # We want to make sure that we preserve order this is why we work with tuples

        entry_tuples = list(entry_map.items())[:3]
        entry_keys = [item[0] for item in entry_tuples]
        entry_values = [item[1] for item in entry_tuples]

        response = self.client.models.embed_content(
            model="gemini-embedding-exp-03-07",
            contents=entry_values,
            config=types.EmbedContentConfig(task_type="CLASSIFICATION")
        )

        embedding_values = map(lambda embedding: embedding.values, response.embeddings)

        # Because we preserved order we can simply zip the original keys with the returned embeddings

        return dict(zip(entry_keys, embedding_values))
