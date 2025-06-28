l = dbo.locale
# Add stock tables
sql = "CREATE TABLE stocklevel ( ID INTEGER NOT NULL, " \
    "Name %(short)s NOT NULL, " \
    "Description %(long)s, " \
    "StockLocationID INTEGER NOT NULL, " \
    "UnitName %(short)s NOT NULL, " \
    "Total INTEGER, " \
    "Balance INTEGER NOT NULL, " \
    "Expiry %(date)s, " \
    "BatchNumber %(short)s, " \
    "CreatedDate %(date)s NOT NULL)" % { "short": dbo.type_shorttext, "long": dbo.type_longtext, "date": dbo.type_datetime }
execute(dbo,sql)
add_index(dbo, "stocklevel_ID", "stocklevel", "ID", True)
add_index(dbo, "stocklevel_Name", "stocklevel", "Name")
add_index(dbo, "stocklevel_UnitName", "stocklevel", "UnitName")
add_index(dbo, "stocklevel_StockLocationID", "stocklevel", "StockLocationID")
add_index(dbo, "stocklevel_Expiry", "stocklevel", "Expiry")
add_index(dbo, "stocklevel_BatchNumber", "stocklevel", "BatchNumber")
sql = "CREATE TABLE stocklocation ( ID INTEGER NOT NULL, " \
    "LocationName %(short)s NOT NULL, " \
    "LocationDescription %(long)s )" % { "short": dbo.type_shorttext, "long": dbo.type_longtext }
execute(dbo,sql)
add_index(dbo, "stocklocation_ID", "stocklocation", "ID", True)
add_index(dbo, "stocklocation_LocationName", "stocklocation", "LocationName", True)
execute(dbo,"INSERT INTO stocklocation VALUES (1, '%s', '')" % _("Stores", l))
sql = "CREATE TABLE stockusage ( ID INTEGER NOT NULL, " \
    "StockUsageTypeID INTEGER NOT NULL, " \
    "StockLevelID INTEGER NOT NULL, " \
    "UsageDate %(date)s NOT NULL, " \
    "Quantity INTEGER NOT NULL, " \
    "Comments %(long)s, " \
    "RecordVersion INTEGER, " \
    "CreatedBy %(short)s, " \
    "CreatedDate %(date)s, " \
    "LastChangedBy %(short)s, " \
    "LastChangedDate %(date)s)" % { "short": dbo.type_shorttext, "long": dbo.type_longtext, "date": dbo.type_datetime }
execute(dbo,sql)
add_index(dbo, "stockusage_ID", "stockusage", "ID", True)
add_index(dbo, "stockusage_StockUsageTypeID", "stockusage", "StockUsageTypeID")
add_index(dbo, "stockusage_StockLevelID", "stockusage", "StockLevelID")
add_index(dbo, "stockusage_UsageDate", "stockusage", "UsageDate")
sql = "CREATE TABLE stockusagetype ( ID INTEGER NOT NULL, " \
    "UsageTypeName %(short)s NOT NULL, " \
    "UsageTypeDescription %(long)s )" % { "short": dbo.type_shorttext, "long": dbo.type_longtext }
execute(dbo,sql)
add_index(dbo, "stockusagetype_ID", "stockusagetype", "ID", True)
add_index(dbo, "stockusagetype_UsageTypeName", "stockusagetype", "UsageTypeName")
execute(dbo,"INSERT INTO stockusagetype VALUES (1, ?, '')", [ _("Administered", l)])
execute(dbo,"INSERT INTO stockusagetype VALUES (2, ?, '')", [ _("Consumed", l)])
execute(dbo,"INSERT INTO stockusagetype VALUES (3, ?, '')", [ _("Donated", l)])
execute(dbo,"INSERT INTO stockusagetype VALUES (4, ?, '')", [ _("Purchased", l)])
execute(dbo,"INSERT INTO stockusagetype VALUES (5, ?, '')", [ _("Sold", l)])
execute(dbo,"INSERT INTO stockusagetype VALUES (6, ?, '')", [ _("Stocktake", l)])
execute(dbo,"INSERT INTO stockusagetype VALUES (7, ?, '')", [ _("Wasted", l)])
