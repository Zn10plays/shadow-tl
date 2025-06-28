import os
from openai import OpenAI
import db.connector as db
from vllm.models import TranslatedResults
from utils.prompts import get_prompt

client = OpenAI(
  # This is the default and can be omitted
  base_url="http://10.128.9.114:8000/v1",
  api_key='abc123',
)

def main():

    completion = client.beta.chat.completions.parse(
        model="google/gemma-3-27b-it",
        max_tokens=5000,
        messages=get_prompt(2, 1),
        temperature=0.2,
        response_format=TranslatedResults,
    )

    print(completion.choices[0].message.content)

    with open("output.txt", "w") as f:
        f.write(completion.choices[0].message.content) 
if __name__ == "__main__":
    main()