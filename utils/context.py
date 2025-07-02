from shadow_db import Novel, Chapter, BibleInfo
import re
from vllm.models import TranslatedResults
from utils.prompts import get_bible_summary_prompt
from utils.genai import manager

###
# Function to retrieve relevant terms from the BibleInfo based on chapter content
# pulls them from the novel bible
###
def get_relevent_terms(chapterid: int) -> list[BibleInfo]:
    chapter = Chapter.get_or_none(Chapter.id == chapterid)

    if not chapter:
        raise ValueError(f"Chapter with id {chapterid} not found.")
    
    bibles = BibleInfo.select().where(BibleInfo.novel == chapter.novel)

    unmatched_notes = []
    matched_notes = []

    # first round pass to see if there is an excat match
    for bible in bibles:
        if bible.raw_name in chapter.content:
            matched_notes.append(bible)
        else:
            unmatched_notes.append(bible)

    # second round pass to see if there is a partial match
    # maybe the name is saved as firstname lastname, but in the chapter it is only referred to as lastname
    for unmatched in unmatched_notes:
        unmatched_name_parts = unmatched.raw_name.split(' ')
        for part in unmatched_name_parts:
            if part in chapter.content:
                matched_notes.append(unmatched)
                break
    # there will not be any duplicates in the matched_notes list
    # no need to check for duplicates

    return matched_notes

def summarize_bible_changes(old_bible: BibleInfo, new_bible: BibleInfo) -> tuple[str, bool]:
    try:
        prompt = get_bible_summary_prompt(old_bible, new_bible)

        response = manager.generate(prompt)

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

    if not existing_info:
        # If it doesn't exist, create a new entry
        info.novel = novel
        info.save()
        return

    summary, success = summarize_bible_changes(existing_info, info)

    if not success:
        print("Failed to summarize the changes, skipping update.")
        print('traceback, old:', existing_info.name,)
        print('description:', existing_info.description, 
              'new:', info.name, 'description:', info.description)
        return
    
    existing_info.description = summary
    # save it
    existing_info.save()
    return

def save_translated_chapter(chapter: Chapter, results: TranslatedResults, force_update=False, vorbose=False):
    if vorbose:
        print(f"Saving translated chapter {chapter.chapter_number} of novel {chapter.novel_id}.")


    if (chapter.is_translated and not force_update):
        print(f"Chapter {chapter.chapter_number} of novel {chapter.novel_id} is already translated. Use force_update=True to overwrite.")
        return    

    chapter.translated_title = results.translated_title
    chapter.summary = results.summary
    chapter.content = results.translation
    chapter.notes_for_next_chapter = results.notes_for_next_chapter
    chapter.is_translated = True

    # update the character bible
    for bible_info in results.character_bible:
        if vorbose:
            print(f"Adding or updating BibleInfo for {bible_info.translated_name} in novel {chapter.novel_id}.")
        add_or_update_bible_info(
            Novel.get(chapter.novel_id),
            BibleInfo(
                name=bible_info.translated_translated,
                raw_name=bible_info.orignal_name,
                classification=bible_info.classification,
                description=bible_info.description,
                novel=chapter.novel
            )
        )

    # save the chapter
    chapter.save()

    if vorbose:
        print(f"Translated chapter {chapter.chapter_number} of novel {chapter.novel_id} saved successfully.")
