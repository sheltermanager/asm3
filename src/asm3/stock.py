
import asm3.utils
import asm3.lookups
from asm3.i18n import _, now, python2display
from asm3.typehints import datetime, Database, List, PostedData, ResultRow, Results

def get_stocklevel_query(dbo: Database) -> str:
    return "SELECT s.*, s.ID AS SLID, l.LocationName AS StockLocationName " \
        "FROM stocklevel s " \
        "INNER JOIN stocklocation l ON s.StockLocationID = l.ID "

def get_unit_sql(dbo: Database) -> str:
    unitsql = ""
    for unitdict in asm3.lookups.get_unit_types(dbo):
        unitsql = unitsql + "WHEN product.UnitTypeID = %s THEN '%s' " % (str(unitdict["ID"]), unitdict["UNITNAME"])
    return unitsql

def get_products(dbo: Database, includeretired=False) -> Results:
    """
    Returns all products
    """

    return dbo.query("SELECT product.*, " \
        "(SELECT SUM(Balance) FROM stocklevel WHERE ProductID = product.ID) AS Balance, " \
        "CASE " \
        "WHEN product.UnitTypeID = 0 THEN '%s' " \
        "WHEN product.UnitTypeID = -1 THEN product.CustomUnit " \
        "%s" \
        "ELSE product.CustomUnit " \
        "END AS Unit " \
        "FROM product " \
        "WHERE IsRetired = %s " \
        "ORDER BY ProductName" % (_("unit"), get_unit_sql(dbo), int(includeretired)))

def get_active_products(dbo: Database) -> Results:
    """
    Returns all products that are not retired
    """
    return dbo.query("SELECT product.*, " \
        "(SELECT SUM(Balance) FROM stocklevel WHERE ProductID = product.ID) AS Balance, " \
        "CASE " \
        "WHEN product.UnitTypeID = 0 THEN '%s' " \
        "WHEN product.UnitTypeID = -1 THEN product.CustomUnit " \
        "%s" \
        "ELSE product.CustomUnit " \
        "END AS Unit " \
        "FROM product " \
        "WHERE IsRetired = %s " \
        "ORDER BY ProductName" % (_("unit"), get_unit_sql(dbo), 0))

def get_depleted_products(dbo: Database) -> Results:
    """
    Returns all products that are not retired and have a balance of zero or less
    """

    return dbo.query("SELECT product.*, " \
        "(SELECT SUM(Balance) FROM stocklevel WHERE ProductID = product.ID) AS Balance, " \
        "CASE " \
        "WHEN product.UnitTypeID = 0 THEN '%s' " \
        "WHEN product.UnitTypeID = -1 THEN product.CustomUnit " \
        "%s" \
        "ELSE product.CustomUnit " \
        "END AS Unit " \
        "FROM product " \
        "WHERE IsRetired = %s " \
        "AND ((SELECT SUM(stockusage.Quantity) FROM stockusage INNER JOIN stocklevel ON stockusage.StockLevelID = stocklevel.ID WHERE stocklevel.ProductID = product.ID) <= 0 " \
        "OR (SELECT SUM(stockusage.Quantity) FROM stockusage INNER JOIN stocklevel ON stockusage.StockLevelID = stocklevel.ID WHERE stocklevel.ProductID = product.ID) IS NULL) " \
        "ORDER BY ProductName" % (_("unit"), get_unit_sql(dbo), 0))

