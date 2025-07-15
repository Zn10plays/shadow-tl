import shadow_db as db

bible = db.BibleInfo.select().where(db.BibleInfo.novel == 1)

# delete all duplicate rows with the same name
for info in bible:
    break # so this is not run by accident
    db.BibleInfo.delete().where((db.BibleInfo.id != info.id) & (db.BibleInfo.name == info.name)).execute()