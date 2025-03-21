# ownercitation table
sql = "CREATE TABLE ownercitation (" \
    "ID INTEGER NOT NULL PRIMARY KEY, " \
    "OwnerID INTEGER NOT NULL, " \
    "AnimalControlID INTEGER, " \
    "CitationTypeID INTEGER NOT NULL, " \
    "CitationDate %(date)s NOT NULL, " \
    "FineAmount INTEGER, " \
    "FineDueDate %(date)s, " \
    "FinePaidDate %(date)s, " \
    "Comments %(long)s, " \
    "RecordVersion INTEGER, " \
    "CreatedBy %(short)s, " \
    "CreatedDate %(date)s, " \
    "LastChangedBy %(short)s, " \
    "LastChangedDate %(date)s)" % { "short": dbo.type_shorttext, "long": dbo.type_longtext, "date": dbo.type_datetime }
execute(dbo,sql)
add_index(dbo, "ownercitation_OwnerID", "ownercitation", "OwnerID")
add_index(dbo, "ownercitation_CitationTypeID", "ownercitation", "CitationTypeID")
add_index(dbo, "ownercitation_CitationDate", "ownercitation", "CitationDate")
add_index(dbo, "ownercitation_FineDueDate", "ownercitation", "FineDueDate")
add_index(dbo, "ownercitation_FinePaidDate", "ownercitation", "FinePaidDate")