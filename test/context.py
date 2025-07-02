from utils.prompts import get_relevent_terms
from shadow_db import Chapter  # Adjusted import to match the new structure

def main():
    chapter = Chapter.get(novel_id=1, chapter_number=2)

    entries= get_relevent_terms(chapter.id)

    for entry in entries:
        print(f"Entry: {entry.name}, Description: {entry.description}")
        

if __name__ == "__main__":
    main()