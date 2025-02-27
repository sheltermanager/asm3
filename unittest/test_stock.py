
import unittest
import base

import asm3.stock
import asm3.utils

class TestStock(unittest.TestCase):
 
    nid = 0

    def setUp(self):

        # Create a stocklevel
        data = {
            "name": "Test Stock",
            "description": "Test Description",
            "location": "1",
            "unitname": "Tablet",
            "total": "50",
            "balance": "50",
            "expiry": "2014-01-01",
            "batchnumber": "00001",
            "usagetype": "1",
            "usagedate": base.today_display()
        }
        post = asm3.utils.PostedData(data, "en")
        self.nid = asm3.stock.insert_stocklevel_from_form(base.get_dbo(), post, "test")

        # Create a supplier
        data = {
            "title": "Mr",
            "forenames": "Test",
            "surname": "Testing",
            "ownertype": "1",
            "address": "123 test street",
            "flags": "supplier"
        }
        post = asm3.utils.PostedData(data, "en")
        self.sid = asm3.person.insert_person_from_form(base.get_dbo(), post, "test", geocode=False)

        # Create a product type
        self.tid = asm3.lookups.insert_lookup(base.get_dbo(), "test", "lkproducttype", "Test Product Type", "Just for testing")

        # Create a stock location
        self.lid = asm3.lookups.insert_lookup(base.get_dbo(), "test", "stocklocation", "Test Stock Location", "Just for testing")

        # Create a stock usage type
        self.uid = asm3.lookups.insert_lookup(base.get_dbo(), "test", "stockusagetype", "Test Usage Type", "Just for testing")

        # Create a product to test
        data = {
            "productname": "Test Product",
            "description": "Test Description",
            "producttypeid": "1",
            "supplierid": str(self.sid),
            "taxrateid": "1"
        }
        post = asm3.utils.PostedData(data, "en")
        self.pid = asm3.stock.insert_product_from_form(base.get_dbo(), post, "test")

    def tearDown(self):
        base.execute("DELETE FROM stockusage WHERE StockLevelID = %d" % self.nid)
        asm3.stock.delete_stocklevel(base.get_dbo(), "test", self.nid)
        base.execute("DELETE FROM owner WHERE ID = %d" % self.sid)
        base.execute("DELETE FROM lkproducttype WHERE ID = %d" % self.tid)
        base.execute("DELETE FROM product WHERE ID = %d" % self.pid)
        base.execute("DELETE FROM stocklocation WHERE ID = %d" % self.lid)
        base.execute("DELETE FROM stockusagetype WHERE ID = %d" % self.uid)

    def test_get_stocklevel(self):
        self.assertIsNotNone(asm3.stock.get_stocklevel(base.get_dbo(), self.nid))

    def test_get_stocklevels(self):
        self.assertNotEqual(0, len(asm3.stock.get_stocklevels(base.get_dbo())))

    def test_get_stocklevels_depleted(self):
        asm3.stock.get_stocklevels_depleted(base.get_dbo())

    def test_get_stocklevels_lowbalance(self):
        asm3.stock.get_stocklevels_lowbalance(base.get_dbo())

    def test_get_stock_names(self):
        self.assertNotEqual(0, len(asm3.stock.get_stock_names(base.get_dbo())))

    def test_get_last_stock_with_name(self):
        asm3.stock.get_last_stock_with_name(base.get_dbo(), "")

    def test_get_stock_items(self):
        self.assertNotEqual(0, len(asm3.stock.get_stock_items(base.get_dbo())))

    def test_get_stock_locations_totals(self):
        self.assertNotEqual(0, len(asm3.stock.get_stock_locations_totals(base.get_dbo())))

    def test_get_stock_units(self):
        self.assertNotEqual(0, len(asm3.stock.get_stock_units(base.get_dbo())))
    
    def test_move_product(self):
        data = {
            "movementdate": base.today_display(),
            "producttypeid": str(self.tid),
            "movementfromtype" : "0",
            "movementfromtype" : "1",
            "movementquantity": "1",
            "unitratio": "1",
            "productid": str(self.pid),
            "movementfrom": str(self.lid),
            "movementto": str(self.uid),
            "comments": "A test movement"
        }
        post = asm3.utils.PostedData(data, "en")
        asm3.stock.insert_productmovement_from_form(base.get_dbo(), "test", post)

    def test_update_stocklevel_from_form(self):
        data = {
            "stocklevelid": str(self.nid),
            "name": "Test Stock",
            "description": "Test Description",
            "location": "1",
            "unitname": "Tablet",
            "total": "50",
            "balance": "50",
            "expiry": "2014-01-01",
            "batchnumber": "00001",
            "usagetype": "1",
            "usagedate": base.today_display()
        }
        post = asm3.utils.PostedData(data, "en")
        asm3.stock.update_stocklevel_from_form(base.get_dbo(), post, "test")

    def test_deduct_stocklevel_from_form(self):
        data = {
            "item": str(self.nid),
            "quantity": "1",
            "usagetype": "1",
            "usagedate": base.today_display(),
            "comments": "test"
        }
        post = asm3.utils.PostedData(data, "en")
        asm3.stock.deduct_stocklevel_from_form(base.get_dbo(), "test", post)

    def test_stock_take_from_mobile_form(self):
        data = {
            "sl%d" % self.nid: "5",
            "usagetype": "1"
        }
        post = asm3.utils.PostedData(data, "en")
        asm3.stock.stock_take_from_mobile_form(base.get_dbo(), "test", post)
       