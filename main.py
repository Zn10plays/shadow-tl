import os
from shadow_db import Novel, Chapter  # Adjusted import to match the new structure
from vllm.connector import translate_chapter
from utils.refrences import save_translated_chapter

def main():
    chapter = Chapter.get(novel_id=1, chapter_number=3)

    results, success = translate_chapter(
        chapter,
        log_stream=True,
        thinking_budget=800,
        temperature=0.2,  # Adjust temperature as needed
        force=True,
        include_thoughts=False
    )

    if not success:
        print(f"Failed to translate chapter {chapter.chapter_number} of novel {chapter.novel}.")
        return

    save_translated_chapter(chapter, results, force=True)
    

if __name__ == "__main__":
    main()