def get_low_balance_products(dbo: Database) -> Results:
    """
    Returns all products that are not retired, have a non-zero globalminimum and have a balance below the globalminimum
    """
    return dbo.query("SELECT product.*, " \
        "(SELECT SUM(Balance) FROM stocklevel WHERE ProductID = product.ID) AS Balance, " \
        "CASE " \
        "WHEN product.UnitTypeID = 0 THEN '%s' " \
        "WHEN product.UnitTypeID = -1 THEN product.CustomUnit " \
        "%s" \
        "ELSE product.CustomUnit " \
        "END AS Unit " \
        "FROM product " \
        "WHERE IsRetired = %s " \
        "AND product.GlobalMinimum > 0 " \
        "AND ((SELECT SUM(stockusage.Quantity) FROM stockusage INNER JOIN stocklevel ON stockusage.StockLevelID = stocklevel.ID WHERE stocklevel.ProductID = product.ID) < product.GlobalMinimum " \
        "OR (product.GlobalMinimum > 0 AND (SELECT SUM(stockusage.Quantity) FROM stockusage INNER JOIN stocklevel ON stockusage.StockLevelID = stocklevel.ID WHERE stocklevel.ProductID = product.ID) IS NULL)) " \
        "ORDER BY product.ProductName" % (_("unit"), get_unit_sql(dbo), 0))

def get_negative_balance_products(dbo: Database) -> Results:
    """
    Returns all products that are not retired and have a negative balance
    """

    return dbo.query("SELECT product.*, " \
        "(SELECT SUM(Balance) FROM stocklevel WHERE ProductID = product.ID) AS Balance, " \
        "CASE " \
        "WHEN product.UnitTypeID = 0 THEN '%s' " \
        "WHEN product.UnitTypeID = -1 THEN product.CustomUnit " \
        "%s" \
        "ELSE product.CustomUnit " \
        "END AS Unit " \
        "FROM product " \
        "WHERE IsRetired = %s " \
        "AND (SELECT SUM(stockusage.Quantity) FROM stockusage INNER JOIN stocklevel ON stockusage.StockLevelID = stocklevel.ID WHERE stocklevel.ProductID = product.ID) < 0 " \
        "ORDER BY ProductName" % (_("unit"), get_unit_sql(dbo), 0))

def get_retired_products(dbo: Database) -> Results:
    """
    Returns all products that are marked as retired - just in case someone would like to un-retire a product
    """

    return dbo.query("SELECT product.*, " \
        "(SELECT SUM(Balance) FROM stocklevel WHERE ProductID = product.ID) AS Balance, " \
        "CASE " \
        "WHEN product.UnitTypeID = 0 THEN '%s' " \
        "WHEN product.UnitTypeID = -1 THEN product.CustomUnit " \
        "%s" \
        "ELSE product.CustomUnit " \
        "END AS Unit " \
        "FROM product " \
        "WHERE IsRetired = %s " \
        "ORDER BY ProductName" % (_("unit"), get_unit_sql(dbo), 1))

def get_stock_movements(dbo: Database, productid: int = 0, stocklevelid: int = 0, fromdate: datetime = False) -> Results:
    """
    Returns product movements
    """

    wheresql = ""
    if productid != 0:
        if fromdate == False:
            fromdate = dbo.today()
        wheresql = "WHERE stocklevel.ProductID = %i AND stockusage.UsageDate >= '%s'" % (productid, fromdate)

    if stocklevelid != 0:
        wheresql = "WHERE stocklevel.ID = %i" % stocklevelid


    return dbo.query("SELECT " \
        "stockusage.ID, " \
        "stockusage.UsageDate, " \
        "product.ID AS ProductID, " \
        "CASE WHEN product.ID IS NULL THEN stocklevel.Name " \
        "ELSE product.ProductName " \
        "END AS ProductName, " \
        "stockusage.Quantity, " \
        "stocklocation.LocationName, " \
        "stockusagetype.UsageTypeName, " \
        "stocklevel.BatchNumber, " \
        "stockusage.Comments, " \
        "CASE WHEN stockusage.Quantity > 0 THEN UsageTypeName ELSE LocationName END AS FromName, " \
        "CASE WHEN stockusage.Quantity > 0 THEN LocationName ELSE UsageTypeName END AS ToName, " \
        "ABS(stockusage.Quantity) AS Quantity, " \
        "CASE " \
        "WHEN product.ID IS NULL THEN stocklevel.UnitName " \
        f"WHEN product.UnitTypeID = 0 AND product.PurchaseUnitTypeID = 0 THEN '{_("unit")}' " \
        "WHEN product.UnitTypeID = 0 AND product.PurchaseUnitTypeID = -1 THEN CustomPurchaseUnit " \
        "WHEN product.UnitTypeID > 0 THEN (SELECT UnitName FROM lksunittype WHERE ID = product.UnitTypeID) " \
        "ELSE product.CustomUnit " \
        "END AS Unit " \
        "FROM stockusage " \
        "INNER JOIN stocklevel ON stockusage.StockLevelID = stocklevel.ID " \
        "LEFT JOIN stocklocation ON stocklevel.StockLocationID = stocklocation.ID " \
        "LEFT JOIN stockusagetype ON stockusage.StockUsageTypeID = stockusagetype.ID " \
        "LEFT JOIN product ON stocklevel.ProductID = product.ID " + wheresql \
        )

