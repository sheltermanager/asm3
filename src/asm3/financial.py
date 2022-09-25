
import asm3.al
import asm3.audit
import asm3.configuration
import asm3.i18n
import asm3.movement
import asm3.paymentprocessor.paypal
import asm3.paymentprocessor.stripeh
import asm3.paymentprocessor.cardcom
import asm3.utils

import sys

BANK = 1
CREDITCARD = 2
LOAN = 3
EXPENSE = 4
INCOME = 5
PENSION = 6
SHARES = 7
ASSET = 8
LIABILITY = 9

BOTH = 0
RECONCILED = 1
NONRECONCILED = 2

THIS_MONTH = 0
THIS_WEEK = 1
THIS_YEAR = 2
LAST_MONTH = 3
LAST_WEEK = 4

WEEKLY = 1
FORTNIGHTLY = 2
MONTHLY = 3
QUARTERLY = 4
HALF_YEARLY = 5
ANNUALLY = 6

ASCENDING = 0
DESCENDING = 1

def get_citation_query(dbo):
    return "SELECT oc.ID, oc.CitationTypeID, oc.CitationDate, oc.Comments, ct.CitationName, " \
        "oc.FineAmount, oc.FineDueDate, oc.FinePaidDate, oc.AnimalControlID, " \
        "oc.OwnerID, ti.IncidentName, " \
        "oc.CreatedBy, oc.CreatedDate, oc.LastChangedBy, oc.LastChangedDate, " \
        "o.OwnerTitle, o.OwnerInitials, o.OwnerSurname, o.OwnerForenames, o.OwnerName " \
        "FROM ownercitation oc " \
        "INNER JOIN citationtype ct ON ct.ID = oc.CitationTypeID " \
        "INNER JOIN owner o ON o.ID = oc.OwnerID " \
        "LEFT OUTER JOIN animalcontrol ac ON ac.ID = oc.AnimalControlID " \
        "LEFT OUTER JOIN incidenttype ti ON ti.ID = ac.IncidentTypeID " 

def get_donation_query(dbo):
    return "SELECT od.ID, od.DonationTypeID, od.DonationPaymentID, dt.DonationName, od.Date, od.DateDue, " \
        "od.Donation, od.MovementID, p.PaymentName, od.IsGiftAid, lk.Name AS IsGiftAidName, od.Frequency, " \
        "od.Quantity, od.UnitPrice, " \
        "od.Donation AS Gross, " \
        "od.Donation - COALESCE(od.VATAmount, 0) - COALESCE(od.Fee, 0) AS Net, " \
        "fr.Frequency AS FrequencyName, od.NextCreated, " \
        "od.ReceiptNumber, od.ChequeNumber, od.Fee, od.IsVAT, od.VATRate, od.VATAmount, " \
        "od.CreatedBy, od.CreatedDate, od.LastChangedBy, od.LastChangedDate, " \
        "od.Comments, o.OwnerTitle, o.OwnerInitials, o.OwnerSurname, o.OwnerForenames, " \
        "o.OwnerName, o.OwnerCode, o.OwnerAddress, o.OwnerTown, o.OwnerCounty, o.OwnerPostcode, " \
        "o.HomeTelephone, o.WorkTelephone, o.MobileTelephone, o.EmailAddress, o.AdditionalFlags, " \
        "a.AnimalName, a.ShelterCode, a.ShortCode, a.ID AS AnimalID, o.ID AS OwnerID, " \
        "a.HasActiveReserve, a.HasTrialAdoption, a.CrueltyCase, a.NonShelterAnimal, " \
        "a.Neutered, a.IsNotAvailableForAdoption, a.IsHold, a.IsQuarantine, a.ShelterLocationUnit, " \
        "a.CombiTestResult, a.FLVResult, a.HeartwormTestResult, " \
        "CASE " \
        "WHEN a.Archived = 0 AND a.ActiveMovementType = 8 THEN " \
        "(SELECT MovementType FROM lksmovementtype WHERE ID=8) " \
        "WHEN a.Archived = 0 AND a.ActiveMovementType = 2 AND a.HasPermanentFoster = 1 THEN " \
        "(SELECT MovementType FROM lksmovementtype WHERE ID=12) " \
        "WHEN a.Archived = 0 AND a.ActiveMovementType = 2 THEN " \
        "(SELECT MovementType FROM lksmovementtype WHERE ID=a.ActiveMovementType) " \
        "WHEN a.Archived = 0 AND a.ActiveMovementType = 1 AND a.HasTrialAdoption = 1 THEN " \
        "(SELECT MovementType FROM lksmovementtype WHERE ID=11) " \
        "WHEN a.Archived = 1 AND a.DeceasedDate Is Not Null AND a.ActiveMovementID = 0 THEN " \
        "(SELECT ReasonName FROM deathreason WHERE ID = a.PTSReasonID) " \
        "WHEN a.Archived = 1 AND a.DeceasedDate Is Not Null AND a.ActiveMovementID <> 0 THEN " \
        "(SELECT MovementType FROM lksmovementtype WHERE ID=a.ActiveMovementType) " \
        "WHEN a.Archived = 1 AND a.DeceasedDate Is Null AND a.ActiveMovementID <> 0 THEN " \
        "(SELECT MovementType FROM lksmovementtype WHERE ID=a.ActiveMovementType) " \
        "ELSE " \
        "(SELECT LocationName FROM internallocation WHERE ID=a.ShelterLocation) " \
        "END AS DisplayLocationName, " \
        "(SELECT LocationName FROM internallocation WHERE ID=a.ShelterLocation) AS ShelterLocationName, " \
        "co.OwnerName AS CurrentOwnerName " \
        "FROM ownerdonation od " \
        "LEFT OUTER JOIN animal a ON a.ID = od.AnimalID " \
        "LEFT OUTER JOIN adoption ad ON ad.ID = a.ActiveMovementID " \
        "LEFT OUTER JOIN owner co ON co.ID = ad.OwnerID " \
        "LEFT OUTER JOIN donationpayment p ON od.DonationPaymentID = p.ID " \
        "LEFT OUTER JOIN lksyesno lk ON lk.ID = od.IsGiftAid " \
        "LEFT OUTER JOIN owner o ON o.ID = od.OwnerID " \
        "LEFT OUTER JOIN donationtype dt ON dt.ID = od.DonationTypeID " \
        "LEFT OUTER JOIN lksdonationfreq fr ON fr.ID = od.Frequency "

def get_licence_query(dbo):
    return "SELECT ol.ID, ol.LicenceTypeID, ol.IssueDate, ol.ExpiryDate, lt.LicenceTypeName, " \
        "ol.LicenceNumber, ol.LicenceFee, ol.Comments, ol.OwnerID, ol.AnimalID, " \
        "ol.CreatedBy, ol.CreatedDate, ol.LastChangedBy, ol.LastChangedDate, " \
        "a.AnimalName, a.ShelterCode, a.ShortCode, a.Sex, " \
        "o.OwnerTitle, o.OwnerInitials, o.OwnerSurname, o.OwnerForenames, o.OwnerName, " \
        "o.OwnerAddress, o.OwnerTown, o.OwnerCounty, o.OwnerPostcode, " \
        "o.HomeTelephone, o.WorkTelephone, o.MobileTelephone " \
        "FROM ownerlicence ol " \
        "INNER JOIN licencetype lt ON lt.ID = ol.LicenceTypeID " \
        "INNER JOIN owner o ON o.ID = ol.OwnerID " \
        "LEFT OUTER JOIN animal a ON a.ID = ol.AnimalID "

def get_voucher_query(dbo):
    return "SELECT ov.*, v.VoucherName, o.OwnerName, " \
        "o.OwnerAddress, o.OwnerTown, o.OwnerCounty, o.OwnerPostcode, " \
        "o.HomeTelephone, o.WorkTelephone, o.MobileTelephone, o.EmailAddress, o.AdditionalFlags, " \
        "a.AnimalName, a.ShelterCode, a.ShortCode " \
        "FROM ownervoucher ov " \
        "INNER JOIN voucher v ON v.ID = ov.VoucherID " \
        "INNER JOIN owner o ON o.ID = ov.OwnerID " \
        "LEFT OUTER JOIN animal a ON ov.AnimalID = a.ID "

def get_account_code(dbo, accountid):
    """
    Returns the code for an accountid
    """
    return dbo.query_string("SELECT Code FROM accounts WHERE ID = ?", [accountid])

