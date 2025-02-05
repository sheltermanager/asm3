
import asm3.utils
from asm3.i18n import _, now, python2display
from asm3.typehints import datetime, Database, List, PostedData, ResultRow, Results

def get_stocklevel_query(dbo: Database) -> str:
    return "SELECT s.*, s.ID AS SLID, l.LocationName AS StockLocationName " \
        "FROM stocklevel s " \
        "INNER JOIN stocklocation l ON s.StockLocationID = l.ID " 

def get_stocklevels(dbo: Database, location: int = 0) -> Results:
    """
    Returns a set of stock levels for a location or 0 for all locations.
    """
    wc = ""
    if location != 0: wc = "AND s.StockLocationID = %d" % location
    return dbo.query("%s WHERE Balance > 0 %s ORDER BY s.StockLocationID, s.Name" % (get_stocklevel_query(dbo), wc))

def get_stocklevels_depleted(dbo: Database) -> Results:
    """ Returns a set of depleted stock levels """
    return dbo.query("%s WHERE Balance <= 0 ORDER BY s.StockLocationID, s.Name" % (get_stocklevel_query(dbo)))

def get_stocklevels_lowbalance(dbo: Database) -> Results:
    """ Returns a set of low balance stock levels """
    return dbo.query("%s WHERE Balance < Low ORDER BY s.StockLocationID, s.Name" % (get_stocklevel_query(dbo)))

def get_stocklevel(dbo: Database, slid: int) -> ResultRow:
    """
    Returns a single stocklevel record
    """
    if slid is None: return None
    return dbo.first_row(dbo.query(get_stocklevel_query(dbo) + " WHERE s.ID = ?", [slid]))

def get_stock_names(dbo: Database) -> List[str]:
    """
    Returns a set of unique stock names for autocomplete.
    """
    names = []
    rows = dbo.query("SELECT DISTINCT Name FROM stocklevel ORDER BY Name")
    for r in rows:
        names.append(r.NAME)
    return names

def get_last_stock_with_name(dbo: Database, name: str) -> str:
    """
    Returns the last description, unit and total we saw for stock with name
    """
    r = dbo.first_row(dbo.query("SELECT Description, UnitName, Total FROM stocklevel WHERE Name LIKE ? ORDER BY ID DESC", [name]))
    if r is not None:
        return "%s|%s|%f" % (r.DESCRIPTION, r.UNITNAME, r.TOTAL)
    return "||"

def get_stock_items(dbo: Database) -> Results:
    """
    Returns a set of stock items.
    """
    rows = dbo.query("SELECT sv.*, sl.LocationName " \
        "FROM stocklevel sv " \
        "INNER JOIN stocklocation sl ON sl.ID = sv.StockLocationID " \
        "WHERE sv.Balance > 0 " \
        "ORDER BY sv.StockLocationID, sv.Name")
    for r in rows:
        r.ITEMNAME = "%s %s %s (%g/%g) [%s]" % (r.NAME, r.BATCHNUMBER, 
            python2display(dbo.locale, r.EXPIRY), r.BALANCE, r.TOTAL, r.LOCATIONNAME)
    return rows

def get_stock_locations_totals(dbo: Database) -> Results:
    """
    Returns a list of all stock locations with the total number of stocked
    items in each.
    """
    return dbo.query("SELECT sl.ID, sl.LocationName, sl.LocationDescription, " \
        "COUNT(s.ID) AS Total " \
        "FROM stocklevel s " \
        "INNER JOIN stocklocation sl ON sl.ID = s.StockLocationID " \
        "WHERE s.Balance > 0 " \
        "GROUP BY sl.ID, sl.LocationName, sl.LocationDescription ORDER BY sl.LocationName")

def get_stock_units(dbo: Database) -> List[str]:
    """
    Returns a set of unique stock units for autocomplete.
    """
    names = []
    rows = dbo.query("SELECT DISTINCT UnitName FROM stocklevel ORDER BY UnitName")
    for r in rows:
        names.append(r.UNITNAME)
    return names

