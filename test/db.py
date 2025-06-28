import db.connector as db

bible = db.BibleInfo.select().where(db.BibleInfo.novel == 1)

print([f'{instance.name}:{instance.description}' for instance in bible], bible.exists())