def get_product_types(dbo: Database) -> Results:
    """
    Returns all producttypes
    """
    return dbo.query("SELECT * FROM lkproducttype ORDER BY ProductTypeName")

def get_tax_rates(dbo: Database) -> Results:
    """
    Returns all tax rates
    """
    return dbo.query("SELECT * FROM lktaxrate ORDER BY TaxRateName")

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

def update_product_from_form(dbo: Database, post: PostedData, username: str) -> None:
    """
    Updates a product item from a dialog. The post should include
    the ID of the product to adjust
    """
    l = dbo.locale
    pid = post.integer("productid")
    if post["productname"] == "":
        raise asm3.utils.ASMValidationError(_("Product must have a name", l))
    
    retired = 0
    if post.integer("active") == 0:
        retired = 1

    dbo.update("product", pid, {
        "ProductName":          post["productname"],
        "Description":          post["productdescription"],
        "ProductTypeID":        post.integer("producttypeid"),
        "SupplierID":           post.integer("supplierid"),
        "UnitTypeID":           post.integer("unittypeid"),
        "CustomUnit":           post["customunit"],
        "PurchaseUnitTypeID":   post.integer("purchaseunittypeid"),
        "CustomPurchaseUnit":   post["custompurchaseunit"],
        "CostPrice":            post.integer("costprice"),
        "RetailPrice":          post.integer("retailprice"),
        "UnitRatio":            post.integer("unitratio"),
        "TaxRateID":            post.integer("taxrateid"),
        "IsRetired":            retired,
        "Barcode":              post["barcode"],
        "PLU":                  post["plu"],
        "GlobalMinimum":        post["globalminimum"]
    }, username)

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

def insert_product_from_form(dbo: Database, post: PostedData, username: str) -> int:
    """
    Inserts a product item from a dialog.
    """
    l = dbo.locale
    if post["productname"] == "":
        raise asm3.utils.ASMValidationError(_("Product must have a name", l))
    
    retired = 0
    if post.integer("active") == 0:
        retired = 1
   
    pid = dbo.insert("product", {
        "ProductName":          post["productname"],
        "Description":          post["productdescription"],
        "ProductTypeID":        post.integer("producttypeid"),
        "SupplierID":           post.integer("supplierid"),
        "UnitTypeID":           post.integer("unittypeid"),
        "CustomUnit":           post["customunit"],
        "PurchaseUnitTypeID":   post.integer("purchaseunittypeid"),
        "CustomPurchaseUnit":   post["custompurchaseunit"],
        "CostPrice":            post.integer("costprice"),
        "RetailPrice":          post.integer("retailprice"),
        "UnitRatio":            post.integer("unitratio"),
        "TaxRateID":            post.integer("taxrateid"),
        "IsRetired":            retired,
        "Barcode":              post["barcode"],
        "PLU":                  post["plu"],
        "GlobalMinimum":        post["globalminimum"],
        "RecentBatchNo":        "",
        "RecentExpiry":         ""
    }, username)

    return pid

