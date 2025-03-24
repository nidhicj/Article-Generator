
import requests
from typing import List
from langchain_core.embeddings import Embeddings


class OllamaEmbeddings(Embeddings):
    def __init__(self, base_url: str, model: str):
        self.base_url = base_url
        self.model = model

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        embeddings = []
        for text in texts:
            response = requests.post(
                f"{self.base_url}/api/embeddings",
                json={"model": self.model, "prompt": text}
            )
            if response.status_code == 200:
                embeddings.append(response.json()["embedding"])
                
            else:
                raise ValueError(f"Error: {response.status_code}, {response.text}")
        return embeddings

    def embed_query(self, text: str) -> List[float]:
        response = requests.post(
            f"{self.base_url}/api/embeddings",
            json={"model": self.model, "prompt": text}
        )
        if response.status_code == 200:
            return response.json()["embedding"]
        else:
            raise ValueError(f"Error: {response.status_code}, {response.text}")