def get_account_codes(dbo, exclude = "", onlyactive = True):
    """
    Returns a list of all account codes in order. 
    exclude: if set, leaves that one out.
    onlyactive: if set, only active accounts are included
    """
    l = []
    for a in get_accounts(dbo, onlyactive):
        if a["CODE"] == exclude: continue
        l.append(a["CODE"])
    return l

def get_account_edit_roles(dbo, accountid):
    """
    Returns a list of edit role ids for this account
    """
    roles = []
    rows = dbo.query("SELECT ar.RoleID FROM accountsrole ar WHERE ar.AccountID = ? AND ar.CanEdit = 1", [accountid])
    for r in rows:
        roles.append(str(r.ROLEID))
    return roles

def get_account_id(dbo, code):
    """
    Returns the id for an account code
    """
    return dbo.query_int("SELECT ID FROM accounts WHERE Code = ?", [code])
    
def get_accounts(dbo, onlyactive = False, onlybank = False, onlyexpense = False, onlyincome = False):
    """
    Returns all of the accounts with reconciled/balance figures
    ID, CODE, DESCRIPTION, ACCOUNTTYPE, DONATIONTYPEID, RECONCILED, BALANCE, VIEWROLEIDS, VIEWROLES, EDITROLEIDS, EDITROLES
    If an accounting period has been set, balances are calculated from that point.
    onlyactive: If set to true, only accounts with ARCHIVED == 0 are returned
    onlybank: If set to true, only accounts with ACCOUNTTYPE = 1 are returned
    onlyexpense: If set to true, only accounts with ACCOUNTTYPE = 4 are returned
    """
    l = dbo.locale
    pfilter = ""
    aperiod = asm3.configuration.accounting_period(dbo)
    if aperiod != "":
        pfilter = " AND TrxDate >= %s" % dbo.sql_date(asm3.i18n.display2python(l, aperiod), wrapParens=True, includeTime=False)
    afilter = ""
    if onlyactive:
        afilter = "AND a.Archived = 0"
    bfilter = ""
    if onlybank:
        bfilter = "AND a.AccountType = %d" % BANK
    efilter = ""
    if onlyexpense:
        efilter = "AND a.AccountType = %d" % EXPENSE
    ifilter = ""
    if onlyincome:
        ifilter = "AND a.AccountType = %d" % INCOME
    roles = dbo.query("SELECT ar.*, r.RoleName FROM accountsrole ar INNER JOIN role r ON ar.RoleID = r.ID")
    accounts = dbo.query("SELECT a.*, at.AccountType AS AccountTypeName, " \
        "dt.DonationName, " \
        "(SELECT SUM(Amount) FROM accountstrx WHERE DestinationAccountID = a.ID%s) AS dest," \
        "(SELECT SUM(Amount) FROM accountstrx WHERE SourceAccountID = a.ID%s) AS src," \
        "(SELECT SUM(Amount) FROM accountstrx WHERE Reconciled = 1 AND DestinationAccountID = a.ID%s) AS recdest," \
        "(SELECT SUM(Amount) FROM accountstrx WHERE Reconciled = 1 AND SourceAccountID = a.ID%s) AS recsrc " \
        "FROM accounts a " \
        "INNER JOIN lksaccounttype at ON at.ID = a.AccountType " \
        "LEFT OUTER JOIN donationtype dt ON dt.ID = a.DonationTypeID " \
        "WHERE a.ID > 0 %s %s %s %s " \
        "ORDER BY a.AccountType, a.Code" % (pfilter, pfilter, pfilter, pfilter, afilter, bfilter, efilter, ifilter))
    for a in accounts:
        dest = a.dest
        src = a.src
        recdest = a.recdest
        recsrc = a.recsrc
        if dest is None: dest = 0
        if src is None: src = 0
        if recdest is None: recdest = 0
        if recsrc is None: recsrc = 0
        a.balance = dest - src
        a.reconciled = recdest - recsrc
        if a.accounttype == INCOME or a.accounttype == EXPENSE:
            a.balance = abs(a.balance)
            a.reconciled = abs(a.reconciled)
        viewroleids = []
        viewrolenames = []
        editroleids = []
        editrolenames = []
        for r in roles:
            if r.accountid == a.id and r.canview == 1:
                viewroleids.append(str(r.roleid))
                viewrolenames.append(str(r.rolename))
            if r.accountid == a.id and r.canedit == 1:
                editroleids.append(str(r.roleid))
                editrolenames.append(str(r.rolename))
        a.viewroleids = "|".join(viewroleids)
        a.viewroles = "|".join(viewrolenames)
        a.editroleids = "|".join(editroleids)
        a.editroles = "|".join(editrolenames)
    return accounts

def get_balance_to_date(dbo, accountid, todate, reconciled=BOTH):
    """
    Returns the balance of accountid to todate.
    reconciled: One of RECONCILED, NONRECONCILED or BOTH to indicate the transactions to include in the balance.
    """
    aid = int(accountid)
    recfilter = ""
    if reconciled == RECONCILED:
        recfilter = " AND Reconciled = 1"
    elif reconciled == NONRECONCILED:
        recfilter = " AND Reconciled = 0"
    r = dbo.first_row( dbo.query("SELECT a.AccountType, " \
        "(SELECT SUM(Amount) FROM accountstrx WHERE SourceAccountID = a.ID AND TrxDate < ? %s) AS withdrawal," \
        "(SELECT SUM(Amount) FROM accountstrx WHERE DestinationAccountID = a.ID AND TrxDate < ? %s) AS deposit " \
        "FROM accounts a " \
        "WHERE a.ID = ?" % (recfilter, recfilter), (todate, todate, aid)) )
    deposit = r.deposit
    withdrawal = r.withdrawal
    if deposit is None: deposit = 0
    if withdrawal is None: withdrawal = 0
    balance = deposit - withdrawal
    #if r.accounttype == INCOME or r.accounttype == EXPENSE: balance = abs(balance)
    return balance

def get_balance_fromto_date(dbo, accountid, fromdate, todate, reconciled=BOTH):
    """
    Returns the balance of accountid from fromdate to todate.
    reconciled: One of RECONCILED, NONRECONCILED or BOTH to indicate the transactions to include in the balance.
    """
    aid = int(accountid)
    recfilter = ""
    if reconciled == RECONCILED:
        recfilter = " AND Reconciled = 1"
    elif reconciled == NONRECONCILED:
        recfilter = " AND Reconciled = 0"
    r = dbo.first_row( dbo.query("SELECT a.AccountType, " \
        "(SELECT SUM(Amount) FROM accountstrx WHERE SourceAccountID = a.ID AND TrxDate >= ? AND TrxDate < ? %s) AS withdrawal," \
        "(SELECT SUM(Amount) FROM accountstrx WHERE DestinationAccountID = a.ID AND TrxDate >= ? AND TrxDate < ? %s) AS deposit " \
        "FROM accounts a " \
        "WHERE a.ID = ?" % (recfilter, recfilter), (fromdate, todate, fromdate, todate, aid)) )
    deposit = r.deposit
    withdrawal = r.withdrawal
    if deposit is None: deposit = 0
    if withdrawal is None: withdrawal = 0
    balance = deposit - withdrawal
    #if r.accounttype == INCOME or r.accounttype == EXPENSE: balance = abs(balance)
    return balance

def mark_reconciled(dbo, trxid):
    """
    Marks a transaction reconciled.
    """
    dbo.update("accountstrx", trxid, {
        "Reconciled": 1
    })