def insert_productmovement_from_form(dbo: Database, post: PostedData, username: str) -> int:
    """
    Inserts a product movement from a dialog.
    """
    movementusagetypeid = asm3.configuration.product_movement_usage_type(dbo)
    l = dbo.locale
    if post["movementdate"] == "":
        raise asm3.utils.ASMValidationError(_("Movement must have a date", l))
    
    #locations = []
    fromlocation = 0
    tolocation = 0

    if post.integer("movementfromtype") == 0 and post.integer("movementtotype") == 1:# Stock to usage
        #locations = [post.integer("movementfrom"), False]
        fromlocation = post.integer("movementfrom")
        usagetypeid = post.integer("movementto")
    elif post.integer("movementfromtype") == 0 and post.integer("movementtotype") == 0:# Stock to stock
        #locations = [post.integer("movementfrom"), post.integer("movementto")]
        fromlocation = post.integer("movementfrom")
        tolocation = post.integer("movementto")
        usagetypeid = movementusagetypeid
    elif post.integer("movementfromtype") == 1 and post.integer("movementtotype") == 0:# Usage to stock
        #locations = [False, post.integer("movementto"),]
        tolocation = post.integer("movementto")
        usagetypeid = post.integer("movementfrom")
    else:# Usage to usage
        #locations = [post.integer("movementfrom"), post.integer("movementto")]
        fromlocation = post.integer("movementfrom")
        tolocation = post.integer("movementto")
        usagetypeid = movementusagetypeid
    
    quantity = post.integer("movementquantity")
    unitratio = post.integer("unitratio")

    # Get current stock levels of the selected product
    stocklevels = dbo.query("SELECT ID, BatchNumber, Balance, Cost, UnitPrice, Total, Low, Expiry, UnitPrice, StockLocationID FROM stocklevel " \
        "WHERE ProductID = ? ORDER BY Balance", [ post.integer("productid") ])
    if fromlocation != 0:
        for stocklevel in stocklevels:
            if quantity == 0:
                break
            if stocklevel["BALANCE"] != 0 and post["batch"] == stocklevel["BATCHNUMBER"] and post.integer("movementfrom") == stocklevel["STOCKLOCATIONID"]:
                if stocklevel["BALANCE"] < 0:
                    remaining = stocklevel["BALANCE"] - quantity
                    quantity = 0
                elif quantity >= stocklevel["BALANCE"]:
                    remaining = 0
                    quantity = quantity - stocklevel["BALANCE"]
                else:
                    remaining = stocklevel["BALANCE"] - quantity
                    quantity = quantity - stocklevel["BALANCE"]
                slpost = {}
                slpost["stocklevelid"] = stocklevel["ID"]
                slpost["productid"] = post.integer("productid")
                slpost["name"] = post["productname"]
                slpost["description"] = post["productdescription"]
                slpost["location"] = fromlocation
                slpost["unitname"] = post["movementunit"]
                slpost["total"] = stocklevel["TOTAL"]
                slpost["balance"] = remaining
                slpost["low"] = stocklevel["LOW"]
                slpost["expiry"] = stocklevel["EXPIRY"]
                slpost["batchnumber"] = stocklevel["BATCHNUMBER"]
                slpost["cost"] = stocklevel["COST"]
                slpost["unitprice"] = stocklevel["UNITPRICE"]
                slpost["usagedate"] = python2display(dbo.locale, dbo.today())
                slpost["usagetype"] = usagetypeid
                slpost["batchnumber"] = post["batch"]
                slpost["expiry"] = post["expiry"]
                slpost["comments"] = post["comments"]

                update_stocklevel_from_form(dbo, asm3.utils.PostedData(slpost, dbo.locale), username)
        
        if quantity > 0:
            slpost = {}
            slpost["productlist"] = post.integer("productid")
            slpost["name"] = post["productname"]
            slpost["description"] = post["productdescription"]
            slpost["location"] = fromlocation
            slpost["unitname"] = post["movementunit"]
            slpost["total"] = unitratio
            slpost["balance"] = quantity * -1
            slpost["low"] = 0
            slpost["expiry"] = post.date("expiry")
            slpost["batchnumber"] = post["batch"]
            slpost["cost"] = post.integer("COSTPRICE")
            slpost["unitprice"] = post.integer("RETAILPRICE")
            slpost["usagedate"] = python2display(dbo.locale, dbo.today())
            slpost["usagetype"] = usagetypeid
            slpost["comments"] = post["comments"]
            insert_stocklevel_from_form(dbo, asm3.utils.PostedData(slpost, dbo.locale), username)
    
    quantity = post.integer("movementquantity")

    if tolocation != 0:
        for stocklevel in stocklevels:
            if quantity == 0:
                break
            if stocklevel["BALANCE"] < stocklevel["TOTAL"] and post["batch"] == stocklevel["BATCHNUMBER"] and post.integer("movementto") == stocklevel["STOCKLOCATIONID"]:
                availablespace = stocklevel["TOTAL"] - stocklevel["BALANCE"]
                if quantity >= availablespace:
                    balance = stocklevel["TOTAL"]
                    quantity = quantity - availablespace
                else:
                    balance = stocklevel["BALANCE"] + quantity
                    quantity = 0
                slpost = {}
                slpost["stocklevelid"] = stocklevel["ID"]
                slpost["productid"] = post.integer("productid")
                slpost["name"] = post["productname"]
                slpost["description"] = post["productdescription"]
                slpost["location"] = tolocation
                slpost["unitname"] = post["movementunit"]
                slpost["total"] = stocklevel["TOTAL"]
                slpost["balance"] = balance
                slpost["low"] = stocklevel["LOW"]
                slpost["expiry"] = stocklevel["EXPIRY"]
                slpost["batchnumber"] = stocklevel["BATCHNUMBER"]
                slpost["cost"] = stocklevel["COST"]
                slpost["unitprice"] = stocklevel["UNITPRICE"]
                slpost["usagedate"] = python2display(dbo.locale, dbo.today())
                slpost["usagetype"] = usagetypeid
                slpost["comments"] = post["comments"]
                update_stocklevel_from_form(dbo, asm3.utils.PostedData(slpost, dbo.locale), username)
        while quantity > 0:
            if quantity <= unitratio:
                remaining = quantity
                quantity = 0
            else:
                quantity = quantity - unitratio
                remaining = unitratio
            slpost = {}
            slpost["productlist"] = post.integer("productid")
            slpost["name"] = post["productname"]
            slpost["description"] = post["productdescription"]
            slpost["location"] = tolocation
            slpost["unitname"] = post["movementunit"]
            slpost["total"] = unitratio
            slpost["balance"] = remaining
            slpost["low"] = 0
            slpost["expiry"] = post.date("expiry")
            slpost["batchnumber"] = post["batch"]
            slpost["cost"] = post.integer("COSTPRICE")
            slpost["unitprice"] = post.integer("RETAILPRICE")
            slpost["usagedate"] = python2display(dbo.locale, dbo.today())
            slpost["usagetype"] = usagetypeid
            slpost["comments"] = post["comments"]
            insert_stocklevel_from_form(dbo, asm3.utils.PostedData(slpost, dbo.locale), username)

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
        "ProductID":        post.integer("productlist"),
        "Description":      post["description"],
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

def delete_product(dbo: Database, username: str, pid: int) -> None:
    """
    Deletes a product record
    """
    dbo.delete("product", "ID=%d" % pid, username)

def delete_stockusage(dbo: Database, username: str, mid: int) -> None:
    """
    Deletes a stockusage record
    """
    dbo.delete("stockusage", "ID=%d" % mid, username)

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

