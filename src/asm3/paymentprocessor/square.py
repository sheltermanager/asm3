
import asm3.al
import asm3.configuration
import asm3.financial
import asm3.utils

from .base import PaymentProcessor, ProcessorError, PayRefError, AlreadyReceivedError

from asm3.sitedefs import BASE_URL
from asm3.typehints import Database

class IncorrectEventError(ProcessorError):
    pass

class Square(PaymentProcessor):
    """ Square provider """
    def __init__(self, dbo: Database):

        PaymentProcessor.__init__(self, dbo, "square")

    def checkoutPage(self, payref: str, return_url: str = "",  item_description: str = "") -> str:
        """ 
        Method to return the provider's checkout page 
        payref: The payments we are charging for (str OWNERCODE-RECEIPTNUMBER)
        return_url: The URL to redirect the browser to when payment is successful.
        item_description: A description of what we are charging for (if blank the payment types are used)
        """
        totalamount = 0
        totalvat = 0
        #vatrate = 0
        paymenttypes = []

        for r in self.getPayments(payref):
            totalamount += r.DONATION
            if r.VATAMOUNT > 0: totalvat += r.VATAMOUNT
            #if r.VATRATE > 0: vatrate = r.VATRATE
            paymenttypes.append(r.DONATIONNAME)

        zp = self._checkForZeroPaymentPage(payref, totalamount)
        if zp != "": return zp

        item_description = item_description or ", ".join(paymenttypes)
        client_reference_id = "%s-%s" % (self.dbo.database, payref) # prefix database to payref
        currency = asm3.configuration.currency_code(self.dbo)

        #asm3.al.debug("create square session: api_key=%s, client_reference_id=%s, " \
        #    "description=%s, amount=%s, currency=%s" % (api_key, client_reference_id, 
        #    item_description, totalamount + totalvat, currency), "square.checkoutPage", self.dbo)

        from square.http.auth.o_auth_2 import BearerAuthCredentials
        from square.client import Client

        client = Client(
        bearer_auth_credentials = BearerAuthCredentials(
            access_token = asm3.configuration.square_access_token(self.dbo)
        ),
        environment='sandbox')

        result = client.locations.list_locations()

        locationid = 'LQQNMQC474MTG'
        
        result = client.checkout.create_payment_link(
            body = {
                "idempotency_key": asm3.utils.uuid_b64(),
                "payment_note": client_reference_id,#.replace("/", ""),
                "quick_pay": {
                    "name": item_description,
                    "price_money": {
                        "amount": totalamount,
                        "currency": currency
                },
                "location_id": locationid
                },
            }
        )

        if result.is_success():
            print("Success!")
            # Construct the page that will redirect us to the real checkout
            s = """<DOCTYPE html>
            <html>
            <head>
            <script>
                location.href = '%s';
            </script>
            </head>
            <body></body>
            </html>""" % (result.body["payment_link"]["url"],)
            return s
        elif result.is_error():
            #print(result.errors)
            print("Failure")

    def receive(self, rawdata: str) -> None:
        """ 
        Method to be called by the provider via an endpoint on receipt of payment.
        validate: Whether or not to skip validation of the IPN - useful for testing
        """
        # Turn the raw data into a JSON document
        e = asm3.utils.json_parse(rawdata)

        payref = e["data"]["object"]["payment"]["note"]

        # Mark our payment as received with the correct amounts
        #def markPaymentReceived(self, payref: str, trxid: str, received: int, vat: int, fee: int, rawdata: str) -> None:
        """ 
        Marks all payments in payref received.
        trxid: Transaction ID from the payment service (for ChequeNumber column)
        received (int): The gross amount received
        vat (int): Any vat/tax amount
        fee (int): The transaction fee aount charged
        rawdata (str): The raw data from the payment service.
        The fee is only applied to the first payment if there are multiple payments in the payref.
        It is expected that received, vat and fee are all integer currency amounts in whole pence.
        If there are licenses waiting to renew on this payment, handles calling out to that functionality too.
        """
        self.markPaymentReceived(payref, e["data"]["object"]["payment"]["id"], e["data"]["object"]["payment"]["amount_money"]["amount"], 0, 0, rawdata)
