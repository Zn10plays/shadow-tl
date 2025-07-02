from dotenv import load_dotenv
from google import genai
import os

load_dotenv()

class GoogleManager:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = genai.Client(api_key=self.api_key)

    def generate(self, prompt: str, model: str = "gemma-3-27b-it", max_tokens: int = 300, temperature: float | None = None) -> str:
        """
        Generate text using the Google API.
        """
        response = self.client.models.generate(
            model=model,
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature
        )
        return response.text
    

manager = GoogleManager(api_key=os.getenv("google_api_key"))