import os
from shadow_db import Novel, Chapter  # Adjusted import to match the new structure
from vllm.connector import translate_chapter

def main():
    results = translate_chapter(
        Chapter.get(novel_id=1, chapter_number=1),
        log_stream=True
    )

    print(results)

    
if __name__ == "__main__":
    main()