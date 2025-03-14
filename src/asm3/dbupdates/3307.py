# Create new animaltest tables
sql = "CREATE TABLE animaltest (ID INTEGER NOT NULL PRIMARY KEY, " \
    "AnimalID INTEGER NOT NULL, " \
    "TestTypeID INTEGER NOT NULL, " \
    "TestResultID INTEGER NOT NULL, " \
    "DateOfTest %(date)s, " \
    "DateRequired %(date)s NOT NULL, " \
    "Cost INTEGER, " \
    "Comments %(long)s, " \
    "RecordVersion INTEGER, " \
    "CreatedBy %(short)s, " \
    "CreatedDate %(date)s, " \
    "LastChangedBy %(short)s, " \
    "LastChangedDate %(date)s)" % { "date": dbo.type_datetime, "long": dbo.type_longtext, "short": dbo.type_shorttext}
execute(dbo,sql)
add_index(dbo, "animaltest_AnimalID", "animaltest", "AnimalID")
sql = "CREATE TABLE testtype (ID INTEGER NOT NULL PRIMARY KEY, " \
    "TestName %(short)s NOT NULL, " \
    "TestDescription %(long)s, " \
    "DefaultCost INTEGER)" % { "short": dbo.type_shorttext, "long": dbo.type_longtext }
execute(dbo,sql)
sql = "CREATE TABLE testresult (ID INTEGER NOT NULL PRIMARY KEY, " \
    "ResultName %(short)s NOT NULL, " \
    "ResultDescription %(long)s)" % { "short": dbo.type_shorttext, "long": dbo.type_longtext }
execute(dbo,sql)