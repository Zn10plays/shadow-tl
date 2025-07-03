import os
from shadow_db import Novel, Chapter  # Adjusted import to match the new structure
from vllm.connector import translate_chapter
from utils.refrences import save_translated_chapter

def main():
    chapter = Chapter.get(novel_id=1, chapter_number=1)

    results, success = translate_chapter(
        chapter,
        log_stream=True
    )

    if not success:
        print(f"Failed to translate chapter {chapter.chapter_number} of novel {chapter.novel}.")
        return

    save_translated_chapter(chapter, results)
    

if __name__ == "__main__":
    main()