# Add licence table
sql = "CREATE TABLE ownerlicence (" \
    "ID INTEGER NOT NULL PRIMARY KEY, " \
    "OwnerID INTEGER NOT NULL, " \
    "AnimalID INTEGER NOT NULL, " \
    "LicenceTypeID INTEGER NOT NULL, " \
    "LicenceNumber %(short)s, " \
    "LicenceFee INTEGER, " \
    "IssueDate %(date)s, " \
    "ExpiryDate %(date)s, " \
    "Comments %(long)s, " \
    "RecordVersion INTEGER, " \
    "CreatedBy %(short)s, " \
    "CreatedDate %(date)s, " \
    "LastChangedBy %(short)s, " \
    "LastChangedDate %(date)s)" % { "short": dbo.type_shorttext, "long": dbo.type_longtext, "date": dbo.type_datetime }
execute(dbo,sql)
add_index(dbo, "ownerlicence_OwnerID", "ownerlicence", "OwnerID")
add_index(dbo, "ownerlicence_AnimalID", "ownerlicence", "AnimalID")
add_index(dbo, "ownerlicence_LicenceTypeID", "ownerlicence", "LicenceTypeID")
add_index(dbo, "ownerlicence_LicenceNumber", "ownerlicence", "LicenceNumber", True)
add_index(dbo, "ownerlicence_IssueDate", "ownerlicence", "IssueDate")
add_index(dbo, "ownerlicence_ExpiryDate", "ownerlicence", "ExpiryDate")