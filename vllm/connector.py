from datetime import datetime
import openai
import os
from shadow_db import Chapter  # Adjusted import to match the new structure
from utils.json import force_validate_TranslationResults
from vllm.models import TranslatedResults
from shadow_db import Logs
from google import genai
from utils.prompts import get_chapter_translation_prompt
import dotenv
from google.genai import types
dotenv.load_dotenv()

backend = os.getenv("BACKEND", "google")  # Default to 'google' if not set

base_url = os.getenv("OPEAN_AI_SERVER_URL", "http://localhost:8000/v1")
base_model = os.getenv("DEFAULT_MODEL", "google/gemma-3-1b-it")

client = None

def get_client():
    global client

    if client is not None:
        return client

    """
    Initialize and return an OpenAI client with the specified base URL and API key.
    """
    backend = os.getenv("BACKEND", "google")  # Default to 'google' if not set

    base_url = os.getenv("OPEAN_AI_SERVER_URL", "http://localhost:8000/v1")
    base_model = os.getenv("DEFAULT_MODEL", "google/gemma-3-1b-it")

    if backend == 'openai':
        api_key = os.getenv("API_KEY", "your_api_key_here")  # Replace with your actual API key

        client = openai.OpenAI(
            api_key=api_key,
            base_url=base_url,
        )
    else:
        client = genai.Client()

    

    # Set the default model if not specified
    if not hasattr(client, 'default_model'):
        client.default_model = base_model
    
    return client

def translate_chapter_OpenAI(chapter: Chapter, local_processing=True, log_stream=False, temperature=None, thinking_budget=0, include_thoughts=False) -> tuple[TranslatedResults, bool]:
    """
    Translate a chapter using the OpenAI client.
    returns translation results, and a boolean indicating success.
    """

    openai_client = get_client()

    prompt = get_chapter_translation_prompt(chapter.chapter_number, chapter.novel)

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
                    },
                },
            },
        },
        stream=local_processing
    )

    if local_processing:
        content = ''

        try:
            for chunk in completion:
                if hasattr(chunk, 'choices') and chunk.choices:
                    if log_stream:
                        print(chunk.choices[0].delta.content, end='', flush=True)
                    content += str(chunk.choices[0].delta.content) if chunk.choices[0].delta.content else ''

            if log_stream:
                print()  # Ensure a newline after the stream

        except Exception as e:
            print(f"Error occurred while processing chunks: {e}")

    else:
        content = completion.choices[0].message.content

    parsed_results, success = force_validate_TranslationResults(content)

    if not success:
        logs = Logs(
            service='translation and parsing',
            message=f"Failed to parse the translation results for chapter {chapter.chapter_number} of novel {chapter.novel}. Content: {content}",
            message_type='error',
            time=datetime.now(),
            instance_id=os.getenv('INSTANCE_ID', 'unknown')
        )

        logs.save()

        print(f"[ERROR] Traceback Log id {logs}: Failed to parse the translation results for chapter {chapter.chapter_number} of novel {chapter.novel}.")

        return TranslatedResults(
            translated_title='!!ERROR ERROR!!',
            summary=f'[ERROR] Traceback Log id {logs}: Failed to parse the translation results for chapter {chapter.chapter_number} of novel {chapter.novel}. ',
            character_bible=[],
            notes_for_next_chapter='',
            translated_content=''
        ), False
    
    return parsed_results, True

def translate_chapter_Google(chapter: Chapter, local_processing=True, log_stream=False, temperature=None, thinking_budget=0, include_thoughts=False) -> tuple[TranslatedResults, bool]:
    
    client = get_client()

    prompt = get_chapter_translation_prompt(chapter.chapter_number, chapter.novel)

    safety_settings = [
        {
            "category": types.HarmCategory.HARM_CATEGORY_HARASSMENT,
            "threshold": types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
        },
        {
            "category": types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
            "threshold": types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
        },
        {
            "category": types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
            "threshold": types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
        },
        {
            "category": types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
            "threshold": types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
        },
        ]


    response = client.models.generate_content(
        model=client.default_model,
        contents=prompt[1]['content'],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=TranslatedResults,
            max_output_tokens=15_000,
            temperature=temperature if temperature is not None else 0.2,
            thinking_config=types.ThinkingConfig(
                thinking_budget=thinking_budget,
                include_thoughts=include_thoughts
            ),
            system_instruction=prompt[0]['content'],
            safety_settings=safety_settings,
        )
    )

    try:
        content = response.text

        if local_processing:
            results, success = force_validate_TranslationResults(content)

            if not success:
                print(f"[ERROR] Failed to parse the translation results for chapter {chapter.chapter_number} of novel {chapter.novel}. Content: {content}")
                return TranslatedResults(
                    translated_title='!!ERROR ERROR!!',
                    summary=f'[ERROR] Failed to parse the translation results for chapter {chapter.chapter_number} of novel {chapter.novel}. Content: {content}',
                    character_bible=[],
                    notes_for_next_chapter='',
                    translated_content=''
                ), False
            
            return results, True



    except Exception as e:
        print(f"Error occurred while processing chunks: {e}")

        logs = Logs(
            service='translation and parsing',
            message=f"Error occurred while processing chunks: {e} \n \n content: {content}",
            message_type='error',
            time=datetime.now(),
            instance_id=os.getenv('INSTANCE_ID', 'unknown')
        )
        logs.save()

        return TranslatedResults(
            translated_title='!!ERROR ERROR!!',
            summary=f'[ERROR] Traceback Log id {logs}: Failed to parse the translation results for chapter {chapter.chapter_number} of novel {chapter.novel}',
            character_bible=[],
            notes_for_next_chapter='',
            translated_content=''
        ), False

def translate_chapter(chapter: Chapter, local_processing=True, log_stream=False, force=False, temperature=None, thinking_budget=0, include_thoughts=False) -> tuple[TranslatedResults, bool]:
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
    
    if backend == 'openai':
        return translate_chapter_OpenAI(
            chapter,
            local_processing=local_processing,
            log_stream=log_stream,
            temperature=temperature,
            thinking_budget=thinking_budget,
            include_thoughts=include_thoughts
        )
    
    else:
        return translate_chapter_Google(
            chapter,
            local_processing=local_processing,
            log_stream=log_stream,
            temperature=temperature,
            thinking_budget=thinking_budget,
            include_thoughts=include_thoughts
        )

