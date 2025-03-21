import asm3.al
import asm3.configuration
import asm3.financial
import asm3.utils

from .base import PaymentProcessor, ProcessorError, PayRefError

from asm3.typehints import Database

class IncorrectEventError(ProcessorError):
    pass

class IncompleteStatusError(ProcessorError):
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
        payment_note = "%s-%s" % (self.dbo.database, payref) # prefix database to payref
        currency = asm3.configuration.currency_code(self.dbo)

        asm3.al.debug("create square session: payment_note=%s, " \
            "description=%s, amount=%s, currency=%s" % (payment_note, 
            item_description, totalamount + totalvat, currency), "square.checkoutPage", self.dbo)

        access_token = asm3.configuration.square_access_token(self.dbo)
        squenv = asm3.sitedefs.SQUARE_PAYMENT_ENVIRONMENT
        body = {
            # NOTE: We used to use payref here, but square will prevent you loading the checkout again for the same payment
            "idempotency_key": asm3.utils.uuid_b64(), 
            "quick_pay": {
                "name": item_description,
                "price_money": {
                    "amount": totalamount - totalvat,
                    "currency": currency
                },
                "location_id": asm3.configuration.square_location_id(self.dbo)
            },
            "payment_note": payment_note,
        }

        # NOTE: Using the "squareup" package from pypi
        from square.http.auth.o_auth_2 import BearerAuthCredentials
        from square.client import Client
        client = Client(bearer_auth_credentials=BearerAuthCredentials(access_token=access_token), environment=squenv)
        result = client.checkout.create_payment_link(body=body)
        response = result.body
        success = result.is_success()

        """
        # NOTE: This was an attempt to do the above without having a dependency on the "squareup" package from pypi
        # NOTE: Not used because I don't think we can use bearer tokens this way without oauth in production, 
        #       The square documentation is not very clear on the subject.
        if squenv == "production": squenv = "" # url is connect.squareup.com or connect.squareupsandbox.com
        url = f"https://connect.squareup{squenv}.com/v2/online-checkout/payment-links"
        headers = { "Authorization": f"Bearer {access_token}", "Square-Version": "2025-01-23", "Content-Type": "application/json" }
        result = asm3.utils.post_json(url, asm3.utils.json(body), headers)
        response = asm3.utils.json_parse(result["response"])
        success = "payment_link" in response and "url" in response["payment_link"]
        """

        if success:
            link = response["payment_link"]["url"]
            # Construct the page that will redirect us to the real checkout
            s = "<DOCTYPE html>\n" \
            "<html>\n" \
            "<head>\n" \
            f'<meta http-equiv="refresh" content="0; url="{link}/" />\n' \
            "</head>\n" \
            "<body></body>\n" \
            "</html>"
            return s
        else: 
            asm3.al.error(f"Failed creating Square payment [got {response}]", "square.checkoutPage", self.dbo)
            s = "<DOCTYPE html>\n" \
            "<html>\n" \
            "<head>\n" \
            "</head>\n" \
            "<body>\n" \
            "<h1>ERROR</h1>\n" \
            f"<p>{response}</p>\n" \
            "</body>\n" \
            "</html>"
            return s

    def receive(self, rawdata: str) -> None:
        """ 
        Method to be called by the provider via an endpoint on receipt of payment.
        validate: Whether or not to skip validation of the IPN - useful for testing
        """
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

        # Check the payref is valid  
        if not self.validatePaymentReference(payref):
            asm3.al.error("payref '%s' failed validation" % payref, "paypal.receive", self.dbo)
            raise PayRefError("payref '%s' is invalid" % payref)

        # Do nothing if we already received payment for this payref - this was removed 
        # because square can send multiple payment.update webhooks, and the last one will
        # have the processing fees attached.
        #if self.isPaymentReceived(payref): 
        #    asm3.al.error("cannot receive payref '%s' again, already received.", "paypal.receive", self.dbo)
        #    raise AlreadyReceivedError("payref '%s' has already been processed." % payref)

        # We're through verification, receive the payments in payref
        self.markPaymentReceived(payref, trxid, received, 0, totalfees, rawdata)
