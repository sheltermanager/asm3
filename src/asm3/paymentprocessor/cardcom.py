from contextlib import suppress
from urllib.parse import parse_qsl
import requests
from asm3.sitedefs import BASE_URL
from asm3.al import debug as asm_debug
from .base import (
    PaymentProcessor,
    ProcessorError,
    PayRefError,
    AlreadyReceivedError,
)


class Cardcom(PaymentProcessor):
    """Coardcom provider http://kb.cardcom.co.il/article/AA-00402/0/"""

    def __init__(self, dbo):
        PaymentProcessor.__init__(self, dbo, "cardcom")


    def getInvoiceItems(self, records):
        for index, record in enumerate(records, start=1):
            description = record.DONATIONNAME
            price = round(record.DONATION, 2)
            yield {f"InvoiceLines{index:d}.Description": description}
            yield {f"InvoiceLines{index:d}.Quantity": 1}
            yield {f"InvoiceLines{index:d}.Price": price}


    def checkoutPage(self, payref, return_url="", item_description=""):
        asm_debug(f"{payref} {return_url} {item_description}")
        payments = self.getPayments(payref)
        total_charge_sum = sum(
            round(r.DONATION, 2) for r in payments
        )

        params = {
            "Operation": "2", #charge + create token,
            "TerminalNumber": "1000", #TODO: add to config
            "UserName": "barak9611", #TODO: add to config
            "SumToBill": f"{total_charge_sum}", #"0.01", #TODO: replace with f"{total_charge_sum}",
            "CoinID": "1", #TODO: not critical - use ASM currency
            "Language": "he", #TODO: not critical - config / use locale?
            "ProductName": "Donation to S.O.S. Pets 1234", #stritem_description,
            "SuccessRedirectUrl": "https://secure.cardcom.solutions/DealWasSuccessful.aspx",
            "ErrorRedirectUrl": "https://secure.cardcom.solutions/DealWasUnSuccessful.aspx?customVar=1234",
            "APILevel": "10",
            "codepage": "65001", #unicode
            "ReturnValue": str(payref),
            "InvoiceHead.CustName": "Test customer", #TODO: fetch from payment
            "InvoiceHead.SendByEmail": "true", #TODO: not critical - config?
            "InvoiceHead.Language": "he", #TODO: not critical - config / use locale?
            "InvoiceHead.Email": "br.shurik+cardcom@gmail.com",  #TODO: fetch from payment
            "SuccessRedirectUrl": "https://secure.cardcom.solutions/DealWasSuccessful.aspx",
            "ErrorRedirectUrl": "https://secure.cardcom.solutions/DealWasUnSuccessful.aspx",
            "IndicatorUrl": f"{BASE_URL}/pp_cardcom", 
        }

        for p in self.getInvoiceItems(payments):
            params.update(p)        

        asm_debug(f"params: {params}")

        try:
            asm_debug("Calling LowProfile URL")
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

            return f"""<DOCTYPE html>
            <html>
            <head>
            <meta http-equiv="Refresh" content="0; URL={cardcom_reply['url']}">
            </head>
            <body></body>
            </html>"""
        except:
            asm_debug(sys.exc_info()[0])

        return f"""<DOCTYPE html>
            <html>
            <head>
            </head>
            <body>SOMETHING WENT WRONG. Check server logs.</body>
            </html>"""


    def receive(self, rawdata):
        response = dict(parse_qsl(rawdata))
        asm_debug(rawdata)
        asm_debug(indicator_response)
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