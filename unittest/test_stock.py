
import unittest
import base

import asm3.stock
import asm3.utils

class TestStock(unittest.TestCase):
 
    nid = 0

    def setUp(self):
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

    def tearDown(self):
        base.execute("DELETE FROM stockusage WHERE StockLevelID = %d" % self.nid)
        asm3.stock.delete_stocklevel(base.get_dbo(), "test", self.nid)

    def test_get_stocklevel(self):
        assert None is not asm3.stock.get_stocklevel(base.get_dbo(), self.nid)

    def test_get_stocklevels(self):
        assert len(asm3.stock.get_stocklevels(base.get_dbo())) > 0

    def test_get_stocklevels_depleted(self):
        asm3.stock.get_stocklevels_depleted(base.get_dbo())

    def test_get_stocklevels_lowbalance(self):
        asm3.stock.get_stocklevels_lowbalance(base.get_dbo())

    def test_get_stock_names(self):
        assert len(asm3.stock.get_stock_names(base.get_dbo())) > 0

    def test_get_last_stock_with_name(self):
        asm3.stock.get_last_stock_with_name(base.get_dbo(), "")

    def test_get_stock_items(self):
        assert len(asm3.stock.get_stock_items(base.get_dbo())) > 0

    def test_get_stock_locations_totals(self):
        assert len(asm3.stock.get_stock_locations_totals(base.get_dbo())) > 0

    def test_get_stock_units(self):
        assert len(asm3.stock.get_stock_units(base.get_dbo())) > 0

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
       