def get_transactions(dbo, accountid, datefrom, dateto, reconciled=BOTH):
    """
    Gets a list of transactions for the account given, between
    two python dates. PERSONID and PERSONNAME are returned for
    linked donations.
    accountid: Account ID as integer
    datefrom: Python from date
    dateto: Python to date
    reconciled: one of RECONCILED, NONRECONCILED or BOTH to filter
    It creates extra columns, THISACCOUNT and OTHERACCOUNT
    for use by the UI when displaying transactions. It also adds 
    THISACCOUNTCODE and OTHERACCOUNTCODE for display purposes, 
    the BALANCE column and WITHDRAWAL and DEPOSIT.
    """
    l = dbo.locale
    period = asm3.configuration.accounting_period(dbo)
    if not asm3.configuration.account_period_totals(dbo):
        period = ""
    # If we have an accounting period set and it's after the from date,
    # use that instead
    if period != "" and asm3.i18n.after(asm3.i18n.display2python(l, period), datefrom):
        datefrom = asm3.i18n.display2python(l, period)
    recfilter = ""
    if reconciled == RECONCILED:
        recfilter = " AND Reconciled = 1"
    elif reconciled == NONRECONCILED:
        recfilter = " AND Reconciled = 0"
    rows = dbo.query("SELECT t.*, srcac.Code AS SrcCode, destac.Code AS DestCode, " \
        "o.OwnerName AS PersonName, o.ID AS PersonID, a.ID AS DonationAnimalID, " \
        "a.AnimalName AS DonationAnimalName, " \
        "od.ReceiptNumber AS DonationReceiptNumber, " \
        "CASE " \
        "WHEN EXISTS(SELECT ItemValue FROM configuration WHERE ItemName Like 'UseShortShelterCodes' AND ItemValue = 'Yes') " \
        "THEN a.ShortCode ELSE a.ShelterCode END AS DonationAnimalCode, " \
        "aca.AnimalName AS CostAnimalName, aca.ID AS CostAnimalID, " \
        "CASE " \
        "WHEN EXISTS(SELECT ItemValue FROM configuration WHERE ItemName Like 'UseShortShelterCodes' AND ItemValue = 'Yes') " \
        "THEN aca.ShortCode ELSE aca.ShelterCode END AS CostAnimalCode " \
        "FROM accountstrx t " \
        "LEFT OUTER JOIN accounts srcac ON srcac.ID = t.SourceAccountID " \
        "LEFT OUTER JOIN accounts destac ON destac.ID = t.DestinationAccountID " \
        "LEFT OUTER JOIN ownerdonation od ON od.ID = t.OwnerDonationID " \
        "LEFT OUTER JOIN owner o ON o.ID = od.OwnerID " \
        "LEFT OUTER JOIN animal a ON a.ID = od.AnimalID " \
        "LEFT OUTER JOIN animalcost ac ON ac.ID = t.AnimalCostID " \
        "LEFT OUTER JOIN animal aca ON aca.ID = ac.AnimalID " \
        "WHERE t.TrxDate >= %s AND t.TrxDate <= %s%s " \
        "AND (t.SourceAccountID = %d OR t.DestinationAccountID = %d) " \
        "ORDER BY t.TrxDate, t.ID" % ( dbo.sql_date(datefrom, includeTime=False), dbo.sql_date(dateto, includeTime=False), recfilter, accountid, accountid))
    balance = 0
    if period != "":
        balance = get_balance_fromto_date(dbo, accountid, asm3.i18n.display2python(l, period), datefrom, reconciled)
    else:
        balance = get_balance_to_date(dbo, accountid, datefrom, reconciled)
    for r in rows:
        # Error scenario - this account is both source and destination
        if r.sourceaccountid == accountid and r.destinationaccountid == accountid:
            r.withdrawal = 0
            r.deposit = 0
            r.thisaccount = accountid
            r.thisaccountcode = r.srccode
            r.otheraccount = accountid
            r.otheraccountcode = "<-->"
            r.balance = balance
        # This account is the source - it's a withdrawal
        elif r.sourceaccountid == accountid:
            r.withdrawal = r.amount
            r.deposit = 0
            r.otheraccount = r.destinationaccountid
            r.otheraccountcode = r.destcode
            r.thisaccount = accountid
            r.thisaccountcode = r.srccode
            balance -= r.amount
            r.balance = balance
        # This account is the destination - it's a deposit
        else:
            r.withdrawal = 0
            r.deposit = r.amount
            r.otheraccount = r.sourceaccountid
            r.otheraccountcode = r.srccode
            r.thisaccount = accountid
            r.thisaccountcode = r.destcode
            balance += r.amount
            r.balance = balance
    return rows
       
def get_donation(dbo, did):
    """
    Returns a single donation by id
    """
    return dbo.first_row( dbo.query(get_donation_query(dbo) + "WHERE od.ID = ?", [did]) )

def get_donations_by_ids(dbo, dids):
    """
    Returns multiple donations with a list of ids
    """
    return dbo.query(get_donation_query(dbo) + "WHERE od.ID IN (%s) ORDER BY od.Date" % ",".join(str(x) for x in dids))

def get_movement_donation(dbo, mid):
    """
    Returns the most recent donation with movement id mid
    """
    return dbo.first_row( dbo.query(get_donation_query(dbo) + "WHERE od.MovementID = ? ORDER BY Date DESC, od.ID DESC", [mid]) )

def get_movement_donations(dbo, mid):
    """
    Returns all donations for a movement
    """
    return dbo.query(get_donation_query(dbo) + "WHERE od.MovementID = ? ORDER BY Date DESC, od.ID DESC", [mid])

def get_next_receipt_number(dbo):
    """ Returns the next receipt number for the frontend """
    return asm3.utils.padleft( asm3.utils.cache_sequence(dbo, "receipt", "SELECT MAX(ReceiptNumber) FROM ownerdonation"), 8 )

def get_donations(dbo, offset = "m31"):
    """
    Returns a recordset of donations
    offset is m for received backwards in days, p for due forwards in days
    ID, DONATIONTYPEID, DONATIONNAME, DATE, DATEDUE, DONATION,
    ISGIFTAID, FREQUENCY, FREQUENCYNAME, NEXTCREATED, COMMENTS, OWNERNAME, 
    ANIMALNAME, SHELTERCODE, OWNERID, ANIMALID
    """
    offsetdays = asm3.utils.cint(offset[1:])
    if offset.startswith("m"):
        return dbo.query(get_donation_query(dbo) + " WHERE od.Date >= ? AND od.Date <= ? ORDER BY od.Date DESC", (dbo.today(offsetdays*-1), dbo.today()))
    elif offset.startswith("p"):
        return dbo.query(get_donation_query(dbo) + " WHERE od.DateDue >= ? AND od.DateDue <= ? ORDER BY od.DateDue DESC", (dbo.today(), dbo.today(offsetdays)))
    elif offset.startswith("d"):
        return dbo.query(get_donation_query(dbo) + " WHERE od.Date Is Null AND od.DateDue <= ? ORDER BY od.DateDue", (dbo.today(),))

def get_donations_due_two_dates(dbo, start, end):
    """
    Returns a recordset of due donations between two dates
    ID, DONATIONTYPEID, DONATIONNAME, DATE, DATEDUE, DONATION,
    ISGIFTAID, FREQUENCY, FREQUENCYNAME, NEXTCREATED, COMMENTS, OWNERNAME, 
    ANIMALNAME, SHELTERCODE, OWNERID, ANIMALID
    """
    return dbo.query(get_donation_query(dbo) + \
        "WHERE od.DateDue >= ? AND od.DateDue <= ? AND od.Date Is Null " \
        "ORDER BY od.DateDue DESC", (start, end))

def get_animal_donations(dbo, aid, sort = ASCENDING):
    """
    Returns all of the owner donation records for an animal, along with
    some owner and animal info.
    ID, DONATIONTYPEID, DONATIONNAME, DATE, DATEDUE, DONATION,
    ISGIFTAID, FREQUENCY, FREQUENCYNAME, NEXTCREATED, COMMENTS, OWNERNAME, 
    ANIMALNAME, SHELTERCODE, OWNERID, ANIMALID
    """
    order = "Date DESC, od.ID DESC"
    if sort == ASCENDING:
        order = "Date, od.ID"
    return dbo.query(get_donation_query(dbo) + \
        "WHERE od.AnimalID = ? " \
        "ORDER BY %s" % order, [aid])

def get_person_donations(dbo, oid, sort = ASCENDING):
    """
    Returns all of the owner donation records for an owner, along with some animal info
    ID, DONATIONTYPEID, DONATIONNAME, DATE, DATEDUE, DONATION,
    ISGIFTAID, FREQUENCY, FREQUENCYNAME, NEXTCREATED, COMMENTS, OWNERNAME, 
    ANIMALNAME, SHELTERCODE, OWNERID, ANIMALID
    """
    order = "Date DESC, od.ID DESC"
    if sort == ASCENDING:
        order = "Date, od.ID"
    return dbo.query(get_donation_query(dbo) + \
        "WHERE od.OwnerID = ? " \
        "ORDER BY %s" % order, [oid])

def get_incident_citations(dbo, iid, sort = ASCENDING):
    """
    Returns all of the citation records for an incident, along with
    some owner info.
    ID, CITATIONTYPEID, CITATIONNAME, CITATIONDATE, FINEDUEDATE, FINEPAIDDATE,
    FINEAMOUNT, OWNERNAME, INCIDENTNAME
    """
    order = "oc.CitationDate DESC"
    if sort == ASCENDING:
        order = "oc.CitationDate"
    return dbo.query(get_citation_query(dbo) + \
        "WHERE oc.AnimalControlID = ? " \
        "ORDER BY %s" % order, [iid])

