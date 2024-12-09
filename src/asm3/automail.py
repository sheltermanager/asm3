
import asm3.al
import asm3.clinic
import asm3.configuration
import asm3.i18n
import asm3.log
import asm3.medical
import asm3.utils
import asm3.wordprocessor

from asm3.typehints import datetime, Database, Results

"""
This module contains all functions that automatically email groups of people.
(NOTE: people - not users, there are some other areas such as messages and diary that email users)
"""

def send_all(dbo: Database) -> None:
    """
    Single function for the batch to call, checks and sends all automated emails
    """
    print("Sending all")
    adopter_followup(dbo)
    vaccination_followup(dbo)
    clinic_reminder(dbo)
    due_payment(dbo)
    fosterer_weekly(dbo)
    licence_reminder(dbo)

def _send_email_from_template(dbo: Database, to: str, subject: str, body: str,
                             logtypeid: int = -1, loglinktypeid = asm3.log.PERSON, 
                             loglinkid: int = 0, logmsg = "", user = "system") -> None:
    """
    Helper function to send an email from an email template, handling tokens 
    and recording a system message in the log.
    to: The to address (cc, bcc and subject will be looked up from tokens)
    subject: The default subject if there's no {{SUBJECT X}} token in the body
    body: The body of the email as generated from wordprocessor.generate_X_doc
    logtypeid: The log type to use. -1 uses the system log type, 0 disables log writing.
    loglinktypeid: The log link type (usually person)
    loglinkid: The link id to use for the log.
    logmsg: The log message
    """
    fromadd = asm3.configuration.email(dbo)
    mt = asm3.wordprocessor.extract_mail_tokens(body)
    cc = mt["CC"] or ""
    bcc = mt["BCC"] or ""
    subject = mt["SUBJECT"] or subject
    try:
        asm3.utils.send_email(dbo, fromadd, to, cc, bcc, subject, body, "html")
        if asm3.configuration.audit_on_send_email(dbo): 
            asm3.audit.email(dbo, user, fromadd, to, cc, bcc, subject, body)
        if logtypeid == -1: logtypeid = asm3.configuration.system_log_type(dbo)
        if logtypeid > 0:
            asm3.log.add_log(dbo, user, loglinktypeid, loglinkid, logtypeid, logmsg)
    except Exception as err:
        asm3.al.error(f"failed sending message '{subject}' to '{to}': {err}", "automail._send_email_from_template", dbo)

def _valid_template(dbo: Database, dtid: int) -> bool:
    """ Returns True if dtid is a valid document template that exists """
    if 0 == dbo.query_int("SELECT COUNT(*) FROM templatedocument WHERE ID=?", [dtid]):
        asm3.al.error(f"invalid document template {dtid}", "automail._valid_template", dbo)
        return False
    return True

def _adopter_followup_query(dbo: Database, cutoff: datetime) -> Results:
    followupspecies = asm3.configuration.email_adopter_followup_species(dbo)
    return dbo.query("SELECT m.ID, m.OwnerID, o.EmailAddress " \
        "FROM adoption m " \
        "INNER JOIN animal a ON a.ID = m.AnimalID " \
        "INNER JOIN owner o ON o.ID = m.OwnerID " \
        "WHERE m.MovementType=1 AND m.MovementDate=? AND " \
        "a.DeceasedDate Is Null AND m.ReturnDate Is Null AND " \
        f"a.SpeciesID IN ({followupspecies}) " \
        "ORDER BY m.ID", [ cutoff ])

