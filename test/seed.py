from db.connector import Novel, Chapter, BibleInfo

data = {}

def main():

    chapter = Chapter.get(Chapter.chapter_number == 1)

    chapter.traslated_title = data["title"]
    chapter.translated_content = data["content"]
    chapter.summary = data["summary"]
    chapter.notes_for_next_chapter = data["notes_for_next_chapter"]

    chapter.is_translated = True
    chapter.save()

    for bible in data["character_bible"]:
        BibleInfo.create(
            name=bible["name"],
            description=bible["description"],
            novel=chapter.novel
        )

    pass

if __name__ == "__main__":
    main()