def get_person_citations(dbo, oid, sort = ASCENDING):
    """
    Returns all of the citation records for a person, along with
    some owner info.
    ID, CITATIONTYPEID, CITATIONNAME, CITATIONDATE, FINEDUEDATE, FINEPAIDDATE,
    FINEAMOUNT, OWNERNAME, INCIDENTNAME
    """
    order = "oc.CitationDate DESC"
    if sort == ASCENDING:
        order = "oc.CitationDate"
    return dbo.query(get_citation_query(dbo) + \
        "WHERE oc.OwnerID = ? " \
        "ORDER BY %s" % order, [oid])

def get_unpaid_fines(dbo):
    """
    Returns all of the unpaid fines
    ID, CITATIONTYPEID, CITATIONNAME, CITATIONDATE, FINEDUEDATE, FINEPAIDDATE,
    FINEAMOUNT, OWNERNAME, INCIDENTNAME
    """
    return dbo.query(get_citation_query(dbo) + \
        "WHERE oc.FineDueDate Is Not Null AND oc.FineDueDate <= ? AND oc.FinePaidDate Is Null " \
        "ORDER BY oc.CitationDate DESC", [dbo.today()])

def get_animal_licences(dbo, aid, sort = ASCENDING):
    """
    Returns all of the licence records for an animal, along with
    some owner and animal info.
    ID, LICENCETYPEID, LICENCETYPENAME, LICENCENUMBER, ISSUEDATE, EXPIRYDATE,
    COMMENTS, OWNERNAME, ANIMALNAME, SHELTERCODE, OWNERID, ANIMALID
    """
    order = "ol.IssueDate DESC"
    if sort == ASCENDING:
        order = "ol.IssueDate"
    return dbo.query(get_licence_query(dbo) + \
        "WHERE ol.AnimalID = ? " \
        "ORDER BY %s" % order, [aid])

def get_person_licences(dbo, oid, sort = ASCENDING):
    """
    Returns all of the licence records for a person, along with
    some owner and animal info.
    ID, LICENCETYPEID, LICENCETYPENAME, LICENCENUMBER, ISSUEDATE, EXPIRYDATE,
    COMMENTS, OWNERNAME, ANIMALNAME, SHELTERCODE, OWNERID, ANIMALID
    """
    order = "ol.IssueDate DESC"
    if sort == ASCENDING:
        order = "ol.IssueDate"
    return dbo.query(get_licence_query(dbo) + \
        "WHERE ol.OwnerID = ? " \
        "ORDER BY %s" % order, [oid])

def get_recent_licences(dbo):
    """
    Returns licences issued in the last 30 days
    ID, LICENCETYPEID, LICENCETYPENAME, LICENCENUMBER, ISSUEDATE, EXPIRYDATE,
    COMMENTS, OWNERNAME, ANIMALNAME, SHELTERCODE, OWNERID, ANIMALID
    """
    return dbo.query(get_licence_query(dbo) + \
        "WHERE ol.IssueDate >= ? " \
        "ORDER BY ol.IssueDate DESC", [dbo.today(offset=-30)])

def get_licence_find_simple(dbo, licnum, dummy = 0):
    return dbo.query(get_licence_query(dbo) + \
        "WHERE UPPER(ol.LicenceNumber) LIKE UPPER(?)", [licnum])

def get_licence(dbo, licenceid):
    """
    Returns a single licence by id
    """
    return dbo.first_row( dbo.query(get_licence_query(dbo) + "WHERE ol.ID = ?", [licenceid]) )

def get_licences(dbo, offset = "i31"):
    """
    Returns a recordset of licences 
    offset is i to go backwards on issue date
    or e to go backwards on expiry date 
    """
    offsetdays = asm3.utils.cint(offset[1:])
    if offset.startswith("i"):
        return dbo.query(get_licence_query(dbo) + " WHERE ol.IssueDate >= ? AND ol.IssueDate <= ? ORDER BY ol.IssueDate DESC", 
            (dbo.today(offsetdays*-1), dbo.today()))
    if offset.startswith("e"):
        return dbo.query(get_licence_query(dbo) + " WHERE ol.ExpiryDate >= ? AND ol.ExpiryDate <= ? ORDER BY ol.ExpiryDate DESC", 
            (dbo.today(offsetdays*-1), dbo.today()))

def get_person_vouchers(dbo, personid):
    """
    Returns a list of vouchers for a person
    """
    return dbo.query(get_voucher_query(dbo) + \
        "WHERE ov.OwnerID = ? ORDER BY ov.DateIssued", [personid])

def get_voucher(dbo, voucherid):
    """
    Returns a single voucher record
    """
    return dbo.first_row(dbo.query(get_voucher_query(dbo) + " WHERE ov.ID = ?", [voucherid]))

def get_voucher_find_simple(dbo, vocode, dummy = 0):
    return dbo.query(get_voucher_query(dbo) + \
        "WHERE UPPER(ov.VoucherCode) LIKE UPPER(?)", [vocode])

def get_vouchers(dbo, offset = "i31"):
    """
    Returns a list of vouchers 
    offset is i to go backwards on issue date
    or e to go forwards on expiry date
    or p to go backwards on presented date
    or a for unpresented
    """
    offsetdays = asm3.utils.cint(offset[1:])
    if offset.startswith("a"):
        return dbo.query(get_voucher_query(dbo) + " WHERE ov.DatePresented Is Null ORDER BY ov.DatePresented DESC")
    if offset.startswith("i"):
        return dbo.query(get_voucher_query(dbo) + " WHERE ov.DateIssued >= ? AND ov.DateIssued <= ? ORDER BY ov.DateIssued DESC", 
            (dbo.today(offsetdays*-1), dbo.today()))
    if offset.startswith("p"):
        return dbo.query(get_voucher_query(dbo) + " WHERE ov.DatePresented >= ? AND ov.DatePresented <= ? ORDER BY ov.DatePresented DESC", 
            (dbo.today(offsetdays*-1), dbo.today()))
    if offset.startswith("e"):
        return dbo.query(get_voucher_query(dbo) + " WHERE ov.DateExpired >= ? AND ov.DateExpired <= ? ORDER BY ov.DateExpired DESC", 
            (dbo.today(), dbo.today(offsetdays)))

def insert_donations_from_form(dbo, username, post, donationdate, force_receive = False, personid = 0, animalid = 0, movementid = 0, ignorezero = True):
    """
    Used for post handlers with the payments widget where
    multiple payments can be sent.
    """
    l = dbo.locale
    created = []
    if post["receiptnumber"] == "":
        post.data["receiptnumber"] = get_next_receipt_number(dbo)
    for i in range(1, 100):
        if post.integer("amount%d" % i) == 0 and ignorezero: continue
        if post.integer("donationtype%d" % i) == 0: break # no type means nothing posted for that line, so stop
        due = post["due%d" % i]
        received = post["received%d" % i]
        # If due and received haven't been given, use the passed in date
        # and set it depending on the force_receive flag or config
        if due == "" and received == "":
            due = ""
            received = donationdate
            if not force_receive and asm3.configuration.movement_donations_default_due(dbo):
                due = donationdate
                received = ""
        don_dict = {
            "person"                : str(personid),
            "animal"                : str(animalid),
            "movement"              : str(movementid),
            "type"                  : post["donationtype%d" % i],
            "payment"               : post["payment%d" % i],
            "destaccount"           : post["destaccount%d" % i],
            "frequency"             : "0",
            "quantity"              : post["quantity%d" % i],
            "unitprice"             : post["unitprice%d" % i],
            "amount"                : post["amount%d" % i],
            "due"                   : due,
            "received"              : received,
            "giftaid"               : post["giftaid%d" % i],
            "chequenumber"          : post["chequenumber%d" % i],
            "receiptnumber"         : post["receiptnumber"],
            "fee"                   : post["fee%d" % i],
            "comments"              : post["comments%d" % i],
            "vat"                   : post["vat%d" % i],
            "vatrate"               : post["vatrate%d" % i],
            "vatamount"             : post["vatamount%d" % i]
        }
        created.append(str(insert_donation_from_form(dbo, username, asm3.utils.PostedData(don_dict, l))))
    return ",".join(created)

