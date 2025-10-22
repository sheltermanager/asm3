
import asm3.i18n

from asm3.typehints import datetime, Database, List, PaymentProcessor, PostedData, ResultRow, Results

def insert_receipt_from_form(dbo: Database, username: str, post: PostedData) -> int:
    """
    Creates a receipt from posted form data
    """
    # l = dbo.locale

    return dbo.insert("salesreceipt", {
        "Date":                dbo.today(),
        "Balance":             post.integer("balance")
    }, username)