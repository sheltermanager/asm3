import asm3.configuration
import asm3.utils

from asm3.i18n import _
from asm3.al import debug as asm_debug
from .base import PaymentProcessor, ProcessorError, PayRefError, AlreadyReceivedError

from asm3.sitedefs import BASE_URL
from asm3.typehints import Database, Dict, Generator, Results

class Cardcom(PaymentProcessor):
    """Cardcom provider http://kb.cardcom.co.il/article/AA-00402/0/"""

    def __init__(self, dbo: Database) -> None:
        PaymentProcessor.__init__(self, dbo, "cardcom")
        self.paymentmethodmapping = asm3.utils.json_parse(asm3.configuration.cardcom_paymentmethodmapping(self.dbo))
        self.paymenttypemapping = asm3.utils.json_parse(asm3.configuration.cardcom_paymenttypemapping(self.dbo))

    def map_item_or_default(self, item: str, mapdict: Dict) -> str:
        asm_debug(f"item: {item}")
        asm_debug(f"mapdict: {mapdict}")
        return mapdict[str(item)] if str(item) in mapdict else mapdict["default"]

    def map_method(self, method: str) -> str:
        return self.map_item_or_default(method, self.paymentmethodmapping)

    def map_type(self, payment_type: str) -> str:
        return self.map_item_or_default(payment_type, self.paymenttypemapping)

    def getReceiptInfo(self, records: Results, total_charge_sum: str) -> Dict:
        methods = []
        payment_types = []
        references = []
        duedates = []
        for index, record in enumerate(records, start=1):
            methods.append(self.map_method(record.DONATIONPAYMENTID))
            payment_types.append(self.map_type(record.DONATIONTYPEID))
            references.append(record.CHEQUENUMBER)
            duedates.append(record.DATEDUE)
        # make sure payment methods and payment types are all mapped to the same target; otherwise, throw errors
        if methods.count(methods[0]) != len(methods):
            raise Exception(_("Payment items must have matching payment methods.")) 
        if payment_types.count(payment_types[0]) != len(payment_types):
            raise Exception(_("Payment items must have matching payment types.")) 
        if references.count(references[0]) != len(references):
            raise Exception(_("Payment items must have matching references."))
        if duedates.count(duedates[0]) != len(duedates):
            raise Exception(_("Payment items must have matching due dates."))
        method = methods[0]
        payment_type = payment_types[0]
        reference = references[0]
        duedate = duedates[0]
        asm_debug(f"method: {method}")
        asm_debug(f"payment_type: {payment_type}")
        asm_debug(f"reference: {reference}") 
        asm_debug(f"duedate: {duedate}")               
        data = {"InvoiceType": payment_type["InvoiceType"], "action": method["action"]}
        receiptfields = {}
        if method["action"] == "receipt":
            # add extra fields for receipt
            if method["method"] == "cash":
                receiptfields = {"Cash": total_charge_sum}
            elif method["method"] == "cheque":
                split_ref = reference.split("-")
                if len(split_ref)<2:
                    raise Exception(_("Cheque reference must be in the format [BANK-][BRANCH-]ACCOUNT-CHEQUENUM"))
                receiptfields = {"Cheque.Sum": total_charge_sum, "Cheque.ChequeNumber": split_ref[-1], "Cheque.AccountNumber": split_ref[-2]}
                if len(split_ref)>2:
                    receiptfields["Cheque.SnifNumber"] = split_ref[-3]
                if len(split_ref)>3:
                    receiptfields["Cheque.BankNumber"] = split_ref[-4]
                receiptfields["Cheque.DateCheque"] = duedate.strftime("%d/%m/%Y")
            elif method["method"] == "custom":
                receiptfields = {"CustomPay.Sum": total_charge_sum, "CustomPay.TransactionID": method["tx_id"], "CustomPay.Asmacta": reference}
            data["receiptfields"] = receiptfields
        return data

    def getInvoiceItems(self, records: Results) -> Generator[Dict, None, None]:
        for index, record in enumerate(records, start=1):
            description = record.DONATIONNAME
            price = round(record.DONATION, 2)
            if record.VATAMOUNT > 0: price += record.VATAMOUNT
            price = price / 100.0
            yield {"InvoiceLines%d.Description" % index: description[:250]}
            yield {"InvoiceLines%d.Quantity" % index: 1}
            yield {"InvoiceLines%d.Price" % index: price} 

    def tokenCharge(self, payref: str, item_description: str = "", installments: int = 1) -> None:
        payments = self.getPayments(payref)
        total_charge_sum = 0.0
        for r in payments:
            total_charge_sum += round(r.DONATION, 2)
            if r.VATAMOUNT: total_charge_sum += r.VATAMOUNT # add VAT for consistency with other ayment providers
        total_charge_sum = total_charge_sum / 100.0
        client_reference_id = "%s-%s" % (self.dbo.name(), payref) # prefix database to payref 
        OwnerID = payments[0].OWNERID
        p = asm3.person.get_person(self.dbo, OwnerID)

        if not asm3.utils.is_valid_email_address(p.EMAILADDRESS):
            raise Exception(_("Invalid email address")) 

        receiptinfo = self.getReceiptInfo(payments, str(total_charge_sum))

        if receiptinfo["action"] == "cc_charge":
            url = "https://secure.cardcom.solutions/interface/ChargeToken.aspx"
            params = {
                "Operation": "2", # charge + create token,
                "TerminalNumber": asm3.configuration.cardcom_terminalnumber(self.dbo),
                "UserName": asm3.configuration.cardcom_username(self.dbo),
                "codepage": "65001", # unicode
                "TokenToCharge.DocTypeToCreate": receiptinfo["InvoiceType"], # asm3.configuration.cardcom_documenttype(self.dbo), # 3 = nonprofit receipt
                "TokenToCharge.SumToBill": str(total_charge_sum),
                "TokenToCharge.CoinID": "1", # TODO: not critical - use ASM currency
                "TokenToCharge.UniqAsmachta": client_reference_id,
                "TokenToCharge.NumOfPayments": installments,
                "InvoiceHead.CustName": p.OWNERNAME[:50] , 
                "InvoiceHead.CustAddresLine1": p.OWNERADDRESS[:50], 
                "InvoiceHead.CustCity": p.OWNERTOWN[:50],            
                "InvoiceHead.CustMobilePH": p.MOBILETELEPHONE[:50],  
                "InvoiceHead.ExtIsVatFree": "true",# no VAT for nonprofit receipts. TODO: config?
                "InvoiceHead.SendByEmail": "true", # TODO: not critical - config?
                "InvoiceHead.Language": "he", # TODO: not critical - config / use locale?
                "InvoiceHead.Email": p.EMAILADDRESS,
                "TokenToCharge.Token": asm3.person.get_extra_id(self.dbo, p, "Cardcom_Token"),
                "TokenToCharge.CardValidityMonth": asm3.person.get_extra_id(self.dbo, p, "Cardcom_CardValidity").split("/")[0],
                "TokenToCharge.CardValidityYear": asm3.person.get_extra_id(self.dbo, p, "Cardcom_CardValidity").split("/")[1][-2:],
                "TokenToCharge.IdentityNumber": asm3.person.get_extra_id(self.dbo, p, "Cardcom_CardOwnerID")
            }

            for p in self.getInvoiceItems(payments):
                params.update(p)

            asm_debug("params: %s" % params, "cardcom.tokenCharge", self.dbo)
            r = asm3.utils.post_form(url, params)
            if not r["status"] < 400:
                raise Exception("Response not ok: %s %s" % (r["status"], r["response"]))

            results = asm3.utils.parse_qs(r["response"])
            asm_debug("parsed response: %s" % results)

            if results["ResponseCode"] != "0":
                asm3.al.error("Bad Cardcom operation response %s: %s" % (results['ResponseCode'], results['Description']), "cardcom.tokenCharge", self.dbo)
                raise ProcessorError("Bad Cardcom operation response %s: %s" % (results['ResponseCode'], results['Description']))

            trxid = "%s/%s" % (results.get('InvoiceResponse.InvoiceNumber',''), results.get('InternalDealNumber',''))
            rcvd = asm3.utils.cint(results.get("ExtShvaParams.Sum36", total_charge_sum / 100.0))

            self.markPaymentReceived(payref, trxid, rcvd, 0, 0, r["response"])

            InvoiceResponseCode = results.get("InvoiceResponse.ResponseCode")
            if InvoiceResponseCode != "0":
                asm3.al.error("Invoice not created for %s. Response code: %s" % (payref, InvoiceResponseCode), "cardcom.tokenCharge", self.dbo)
        else:
            raise Exception(_("Token charge does not support this payment method."))


    def checkoutPage(self, payref: str, return_url: str = "", item_description: str = "") -> str:
        try:
            url = self.checkoutUrl(payref, return_url, item_description)
            return """<DOCTYPE html>
            <html>
            <head>
            <meta http-equiv="Refresh" content="0; URL=%s">
            </head>
            <body></body>
            </html>""" % url
        except Exception as err:
            return """<DOCTYPE html>
                <html>
                <head>
                </head>
                <body>%s</body>
                </html>""" % err

    def checkoutUrl(self, payref: str, return_url: str = "", item_description: str = "") -> str:
        asm_debug("%s %s %s" % (payref, return_url, item_description), "cardcom.checkoutUrl", self.dbo)
        payments = self.getPayments(payref)
        total_charge_sum = sum(
            round(r.DONATION, 2) for r in payments
        )
        client_reference_id = "%s-%s" % (self.dbo.name(), payref) # prefix database to payref 
        OwnerID = payments[0].OWNERID
        p = asm3.person.get_person(self.dbo, OwnerID)

        if not asm3.utils.is_valid_email_address(p.EMAILADDRESS):
            raise Exception(_("Invalid email address"))

        receiptinfo = self.getReceiptInfo(payments, str(total_charge_sum / 100.0))

        asm_debug(f"receiptinfo: {receiptinfo}")

        if receiptinfo["action"] == "cc_charge":
            url = "https://secure.cardcom.solutions/Interface/LowProfile.aspx"
            params = {
                "TerminalNumber": asm3.configuration.cardcom_terminalnumber(self.dbo),
                "UserName": asm3.configuration.cardcom_username(self.dbo),
                "SumToBill": str(total_charge_sum / 100.0),
                "CoinID": "1", # TODO: not critical - use ASM currency
                "Language": "he", # TODO: not critical - config / use locale?
                "SuccessRedirectUrl": asm3.configuration.cardcom_successurl(self.dbo), # "https://secure.cardcom.solutions/DealWasSuccessful.aspx",
                "ErrorRedirectUrl": asm3.configuration.cardcom_errorurl(self.dbo), # "https://secure.cardcom.solutions/DealWasUnSuccessful.aspx?customVar=1234",
                "APILevel": "10",
                "IsVirtualTerminalMode": "true",
                "codepage": "65001", # unicode
                "ReturnValue": client_reference_id,
                "IndicatorUrl": "%s/pp_cardcom" % BASE_URL, 
            }

            # determine operation by total charge amount. If charge amount>0, charge and create token (this will also create a tax document). If charge amount==0, only create token
            more_params = {}
            if total_charge_sum > 0: 
                more_params = {
                    "Operation": "2",  # charge + create token
                    "DocTypeToCreate": receiptinfo["InvoiceType"], # asm3.configuration.cardcom_documenttype(self.dbo), # 3 = nonprofit receipt
                    "InvoiceHead.CustName": p.OWNERNAME[:50] , 
                    "InvoiceHead.CustAddresLine1": p.OWNERADDRESS[:50], 
                    "InvoiceHead.CustCity": p.OWNERTOWN[:50],            
                    "InvoiceHead.CustMobilePH": p.MOBILETELEPHONE[:50],  
                    "InvoiceHead.ExtIsVatFree": "true",# no VAT for nonprofit receipts. TODO: config?
                    "InvoiceHead.SendByEmail": "true", # TODO: not critical - config?
                    "InvoiceHead.Language": "he", # TODO: not critical - config / use locale?
                    "InvoiceHead.Email": p.EMAILADDRESS,
                    }
                for p in self.getInvoiceItems(payments):
                    more_params.update(p)   
            else: # if total_charge_sum == 0:
                more_params = {
                    "Operation": "3" # only create token
                    }

            params.update(more_params)

            asm_debug("params: %s" % params, "cardcom.checkoutUrl", self.dbo)
            r = asm3.utils.post_form(url, params)
            asm_debug("response %s, text: %s" % (r["status"], r["response"]), "cardcom.checkoutUrl", self.dbo)
            if not r["status"] < 400:
                raise Exception("Response not ok: %s %s" % (r["status"], r["response"]))
            cardcom_reply = asm3.utils.parse_qs(r["response"])
            if "url" not in cardcom_reply:
                raise Exception("No url in response text: %s" % r["response"])
            asm_debug("return cardcom url: %s" % cardcom_reply['url'], "cardcom.checkoutUrl", self.dbo)
            return cardcom_reply['url']
        elif receiptinfo["action"] == "receipt" and asm3.configuration.cardcom_handlenonccpayments(self.dbo):
            url = "https://secure.cardcom.solutions/Interface/CreateInvoice.aspx"
            params = {
                "TerminalNumber": asm3.configuration.cardcom_terminalnumber(self.dbo),
                "UserName": asm3.configuration.cardcom_username(self.dbo),
                "InvoiceType": receiptinfo["InvoiceType"],
                "Language": "he", # TODO: not critical - config / use locale?
                "InvoiceHead.CustName": p.OWNERNAME[:50] , 
                "InvoiceHead.CustAddresLine1": p.OWNERADDRESS[:50], 
                "InvoiceHead.CustCity": p.OWNERTOWN[:50],            
                "InvoiceHead.CustMobilePH": p.MOBILETELEPHONE[:50],  
                "InvoiceHead.ExtIsVatFree": "true",# no VAT for nonprofit receipts. TODO: config?
                "InvoiceHead.SendByEmail": "true", # TODO: not critical - config?
                "InvoiceHead.Language": "he", # TODO: not critical - config / use locale?
                "InvoiceHead.Email": p.EMAILADDRESS,
            }
            params.update(receiptinfo["receiptfields"])
            for p in self.getInvoiceItems(payments):
                params.update(p)
            asm_debug("params: %s" % params, "cardcom.checkoutUrl", self.dbo)
            r = asm3.utils.post_form(url, params)
            asm_debug("response %s, text: %s" % (r["status"], r["response"]), "cardcom.checkoutUrl", self.dbo)
            if not r["status"] < 400:
                raise Exception("Response not ok: %s %s" % (r["status"], r["response"]))
            cardcom_reply = asm3.utils.parse_qs(r["response"])
            if "ResponseCode" in cardcom_reply and cardcom_reply["ResponseCode"]!="0":
                raise Exception(f"Cardcom error: {cardcom_reply}")
            trxid = ""
            # append receipt number to cheque or other payment type reference
            if payments[0].CHEQUENUMBER != "":
                trxid = payments[0].CHEQUENUMBER + '/' + cardcom_reply.get('InvoiceNumber','')
            else:
                trxid = cardcom_reply.get('InvoiceNumber','')
            rcvd = asm3.utils.cint(total_charge_sum / 100.0)
            self.markPaymentReceived(payref, trxid, rcvd, 0, 0, r["response"])
            return asm3.configuration.cardcom_successurl(self.dbo)
        else:
            asm_debug(f"receiptinfo: {receiptinfo}")
            raise Exception(f"Cardcom error: {cardcom_reply['Description']}")

    def receive(self, rawdata: str) -> None:
        asm_debug(rawdata, "cardcom.receive", self.dbo)
        # make request to retrieve more information on the transaction
        params = asm3.utils.parse_qs(rawdata)
        url = "https://secure.cardcom.solutions/Interface/BillGoldGetLowProfileIndicator.aspx"
        params = {
            "codepage": "65001", # unicode
            "terminalnumber": params["terminalnumber"],
            "username": asm3.configuration.cardcom_username(self.dbo),
            "lowprofilecode": params["lowprofilecode"]
        }

        r = asm3.utils.get_url(url, params=params)
        if r["status"] < 400:
            # parse results
            raw_results = r["response"]
            results = asm3.utils.parse_qs(raw_results)
            asm_debug(results, "cardcom.receive", self.dbo)
            #check 
            if results.get("OperationResponse") != "0":
                asm3.al.error("Bad Cardcom operation response %s: %s" % (results['OperationResponse'], results['OperationResponseText']), "cardcom.receive", self.dbo)
                raise ProcessorError("Bad Cardcom operation response %s: %s" % (results['OperationResponse'], results['OperationResponseText']))

            #if results.get("DealResponse") != "0":
            #    asm3.al.error("Bad Cardcom Deal response %s" % results['DealResponse'], "cardcom.receive", self.dbo)
            #    raise ProcessorError("Bad Cardcom deal response %s" % results['DealResponse'])

            #ReturnValue contains db-payref. Extract payref
            client_reference_id = results.get("ReturnValue","")
            payref = client_reference_id[client_reference_id.find("-")+1:]
            asm_debug("payref: %s" % payref)

            # Check the payref is valid 
            if not self.validatePaymentReference(payref):
                asm3.al.error("payref '%s' failed validation" % payref, "cardcom.receive", self.dbo)
                raise PayRefError("payref '%s' is invalid" % payref)

            # Do nothing if we already received payment for this payref
            if self.isPaymentReceived(payref): 
                asm3.al.error("cannot receive payref '%s' again, already received.", "cardcom.receive", self.dbo)
                raise AlreadyReceivedError("payref '%s' has already been processed." % payref)

            #Combine Invoice Number + DealNumber
            trxid = "%s/%s" % (results.get('InvoiceNumber',''), results.get('InternalDealNumber',''))
            rcvd = asm3.utils.cint(results.get("ExtShvaParams.Sum36"))

            # get payments
            payments = self.getPayments(payref)

            # get owner ID in order to add/update token information
            OwnerID = payments[0].OWNERID

            # Mark our payment as received with the correct amounts
            self.markPaymentReceived(payref, trxid, rcvd, 0, 0, raw_results)

            user = "cardcom"

            Token = results.get("Token")
            if Token is None:
                asm_debug("Token field not found in result. Trying ExtShvaParams.CardToken", "cardcom.receive", self.dbo)
                Token = results.get("ExtShvaParams.CardToken")
            TokenExDate = results.get("TokenExDate")
            CardOwnerID = results.get("CardOwnerID")
            CardValidity = "%s/%s" % (results.get('CardValidityMonth'), results.get('CardValidityYear'))
            Last4Digits = results.get("ExtShvaParams.CardNumber5")
            CCType = results.get("ExtShvaParams.CardName")
            CCOwner = results.get("ExtShvaParams.CardOwnerName")

            if Token is not None:
                asm_debug("OwnerID=%s" % OwnerID)
                p = asm3.person.get_person(self.dbo, OwnerID)
                asm_debug("p=%s" % p)
                asm3.person.set_extra_id(self.dbo, user, p, "Cardcom_Token", Token)
                asm3.person.set_extra_id(self.dbo, user, p, "Cardcom_TokenExDate", TokenExDate)
                asm3.person.set_extra_id(self.dbo, user, p, "Cardcom_CardOwnerID", CardOwnerID)
                asm3.person.set_extra_id(self.dbo, user, p, "Cardcom_CardValidity", CardValidity)
                asm3.person.set_extra_id(self.dbo, user, p, "Cardcom_Last4Digits", Last4Digits)
                asm3.person.set_extra_id(self.dbo, user, p, "Cardcom_CCType", CCType)
                asm3.person.set_extra_id(self.dbo, user, p, "Cardcom_CCOwner", CCOwner)
            else:
                asm_debug("Token is empty. Not storing anything in EXTRAIDS", "cardcom.receive", self.dbo)
                
            
            InvoiceResponseCode = results.get("InvoiceResponseCode")
            if InvoiceResponseCode != "0":
                asm3.al.error("Invoice not created for %s. Response code: %s" % (payref, InvoiceResponseCode), "cardcom.receive", self.dbo)