def insert_donation_from_form(dbo, username, post):
    """
    Creates a payment record from posted form data 
    """
    if post["receiptnumber"] == "":
        post.data["receiptnumber"] = get_next_receipt_number(dbo)
    
    donationid = dbo.insert("ownerdonation", {
        "OwnerID":              post.integer("person"),
        "AnimalID":             post.integer("animal"),
        "MovementID":           post.integer("movement"),
        "DonationTypeID":       post.integer("type"),
        "DonationPaymentID":    post.integer("payment"),
        "Frequency":            post.integer("frequency"),
        "Quantity":             post.integer("quantity"),
        "UnitPrice":            post.integer("unitprice"),
        "Donation":             post.integer("amount"),
        "DateDue":              post.date("due"),
        "Date":                 post.date("received"),
        "NextCreated":          0,
        "ChequeNumber":         post["chequenumber"],
        "ReceiptNumber":        post["receiptnumber"],
        "Fee":                  post.integer("fee"),
        "IsGiftAid":            post.boolean("giftaid"),
        "IsVAT":                post.boolean("vat"),
        "VATRate":              post.floating("vatrate"),
        "VATAmount":            post.integer("vatamount"),
        "Comments":             post["comments"]
    }, username)

    if asm3.configuration.donation_trx_override(dbo):
        update_matching_donation_transaction(dbo, username, donationid, post.integer("destaccount"))
    else:
        update_matching_donation_transaction(dbo, username, donationid)

    check_create_next_donation(dbo, username, donationid)
    asm3.movement.update_movement_donation(dbo, post.integer("movement"))
    return donationid

def update_donation_from_form(dbo, username, post):
    """
    Updates a payment record from posted form data
    """
    donationid = post.integer("donationid")
    if post["receiptnumber"] == "":
        post.data["receiptnumber"] = dbo.query_string("SELECT ReceiptNumber FROM ownerdonation WHERE ID = ?", [donationid])

    receiveddate = dbo.query_date("SELECT Date FROM ownerdonation WHERE ID = ?", [donationid])

    dbo.update("ownerdonation", donationid, {
        "OwnerID":              post.integer("person"),
        "AnimalID":             post.integer("animal"),
        "MovementID":           post.integer("movement"),
        "DonationTypeID":       post.integer("type"),
        "DonationPaymentID":    post.integer("payment"),
        "Frequency":            post.integer("frequency"),
        "Quantity":             post.integer("quantity"),
        "UnitPrice":            post.integer("unitprice"),
        "Donation":             post.integer("amount"),
        "DateDue":              post.date("due"),
        "Date":                 post.date("received"),
        "ChequeNumber":         post["chequenumber"],
        "ReceiptNumber":        post["receiptnumber"],
        "Fee":                  post.integer("fee"),
        "IsGiftAid":            post.boolean("giftaid"),
        "IsVAT":                post.boolean("vat"),
        "VATRate":              post.floating("vatrate"),
        "VATAmount":            post.integer("vatamount"),
        "Comments":             post["comments"]
    }, username)

    if asm3.configuration.donation_trx_override(dbo) and receiveddate is None:
        update_matching_donation_transaction(dbo, username, donationid, post.integer("destaccount"))
    else:
        update_matching_donation_transaction(dbo, username, donationid)

    check_create_next_donation(dbo, username, donationid)
    asm3.movement.update_movement_donation(dbo, post.integer("movement"))

def delete_donation(dbo, username, did):
    """
    Deletes a payment record
    """
    movementid = dbo.query_int("SELECT MovementID FROM ownerdonation WHERE ID = ?", [did])
    dbo.delete("accountstrx", "OwnerDonationID = %d" % did, username) # remove matching trx if exists
    dbo.delete("ownerdonation", did, username)
    asm3.movement.update_movement_donation(dbo, movementid)

def receive_donation(dbo, username, did, chequenumber = "", amount = 0, vat = 0, fee = 0, rawdata = ""):
    """
    Marks a donation received. If any of the optional parameters are passed, they are updated.
    The monetary amounts are expected to be integer currency amounts, not floats.
    """
    if id is None or did == "": return
    row = dbo.first_row(dbo.query("SELECT * FROM ownerdonation WHERE ID = ?", [did]))
    
    d = { "Date": dbo.today(), "AnimalID": row.ANIMALID, "OwnerID": row.OWNERID }
    if fee > 0: d["Fee"] = fee
    if amount > 0: d["Donation"] = amount
    if vat > 0: d["VAT"] = amount
    if chequenumber != "": d["ChequeNumber"] = chequenumber
    d["PaymentProcessorData"] = rawdata
    dbo.update("ownerdonation", did, d, username)

    asm3.audit.edit(dbo, username, "ownerdonation", did, asm3.audit.get_parent_links(row), "receipt %s, id %s: received" % (row.RECEIPTNUMBER, did))
    update_matching_donation_transaction(dbo, username, did)
    check_create_next_donation(dbo, username, did)

def check_create_next_donation(dbo, username, odid):
    """
    Checks to see if a donation is now received and the next in 
    a sequence needs to be created for donations with a frequency 
    """
    asm3.al.debug("Create next donation %d" % odid, "financial.check_create_next_donation", dbo)
    d = dbo.first_row(dbo.query("SELECT * FROM ownerdonation WHERE ID = ?", [odid]))
    if d is None:
        asm3.al.error("No donation found for %d" % odid, "financial.check_create_next_donation", dbo)
        return

    # If we have a frequency > 0, the nextcreated flag isn't set
    # and there's a datereceived and due then we need to create the
    # next donation in the sequence
    if d.DATEDUE is not None and d.DATE is not None and d.FREQUENCY > 0 and d.NEXTCREATED == 0:
        nextdue = d.DATEDUE
        if d.FREQUENCY == WEEKLY:
            nextdue = asm3.i18n.add_days(nextdue, 7)
        elif d.FREQUENCY == FORTNIGHTLY:
            nextdue = asm3.i18n.add_days(nextdue, 14)
        elif d.FREQUENCY == MONTHLY:
            nextdue = asm3.i18n.add_months(nextdue, 1)
        elif d.FREQUENCY == QUARTERLY:
            nextdue = asm3.i18n.add_months(nextdue, 3)
        elif d.FREQUENCY == HALF_YEARLY:
            nextdue = asm3.i18n.add_months(nextdue, 6)
        elif d.FREQUENCY == ANNUALLY:
            nextdue = asm3.i18n.add_years(nextdue, 1)
        asm3.al.debug("Next donation due %s" % str(nextdue), "financial.check_create_next_donation", dbo)

        # Update nextcreated flag for this donation
        dbo.execute("UPDATE ownerdonation SET NextCreated = 1 WHERE ID = ?", [odid])

        # Create the new donation due record
        dbo.insert("ownerdonation", {
            "AnimalID":             d.ANIMALID,
            "OwnerID":              d.OWNERID,
            "MovementID":           d.MOVEMENTID,
            "DonationTypeID":       d.DONATIONTYPEID,
            "DateDue":              nextdue,
            "Date":                 None,
            "Quantity":             d.QUANTITY,
            "UnitPrice":            d.UNITPRICE,
            "Donation":             d.DONATION,
            "IsGiftAid":            d.ISGIFTAID,
            "DonationPaymentID":    d.DONATIONPAYMENTID,
            "Frequency":            d.FREQUENCY,
            "NextCreated":          0,
            "ChequeNumber":         "",
            "ReceiptNumber":        get_next_receipt_number(dbo),
            "IsVAT":                d.ISVAT,
            "VATRate":              d.VATRATE,
            "VATAmount":            d.VATAMOUNT,
            "Comments":             d.COMMENTS
        }, username)