def adopter_followup(dbo: Database, user = "system") -> None:
    """
    Finds all people who adopted an animal X days ago and sends them 
    a followup email using the configured template.
    Filters out dead and returned animals.
    """
    l = dbo.locale
    if not asm3.configuration.email_adopter_followup(dbo): 
        asm3.al.debug("EmailAdopterFollowup option set to No", "automail.adopter_followup", dbo)
        return
    
    days = asm3.configuration.email_adopter_followup_days(dbo)
    cutoff = dbo.today(offset = days*-1)
    dtid = asm3.configuration.email_adopter_followup_template(dbo)
    asm3.al.debug(f"adopter followup: {days} days, email template {dtid}", "automail.adopter_followup", dbo)
    if not _valid_template(dbo, dtid): return

    rows = _adopter_followup_query(dbo, cutoff)
    for r in rows:
        body = asm3.wordprocessor.generate_movement_doc(dbo, dtid, r.ID, user)
        _send_email_from_template(dbo, r.EMAILADDRESS, asm3.i18n._("Adoption Followup", l), body, loglinkid=r.OWNERID, logmsg=f"AF01:{r.ID}")

    asm3.al.info(f"Sent {len(rows)} adopter followup emails.", "automail.adopter_followup", dbo)

def _vaccination_followup_query(dbo: Database, cutoff: datetime) -> Results:
    return dbo.query("SELECT a.ID, a.OwnerID, o.EmailAddress " \
        "FROM animal a " \
        "INNER JOIN owner o ON o.ID = a.OwnerID " \
        "INNER JOIN animalvaccination v ON v.AnimalID = a.ID " \
        "WHERE a.ActiveMovementType=1 AND v.DateRequired=? AND " \
        "a.DeceasedDate Is Null " \
        "UNION SELECT a.ID, a.OwnerID, o.EmailAddress " \
        "FROM animal a " \
        "INNER JOIN owner o ON o.ID = a.OwnerID " \
        "INNER JOIN animalvaccination v ON v.AnimalID = a.ID " \
        "WHERE v.DateRequired=? AND a.NonShelterAnimal = 1 " \
        "AND a.DeceasedDate Is Null " \
        "ORDER BY a.ID", [ cutoff, cutoff ])

def vaccination_followup(dbo: Database, user = "system") -> None:
    """
    Finds all off site animals with a vaccination due in the next X days and sends the owner
    a followup email using the configured template.
    Filters out dead and returned animals.
    """
    l = dbo.locale
    if not asm3.configuration.email_vaccination_followup(dbo):
        asm3.al.debug("EmailVaccinationFollowup option set to No", "automail.vaccination_followup", dbo)
        return
    days = asm3.configuration.email_vaccination_followup_days(dbo)
    cutoff = dbo.today(offset = days*-1)
    dtid = asm3.configuration.email_vaccination_followup_template(dbo)
    asm3.al.debug(f"vaccination followup: {days} days, email template {dtid}", "automail.vaccination_followup", dbo)
    if not _valid_template(dbo, dtid): return
    rows = _vaccination_followup_query(dbo, cutoff)
    for r in rows:
        body = asm3.wordprocessor.generate_animal_doc(dbo, dtid, r.ID, user)
        _send_email_from_template(dbo, r.EMAILADDRESS, asm3.i18n._("Vaccination Followup", l), body, loglinkid=r.OWNERID, logmsg=f"AF01:{r.ID}")
    asm3.al.info(f"Sent {len(rows)} vaccintion followup emails.", "automail.vaccination_followup", dbo)

def _clinic_reminder_query(dbo: Database, cutoff: datetime) -> Results:
    cutoff2 = asm3.i18n.add_days(cutoff, 1)
    return dbo.query("SELECT ca.ID, ca.OwnerID, o.EmailAddress " \
        "FROM clinicappointment ca " \
        "INNER JOIN owner o ON o.ID = ca.OwnerID " \
        "WHERE ca.DateTime >= ? AND ca.DateTime < ? AND ca.Status = 0 " \
        "ORDER BY ca.ID", [cutoff, cutoff2])

