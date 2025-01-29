
import asm3.al
import asm3.configuration
import asm3.financial
import asm3.utils

from .base import PaymentProcessor, ProcessorError, PayRefError, AlreadyReceivedError

from asm3.sitedefs import BASE_URL, PAYPAL_VALIDATE_IPN_URL
from asm3.typehints import Database

class IncompleteStatusError(ProcessorError):
    pass
class InvalidIPNError(ProcessorError):
    pass

class PayPal(PaymentProcessor):
    """ PayPal provider """

    def __init__(self, dbo: Database) -> None:
        PaymentProcessor.__init__(self, dbo, "paypal")        

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

        if item_description == "": item_description = ", ".join(paymenttypes)
        if return_url == "": return_url = "%s/static/pages/payment_success.html" % BASE_URL

        d = {
            "cmd":              "_xclick",
            "business":         asm3.configuration.paypal_email(self.dbo),
            "item_name":        item_description,
            "item_number":      payref,
            "amount":           "%0.2f" % ((totalamount - totalvat) / 100.0), 
            "currency_code":    asm3.configuration.currency_code(self.dbo),
            "custom":           self.dbo.name(),
            "tax_rate":         vatrate,
            "tax":              "%0.2f" % (totalvat / 100.0),
            "notify_url":       BASE_URL + "/pp_paypal", # callback url
            "button_subtype":   "services",
            "no_note":          0,
            "cn":               "",
            "no_shipping":      1,
            "rm":               1,
            "return":           return_url 
        }
        paypalform = []
        for k, v in d.items():
            paypalform.append('<input type="hidden" name="%s" value="%s">' % (k, v))

        return '<html><body>' \
            '<form id="paypalbuy" action="https://www.paypal.com/cgi-bin/webscr" method="post">' \
            '%s' \
            '<input type="hidden" name="bn" value="PP-BuyNowBF:btn_buynowCC_LG.gif:NonHosted">' \
            '<input type="image" src="https://www.paypalobjects.com/en_US/GB/i/btn/btn_buynowCC_LG.gif" border="0" name="submit" alt="PayPal">' \
            '<img alt="" border="0" src="https://www.paypalobjects.com/en_GB/i/scr/pixel.gif" width="1" height="1">' \
            '</form>' \
            '<script>' \
            'document.forms[0].submit()' \
            '</script>' \
            '</body></html>' % "".join(paypalform)

    def receive(self, rawdata: str, validate_ipn: bool = True) -> None:
        """ 
        Method to be called by the provider via an endpoint on receipt of payment.
        validate: Whether or not to skip validation of the IPN - useful for testing
        """
        # Extract the values we're interested in from the URLencoded data
        status = self.getDataParam(rawdata, "payment_status")
        payref = self.getDataParam(rawdata, "item_number")
        trxid = self.getDataParam(rawdata, "txn_id")
        # NOTE: The call to markPaymentReceived handles deducting the fee from received
        received = self.getDataParamC(rawdata, "mc_gross")
        fee = self.getDataParamC(rawdata, "mc_fee")
        vat = self.getDataParamC(rawdata, "tax")

        # If the payment status is not Completed, forget it
        if status != "Completed":
            asm3.al.error("PayPal status is not 'Completed' ('%s')" % status, "paypal.receive", self.dbo)
            raise IncompleteStatusError("payment status is not 'Completed'")

        # Check the payref is valid 
        if not self.validatePaymentReference(payref):
            asm3.al.error("payref '%s' failed validation" % payref, "paypal.receive", self.dbo)
            raise PayRefError("payref '%s' is invalid" % payref)

        # Do nothing if we already received payment for this payref
        if self.isPaymentReceived(payref): 
            asm3.al.error("cannot receive payref '%s' again, already received.", "paypal.receive", self.dbo)
            raise AlreadyReceivedError("payref '%s' has already been processed." % payref)

        # Validate the IPN with PayPal by posting it back to them
        # with an extra &cmd=_notify-validate parameter. If they
        # don't send back a response containing "INVALID", we
        # know we're good.
        if validate_ipn:
            try:
                response = asm3.utils.post_data(PAYPAL_VALIDATE_IPN_URL, rawdata + "&cmd=_notify-validate")
                asm3.al.debug("Verify POST returned: %s" % response["response"], "paypal.receive", self.dbo)
                if response["response"].find("INVALID") != -1: 
                    raise InvalidIPNError("PayPal returned an INVALID response")
            except Exception as e:
                asm3.al.error("Error validating PayPal IPN: %s" % e, "paypal.receive", self.dbo)
                raise e

        # We're through verification, receive the payments in payref
        self.markPaymentReceived(payref, trxid, received, vat, fee, rawdata)

