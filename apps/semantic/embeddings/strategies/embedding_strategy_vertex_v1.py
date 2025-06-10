import vertexai

from vertexai.language_modelsvision_models import MultiModalEmbeddingModel

from semantic.embeddings.embedding_strategy import EmbeddingStrategy


class VertexEmbeddingStrategy(EmbeddingStrategy):
    def __init__(self):
        vertexai.init(project="edugraph-438718", location="europe-southwest1")

    def embed_entry(self, entry) -> list:
        model = MultiModalEmbeddingModel.from_pretrained("multimodalembedding@001")

        embeddings = model.get_embeddings(
            texts=entry,
            dimension=1408,
        )

        return embeddings.text_embedding
