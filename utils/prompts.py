import shadow_db as db
from shadow_db import Novel, Chapter, BibleInfo
from typing import List

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


Models = {
    'GEMMA3': 1,
    'MISTRAL': 2,
}

system_prompt = "You are an translation agent at a webnovel publishing company. You are tasked with translating chapters of web novels from Koren to English." \
    " When you translate chapter, be ware of what the names, places, and other proper nouns in the chapter. Also be mindful of the tone, setting, and flow of the chapter." \
    " before you translate, summarize the chapter, once you are completed, write a character bible in order to mantain consistency in the translation. The character bible" \
    " should include the names and places (original, and translated), and other proper nouns in the chapter, as well as their classification (person, place, item, skill) descriptions" \
    " and any other relevant information. Finially, be sure to write notes for the next chapter to help other translators."

def get_chapter_translation_prompt(chapter_number, novel_id, model=Models['GEMMA3']):
    # Fetch the chapter content from the database
    try:
        chapter = db.Chapter.get((db.Chapter.chapter_number == chapter_number) & (db.Chapter.novel == novel_id))
        # return chapter.content
    except db.Chapter.DoesNotExist:
        print(f"Chapter {chapter_number} not found.")
        return None
    
    # look for previous chapter
    if (chapter_number > 1):
        print('chapter number is greater than 1')
        previous_chapter = db.Chapter.get_or_none((db.Chapter.chapter_number == chapter_number - 1) & (db.Chapter.novel == novel_id))
    else:
        previous_chapter = None 

    # get character bible for the novel
    character_bible = get_relevent_terms(novel_id)

    content = f'Translate the following chapter to English, the title is {chapter.title} and it is number {chapter.chapter_number}. \n\n'

    if previous_chapter and previous_chapter.is_translated:
        content += f' Here is some background info. Summary for the previous chapter: {previous_chapter.summary}. \n\n'

    if len(character_bible) > 0:
        content += 'Here is the character bible for the novel: \n'
        for bible in character_bible:
            content += f"{bible.name} ({bible.classification}): {bible.description}\n"
        content += '\n Update it as needed after translating the new chapter.\n\n'


    content += f'Here is the chapter content, translate the follwing chapter: \n{chapter.content}'

    if model == Models['GEMMA3']:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": content},
        ] 
    elif model == Models['MISTRAL']:
        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': [
                {
                    'type': 'text',
                    'text': content
                }
            ]},
        ]

    return messages

def get_bible_summary_prompt(oldBible: db.BibleInfo, newBible: db.BibleInfo):
    """
    Generate a prompt to summarize the changes in the BibleInfo.
    """
    return f"""
    Update the following {oldBible.classification} description based on the new context provided. The updated description should be concise and integrate new relevant information while preserving key existing details.
    {oldBible.classification} name: {oldBible.name}
    Current description: "{oldBible.description}"

    new context: "{newBible.description}"

    answer in quotations for example: "here is the description"
    """