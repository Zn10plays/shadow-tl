from peewee import *
from datetime import datetime

# SQLite DB initialization
db = SqliteDatabase('./db/webnovels.db')

# Base model
class BaseModel(Model):
    class Meta:
        database = db

# Novel model
class Novel(BaseModel):
    title = CharField(500)
    url = CharField(500, unique=True)
    last_updated = DateTimeField(default=datetime.now)

class BibleInfo(BaseModel):
    """
    Model to represent character or place information.
    """
    name = CharField(max_length=255)
    description = TextField()
    novel = ForeignKeyField(Novel, backref='bible_info', on_delete='CASCADE')

# Chapter model
class Chapter(BaseModel):
    novel = ForeignKeyField(Novel, backref='chapters', on_delete='CASCADE')
    content = TextField()
    accessed_at = DateTimeField(default=datetime.now)
    title = CharField(500)
    url = CharField(500)
    chapter_number = IntegerField()
    is_filled = BooleanField(default=False)
    is_translated = BooleanField(default=False)
    translated_content = TextField(null=True)
    summary = TextField(null=True)
    notes_for_next_chapter = TextField(null=True)

    class Meta:
        indexes = (
            (('novel', 'chapter_number'), True),  # Unique per novel
        )

# Create tables
db.connect()
db.create_tables([Novel, Chapter, BibleInfo], safe=True)

def add_novel(title, url):
    try:
        novel, created = Novel.get_or_create(title=title, url=url)
        if created:
            print(f"Novel '{title}' added.")
        else:
            print(f"Novel '{title}' already exists.")
        return novel
    except IntegrityError:
        print("Novel URL must be unique.")
        return None

def add_chapter(novel_url, title, content, url, chapter_number, overwrite=False):
    try:
        novel = Novel.get(Novel.url == novel_url)

        existing_chapter = Chapter.get_or_none(
            Chapter.url == url,
        )

        if not overwrite and existing_chapter:
            print(f"Chapter {chapter_number} already exists in novel '{novel.title}'.")
            return existing_chapter

        chapter = Chapter.create(
            novel=novel,
            title=title,
            content=content,
            url=url,
            chapter_number=chapter_number
        )
        novel.last_updated = datetime.now()
        novel.save()
        print(f"Chapter '{title}' added to novel '{novel.title}'.")
        return chapter
    except Novel.DoesNotExist:
        print("Novel not found.")
    except IntegrityError:
        print("Chapter number must be unique per novel.")

def get_novel(url):
    try:
        novel = Novel.get(Novel.url == url)
        print(f"Title: {novel.title}, Last Updated: {novel.last_updated}")
        return novel
    except Novel.DoesNotExist:
        print("Novel not found.")

def list_chapters(novel_url):
    try:
        novel = Novel.get(Novel.url == novel_url)
        chapters = novel.chapters.order_by(Chapter.chapter_number)
        for chapter in chapters:
            print(f"Chapter {chapter.chapter_number}: {chapter.title}")
        return chapters
    except Novel.DoesNotExist:
        print("Novel not found.")

def remove_novel(url):
    try:
        novel = Novel.get(Novel.url == url)
        novel.delete_instance(recursive=True)
        print(f"Novel '{novel.title}' and its chapters removed.")
    except Novel.DoesNotExist:
        print("Novel not found.")

def remove_chapter(novel_url, chapter_number):
    try:
        novel = Novel.get(Novel.url == novel_url)
        chapter = Chapter.get(Chapter.novel == novel, Chapter.chapter_number == chapter_number)
        chapter.delete_instance()
        print(f"Chapter {chapter_number} removed from '{novel.title}'.")
    except (Novel.DoesNotExist, Chapter.DoesNotExist):
        print("Novel or chapter not found.")

def add_bible_info(novel_url, name, description):
    try:
        novel = Novel.get(Novel.url == novel_url)
        bible_info, created = BibleInfo.get_or_create(
            name=name,
            novel=novel,
            defaults={'description': description}
        )
        if created:
            print(f"Bible info '{name}' added to novel '{novel.title}'.")
        else:
            print(f"Bible info '{name}' already exists in novel '{novel.title}'.")
        return bible_info
    except Novel.DoesNotExist:
        print("Novel not found.")

def update_bible_info(novel_url, name, description):
    try:
        novel = Novel.get(Novel.url == novel_url)
        bible_info = BibleInfo.get(BibleInfo.name == name, BibleInfo.novel == novel)
        bible_info.description = description
        bible_info.save()
        print(f"Bible info '{name}' updated in novel '{novel.title}'.")
        return bible_info
    except (Novel.DoesNotExist, BibleInfo.DoesNotExist):
        print("Novel or bible info not found.")

def list_bible_info(novel_url):
    try:
        novel = Novel.get(Novel.url == novel_url)
        bible_info_list = novel.bible_info
        for info in bible_info_list:
            print(f"Name: {info.name}, Description: {info.description}")
        return bible_info_list
    except Novel.DoesNotExist:
        print("Novel not found.")