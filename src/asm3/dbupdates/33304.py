# Add trap loan table
sql = "CREATE TABLE ownertraploan (" \
    "ID INTEGER NOT NULL PRIMARY KEY, " \
    "OwnerID INTEGER NOT NULL, " \
    "TrapTypeID INTEGER NOT NULL, " \
    "LoanDate %(date)s NOT NULL, " \
    "DepositAmount INTEGER, " \
    "DepositReturnDate %(date)s, " \
    "TrapNumber %(short)s, " \
    "ReturnDueDate %(date)s, " \
    "ReturnDate %(date)s, " \
    "Comments %(long)s, " \
    "RecordVersion INTEGER, " \
    "CreatedBy %(short)s, " \
    "CreatedDate %(date)s, " \
    "LastChangedBy %(short)s, " \
    "LastChangedDate %(date)s)" % { "short": dbo.type_shorttext, "long": dbo.type_longtext, "date": dbo.type_datetime }
execute(dbo,sql)
add_index(dbo, "ownertraploan_OwnerID", "ownertraploan", "OwnerID")
add_index(dbo, "ownertraploan_TrapTypeID", "ownertraploan", "TrapTypeID")
add_index(dbo, "ownertraploan_ReturnDueDate", "ownertraploan", "ReturnDueDate")
add_index(dbo, "ownertraploan_ReturnDate", "ownertraploan", "ReturnDate")