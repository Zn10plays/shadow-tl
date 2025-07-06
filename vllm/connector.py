import openai
import os
from shadow_db import Chapter  # Adjusted import to match the new structure
from vllm.models import TranslatedResults
from utils.prompts import get_chapter_translation_prompt
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
    base_url = os.getenv("VLLM_BACKEND_URL", "http://localhost:8000/v1")
    api_key = os.getenv("VLLM_KEY", "your_api_key_here")  # Replace with your actual API key
    base_model = os.getenv("VLLM_DEFAULT_MODEL", "google/gemma-3-1b-it")

    client = openai.OpenAI(
        base_url=base_url,
        api_key=api_key,
    )

    # Set the default model if not specified
    if not hasattr(client, 'default_model'):
        client.default_model = base_model
    
    return client

def translate_chapter(chapter: Chapter, log_stream=False, force=False, temperature=None, thinking_budget=0, include_thoughts=False) -> tuple[TranslatedResults, bool]:
    """
    Translate a chapter using the OpenAI client.
    returns translation results, and a boolean indicating success.
    """

    if not isinstance(chapter, Chapter):
        raise TypeError("Expected 'chapter' to be an instance of Chapter class.")
    
    if chapter.is_translated and not force:
        """
        If the chapter is already translated and force is not set, return the existing translation.
        """
        print(f"Chapter {chapter.chapter_number} of novel {chapter.novel} is already translated.")
        return TranslatedResults(
            translated_title=chapter.translated_title,
            summary=chapter.summary,
            character_bible=[],
            notes_for_next_chapter=chapter.notes_for_next_chapter,
            translated_content=chapter.translated_content
        ), True

    openai_client = get_openai_client()

    prompt = get_chapter_translation_prompt(chapter.chapter_number, chapter.novel)

    try:
        completion = openai_client.chat.completions.create(
            model=openai_client.default_model,
            max_tokens=15_000,
            messages=prompt,
            temperature=temperature,
            response_format={
                'type': 'json_schema',
                "json_schema": {
                    'name': 'TranslatedResults',
                    "schema": TranslatedResults.model_json_schema(),
                }
            },
            extra_body={
                'extra_body': {
                    "google": {
                        "thinking_config": {
                            "thinking_budget": thinking_budget,
                            "include_thoughts": include_thoughts
                        }
                    }
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
            if content.startswith('{') and content.endswith('}'):
                print (f"Translated content for chapter {chapter.chapter_number} of novel {chapter.novel}: {content}")
                return TranslatedResults.model_validate_json(content), True
            else:
                raise ValueError("Streamed content is not a valid JSON object.")

        return TranslatedResults.model_validate_json(completion.choices[0].message.content), True
    
    except Exception as e:

        print(f"Error translating chapter {chapter.chapter_number} of novel {chapter.novel_id}: {e}")
        return TranslatedResults(
            translated_title='ERROR!!- Unable to translate chapter',
            summary='ERROR!!- Unable to summarize chapter',
            character_bible=[],
            notes_for_next_chapter='ERROR!!- Unable to provide notes for next chapter',
            translated_content='ERROR!!- Unable to translate chapter content'
        ), False