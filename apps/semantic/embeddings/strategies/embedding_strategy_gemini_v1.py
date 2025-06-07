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

        def split_list_into_chunks(data_list, chunk_size):
            chunks = []
            for i in range(0, len(data_list), chunk_size):
                chunks.append(data_list[i:i + chunk_size])
            return chunks

        # We want to make sure that we preserve order this is why we work with tuples

        entry_tuples = list(entry_map.items())
        entry_keys = [item[0] for item in entry_tuples]
        entry_values = [item[1] for item in entry_tuples]

        entry_value_chunks = split_list_into_chunks(entry_values, 20)
        embeddings = []

        for index, entry_value_chunk in enumerate(entry_value_chunks):
            print("Processing chunk {}".format(index))
            response = self.client.models.embed_content(
                model="embedding-001",
                contents=entry_value_chunk,
                config=types.EmbedContentConfig(task_type="CLASSIFICATION")
            )
            embeddings.extend(response.embeddings)

        # Because we preserved order we can simply zip the original keys with the returned embeddings

        embeddings_values =  map(lambda x: x.values, embeddings)

        return dict(zip(entry_keys, embeddings_values))


