import shadow_db as db

Models = {
    'GEMMA3': 1,
    'MISTRAL': 2,
}

system_prompt = "You are an translation agent at a webnovel publishing company. You are tasked with translating chapters of web novels from Koren to English." \
    " When you translate chapter, be ware of what the names, places, and other proper nouns in the chapter. Also be mindful of the tone, setting, and flow of the chapter." \
    " before you translate, summarize the chapter, once you are completed, write a character bible in order to mantain consistency in the translation. The character bible" \
    " should include the names and places (original, and translated), and other proper nouns in the chapter, as well as their descriptions and any other relevant information. " \
    " Finially, be sure to write notes for the next chapter to help other translators."

def get_prompt(chapter_number, novel_id, model=Models['GEMMA3']):
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
    character_bible = db.BibleInfo.select().where(db.BibleInfo.novel == novel_id)

    content = f'Translate the following chapter to English, the title is {chapter.title} and it is number {chapter.chapter_number}. \n\n'

    if previous_chapter and previous_chapter.is_translated:
        content += f' Here is some background info. Summary for the previous chapter: {previous_chapter.summary}. \n\n'

    if character_bible.exists():
        content += 'Here is the character bible for the novel: \n'
        for bible in character_bible:
            content += f"{bible.name}: {bible.description}\n"
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
