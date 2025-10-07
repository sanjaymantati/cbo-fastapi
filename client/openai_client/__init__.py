import os
import logging
from openai import OpenAI

logging.basicConfig(level=logging.DEBUG)


class OpenAIClient:
    def __init__(self):
        self.api_key = os.environ.get("OPENAI_API_KEY")
        self.base_url = os.environ.get("OPENAI_BASE_URL")

    def get_client(self):
        return OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
