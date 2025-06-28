import db.connector as db

bible = db.BibleInfo.select().where(db.BibleInfo.novel == 1)

print(bible, bible.exists())