def clinic_reminder(dbo: Database, user = "system") -> None:
    """
    Finds all people who have a clinic appointment in X days and sends
    them a reminder email using the configured template.
    """
    l = dbo.locale
    if not asm3.configuration.email_clinic_reminder(dbo):
        asm3.al.debug("EmailClinicReminder option set to No", "automail.clinic_reminder", dbo)
        return

    days = asm3.configuration.email_clinic_reminder_days(dbo)
    cutoff = dbo.today(offset = days)
    dtid = asm3.configuration.email_clinic_reminder_template(dbo)
    asm3.al.debug(f"clinic reminder: {days} days, email template {dtid}", "automail.clinic_reminder", dbo)
    if not _valid_template(dbo, dtid): return

    rows = _clinic_reminder_query(dbo, cutoff)
    for r in rows:
        body = asm3.wordprocessor.generate_clinic_doc(dbo, dtid, r.ID, user)
        _send_email_from_template(dbo, r.EMAILADDRESS, asm3.i18n._("Clinic Reminder", l), body, loglinkid=r.OWNERID, logmsg=f"CR01:{r.ID}")

    asm3.al.info(f"Sent {len(rows)} clinic reminder emails.", "automail.clinic_reminder", dbo)

def _due_payment_query(dbo: Database, cutoff: datetime) -> Results:
    return dbo.query("SELECT od.ID, od.OwnerID, o.EmailAddress " \
        "FROM ownerdonation od " \
        "INNER JOIN owner o ON o.ID = od.OwnerID " \
        "WHERE od.Date Is Null AND od.DateDue = ? " \
        "ORDER BY od.ID", [cutoff])

def due_payment(dbo: Database, user = "system") -> None:
    """
    Finds all people who have a payment due in X days and sends
    them a reminder email using the configured template.
    """
    l = dbo.locale
    if not asm3.configuration.email_due_payment(dbo):
        asm3.al.debug("EmailDuePayment option set to No", "automail.due_payment", dbo)
        return

    days = asm3.configuration.email_due_payment_days(dbo)
    cutoff = dbo.today(offset = days)
    dtid = asm3.configuration.email_due_payment_template(dbo)
    asm3.al.debug(f"due payment: {days} days, email template {dtid}", "automail.due_payment", dbo)
    if not _valid_template(dbo, dtid): return

    rows = _due_payment_query(dbo, cutoff)
    for r in rows:
        body = asm3.wordprocessor.generate_donation_doc(dbo, dtid, [ r.ID ], user)
        _send_email_from_template(dbo, r.EMAILADDRESS, asm3.i18n._("Payment Due", l), body, loglinkid=r.OWNERID, logmsg=f"DP01:{r.ID}")

    asm3.al.info(f"Sent {len(rows)} due payment emails.", "automail.due_payment", dbo)

def _fosterer_weekly_activefosterers(dbo: Database):
    return dbo.query("SELECT ID, OwnerName, EmailAddress FROM owner " \
        "WHERE EmailAddress <> '' AND EXISTS(SELECT OwnerID FROM adoption WHERE OwnerID = owner.ID AND MovementType = 2 AND MovementDate <= ? " \
        "AND (ReturnDate Is Null OR ReturnDate > ?)) ORDER BY OwnerName", ( dbo.today(), dbo.today() ))

def _fosterer_weekly_animals(dbo: Database, personid: int):
    return dbo.query("SELECT a.AnimalName, a.ShelterCode, x.Sex, a.SpeciesID, s.SpeciesName, a.BreedName, " \
        "a.AnimalAge, a.DateOfBirth, a.Neutered, a.Identichipped, a.IdentichipNumber, " \
        "m.AnimalID, m.MovementDate " \
        "FROM adoption m " \
        "INNER JOIN animal a ON a.ID = m.AnimalID " \
        "LEFT OUTER JOIN species s ON s.ID = a.SpeciesID " \
        "LEFT OUTER JOIN lksex x ON x.ID = a.Sex " \
        "WHERE m.OwnerID = ? AND MovementType = 2 " \
        "AND MovementDate <= ? AND a.DeceasedDate Is Null " \
        "AND (ReturnDate Is Null OR ReturnDate > ?) ORDER BY MovementDate", ( personid, dbo.today(), dbo.today() ))

