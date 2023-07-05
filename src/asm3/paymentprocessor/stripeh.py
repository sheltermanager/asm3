
import asm3.al
import asm3.configuration
import asm3.financial
import asm3.utils

from .base import PaymentProcessor, ProcessorError, PayRefError, AlreadyReceivedError

from asm3.sitedefs import BASE_URL

STRIPE_API_VERSION = "2018-08-23"

class IncorrectEventError(ProcessorError):
    pass

class Stripe(PaymentProcessor):
    """ Stripe provider """
    def __init__(self, dbo):

        PaymentProcessor.__init__(self, dbo, "stripe")

    def checkoutPage(self, payref, return_url = "",  item_description = ""):
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

        item_description = item_description or ", ".join(paymenttypes)
        client_reference_id = "%s-%s" % (self.dbo.database, payref) # prefix database to payref 

        # Stripe will reject blank URLs
        if return_url == "": return_url = "%s/static/pages/payment_success.html" % BASE_URL
        cancel_url = "%s/static/pages/payment_cancelled.html" % BASE_URL

        # Stripe reject URLs that are not absolute and include the protocol
        if not return_url.startswith("http"): return_url = "https://%s" % return_url

        api_key = asm3.configuration.stripe_secret_key(self.dbo)
        currency = asm3.configuration.currency_code(self.dbo)

        asm3.al.debug("create stripe session: api_key=%s, client_reference_id=%s, " \
            "description=%s, amount=%s, currency=%s" % (api_key, client_reference_id, 
            item_description, totalamount + totalvat, currency), "stripe.checkoutPage", self.dbo)

        import stripe # we want this to throw a non-ProcessorError if module is unavailable
        stripe.api_version = STRIPE_API_VERSION

        # Create the stripe checkout session
        session = stripe.checkout.Session.create(
            api_key=api_key,
            client_reference_id=client_reference_id,
            payment_intent_data={ 'description': item_description },
            payment_method_types=["card"],
            line_items=[{
                "name": item_description,
                "description": item_description,
                "amount": totalamount + totalvat, # Payment amounts in ASM are always exclusive of tax
                "currency": currency,
                "quantity": 1
            }],
            success_url=return_url,
            cancel_url=cancel_url
        )

        # Construct the page that will redirect us to the real checkout
        s = """<DOCTYPE html>
        <html>
        <head>
        <script src="https://js.stripe.com/v3/"></script>
        <script>
            stripe = new Stripe('%s');
            stripe.redirectToCheckout({ sessionId: '%s' }).then(function(result) {
                alert(result.error.message);
            });
        </script>
        </head>
        <body></body>
        </html>""" % (asm3.configuration.stripe_key(self.dbo), session.id)
        return s

    def receive(self, rawdata):
        """ 
        Method to be called by the provider via an endpoint on receipt of payment.
        validate: Whether or not to skip validation of the IPN - useful for testing
        """
        # Turn the raw data into a JSON document
        e = asm3.utils.json_parse(rawdata)
        if e["type"] != "checkout.session.completed":
            raise IncorrectEventError("this handler is only for checkout.session.completed webhooks")

        # Extract the payment intent and client reference
        payment_intent_id = e["data"]["object"]["payment_intent"]
        client_reference_id = e["data"]["object"]["client_reference_id"]
        
        # Remove the database from the client reference to get the payref
        payref = client_reference_id[client_reference_id.find("-")+1:]

        # Check the payref is valid 
        if not self.validatePaymentReference(payref):
            asm3.al.error("payref '%s' failed validation" % payref, "stripe.receive", self.dbo)
            raise PayRefError("payref '%s' is invalid" % payref)

        # Do nothing if we already received payment for this payref
        if self.isPaymentReceived(payref): 
            asm3.al.error("cannot receive payref '%s' again, already received.", "stripe.receive", self.dbo)
            raise AlreadyReceivedError("payref '%s' has already been processed." % payref)

        import stripe # we want this to throw a non-ProcessorError if module is unavailable
        stripe.api_version = STRIPE_API_VERSION

        # Load the Stripe Charge and BalanceTransaction records (needed to get the fee
        # and charge_id is the transaction id stamped on the record)
        # There is deliberately no error handling around this code. If any of it fails, the
        # exception will bubble up to our global error handler and send an email,
        # and a 500 will go back to stripe for them to keep trying until we fix it.
        api_key = asm3.configuration.stripe_secret_key(self.dbo)
        intent = stripe.PaymentIntent.retrieve(payment_intent_id, api_key=api_key)
        charge = intent["charges"]["data"][0]
        charge_id = charge["id"]
        balance_txn_id = charge["balance_transaction"]
        txn = stripe.BalanceTransaction.retrieve(balance_txn_id, api_key=api_key)
        asm3.al.debug("retrieved paymentintent %s, charge %s and balancetransaction %s" %
            (payment_intent_id, charge_id, balance_txn_id), "stripe.receive", self.dbo)

        # Mark our payment as received with the correct amounts
        self.markPaymentReceived(payref, payment_intent_id, txn.amount, 0, txn.fee, rawdata)

        # Finally, add the payref to the payment intent so the user can see it in their dashboard.
        # We do this last so nothing important is stopped if it fails.
        stripe.PaymentIntent.modify(payment_intent_id, metadata={ "payref": payref }, api_key=api_key)
