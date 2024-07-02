import os

class EnvFetcher:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY") or ""
        if not self.api_key:
            raise Exception("OpenAI_API_KEY is not set.")
        self.db_url = os.getenv("GRAPH_DB_URL") or "bolt://localhost:7687"
        if not self.db_url:
            raise Exception("GRAPH_DB_URL is not set.")
        self.db_username = os.getenv("GRAPH_DB_USERNAME") or ""
        if not self.db_username:
            raise Exception("GRAPH_DB_USERNAME is not set.")
        self.db_password = os.getenv("GRAPH_DB_PASSWORD") or ""
        if not self.db_password:
            raise Exception("GRAPH_DB_PASSWORD is not set.")