def fosterer_weekly(dbo: Database, user = "system") -> None:
    """
    Finds all people on file with at least 1 active foster, then constructs an email 
    containing any info on overdue medical items and items due in the current week. 
    Intended to be sent as part of the overnight batch on the first day of the week.
    Unlike the other functions in this module, this one pre-dates email templates and
    does not use them, instead allowing the user to configure some extra text to be included.
    """
    l = dbo.locale

    # If this option is not turned on, bail out
    if not asm3.configuration.fosterer_emails(dbo): 
        asm3.al.debug("FostererEmails configuration option is set to No", "automail.fosterer_weekly", dbo)
        return

    # Check the day of the week, (default is 0 for monday)
    sendday = asm3.configuration.fosterer_email_send_day(dbo)
    if dbo.now().weekday() != sendday:
        asm3.al.debug(f"now.weekday != {sendday}: no need to send fosterer emails", "automail.fosterer_weekly", dbo)
        return

    # Custom message and reply to if set
    msg = asm3.configuration.fosterer_emails_msg(dbo)
    replyto = asm3.configuration.fosterer_emails_reply_to(dbo)
    if replyto == "": replyto = asm3.configuration.email(dbo)

    # Number of days to go back when looking for overdue medical items (negative integer, default -30)
    overduedays = asm3.configuration.fosterer_email_overdue_days(dbo)
    asm3.al.debug("go back %s days when considering overdue medical items" % overduedays, "automail.fosterer_weekly", dbo)

    activefosterers = _fosterer_weekly_activefosterers(dbo)
    asm3.al.debug("%d active fosterers found" % len(activefosterers), "automail.fosterer_weekly", dbo)

    def pb(l, s):
        l.append("<p><b>%s</b></p>" % s)
    def br(l, s):
        l.append("%s<br>" % s)
    def brb(l, s):
        l.append("<b>%s</b><br>" % s)

    for f in activefosterers:
        lines = [ ]
        if msg != "":
            lines.append(msg)
            lines.append("<hr/>")

        animals = _fosterer_weekly_animals(dbo, f.ID)
        asm3.al.debug("%d animals found for fosterer '%s'" % (len(animals), f.OWNERNAME), "automail.fosterer_weekly", dbo)

        hasmedicaldue = False
        for a in animals:
            pb(lines, "%s - %s" % (a.ANIMALNAME, a.SHELTERCODE) )
            lines.append("<p>")
            br(lines, asm3.i18n._("{0} {1} {2} aged {3}", l).format(a.SEX, a.BREEDNAME, a.SPECIESNAME, a.ANIMALAGE))
            br(lines, asm3.i18n._("Fostered to {0} since {1}", l).format( f.OWNERNAME, asm3.i18n.python2display(l, a.MOVEMENTDATE) ))
            
            if a.DATEOFBIRTH < dbo.today(offset=-182) and a.NEUTERED == 0 and a.SPECIESID in (1, 2):
                brb(lines, asm3.i18n._("WARNING: This animal is over 6 months old and has not been neutered/spayed", l))

            if a.IDENTICHIPPED == 0 or (a.IDENTICHIPPED == 1 and a.IDENTICHIPNUMBER == "") and a.SPECIESID in (1, 2):
                brb(lines, asm3.i18n._("WARNING: This animal has not been microchipped", l))
            lines.append("</p>")

            overdue = asm3.medical.get_combined_due(dbo, a.ANIMALID, dbo.today(offset=overduedays), dbo.today(offset=-1))
            if len(overdue) > 0:
                hasmedicaldue = True
                pb(lines, asm3.i18n._("Overdue medical items", l))
                lines.append("<p>")
                for m in overdue:
                    br(lines, "{0}: {1} {2} {3}/{4} {5}".format( asm3.i18n.python2display(l, m.DATEREQUIRED), \
                        m.TREATMENTNAME, m.DOSAGE, m.TREATMENTNUMBER, m.TOTALTREATMENTS, m.COMMENTS ))
                lines.append("</p>")

            nextdue = asm3.medical.get_combined_due(dbo, a.ANIMALID, dbo.today(), dbo.today(offset=7))
            if len(nextdue) > 0:
                hasmedicaldue = True
                pb(lines, asm3.i18n._("Upcoming medical items", l))
                lines.append("<p>")
                for m in nextdue:
                    br(lines, "{0}: {1} {2} {3}/{4} {5}".format( asm3.i18n.python2display(l, m.DATEREQUIRED), \
                        m.TREATMENTNAME, m.DOSAGE, m.TREATMENTNUMBER, m.TOTALTREATMENTS, m.COMMENTS ))
                lines.append("</p>")

            clinics = asm3.clinic.get_animal_appointments_due(dbo, a.ANIMALID, dbo.today(), dbo.today(offset=7))
            if len(clinics) > 0:
                hasmedicaldue = True
                pb(lines, asm3.i18n._("Upcoming clinic appointments", l))
                lines.append("<p>")
                for c in clinics:
                    br(lines, "{0}: {1} {2}".format( asm3.i18n.python2displaytime(l, c.DATETIME), c.APPTFOR, c.REASONFORAPPOINTMENT ))
                lines.append("</p>")
            
            lines.append("<hr>") # separate each animal

        # Email is complete, send to the fosterer (assuming there were some animals to send)
        if len(animals) > 0:
            # If the option to send emails if there were no medical items is off and there
            # weren't any medical items, skip to the next fosterer
            if asm3.configuration.fosterer_email_skip_no_medical(dbo) and not hasmedicaldue: continue
            subject = asm3.i18n._("Fosterer Medical Report", l)
            body = "\n".join(lines)
            asm3.utils.send_email(dbo, replyto, f.EMAILADDRESS, subject=subject, body=body, contenttype="html", exceptions=False)
            if asm3.configuration.audit_on_send_email(dbo): 
                asm3.audit.email(dbo, user, replyto, f.EMAILADDRESS, "", "", subject, body)

