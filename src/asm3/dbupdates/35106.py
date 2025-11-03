from asm3.configuration import email_diary_notes
from asm3.dbupdate import execute

if email_diary_notes(dbo):
    execute(dbo, "UPDATE configuration SET ItemValue = ? WHERE ItemName = ?", ["EmailDiaryNotes", "1"])
else:
    execute(dbo, "UPDATE configuration SET ItemValue = ? WHERE ItemName = ?", ["EmailDiaryNotes", "-1"])
