from contextlib import suppress
from urllib.parse import parse_qsl
import requests
import asm3.configuration
from asm3.sitedefs import BASE_URL
from asm3.al import debug as asm_debug
from .base import (
    PaymentProcessor,
    ProcessorError,
    PayRefError,
    AlreadyReceivedError,
)

import os, sys


class Cardcom(PaymentProcessor):
    """Coardcom provider http://kb.cardcom.co.il/article/AA-00402/0/"""

    def __init__(self, dbo):
        PaymentProcessor.__init__(self, dbo, "cardcom")


    def getInvoiceItems(self, records):
        import html
        for index, record in enumerate(records, start=1):
            description = record.DONATIONNAME
            price = round(record.DONATION, 2)
            if record.VATAMOUNT > 0: price += record.VATAMOUNT
            price = price / 100.0
            yield {f"InvoiceLines{index:d}.Description": html.unescape(description)} # TODO: trim to first 250 chars
            yield {f"InvoiceLines{index:d}.Quantity": 1}
            yield {f"InvoiceLines{index:d}.Price": price} 

    def checkoutPage(self, payref, return_url="", item_description=""):
        try:
            url = self.checkoutUrl(payref, return_url, item_description)
            return f"""<DOCTYPE html>
            <html>
            <head>
            <meta http-equiv="Refresh" content="0; URL={cardcom_reply['url']}">
            </head>
            <body></body>
            </html>"""
        except:
            return f"""<DOCTYPE html>
                <html>
                <head>
                </head>
                <body>{sys.exc_info()[0]}</body>
                </html>"""

    def checkoutUrl(self, payref, return_url="", item_description=""):
        asm_debug(f"{payref} {return_url} {item_description}")
        payments = self.getPayments(payref)
        total_charge_sum = sum(
            round(r.DONATION, 2) for r in payments
        )

        client_reference_id = "%s-%s" % (self.dbo.database, payref) # prefix database to payref 

        params = {
            "Operation": "2", #charge + create token,
            "TerminalNumber": asm3.configuration.cardcom_terminalnumber(self.dbo), #
            "UserName": asm3.configuration.cardcom_username(self.dbo), #
            "SumToBill": f"{total_charge_sum / 100.0}",
            "CoinID": "1", #TODO: not critical - use ASM currency
            "Language": "he", #TODO: not critical - config / use locale?
            "ProductName": "Donation to S.O.S. Pets 1234", # TODO: trim to first 50 chars
            "SuccessRedirectUrl": asm3.configuration.cardcom_successurl(self.dbo), # "https://secure.cardcom.solutions/DealWasSuccessful.aspx",
            "ErrorRedirectUrl": asm3.configuration.cardcom_errorurl(self.dbo), #"https://secure.cardcom.solutions/DealWasUnSuccessful.aspx?customVar=1234",
            "APILevel": "10",
            "codepage": "65001", #unicode
            "ReturnValue": client_reference_id,
            "InvoiceHead.CustName": "Test customer", #TODO: fetch from payment, # TODO: trim to first 50 chars
            "InvoiceHead.SendByEmail": "true", #TODO: not critical - config?
            "InvoiceHead.Language": "he", #TODO: not critical - config / use locale?
            "InvoiceHead.Email": "br.shurik+cardcom@gmail.com",  #TODO: fetch from payment
            "IndicatorUrl": f"{BASE_URL}/pp_cardcom", 
        }

        for p in self.getInvoiceItems(payments):
            params.update(p)        

        asm_debug(f"params: {params}")
        response = requests.post(
            "https://secure.cardcom.solutions/Interface/LowProfile.aspx",
            data=params,
        )
        asm_debug(f"response {response.status_code} , text: {response.text}")
        if response.status_code != 200:
            return ""
        cardcom_reply = dict(parse_qsl(response.text))
        if "url" not in cardcom_reply:
            raise Exception(f"No url in response text: {response.text}")
        asm_debug(f"return cardcom url: {cardcom_reply['url']}")
        return f"{cardcom_reply['url']}"



    def receive(self, rawdata):
        response = rawdata
        asm_debug(rawdata)
        return
"""        
        with suppress(KeyError):
            if (
                response["Operation"] == 1
                and response["OperationResponse"] == 0
                and response["DealResponse"] == 0
            ):
                payref = response["ReturnValue"]
                if not self.validatePaymentReference(payref):
                    raise PayRefError(f"payref {payref} is invalid")
                if self.isPaymentReceived(payref):
                    raise AlreadyReceivedError(
                        f"payref {payref} has already been processed."
                    )
            self.markPaymentReceived(
                payref, response["InternalDealNumber"], 0, 0, 0, rawdata
            )
"""