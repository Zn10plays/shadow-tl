import os
from shadow_db import Novel, Chapter  # Adjusted import to match the new structure
from vllm.connector import translate_chapter
from utils.context import save_translated_chapter

def main():
    chapter = Chapter.get(novel_id=1, chapter_number=1)

    results = translate_chapter(
        chapter,
        log_stream=True
    )

    save_translated_chapter(chapter, results, vorbose=True)
    

if __name__ == "__main__":
    main()