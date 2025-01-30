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
        vatrate = 0
        paymenttypes = []

        for r in self.getPayments(payref):
            totalamount += r.DONATION
            if r.VATAMOUNT > 0: totalvat += r.VATAMOUNT
            if r.VATRATE > 0: vatrate = r.VATRATE
            paymenttypes.append(r.DONATIONNAME)

        zp = self._checkForZeroPaymentPage(payref, totalamount)
        if zp != "": return zp

        item_description = item_description or ", ".join(paymenttypes)
        payment_note = "%s-%s" % (self.dbo.database, payref) # prefix database to payref
        currency = asm3.configuration.currency_code(self.dbo)

        asm3.al.debug("create square session: payment_note=%s, " \
            "description=%s, amount=%s, currency=%s" % (payment_note, 
            item_description, totalamount + totalvat, currency), "square.checkoutPage", self.dbo)

        from square.http.auth.o_auth_2 import BearerAuthCredentials
        from square.client import Client

        squareenvironment = asm3.sitedefs.SQUARE_PAYMENT_ENVIRONMENT

        client = Client(
        bearer_auth_credentials = BearerAuthCredentials(
            access_token = asm3.configuration.square_access_token(self.dbo)
        ),
        environment=squareenvironment)

        #locationid = asm3.configuration.square_location_id(self.dbo)
        
        result = client.checkout.create_payment_link(
            body = {
                "idempotency_key": payref,
                #"amount_money": {
                #    "amount": "%0.2f" % ((totalamount - totalvat) / 100.0),
                #    "currency": currency
                #},
                "quick_pay": {
                    "name": item_description,
                    "price_money": {
                        "amount": int(totalamount - totalvat),
                        "currency": currency
                    },
                    "location_id": asm3.configuration.square_location_id(self.dbo)
                },
                "payment_note": payment_note,
            }
        )

        if result.is_success():
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
        # Extract the values we're interested in from the URLencoded data
        #j["data"]["object"]["payment"]["status"] != "COMPLETED"

        e = asm3.utils.json_parse(rawdata)
        status = e["data"]["object"]["payment"]["status"]
        payref = e["data"]["object"]["payment"]["note"]
        trxid = e["data"]["object"]["payment"]["id"]
        # NOTE: The call to markPaymentReceived handles deducting the fee from received
        received = e["data"]["object"]["payment"]["amount_money"]["amount"]
        totalfees = 0
        if "processing_fee" in e["data"]["object"]["payment"]:
            fees = e["data"]["object"]["payment"]["processing_fee"]
            for fee in fees:
                totalfees = totalfees + fee["amount_money"]["amount"]
        
        # If the payment status is not Completed, forget it
        if status != "COMPLETED":
            asm3.al.error("Square payment status is not 'Completed' ('%s')" % status, "square.receive", self.dbo)
            raise IncompleteStatusError("payment status is not 'Completed'")

        # Check the payref is valid  ## Need to upcomment when Bob's fix for dbpaths that contain hyphens has been merged - Adam.
        #if not self.validatePaymentReference(payref):
        #    asm3.al.error("payref '%s' failed validation" % payref, "paypal.receive", self.dbo)
        #    raise PayRefError("payref '%s' is invalid" % payref)

        # Do nothing if we already received payment for this payref removed to allow follow on fees
        #if self.isPaymentReceived(payref): 
        #    asm3.al.error("cannot receive payref '%s' again, already received.", "paypal.receive", self.dbo)
        #    raise AlreadyReceivedError("payref '%s' has already been processed." % payref)

        # We're through verification, receive the payments in payref
        self.markPaymentReceived(payref, trxid, received, 0, totalfees, rawdata)
