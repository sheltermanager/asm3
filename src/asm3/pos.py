
from asm3.i18n import _, python2display
import asm3.stock
import asm3.configuration
import json

from asm3.typehints import Database, PostedData

def insert_receipt_from_form(dbo: Database, username: str, post: PostedData) -> int:
    """
    Creates a receipt from posted form data
    """
    # l = dbo.locale

    receiptitems = json.loads(post.data.jsondata)
    pass

    salesreceiptid = dbo.insert("salesreceipt", {
        "Date":                dbo.today(),
        "Balance":             post.integer("balance")
    }, username)

    for receiptitem in receiptitems:
        stockusagedata = {
            "movementdate": python2display(dbo.locale, dbo.today()),
            "producttypeid": int(receiptitem["producttypeid"]),
            "productname": receiptitem["description"],
            "movementfromtype" : 0,
            "movementtotype" : 1,
            "movementquantity": int(receiptitem["quantity"]),
            "unitratio": "1",
            "movementunit": "unit",
            "usagedate": python2display(dbo.locale, dbo.today()),
            "productid": int(receiptitem["productid"]),
            "movementfrom": asm3.configuration.pos_stock_location(dbo),
            "movementto": asm3.configuration.pos_stock_usage_type(dbo),
            "comments": _("Created via POS")
        }
        stockusagepost = asm3.utils.PostedData(stockusagedata, "en")
        asm3.stock.insert_productmovement_from_form(dbo, stockusagepost, username)
        dbo.insert("salesreceiptdetail", {
            "SalesReceiptID":      salesreceiptid, 
            "ProductID":           receiptitem["productid"],
            "TaxRate":             receiptitem["taxrate"],
            "Price":               receiptitem["price"],
            "Description":         receiptitem["description"]
        }, username)

    return salesreceiptid

