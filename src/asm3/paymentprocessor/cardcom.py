from asm3.i18n import _
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
import html

import os, sys


class Cardcom(PaymentProcessor):
    """Cardcom provider http://kb.cardcom.co.il/article/AA-00402/0/"""

    def __init__(self, dbo):
        PaymentProcessor.__init__(self, dbo, "cardcom")


    def getInvoiceItems(self, records):
        for index, record in enumerate(records, start=1):
            description = record.DONATIONNAME
            price = round(record.DONATION, 2)
            if record.VATAMOUNT > 0: price += record.VATAMOUNT
            price = price / 100.0
            yield {f"InvoiceLines{index:d}.Description": html.unescape(description)[:250]}
            yield {f"InvoiceLines{index:d}.Quantity": 1}
            yield {f"InvoiceLines{index:d}.Price": price} 

    def tokenCharge(self, payref, item_description=""):
        payments = self.getPayments(payref)
        total_charge_sum = sum(
            round(r.DONATION, 2) + (r.VATAMOUNT if r.VATAMOUNT > 0 else 0) for r in payments # add VAT for consistency with other payment providers
        ) / 100.0
        client_reference_id = "%s-%s" % (self.dbo.database, payref) # prefix database to payref 
        OwnerID = payments[0].OWNERID
        p = asm3.person.get_person(self.dbo, OwnerID)

        if not asm3.utils.is_valid_email_address(p.EMAILADDRESS):
            raise Exception(_("Invalid email address")) 

        url = "https://secure.cardcom.solutions/interface/ChargeToken.aspx"
        params = {
            "Operation": "2", #charge + create token,
            "TerminalNumber": asm3.configuration.cardcom_terminalnumber(self.dbo), #
            "UserName": asm3.configuration.cardcom_username(self.dbo), #
            "codepage": "65001", #unicode
            "TokenToCharge.DocTypeToCreate": asm3.configuration.cardcom_documenttype(self.dbo), #3=#nonprofit receipt
            "TokenToCharge.SumToBill": f"{total_charge_sum}",
            "TokenToCharge.CoinID": "1", #TODO: not critical - use ASM currency
            "TokenToCharge.UniqAsmachta": client_reference_id,
            "InvoiceHead.CustName": html.unescape(p.OWNERNAME)[:50] , 
            "InvoiceHead.CustAddresLine1": html.unescape(p.OWNERADDRESS)[:50], 
            "InvoiceHead.CustCity": html.unescape(p.OWNERTOWN)[:50],            
            "InvoiceHead.CustMobilePH": html.unescape(p.MOBILETELEPHONE)[:50],  
            "InvoiceHead.ExtIsVatFree": "true",#no VAT for nonprofit receipts. #TODO: config?
            "InvoiceHead.SendByEmail": "true", #TODO: not critical - config?
            "InvoiceHead.Language": "he", #TODO: not critical - config / use locale?
            "InvoiceHead.Email": p.EMAILADDRESS,
            "TokenToCharge.Token": asm3.person.get_extra_id(self.dbo, p, "Cardcom_Token"),
            "TokenToCharge.CardValidityMonth": asm3.person.get_extra_id(self.dbo, p, "Cardcom_CardValidity").split("/")[0],
            "TokenToCharge.CardValidityYear": asm3.person.get_extra_id(self.dbo, p, "Cardcom_CardValidity").split("/")[1][-2:],
            "TokenToCharge.IdentityNumber": asm3.person.get_extra_id(self.dbo, p, "Cardcom_CardOwnerID")
        }

        for p in self.getInvoiceItems(payments):
            params.update(p)

        asm_debug(f"params: {params}", "cardcom.tokenCharge", self.dbo)
        response = requests.post(url, data=params)
        if not response.ok:
            raise Exception(f"Response not ok: {response.status_code} {response.text}")

        results = dict(parse_qsl(response.text))
        asm_debug(f"parsed response: {results}")

        if results["ResponseCode"] != "0":
            asm3.al.error(f"Bad Cardcom operation response {results['ResponseCode']}: {results['Description']}", "cardcom.tokenCharge", self.dbo)
            raise ProcessorError(f"Bad Cardcom operation response {results['ResponseCode']}: {results['Description']}")

        trxid = f"{results.get('InvoiceResponse.InvoiceNumber','')}/{results.get('InternalDealNumber','')}"
        rcvd = asm3.utils.cint(results.get("ExtShvaParams.Sum36", total_charge_sum / 100.0))

        self.markPaymentReceived(payref, trxid, rcvd, 0, 0, response.text)

        InvoiceResponseCode = results.get("InvoiceResponse.ResponseCode")
        if InvoiceResponseCode != "0":
            asm3.al.error(f"Invoice not created for {payref}. Response code: {InvoiceResponseCode}", "cardcom.tokenCharge", self.dbo)


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
        asm_debug(f"{payref} {return_url} {item_description}", "cardcom.checkoutUrl", self.dbo)
        payments = self.getPayments(payref)
        total_charge_sum = sum(
            round(r.DONATION, 2) for r in payments
        )
        client_reference_id = "%s-%s" % (self.dbo.database, payref) # prefix database to payref 
        OwnerID = payments[0].OWNERID
        p = asm3.person.get_person(self.dbo, OwnerID)

        if not asm3.utils.is_valid_email_address(p.EMAILADDRESS):
            raise Exception(_("Invalid email address"))


        url = "https://secure.cardcom.solutions/Interface/LowProfile.aspx"
        params = {
            "DocTypeToCreate": asm3.configuration.cardcom_documenttype(self.dbo), #3=#nonprofit receipt
            "Operation": "2", #charge + create token,
            "TerminalNumber": asm3.configuration.cardcom_terminalnumber(self.dbo), #
            "UserName": asm3.configuration.cardcom_username(self.dbo), #
            "SumToBill": f"{total_charge_sum / 100.0}",
            "CoinID": "1", #TODO: not critical - use ASM currency
            "Language": "he", #TODO: not critical - config / use locale?
            "SuccessRedirectUrl": asm3.configuration.cardcom_successurl(self.dbo), # "https://secure.cardcom.solutions/DealWasSuccessful.aspx",
            "ErrorRedirectUrl": asm3.configuration.cardcom_errorurl(self.dbo), #"https://secure.cardcom.solutions/DealWasUnSuccessful.aspx?customVar=1234",
            "APILevel": "10",
            "IsVirtualTerminalMode": "true",
            "codepage": "65001", #unicode
            "ReturnValue": client_reference_id,
            "InvoiceHead.CustName": html.unescape(p.OWNERNAME)[:50] , 
            "InvoiceHead.CustAddresLine1": html.unescape(p.OWNERADDRESS)[:50], 
            "InvoiceHead.CustCity": html.unescape(p.OWNERTOWN)[:50],            
            "InvoiceHead.CustMobilePH": html.unescape(p.MOBILETELEPHONE)[:50],  
            "InvoiceHead.ExtIsVatFree": "true",#no VAT for nonprofit receipts. #TODO: config?
            "InvoiceHead.SendByEmail": "true", #TODO: not critical - config?
            "InvoiceHead.Language": "he", #TODO: not critical - config / use locale?
            "InvoiceHead.Email": p.EMAILADDRESS,
            "IndicatorUrl": f"{BASE_URL}/pp_cardcom", 
        }

        for p in self.getInvoiceItems(payments):
            params.update(p)        

        asm_debug(f"params: {params}", "cardcom.checkoutUrl", self.dbo)
        response = requests.post(url, data=params)
        asm_debug(f"response {response.status_code} , text: {response.text}", "cardcom.checkoutUrl", self.dbo)
        if not response.ok:
            raise Exception(f"Response not ok: {response.status_code} {response.text}")
        cardcom_reply = dict(parse_qsl(response.text))
        if "url" not in cardcom_reply:
            raise Exception(f"No url in response text: {response.text}")
        asm_debug(f"return cardcom url: {cardcom_reply['url']}", "cardcom.checkoutUrl", self.dbo)
        return f"{cardcom_reply['url']}"



    def receive(self, rawdata):
        asm_debug(rawdata, "cardcom.receive", self.dbo)
        # make request to retrieve more information on the transaction
        params = dict(parse_qsl(rawdata))
        url = 'https://secure.cardcom.solutions/Interface/BillGoldGetLowProfileIndicator.aspx'
        params = {
            "codepage": "65001", #unicode
            "terminalnumber": params["terminalnumber"],
            "username": asm3.configuration.cardcom_username(self.dbo), #
            "lowprofilecode": params["lowprofilecode"]
        }

        response = requests.get(url, params=params)
        if response.ok:
            # parse results
            raw_results = response.text
            results = dict(parse_qsl(raw_results))
            #check 
            if results.get("OperationResponse") != "0":
                asm3.al.error(f"Bad Cardcom operation response {results['OperationResponse']}: {results['OperationResponseText']}", "cardcom.receive", self.dbo)
                raise ProcessorError(f"Bad Cardcom operation response {results['OperationResponse']}: {results['OperationResponseText']}")

            if results.get("DealResponse") != "0":
                asm3.al.error(f"Bad Cardcom operation response {results['DealResponse']}", "cardcom.receive", self.dbo)
                raise ProcessorError(f"Bad Cardcom operation response {results['DealResponse']}")

            #ReturnValue contains db-payref. Extract payref
            client_reference_id = results.get("ReturnValue","")
            payref = client_reference_id[client_reference_id.find("-")+1:]
            asm_debug(f"payref: {payref}")

            # Check the payref is valid 
            if not self.validatePaymentReference(payref):
                asm3.al.error("payref '%s' failed validation" % payref, "cardcom.receive", self.dbo)
                raise PayRefError("payref '%s' is invalid" % payref)

            # Do nothing if we already received payment for this payref
            if self.isPaymentReceived(payref): 
                asm3.al.error("cannot receive payref '%s' again, already received.", "cardcom.receive", self.dbo)
                raise AlreadyReceivedError("payref '%s' has already been processed." % payref)

            #Combine Invoice Number + DealNumber
            trxid = f"{results.get('InvoiceNumber','')}/{results.get('InternalDealNumber','')}"
            rcvd = asm3.utils.cint(results.get("ExtShvaParams.Sum36"))

            # get payments
            payments = self.getPayments(payref)

            # get owner ID in order to add/update token information
            OwnerID = payments[0].OWNERID

            # Mark our payment as received with the correct amounts
            self.markPaymentReceived(payref, trxid, rcvd, 0, 0, raw_results)


            user = "cardcom"

            Token = results.get("Token")
            TokenExDate = results.get("TokenExDate")
            CardOwnerID = results.get("CardOwnerID")
            CardValidity = f"{results.get('CardValidityMonth')}/{results.get('CardValidityYear')}"
            Last4Digits = results.get("ExtShvaParams.CardNumber5")
            CCType = results.get("ExtShvaParams.CardName")
            CCOwner = results.get("ExtShvaParams.CardOwnerName")

            if Token is not None:
                asm_debug(f"OwnerID={OwnerID}")
                p = asm3.person.get_person(self.dbo, OwnerID)
                asm_debug(f"p={p}")
                asm3.person.set_extra_id(self.dbo, user, p, "Cardcom_Token", Token)
                asm3.person.set_extra_id(self.dbo, user, p, "Cardcom_TokenExDate", TokenExDate)
                asm3.person.set_extra_id(self.dbo, user, p, "Cardcom_CardOwnerID", CardOwnerID)
                asm3.person.set_extra_id(self.dbo, user, p, "Cardcom_CardValidity", CardValidity)
                asm3.person.set_extra_id(self.dbo, user, p, "Cardcom_Last4Digits", Last4Digits)
                asm3.person.set_extra_id(self.dbo, user, p, "Cardcom_CCType", CCType)
                asm3.person.set_extra_id(self.dbo, user, p, "Cardcom_CCOwner", CCOwner)
            
            InvoiceResponseCode = results.get("InvoiceResponseCode")
            if InvoiceResponseCode != "0":
                asm3.al.error(f"Invoice not created for {payref}. Response code: {InvoiceResponseCode}", "cardcom.receive", self.dbo)

        return
