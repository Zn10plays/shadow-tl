from shadow_db import Novel, Chapter, BibleInfo
import re
from vllm.models import TranslatedResults
from utils.prompts import get_bible_summary_prompt

def summarize_bible_changes(old_bible: BibleInfo, new_bible: BibleInfo) -> tuple[str, bool]:
    try:
        prompt = get_bible_summary_prompt(old_bible, new_bible)

        # response = manager.generate(prompt)
        response = '"funny hahahah"'

        # the res is in ""
        if response.startswith('"') and response.endswith('"'):
            response = response[1:-1]
        else:
            raise ValueError("Response from the model is not in the expected format.")
        
        # Extract the content inside the quotes
        response = re.search(r'"(.*?)"', response).group(0)[1:-1]  

        return response, True
    except Exception as e:

        print(ValueError("Unable to summarize the bible changes. Exception"+ str(e)))
        return "Unable to summarize the bible changes.", False

def add_or_update_bible_info(novel: Novel, info: BibleInfo):
    """
    logically add or update the bible info for a novel
    """

    # Check if the info already exists
    existing_info: BibleInfo = BibleInfo.get_or_none(
        (BibleInfo.novel == novel) & 
        (BibleInfo.raw_name == info.raw_name)
    )

    # if new or classification is different, we need to update it
    if not existing_info or existing_info.classification != info.classification:
        # If it doesn't exist, create a new entry
        info.novel = novel.get_id()
        info.save()
        return

    # if it exists, we need to update it
    existing_info.description = info.description
    # save it
    existing_info.save()
    return

def save_translated_chapter(chapter: Chapter, results: TranslatedResults, force=False, verbose=False):
    if verbose:
        print(f"Saving translated chapter {chapter.chapter_number} of novel {chapter.novel_id}.")

    if (chapter.is_translated and not force):
        print(f"Chapter {chapter.chapter_number} of novel {chapter.novel} is already translated. Use force=True to overwrite.")
        return

    chapter.translated_title = results.translated_title
    chapter.summary = results.summary
    chapter.translated_content = results.translated_content
    chapter.notes_for_next_chapter = results.notes_for_next_chapter
    chapter.is_translated = True

    # update the character bible
    for bible_info in results.character_bible:
        if verbose:
            print(f"Adding or updating BibleInfo for {bible_info.translated_name} in novel {chapter.novel_id}.")
        add_or_update_bible_info(
            Novel.get(chapter.novel_id),
            BibleInfo(
                name=bible_info.translated_name,
                raw_name=bible_info.orignal_name,
                classification=bible_info.classification,
                description=bible_info.description,
                novel=chapter.novel
            )
        )

    # save the chapter
    chapter.save()

    if verbose:
        print(f"Translated chapter {chapter.chapter_number} of novel {chapter.novel_id} saved successfully.")
