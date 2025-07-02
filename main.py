import os
from shadow_db import Novel, Chapter  # Adjusted import to match the new structure
from vllm.connector import translate_chapter
from utils.context import add_or_update_bible_info

def main():
    results = translate_chapter(
        Chapter.get(novel_id=1, chapter_number=1),
        log_stream=True
    )

    print(results)

    for bible in results.character_bible:
        add_or_update_bible_info(
            Novel.get(1),
            bible
        )
        print(f'successfully added: {bible.name} ({bible.classification})')

if __name__ == "__main__":
    main()