def update_matching_cost_transaction(dbo, username, acid, destinationaccount = 0):
    """
    Creates a matching account transaction for a cost or updates
    an existing trx if it already exists
    """
    # Don't do anything if we aren't creating matching transactions
    if not asm3.configuration.create_cost_trx(dbo): 
        asm3.al.debug("Create cost trx is off, not creating trx.", "financial.update_matching_cost_transaction", dbo)
        return

    # Find the cost record
    ac = dbo.query("SELECT * FROM animalcost WHERE ID = ?", [acid])
    if ac is None or len(ac) == 0:
        asm3.al.error("No matching transaction for %d found in database, bailing" % int(acid), "financial.update_matching_cost_transaction", dbo)
        return
    c = ac[0]

    # If cost paid dates are on and the cost hasn't been paid, don't do anything
    if asm3.configuration.show_cost_paid(dbo) and c.COSTPAIDDATE is None: 
        asm3.al.debug("Cost not paid, not creating trx.", "financial.update_matching_cost_transaction", dbo)
        return

    # Do we already have an existing transaction for this donation?
    # If we do, we only need to check the amounts as it's now the
    # users problem if they picked the wrong cost type/account
    trxid = dbo.query_int("SELECT ID FROM accountstrx WHERE AnimalCostID = ?", [acid])
    if trxid != 0:
        asm3.al.debug("Already have an existing transaction, updating amount to %d" % c.COSTAMOUNT, "financial.update_matching_cost_transaction", dbo)
        dbo.update("accountstrx", trxid, { "Amount": c.COSTAMOUNT })
        return

    # Get the target account for this type of cost
    target = dbo.query_int("SELECT AccountID FROM costtype WHERE ID = ?", [c.COSTTYPEID])
    if target == 0:
        # This shouldn't happen, but we can't go ahead without an account
        asm3.al.error("No target account found for cost type, can't create trx", "financial.update_matching_cost_transaction", dbo)
        return

    # Get the source account if we weren't given one
    source = destinationaccount
    if source == 0:
        source = asm3.configuration.cost_source_account(dbo)
        asm3.al.debug("Source account in config is: %s" % target, "financial.update_matching_cost_transaction", dbo)
        # If no source is configured, use the first bank account on file
        if source == 0:
            source = dbo.query_int("SELECT ID FROM accounts WHERE AccountType = 1")
            asm3.al.debug("Got blank source, getting first bank account: %s" % source, "financial.update_matching_cost_transaction", dbo)
            if source == 0:
                # Shouldn't happen, but we have no bank accounts on file
                asm3.al.error("No bank accounts on file, can't set target for cost trx", "financial.update_matching_cost_transaction", dbo)
                return
        # Has a mapping been created by the user for this cost type
        # to a destination other than the default?
        # TODO: If requested in future possibly, not present right now
        # maps = asm3.configuration.cost_account_mappings(dbo)
        #if str(c["COSTTYPEID"]) in maps:
        #    target = maps[str(c["COSTTYPEID"])]
        #    asm3.al.debug("Found override for costtype %s, got new target account %s" % (str(c["COSTTYPEID"]), str(target)), "financial.update_matching_cost_transaction", dbo)
    # Is the cost for a negative amount? If so, flip the accounts
    # round as this must be a refund and make the amount positive.
    amount = c.COSTAMOUNT
    if amount < 0:
        oldtarget = target
        target = source
        source = oldtarget
        amount = abs(amount)

    trxdate = c.COSTDATE
    if c.COSTPAIDDATE is not None: trxdate = c.COSTPAIDDATE

    # Create the transaction
    tid = dbo.insert("accountstrx", {
        "TrxDate":          trxdate,
        "Description":      c.DESCRIPTION,
        "Reconciled":       0,
        "Amount":           amount,
        "SourceAccountID":  source,
        "DestinationAccountID": target,
        "OwnerDonationID":  0,
        "AnimalCostID":     acid
    }, username)
    asm3.al.debug("Trx created with ID %d" % tid, "financial.update_matching_cost_transaction", dbo)

def update_matching_donation_transaction(dbo, username, odid, destinationaccount = 0):
    """
    Creates a matching account transaction for a donation/payment or updates
    an existing trx if it already exists
    """
    l = dbo.locale
    # Don't do anything if we aren't creating matching transactions
    if not asm3.configuration.create_donation_trx(dbo): 
        asm3.al.debug("Create donation trx is off, not creating trx.", "financial.update_matching_donation_transaction", dbo)
        return

    # Find the donation record
    dr = dbo.query("SELECT * FROM ownerdonation WHERE ID = ?", [odid])
    if dr is None or len(dr) == 0:
        asm3.al.error("No matching transaction for %d found in database, bailing" % int(odid), "financial.update_matching_donation_transaction", dbo)
        return
    d = dr[0]

    # If the donation hasn't been received, don't do anything
    if d.DATE is None: 
        asm3.al.debug("Donation not received, not creating trx.", "financial.update_matching_donation_transaction", dbo)
        return

    # Do we already have an existing transaction for this donation?
    # If we do, we only need to check the amounts as it's now the
    # users problem if they picked the wrong donationtype/account.
    # NOTE: Deliberately choose the first because if a transaction for
    # any handling fee was created, it will have a higher ID while
    # still having the same ownerdonation.ID for display/report purposes.
    trxid = dbo.query_int("SELECT ID FROM accountstrx WHERE OwnerDonationID = ? ORDER BY ID", [odid])
    if trxid != 0:
        asm3.al.debug("Already have an existing transaction, updating amount to %d" % abs(d.DONATION), "financial.update_matching_donation_transaction", dbo)
        dbo.execute("UPDATE accountstrx SET Amount = ? WHERE ID = ?", (abs(d.DONATION), trxid))
        return

    # Get the source account for this type of donation
    source = dbo.query_int("SELECT AccountID FROM donationtype WHERE ID = ?", [d.DONATIONTYPEID])
    if source == 0:
        # This shouldn't happen, but we can't go ahead without an account
        asm3.al.error("No source account found for donation type, can't create trx", "financial.update_matching_donation_transaction", dbo)
        return

    # Get the target account if we weren't given one
    target = destinationaccount
    if target == 0:
        target = asm3.configuration.donation_target_account(dbo)
        asm3.al.debug("Target account in config is: %s" % target, "financial.update_matching_donation_transaction", dbo)
        # If no target is configured, use the first bank account on file
        if target == 0:
            target = dbo.query_int("SELECT ID FROM accounts WHERE AccountType = 1")
            asm3.al.debug("Got blank target, getting first bank account: %s" % target, "financial.update_matching_donation_transaction", dbo)
            if target == 0:
                # Shouldn't happen, but we have no bank accounts on file
                asm3.al.error("No target available for trx. Bailing.", "financial.update_matching_donation_transaction", dbo)
                return

        # Has a mapping been created by the user for this donation type
        # to a destination other than the default?
        maps = asm3.configuration.donation_account_mappings(dbo)
        if str(d.DONATIONTYPEID) in maps:
            target = maps[str(d.DONATIONTYPEID)]
            asm3.al.debug("Found override for donationtype %s, got new target account %s" % (d.DONATIONTYPEID, target), "financial.update_matching_donation_transaction", dbo)
            if not asm3.utils.is_numeric(target):
                asm3.al.error("Target account '%s' is not valid, falling back to default from config" % target, "financial.update_matching_donation_transaction", dbo)
                target = asm3.configuration.donation_target_account(dbo)

    # Is the donation for a negative amount? If so, flip the accounts
    # round as this is a refund and make the amount positive.
    amount = d.DONATION
    isrefund = False
    if amount < 0:
        oldtarget = target
        target = source
        source = oldtarget
        amount = abs(amount)
        isrefund = True

    # Is there a tax portion? If so, remove it from the amount before creating
    # the transaction as we're going to do a separate transaction for the tax
    if d.VATAMOUNT > 0 and not isrefund:
        amount -= d.VATAMOUNT

    # Create the transaction
    tid = dbo.insert("accountstrx", {
        "TrxDate":              d.DATE,
        "Description":          d.COMMENTS,
        "Reconciled":           0,
        "Amount":               amount,
        "SourceAccountID":      source,
        "DestinationAccountID": target,
        "AnimalCostID":         0,
        "OwnerDonationID":      odid
    }, username)
    asm3.al.debug("Trx created with ID %d" % int(tid), "financial.update_matching_donation_transaction", dbo)

    # Is there a vat/tax portion of this payment that we need to create a transaction for?
    if d.VATAMOUNT and d.VATAMOUNT > 0 and not isrefund:
        vatac = asm3.configuration.donation_vat_account(dbo)
        if 0 == dbo.query_int("SELECT ID FROM accounts WHERE ID = ?", [vatac]):
            vatac = dbo.query_int("SELECT ID FROM accounts WHERE AccountType=? ORDER BY ID", [INCOME])
            asm3.al.error("No vat account configured, falling back to first income ac %s" % vatac, "financial.update_matching_donation_transaction", dbo)
        tid = dbo.insert("accountstrx", {
            "TrxDate":              d.DATE,
            "Description":          asm3.i18n._("Sales Tax", l),
            "Reconciled":           0,
            "Amount":               d.VATAMOUNT,
            "SourceAccountID":      vatac,
            "DestinationAccountID": target,
            "AnimalCostID":         0,
            "OwnerDonationID":      odid
        }, username)
        asm3.al.debug("VAT trx created with ID %d" % int(tid), "financial.update_matching_donation_transaction", dbo)

    # Is there a fee on this payment that we need to create a transaction for?
    if d.FEE and d.FEE > 0 and not isrefund:
        feeac = asm3.configuration.donation_fee_account(dbo)
        if 0 == dbo.query_int("SELECT ID FROM accounts WHERE ID = ?", [feeac]):
            feeac = dbo.query_int("SELECT ID FROM accounts WHERE AccountType=? ORDER BY ID", [EXPENSE])
            asm3.al.error("No expense account configured, falling back to first expense ac %s" % feeac, "financial.update_matching_donation_transaction", dbo)
        tid = dbo.insert("accountstrx", {
            "TrxDate":              d.DATE,
            "Description":          asm3.i18n._("Transaction Fee", l),
            "Reconciled":           0,
            "Amount":               d.FEE,
            "SourceAccountID":      target,
            "DestinationAccountID": feeac,
            "AnimalCostID":         0,
            "OwnerDonationID":      odid
        }, username)
        asm3.al.debug("Fee trx created with ID %d" % int(tid), "financial.update_matching_donation_transaction", dbo)

