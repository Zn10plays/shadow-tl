import os
from shadow_db import Novel, Chapter  # Adjusted import to match the new structure
from vllm.connector import translate_chapter
from utils.refrences import save_translated_chapter
from tqdm import tqdm

def main():
    for i in tqdm(range(500), desc="Translating chapters"):
        chapter = Chapter.get(novel_id=1, chapter_number=i+1)

        if chapter.is_translated or not chapter.is_filled:
            # print(f"Chapter {chapter.chapter_number} of novel {chapter.novel} is already translated.")
            # if chapter is translated, or lacking content, skip it
            continue

        results, success = translate_chapter(
            chapter,
            # log_stream=True,
            thinking_budget=300,
            temperature=0.2,
            # force=True,
            include_thoughts=False
        )

        if not success:
            print(f"Failed to translate chapter {chapter.chapter_number} of novel {chapter.novel}.")
            input('press enter to continue')
            return

        save_translated_chapter(chapter, results)

        break
    

if __name__ == "__main__":
    main()