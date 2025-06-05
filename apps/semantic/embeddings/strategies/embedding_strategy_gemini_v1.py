from google.generativeai import embed_content
import google.generativeai as gemini
from google.genai import types

from semantic.embeddings.embedding_strategy import EmbeddingStrategy
from semantic.ontology_util import definition_of_entity


class GeminiEmbeddingStrategy(EmbeddingStrategy):
    def __init__(self):
        self.model = gemini.GenerativeModel(
            model_name="gemini-2.0-flash",
        )

    def embed_entity(self, entity):
        response = embed_content(
            model="gemini-embedding-exp-03-07",
            contents=definition_of_entity(entity),
            config=types.EmbedContentConfig(task_type="SEMANTIC_SIMILARITY")
        )