def insert_account_from_costtype(dbo, name, desc):
    """
    Creates an account from a donation type record
    """
    l = dbo.locale
    acode = asm3.i18n._("Expense::", l) + name.replace(" ", "")
    return dbo.insert("accounts", {
        "Code":             acode,
        "Archived":         0,
        "AccountType":      EXPENSE,
        "Description":      desc,
        "DonationTypeID":   0, # ASM2_COMPATIBILITY
        "CostTypeID":       0 # ASM2_COMPATIBILITY
    }, "system")

def insert_account_from_donationtype(dbo, name, desc):
    """
    Creates an account from a donation type record
    """
    l = dbo.locale
    acode = asm3.i18n._("Income::", l) + name.replace(" ", "")
    return dbo.insert("accounts", {
        "Code":             acode,
        "Archived":         0,
        "AccountType":      INCOME,
        "Description":      desc,
        "DonationTypeID":   0, # ASM2_COMPATIBILITY
        "CostTypeID":       0 # ASM2_COMPATIBILITY
    }, "system")

def insert_account_roles(dbo, username, accountid, post):
    """
    accountid:  the account we're setting edit and view roles
    post:       a post object containing viewroles and editroles members
    """

    dbo.delete("accountsrole", "AccountID=%d" % accountid)

    for rid in post.integer_list("viewroles"):
        dbo.insert("accountsrole", {
            "AccountID":    accountid,
            "RoleID":       rid,
            "CanView":      1,
            "CanEdit":      0
        }, generateID=False)

    for rid in post.integer_list("editroles"):
        if rid in post.integer_list("viewroles"):
            dbo.update("accountsrole", "AccountID=%d AND RoleID=%d" % (accountid, rid), {
                "CanEdit":  1
            })
        else:
            dbo.insert("accountsrole", {
                "AccountID":    accountid,
                "RoleID":       rid,
                "CanView":      0,
                "CanEdit":      1
            }, generateID=False)

def insert_account_from_form(dbo, username, post):
    """
    Creates an account from posted form data 
    """
    l = dbo.locale

    if post["code"] == "":
        raise asm3.utils.ASMValidationError(asm3.i18n._("Account code cannot be blank.", l))
    if 0 != dbo.query_int("SELECT COUNT(*) FROM accounts WHERE Code Like ?", [post["code"]]):
        raise asm3.utils.ASMValidationError(asm3.i18n._("Account code '{0}' has already been used.", l).format(post["code"]))

    accountid = dbo.insert("accounts", {
        "Code":             post["code"],
        "Archived":         post.integer("archived"),
        "AccountType":      post.integer("type"),
        "Description":      post["description"],
        "DonationTypeID":   0, # ASM2_COMPATIBILITY
        "CostTypeID":       0 # ASM2_COMPATIBILITY
    }, username)

    insert_account_roles(dbo, username, accountid, post)

    return accountid

def update_account_from_form(dbo, username, post):
    """
    Updates an account from posted form data
    """
    l = dbo.locale
    accountid = post.integer("accountid")
    if post["code"] == "":
        raise asm3.utils.ASMValidationError(asm3.i18n._("Account code cannot be blank.", l))

    if 0 != dbo.query_int("SELECT COUNT(*) FROM accounts WHERE Code Like ? AND ID <> ?", (post["code"], accountid)):
        raise asm3.utils.ASMValidationError(asm3.i18n._("Account code '{0}' has already been used.", l).format(post["code"]))

    dbo.update("accounts", accountid, {
        "Code":             post["code"],
        "AccountType":      post.integer("type"),
        "Archived":         post.integer("archived"),
        "Description":      post["description"]
    }, username)

    insert_account_roles(dbo, username, accountid, post)

def delete_account(dbo, username, aid):
    """
    Deletes an account
    """
    dbo.delete("accountstrx", "SourceAccountID=%d OR DestinationAccountID=%d" % (aid, aid), username)
    dbo.delete("accountsrole", "AccountID=%d" % aid)
    dbo.delete("accounts", aid, username)

def insert_trx_from_form(dbo, username, post):
    """
    Creates a transaction from posted form data
    """
    l = dbo.locale
    amount = 0
    source = 0
    target = 0
    deposit = post.integer("deposit")
    withdrawal = post.integer("withdrawal")
    account = post.integer("accountid")
    other = get_account_id(dbo, post["otheraccount"])

    if other == 0:
        raise asm3.utils.ASMValidationError(asm3.i18n._("Account code '{0}' is not valid.", l).format(post["otheraccount"]))
    if post.date("trxdate") is None:
        raise asm3.utils.ASMValidationError(asm3.i18n._("Date '{0}' is not valid.", l).format(post["trxdate"]))

    if deposit > 0:
        amount = deposit
        source = other
        target = account
    else:
        amount = withdrawal
        source = account
        target = other

    return dbo.insert("accountstrx", {
        "TrxDate":              post.date("trxdate"),
        "Description":          post["description"],
        "Reconciled":           post.boolean("reconciled"),
        "Amount":               amount,
        "SourceAccountID":      source,
        "DestinationAccountID": target,
        "OwnerDonationID":      0
    }, username)

def update_trx_from_form(dbo, username, post):
    """
    Updates a transaction from posted form data
    """
    l = dbo.locale
    amount = 0
    source = 0
    target = 0
    deposit = post.integer("deposit")
    withdrawal = post.integer("withdrawal")
    account = post.integer("accountid")
    trxid = post.integer("trxid")
    other = get_account_id(dbo, post["otheraccount"])

    if other == 0:
        raise asm3.utils.ASMValidationError(asm3.i18n._("Account code '{0}' is not valid.", l).format(post["otheraccount"]))
    if deposit > 0:
        amount = deposit
        source = other
        target = account
    else:
        amount = withdrawal
        source = account
        target = other

    return dbo.update("accountstrx", trxid, {
        "TrxDate":              post.date("trxdate"),
        "Description":          post["description"],
        "Reconciled":           post.boolean("reconciled"),
        "Amount":               amount,
        "SourceAccountID":      source,
        "DestinationAccountID": target
    }, username)

def delete_trx(dbo, username, tid):
    """
    Deletes a transaction
    """
    dbo.delete("accountstrx", tid, username)

def insert_voucher_from_form(dbo, username, post):
    """
    Creates a voucher record from posted form data 
    """
    return dbo.insert("ownervoucher", {
        "AnimalID":     post.integer("animal"),
        "OwnerID":      post.integer("person"),
        "VoucherID":    post.integer("type"),
        "VoucherCode":  post["vouchercode"],
        "DateIssued":   post.date("issued"),
        "DateExpired":  post.date("expires"),
        "DatePresented": post.date("presented"),
        "Value":        post.integer("amount"),
        "Comments":     post["comments"]
    }, username)

def update_voucher_from_form(dbo, username, post):
    """
    Updates a voucher record from posted form data
    """
    dbo.update("ownervoucher", post.integer("voucherid"), {
        "AnimalID":      post.integer("animal"),
        "OwnerID":      post.integer("person"),
        "VoucherID":    post.integer("type"),
        "VoucherCode":  post["vouchercode"],
        "DateIssued":   post.date("issued"),
        "DateExpired":  post.date("expires"),
        "DatePresented": post.date("presented"),
        "Value":        post.integer("amount"),
        "Comments":     post["comments"]
    }, username)

def delete_voucher(dbo, username, vid):
    """
    Deletes a voucher record
    """
    dbo.delete("ownervoucher", vid, username)

def insert_citation_from_form(dbo, username, post):
    """
    Creates a citation record from posted form data 
    """
    return dbo.insert("ownercitation", {
        "OwnerID":              post.integer("person"),
        "AnimalControlID":      post.integer("incident"),
        "CitationTypeID":       post.integer("type"),
        "CitationDate":         post.date("citationdate"),
        "FineAmount":           post.integer("fineamount"),
        "FineDueDate":          post.date("finedue"),
        "FinePaidDate":         post.date("finepaid"),
        "Comments":             post["comments"]
    }, username)

