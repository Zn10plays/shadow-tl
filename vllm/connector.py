import openai
import os
from shadow_db import Novel, Chapter  # Adjusted import to match the new structure
from vllm.models import TranslatedResults
from utils.prompts import get_prompt
import dotenv
dotenv.load_dotenv()

client = None

def get_openai_client():
    global client

    if client is not None:
        return client

    """
    Initialize and return an OpenAI client with the specified base URL and API key.
    """
    base_url = os.getenv("VLLM_BACKEND_URL", "http://localhost:8000")
    api_key = os.getenv("VLLM_KEY", "your_api_key_here")  # Replace with your actual API key
    base_model = os.getenv("VLLM_DEFAULT_MODEL", "google/gemma-3-1b-it")

    if not base_url.endswith("/v1"):
        base_url = f"{base_url}/v1"

    client = openai.OpenAI(
        base_url=base_url,
        api_key=api_key,
    )

    # Set the default model if not specified
    if not hasattr(client, 'default_model'):
        client.default_model = base_model
    
    return client

def translate_chapter(chapter: Chapter, log_stream=False) -> TranslatedResults:
    """
    Translate a chapter using the OpenAI client.
    """
    openai_client = get_openai_client()

    try:
        completion = openai_client.chat.completions.create(
            model=openai_client.default_model,
            max_tokens=5000,
            messages=get_prompt(chapter.novel_id, chapter.chapter_number),
            temperature=0.2,
            response_format={
                'type': 'json_schema',
                "json_schema": {
                    'name': 'TranslatedResults',
                    "schema": TranslatedResults.model_json_schema(),
                }

            },
            stream=log_stream
        )

        if log_stream:
            content = ''

            for chunk in completion:
                if hasattr(chunk, 'choices') and chunk.choices:
                    print(chunk.choices[0].delta.content, end='', flush=True)
                    content += chunk.choices[0].delta.content

            print()  # Ensure a newline after the stream

            # json parse the content
            content = content.strip()
            if content.startswith('{') and content.endswith('}'):
                content = TranslatedResults.model_validate_json(content)
            else:
                raise ValueError("Streamed content is not a valid JSON object.")

            return TranslatedResults(
                title=chapter.title,
                summary=chapter.summary,
                content=content,
                character_bible=[],
                notes_for_next_chapter=""
            )

        return completion.choices[0].message.content
    
    except Exception as e:
        print(f"Error translating chapter {chapter.chapter_number} of novel {chapter.novel_id}: {e}")
        return TranslatedResults(
            title="!!Error!!",
            summary="An error occurred during translation.",
            content="",
            character_bible=[],
            notes_for_next_chapter=""
        )