#!/usr/bin/python

import audit
import db
import utils
from i18n import _, now, python2display

def get_stocklevel_query(dbo):
    return "SELECT s.*, s.ID AS SLID, l.LocationName AS StockLocationName " \
        "FROM stocklevel s " \
        "INNER JOIN stocklocation l ON s.StockLocationID = l.ID " 

def get_stocklevels(dbo, location = 0):
    """
    Returns a set of stock levels for a location or 0 for all locations.
    """
    wc = ""
    if location != 0: wc = "AND s.StockLocationID = %d" % location
    return db.query(dbo, "%s WHERE Balance > 0 %s ORDER BY s.StockLocationID, s.Name" % (get_stocklevel_query(dbo), wc))

def get_stocklevel(dbo, slid):
    """
    Returns a single stocklevel record
    """
    if slid is None: return None
    sl = db.query(dbo, get_stocklevel_query(dbo) + " WHERE s.ID = %d" % slid)
    if len(sl) == 0: return None
    return sl[0]

def get_stock_names(dbo):
    """
    Returns a set of unique stock names for autocomplete.
    """
    names = []
    rows = db.query(dbo, "SELECT DISTINCT Name FROM stocklevel ORDER BY Name")
    for r in rows:
        names.append(r["NAME"])
    return names

def get_last_stock_with_name(dbo, name):
    """
    Returns the last description, unit and total we saw for stock with name
    """
    rows = db.query(dbo, "SELECT Description, UnitName, Total FROM stocklevel WHERE Name LIKE %s ORDER BY ID DESC" % db.ds(name))
    if len(rows) > 0:
        return "%s|%s|%f" % (rows[0]["DESCRIPTION"], rows[0]["UNITNAME"], rows[0]["TOTAL"])
    return "||"

def get_stock_items(dbo):
    """
    Returns a set of stock items.
    """
    rows = db.query(dbo, "SELECT sv.*, sl.LocationName " \
        "FROM stocklevel sv " \
        "INNER JOIN stocklocation sl ON sl.ID = sv.StockLocationID " \
        "WHERE sv.Balance > 0 " \
        "ORDER BY sv.StockLocationID, sv.Name")
    for r in rows:
        r["ITEMNAME"] = "%s - %s %s %s (%g/%g)" % (r["LOCATIONNAME"], r["NAME"], r["BATCHNUMBER"], 
            python2display(dbo.locale, r["EXPIRY"]), r["BALANCE"], r["TOTAL"])
    return rows

def get_stock_locations_totals(dbo):
    """
    Returns a list of all stock locations with the total number of stocked
    items in each.
    """
    rows = db.query(dbo, "SELECT sl.ID, sl.LocationName, COUNT(s.ID) AS Total FROM stocklevel s INNER JOIN stocklocation sl ON sl.ID = s.StockLocationID WHERE s.Balance > 0 GROUP BY sl.ID, sl.LocationName ORDER BY sl.LocationName")
    return rows

def get_stock_units(dbo):
    """
    Returns a set of unique stock units for autocomplete.
    """
    names = []
    rows = db.query(dbo, "SELECT DISTINCT UnitName FROM stocklevel ORDER BY UnitName")
    for r in rows:
        names.append(r["UNITNAME"])
    return names

def update_stocklevel_from_form(dbo, post, username):
    """
    Updates a stocklevel item from a dialog. The post should include
    the ID of the stocklevel to adjust and a usage record will be
    written so usage data should be sent too.
    """
    l = dbo.locale
    slid = post.integer("stocklevelid")
    if post["name"] == "":
        raise utils.ASMValidationError(_("Stock level must have a name", l))
    if post["unitname"] == "":
        raise utils.ASMValidationError(_("Stock level must have a unit", l))
    preaudit = db.query(dbo, "SELECT * FROM stocklevel WHERE ID = %d" % slid)
    if len(preaudit) == 0:
        raise utils.ASMValidationError("stocklevel %d does not exist, cannot adjust" % slid)
    db.execute(dbo, db.make_update_sql("stocklevel", "ID=%d" % slid, (
        ( "Name", post.db_string("name") ),
        ( "Description", post.db_string("description") ),
        ( "StockLocationID", post.db_integer("location") ),
        ( "UnitName", post.db_string("unitname") ),
        ( "Total", post.db_floating("total") ),
        ( "Balance", post.db_floating("balance") ),
        ( "Expiry", post.db_date("expiry") ),
        ( "BatchNumber", post.db_string("batchnumber") )
    )))
    postaudit = db.query(dbo, "SELECT * FROM stocklevel WHERE ID = %d" % slid)
    diff = postaudit[0]["BALANCE"] - preaudit[0]["BALANCE"]
    if diff != 0: insert_stockusage(dbo, username, slid, diff, post.date("usagedate"), post.integer("usagetype"), post["comments"])
    audit.edit(dbo, username, "animalcontrol", audit.map_diff(preaudit, postaudit))