def update_citation_from_form(dbo, username, post):
    """
    Updates a citation record from posted form data
    """
    dbo.update("ownercitation", post.integer("citationid"), {
        "CitationTypeID":       post.integer("type"),
        "CitationDate":         post.date("citationdate"),
        "FineAmount":           post.integer("fineamount"),
        "FineDueDate":          post.date("finedue"),
        "FinePaidDate":         post.date("finepaid"),
        "Comments":             post["comments"]
    }, username)

def delete_citation(dbo, username, cid):
    """
    Deletes a citation record
    """
    dbo.delete("ownercitation", cid, username)

def insert_licence_from_form(dbo, username, post):
    """
    Creates a licence record from posted form data 
    """
    l = dbo.locale
    if asm3.configuration.unique_licence_numbers(dbo) and 0 != dbo.query_int("SELECT COUNT(*) FROM ownerlicence WHERE LicenceNumber = ?", [post["number"]]):
        raise asm3.utils.ASMValidationError(asm3.i18n._("License number '{0}' has already been issued.", l).format(post["number"]))
    if post.date("issuedate") is None or post.date("expirydate") is None:
        raise asm3.utils.ASMValidationError(asm3.i18n._("Issue date and expiry date must be valid dates.", l))

    return dbo.insert("ownerlicence", {
        "OwnerID":          post.integer("person"),
        "AnimalID":         post.integer("animal"),
        "LicenceTypeID":    post.integer("type"),
        "LicenceNumber":    post["number"],
        "LicenceFee":       post.integer("fee"),
        "IssueDate":        post.date("issuedate"),
        "ExpiryDate":       post.date("expirydate"),
        "Comments":         post["comments"]
    }, username)

def update_licence_from_form(dbo, username, post):
    """
    Updates a licence record from posted form data
    """
    l = dbo.locale
    licenceid = post.integer("licenceid")
    if asm3.configuration.unique_licence_numbers(dbo) and 0 != dbo.query_int("SELECT COUNT(*) FROM ownerlicence WHERE LicenceNumber = ? AND ID <> ?", (post["number"], licenceid)):
        raise asm3.utils.ASMValidationError(asm3.i18n._("License number '{0}' has already been issued.", l).format(post["number"]))
    if post.date("issuedate") is None or post.date("expirydate") is None:
        raise asm3.utils.ASMValidationError(asm3.i18n._("Issue date and expiry date must be valid dates.", l))

    dbo.update("ownerlicence", licenceid, {
        "OwnerID":          post.integer("person"),
        "AnimalID":         post.integer("animal"),
        "LicenceTypeID":    post.integer("type"),
        "LicenceNumber":    post["number"],
        "LicenceFee":       post.integer("fee"),
        "IssueDate":        post.date("issuedate"),
        "ExpiryDate":       post.date("expirydate"),
        "Comments":         post["comments"]
    }, username)

def delete_licence(dbo, username, lid):
    """
    Deletes a licence record
    """
    dbo.delete("ownerlicence", lid, username)

def get_payment_processor(dbo, name):
    """
    Returns a new payment processor object for name
    """
    if name == "paypal": 
        return asm3.paymentprocessor.paypal.PayPal(dbo)
    elif name == "stripe":
        return asm3.paymentprocessor.stripeh.Stripe(dbo)
    elif name == "cardcom":
        return asm3.paymentprocessor.cardcom.Cardcom(dbo)
    else:
        raise KeyError("No payment processor available for '%s'" % name)

def giftaid_spreadsheet(dbo, path, fromdate, todate):
    """
    Generates an HMRC giftaid spreadsheet in their ODS format. The template
    is stored in src/static/docs/giftaid.ods
    path: The path to the ASM installation
    fromdate: Python date, the date to include donations from
    todate: Python date, the date to include donations to
    """
    def housenumber(s):
        """
        If the first word of the address starts with a number, return
        that as the house number, otherwise use the first line
        """
        houseno = ""
        lines = s.strip().split("\n")
        if len(lines) > 0:
            bits = lines[0].strip().split(" ")
            if len(bits) > 0 and len(bits[0]) > 0 and asm3.utils.cint(bits[0][0]) > 0:
                houseno = bits[0]
            else:
                houseno = lines[0]
        return houseno

    def xmlescape(s):
        return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    # Get the zip file containing our tax year template and load
    # it into an in-memory file
    try:
        # Load the content.xml file from the template ods
        templateods = path + "static/docs/giftaid.ods"
        content = asm3.utils.bytes2str(asm3.utils.zip_extract(templateods, "content.xml"))

        dons = dbo.query("SELECT od.Date AS DonationDate, od.Donation AS DonationAmount, o.* " \
            "FROM ownerdonation od " \
            "INNER JOIN owner o ON od.OwnerID = o.ID " \
            "WHERE od.IsGiftAid = 1 AND od.Date Is Not Null AND " \
            "od.Date >= ? AND od.Date <= ? ORDER BY od.Date", (fromdate, todate))
        asm3.al.debug("got %d giftaid donations for %s -> %s" % (len(dons), str(fromdate), str(todate)), "financial.giftaid_spreadsheet", dbo)

        # Insert them into the content.xml
        # We just replace the first occurrence each time
        subearly = False
        dontotal = 0
        for d in dons:
            if not subearly:
                # This is the date field at the top, turn it into a date
                subearly = True
                content = content.replace("table:style-name=\"ce21\" office:value-type=\"string\">", 
                    "table:style-name=\"ce36\" office:value-type=\"date\" office:date-value=\"%s\">" % \
                    asm3.i18n.format_date(d.DONATIONDATE, "%Y-%m-%d" ))
                content = content.replace("DONEARLIESTDONATION", asm3.i18n.format_date(d.DONATIONDATE, "%d/%m/%y"))
            content = content.replace("DONTITLE", xmlescape(d.OWNERTITLE), 1)
            content = content.replace("DONFIRSTNAME", xmlescape(d.OWNERFORENAMES), 1)
            content = content.replace("DONLASTNAME", xmlescape(d.OWNERSURNAME), 1)
            content = content.replace("DONHOUSENUMBER", xmlescape(housenumber(d.OWNERADDRESS)), 1)
            content = content.replace("DONPOSTCODE", xmlescape(d.OWNERPOSTCODE), 1)
            content = content.replace("DONAGGREGATE", "", 1)
            content = content.replace("DONSPONSOR", "", 1)
            # Switch the string date format to a real date with the correct value
            content = content.replace("table:style-name=\"ce36\" office:value-type=\"string\">", 
                "table:style-name=\"ce36\" office:value-type=\"date\" office:date-value=\"%s\">" % \
                asm3.i18n.format_date(d.DONATIONDATE, "%Y-%m-%d"), 1)
            content = content.replace("DONDATE", asm3.i18n.format_date(d.DONATIONDATE, "%d/%m/%y"), 1)
            donamt = str(float(d.DONATIONAMOUNT) / 100)
            dontotal += float(d.DONATIONAMOUNT) / 100
            content = content.replace("<text:p>54,321.00</text:p>", "<text:p>" + donamt + "</text:p>", 1)
            content = content.replace("office:value=\"54321\"", "office:value=\"" + donamt + "\"", 1)

        # Clear out anything remaining
        content = content.replace("DONTITLE", "")
        content = content.replace("DONFIRSTNAME", "")
        content = content.replace("DONLASTNAME", "")
        content = content.replace("DONHOUSENUMBER", "")
        content = content.replace("DONPOSTCODE", "")
        content = content.replace("DONAGGREGATE", "")
        content = content.replace("DONSPONSOR", "")
        content = content.replace("DONDATE", "")
        content = content.replace("<text:p>54,321.00</text:p>", "<text:p></text:p>")
        content = content.replace("office:value=\"54321\"", "office:value=\"\"")

        # Update the total at the top
        content = content.replace("54,321,000.00</text:p>", str(dontotal) + "</text:p>", 1)
        content = content.replace("office:value=\"54321000\"", "office:value=\"" + str(dontotal) + "\"", 1)

        # Update the file and return the replacement zip 
        return asm3.utils.zip_replace(templateods, "content.xml", asm3.utils.str2bytes(content))

    except Exception as zderr:
        asm3.al.error("failed generating spreadsheet: %s" % str(zderr), "financial.giftaid_spreadsheet", dbo, sys.exc_info())
        raise asm3.utils.ASMError("Failed generating spreadsheet: %s" % str(zderr))