def update_stocklevel_from_form(dbo: Database, post: PostedData, username: str) -> None:
    """
    Updates a stocklevel item from a dialog. The post should include
    the ID of the stocklevel to adjust and a usage record will be
    written so usage data should be sent too.
    """
    l = dbo.locale
    slid = post.integer("stocklevelid")
    if slid == 0:
        raise asm3.utils.ASMValidationError("Invalid stock level")
    if post["name"] == "":
        raise asm3.utils.ASMValidationError(_("Stock level must have a name", l))
    if post["unitname"] == "":
        raise asm3.utils.ASMValidationError(_("Stock level must have a unit", l))
    if post.date("usagedate") is None:
        raise asm3.utils.ASMValidationError(_("Stock usage must have a date", l))

    diff = post.floating("balance") - dbo.query_float("SELECT Balance FROM stocklevel WHERE ID = ?", [slid])

    dbo.update("stocklevel", slid, {
        "Name":             post["name"],
        "Description":      post["description"],
        "Barcode":          post["barcode"],
        "StockLocationID":  post.integer("location"),
        "UnitName":         post["unitname"],
        "Total":            post.floating("total"),
        "Balance":          post.floating("balance"),
        "Low":              post.floating("low"),
        "Expiry":           post.date("expiry"),
        "BatchNumber":      post["batchnumber"],
        "Cost":             post.integer("cost"),
        "UnitPrice":        post.integer("unitprice")
    }, username, setLastChanged=False, setRecordVersion=False)

    if diff != 0: 
        insert_stockusage(dbo, username, slid, diff, post.date("usagedate"), post.integer("usagetype"), post["comments"])

def insert_stocklevel_from_form(dbo: Database, post: PostedData, username: str) -> int:
    """
    Inserts a stocklevel item from a dialog.
    A usage record will be written, so usage data should be sent too.
    """
    l = dbo.locale
    if post["name"] == "":
        raise asm3.utils.ASMValidationError(_("Stock level must have a name", l))
    if post["unitname"] == "":
        raise asm3.utils.ASMValidationError(_("Stock level must have a unit", l))
    if post.date("usagedate") is None:
        raise asm3.utils.ASMValidationError(_("Stock usage must have a date", l))
   
    nid = dbo.insert("stocklevel", {
        "Name":             post["name"],
        "Description":      post["description"],
        "Barcode":          post["barcode"],
        "StockLocationID":  post.integer("location"),
        "UnitName":         post["unitname"],
        "Total":            post.floating("total"),
        "Balance":          post.floating("balance"),
        "Low":              post.floating("low"),
        "Expiry":           post.date("expiry"),
        "BatchNumber":      post["batchnumber"],
        "Cost":             post.integer("cost"),
        "UnitPrice":        post.integer("unitprice"),
        "CreatedDate":      dbo.now()
    }, username, setCreated=False, setRecordVersion=False)

    insert_stockusage(dbo, username, nid, post.floating("balance"), post.date("usagedate"), post.integer("usagetype"), post["comments"])
    return nid

def delete_stocklevel(dbo: Database, username: str, slid: int) -> None:
    """
    Deletes a stocklevel record
    """
    dbo.delete("stockusage", "StockLevelID=%d" % slid, username)
    dbo.delete("stocklevel", slid, username)

def insert_stockusage(dbo: Database, username: str, slid: int, diff: float, usagedate: datetime, usagetype: int, comments: str) -> int:
    """
    Inserts a new stock usage record
    """
    if slid == 0: raise asm3.utils.ASMValidationError("Invalid stock level")
    return dbo.insert("stockusage", {
        "StockUsageTypeID":     usagetype,
        "StockLevelID":         slid,
        "UsageDate":            usagedate,
        "Quantity":             diff,
        "Comments":             comments
    }, username)

def deduct_stocklevel_from_form(dbo: Database, username: str, post: PostedData) -> int:
    """
    Should include a stocklevel in the post as "item" and 
    stockusage fields. Creates a usage record and deducts
    the stocklevel.
    """
    item = post.integer("item")
    if item == 0: raise asm3.utils.ASMValidationError("Invalid stock level")
    quantity = post.floating("quantity")
    usagetype = post.integer("usagetype")
    usagedate = post.date("usagedate")
    comments = post["usagecomments"]
    curq = dbo.query_float("SELECT Balance FROM stocklevel WHERE ID = ?", [item])
    newq = curq - quantity
    dbo.update("stocklevel", item, { "Balance": newq })
    return insert_stockusage(dbo, username, item, quantity * -1, usagedate, usagetype, comments)

def stock_take_from_mobile_form(dbo: Database, username: str, post: PostedData) -> None:
    """
    Post should contain sl{ID} values for new balances.
    """
    if post.integer("usagetype") == 0:
        raise asm3.utils.ASMValidationError("No usage type passed")

    for k in post.data.keys():
        if k.startswith("sl"):
            slid = asm3.utils.cint(k.replace("sl", ""))
            sl = get_stocklevel(dbo, slid)
            slb = asm3.utils.cfloat(sl.BALANCE) # balance
            sln = post.floating(k)         # new balance
            # If the balance hasn't changed, do nothing
            if slb == sln: continue
            # Update the level
            dbo.update("stocklevel", slid, { "Balance": sln })
            # Write a stock usage record for the difference
            insert_stockusage(dbo, username, slid, sln - slb, now(dbo.timezone), post.integer("usagetype"), "")
