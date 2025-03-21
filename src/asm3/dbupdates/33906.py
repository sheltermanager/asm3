l = dbo.locale
# Add ownerrota.WorkTypeID
add_column(dbo, "ownerrota", "WorkTypeID", "INTEGER")
add_index(dbo, "ownerrota_WorkTypeID", "ownerrota", "WorkTypeID")
execute(dbo,"UPDATE ownerrota SET WorkTypeID = 1")
# Add lkworktype
sql = "CREATE TABLE lkworktype ( ID INTEGER NOT NULL PRIMARY KEY, " \
    "WorkType %(short)s NOT NULL)" % { "short": dbo.type_shorttext }
execute(dbo,sql)
execute(dbo,"INSERT INTO lkworktype (ID, WorkType) VALUES (?, ?)", [1, _("General", l)] )
execute(dbo,"INSERT INTO lkworktype (ID, WorkType) VALUES (?, ?)", [2, _("Kennel", l)] )
execute(dbo,"INSERT INTO lkworktype (ID, WorkType) VALUES (?, ?)", [3, _("Cattery", l)] )
execute(dbo,"INSERT INTO lkworktype (ID, WorkType) VALUES (?, ?)", [4, _("Reception", l)] )
execute(dbo,"INSERT INTO lkworktype (ID, WorkType) VALUES (?, ?)", [5, _("Office", l)] )
