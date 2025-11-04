from asm3.configuration import email_diary_notes
from asm3.dbupdate import execute

queryresult = dbo.query("SELECT ItemValue FROM configuration WHERE ItemName = ?", ["EmailDiaryNotes",])

if queryresult:
    itemvalue = queryresult[0].ITEMVALUE

    if itemvalue == "Yes":
        execute(dbo, "UPDATE configuration SET ItemValue = ? WHERE ItemName = ?", ["EmailDiaryNotes", "1"])
    else:
        execute(dbo, "UPDATE configuration SET ItemValue = ? WHERE ItemName = ?", ["EmailDiaryNotes", "-1"])
else:
    execute(dbo, "INSERT INTO configuration (ItemName, ItemValue) VALUES (?, ?)", ["EmailDiaryNotes", "1"])