def _licence_reminder_query(dbo: Database, cutoff: datetime) -> Results:
    return dbo.query("SELECT ol.ID, ol.OwnerID, o.EmailAddress " \
        "FROM ownerlicence ol " \
        "INNER JOIN owner o ON o.ID = ol.OwnerID " \
        "WHERE ol.ExpiryDate = ? AND Renewed = 0 " \
        "ORDER BY ol.ID", [cutoff])

def licence_reminder(dbo: Database, user = "system") -> None:
    """
    Finds all people who have a licence expiring in X days and sends
    them a reminder email using the configured template.
    """
    l = dbo.locale
    if not asm3.configuration.email_licence_reminder(dbo):
        asm3.al.debug("EmailLicenceReminder option set to No", "automail.licence_reminder", dbo)
        return

    days = asm3.configuration.email_licence_reminder_days(dbo)
    cutoff = dbo.today(offset = days)
    dtid = asm3.configuration.email_licence_reminder_template(dbo)
    asm3.al.debug(f"licence reminder: {days} days, email template {dtid}", "automail.licence_reminder", dbo)
    if not _valid_template(dbo, dtid): return

    rows = _licence_reminder_query(dbo, cutoff)
    for r in rows:
        body = asm3.wordprocessor.generate_licence_doc(dbo, dtid, r.ID, user)
        _send_email_from_template(dbo, r.EMAILADDRESS, asm3.i18n._("License Renewal", l), body, loglinkid=r.OWNERID, logmsg=f"LR01:{r.ID}")

    asm3.al.info(f"Sent {len(rows)} licence reminder emails.", "automail.licence_reminder", dbo)