def insert_stocklevel_from_form(dbo, post, username):
    """
    Inserts a stocklevel item from a dialog. The post should include
    the ID of the stocklevel to adjust and a usage record will be
    written so usage data should be sent too.
    """
    l = dbo.locale
    slid = post.integer("id")
    if post["name"] == "":
        raise utils.ASMValidationError(_("Stock level must have a name", l))
    if post["unitname"] == "":
        raise utils.ASMValidationError(_("Stock level must have a unit", l))

    nid = db.get_id(dbo, "stocklevel")
    db.execute(dbo, db.make_insert_sql("stocklevel", (
        ( "ID", db.di(nid) ),
        ( "Name", post.db_string("name") ),
        ( "Description", post.db_string("description") ),
        ( "StockLocationID", post.db_integer("location") ),
        ( "UnitName", post.db_string("unitname") ),
        ( "Total", post.db_floating("total") ),
        ( "Balance", post.db_floating("balance") ),
        ( "Expiry", post.db_date("expiry") ),
        ( "BatchNumber", post.db_string("batchnumber") ),
        ( "CreatedDate", db.todaysql() )
    )))
    insert_stockusage(dbo, username, slid, post.floating("balance"), post.date("usagedate"), post.integer("usagetype"), post["comments"])
    audit.create(dbo, username, "stocklevel", str(nid))
    return nid

def delete_stocklevel(dbo, username, slid):
    """
    Deletes a stocklevel record
    """
    audit.delete(dbo, username, "stocklevel", str(db.query(dbo, "SELECT * FROM stocklevel WHERE ID=%d" % slid)))
    db.execute(dbo, "DELETE FROM stockusage WHERE StockLevelID = %d" % slid)
    db.execute(dbo, "DELETE FROM stocklevel WHERE ID = %d" % slid)

def insert_stockusage(dbo, username, slid, diff, usagedate, usagetype, comments):
    """
    Inserts a new stock usage record
    """
    nid = db.get_id(dbo, "stockusage")
    db.execute(dbo, db.make_insert_user_sql(dbo, "stockusage", username, (
        ( "ID", db.di(nid)),
        ( "StockUsageTypeID", db.di(usagetype) ),
        ( "StockLevelID", db.di(slid) ),
        ( "UsageDate", db.dd(usagedate) ),
        ( "Quantity", db.df(diff) ),
        ( "Comments", db.ds(comments) )
    )))
    audit.create(dbo, username, "stockusage", str(nid))

def deduct_stocklevel_from_form(dbo, username, post):
    """
    Should include a stocklevel in the post as "item" and 
    stockusage fields. Creates a usage record and deducts
    the stocklevel.
    """
    item = post.integer("item")
    quantity = post.floating("quantity")
    usagetype = post.integer("usagetype")
    usagedate = post.date("usagedate")
    comments = post["usagecomments"]
    curq = db.query_float(dbo, "SELECT Balance FROM stocklevel WHERE ID = %d" % item)
    newq = curq - quantity
    db.execute(dbo, "UPDATE stocklevel SET Balance = %f WHERE ID = %d" % (newq, item))
    insert_stockusage(dbo, username, item, quantity, usagedate, usagetype, comments)

def stock_take_from_mobile_form(dbo, username, post):
    """
    Post should contain sl{ID} values for new balances.
    """
    if post.integer("usagetype") == 0:
        raise utils.ASMValidationError("No usage type passed")
    for k in post.data.iterkeys():
        if k.startswith("sl"):
            slid = utils.cint(k.replace("sl", ""))
            sl = get_stocklevel(dbo, slid)
            slb = utils.cfloat(sl["BALANCE"]) # balance
            sln = post.floating(k)            # new balance
            # If the balance hasn't changed, do nothing
            if slb == sln: continue
            # Update the level
            db.execute(dbo, "UPDATE stocklevel SET Balance = %f WHERE ID = %d" % ( sln, slid ))
            # Write a stock usage record for the difference
            insert_stockusage(dbo, username, slid, sln - slb, now(dbo.timezone), post.integer("usagetype"), "")

