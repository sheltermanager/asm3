
"""
Main ASM search functionality
"""

import asm3.animal
import asm3.animalcontrol
import asm3.configuration
import asm3.financial
import asm3.lostfound
import asm3.person
import asm3.publishers.base
import asm3.users
import asm3.waitinglist
from asm3.i18n import _, now

import datetime
import time

THE_PAST = datetime.datetime(1900,1,1,0,0,0)

def search(dbo, session, q):

    """
    Performs a database wide search for the term given.
    special tokens:

    a:term      Only search animals for term
    ac:term     Only search animal control incidents for term
    p:term      Only search people for term
    la:term     Only search lost animals for term
    li:num      Only search licence numbers for term
    fa:term     Only search found animals for term
    lo:term     Only search logs for term
    vo:term     Only search voucher codes for term
    wl:term     Only search waiting list entries for term

    sort:az     Sort results alphabetically az
    sort:za     Sort results alphabetically za
    sort:mr     Sort results most recently changed first
    sort:lr     Sort results least recently changed first

    -- update this list in header.js/bind_search/keywords
    activelost, activefound, 
    onshelter/os, notforadoption, hold, holdtoday, quarantine, deceased, 
    forpublish, people, vets, retailers, staff, fosterers, volunteers, 
    shelters, aco, banned, homechecked, homecheckers, members, donors, drivers,
    reservenohomecheck, nevervacc, norabies, notmicrochipped, unsigned, signed

    returns a tuple of:
    results, timetaken, explain, sortname
    """
    # ar (add results) inner method
    def ar(rlist, rtype, sortfield):
        # Return brief records to save bandwidth
        if rtype == "ANIMAL":
            rlist = asm3.animal.get_animals_brief(rlist)
        if rtype == "PERSON":
            pass # TODO:
        for r in rlist:
            r["RESULTTYPE"] = rtype
            if sortfield == "RELEVANCE":
                # How "relevant" is this record to what was searched for?
                # animal name and code weight higher than other elements.
                # Note that the code below modifies inbound var q, so by the
                # time we read it here, it should only contain the search term 
                # itself. Weight everything else by last changed date so there
                # is some semblance of useful order for less relevant items
                qlow = q.lower()
                if rtype == "ANIMAL":
                    r["SORTON"] = r["LASTCHANGEDDATE"]
                    if r["SORTON"] is None: r["SORTON"] = THE_PAST 
                    if r["ANIMALNAME"].lower() == qlow or r["SHELTERCODE"].lower() == qlow or r["SHORTCODE"].lower() == qlow:
                        r["SORTON"] = now()
                    # Put matches where term present just behind direct matches
                    elif r["ANIMALNAME"].lower().find(qlow) != -1 or r["SHELTERCODE"].lower().find(qlow) != -1 or r["SHORTCODE"].lower().find(qlow) != -1:
                        r["SORTON"] = now() - datetime.timedelta(seconds=1)
                elif rtype == "PERSON":
                    r["SORTON"] = r["LASTCHANGEDDATE"]
                    if r["SORTON"] is None: r["SORTON"] = THE_PAST
                    # Count how many of the keywords in the search were present
                    # in the owner name field - if it's all of them then raise
                    # the relevance.
                    qw = qlow.split(" ")
                    qm = 0
                    for w in qw:
                        if r["OWNERNAME"].lower().find(w) != -1:
                            qm += 1
                    if qm == len(qw):
                        r["SORTON"] = now()
                    # Put matches where term present just behind direct matches
                    if r["OWNERSURNAME"].lower().find(qlow) or r["OWNERNAME"].lower().find(qlow):
                        r["SORTON"] = now() - datetime.timedelta(seconds=1)
                elif rtype == "LICENCE":
                    r["SORTON"] = r["ISSUEDATE"]
                    if r["SORTON"] is None: r["SORTON"] = THE_PAST
                    if r["LICENCENUMBER"].lower() == qlow: r["SORTON"] = now()
                else:
                    r["SORTON"] = r["LASTCHANGEDDATE"]
            else:
                r["SORTON"] = r[sortfield]
                if r["SORTON"] is None and sortfield.endswith("DATE"): r["SORTON"] = THE_PAST
            results.append(r)

    l = dbo.locale

    # start the clock
    starttime = time.time()

    # The returned results
    results = []
    
    # An i18n explanation of what was searched for
    explain = ""

    # Max records to be returned by search
    limit = asm3.configuration.record_search_limit(dbo)

    # Default sort for the search
    searchsort = asm3.configuration.search_sort(dbo)

    q = q.replace("'", "`")
    q = asm3.utils.truncate(q, 30) # limit search queries to 30 chars

    # Allow the sort to be overridden
    if q.find("sort:") != -1:
        if "sort:az" in q:
            searchsort = 0
            q = q.replace("sort:az", "")
        elif "sort:za" in q:
            searchsort = 1
            q = q.replace("sort:za", "")
        elif "sort:lr" in q:
            searchsort = 2
            q = q.replace("sort:lr", "")
        elif "sort:mr" in q:
            searchsort = 3
            q = q.replace("sort:mr", "")
        elif "sort:as" in q:
            searchsort = 4
            q = q.replace("sort:as", "")
        elif "sort:sa" in q:
            searchsort = 5
            q = q.replace("sort:sa", "")
        elif "sort:rel" in q:
            searchsort = 6
            q = q.replace("sort:rel", "")

    q = q.strip()

    # Handle sorting ===========================
    animalsort = ""
    personsort = ""
    wlsort = ""
    acsort = ""
    lasort = ""
    lisort = ""
    fasort = ""
    vosort = ""
    losort = ""
    sortdir = "a"
    sortname = ""
    # alphanumeric ascending
    if searchsort == 0:
        animalsort = "ANIMALNAME"
        personsort = "OWNERNAME"
        wlsort = "OWNERNAME"
        acsort = "OWNERNAME"
        lasort = "OWNERNAME"
        lisort = "OWNERNAME"
        fasort = "OWNERNAME"
        vosort = "OWNERNAME"
        losort = "RECORDDETAIL"
        sortdir = "a"
        sortname = _("Alphabetically A-Z", l)
    # alphanumeric descending
    elif searchsort == 1:
        animalsort = "ANIMALNAME"
        personsort = "OWNERNAME"
        wlsort = "OWNERNAME"
        acsort = "OWNERNAME"
        lasort = "OWNERNAME"
        lisort = "OWNERNAME"
        fasort = "OWNERNAME"
        vosort = "OWNERNAME"
        losort = "RECORDDETAIL"
        sortdir = "d"
        sortname = _("Alphabetically Z-A", l)
    # last changed ascending
    elif searchsort == 2:
        animalsort = "LASTCHANGEDDATE"
        personsort = "LASTCHANGEDDATE"
        wlsort = "LASTCHANGEDDATE"
        acsort = "LASTCHANGEDDATE"
        lasort = "LASTCHANGEDDATE"
        lisort = "ISSUEDATE"
        fasort = "LASTCHANGEDDATE"
        vosort = "DATEISSUED"
        losort = "LASTCHANGEDDATE"
        sortdir = "a"
        sortname = _("Least recently changed", l)
    # last changed descending
    elif searchsort == 3:
        animalsort = "LASTCHANGEDDATE"
        personsort = "LASTCHANGEDDATE"
        acsort = "LASTCHANGEDDATE"
        wlsort = "LASTCHANGEDDATE"
        lasort = "LASTCHANGEDDATE"
        lisort = "ISSUEDATE"
        fasort = "LASTCHANGEDDATE"
        vosort = "DATEISSUED"
        losort = "LASTCHANGEDDATE"
        sortdir = "d"
        sortname = _("Most recently changed", l)
    # species ascending
    elif searchsort == 4:
        animalsort = "SPECIESNAME"
        personsort = "OWNERNAME"
        acsort = "SPECIESNAME"
        wlsort = "SPECIESNAME"
        lasort = "SPECIESNAME"
        lisort = "COMMENTS"
        fasort = "SPECIESNAME"
        vosort = "COMMENTS"
        losort = "RECORDDETAIL"
        sortdir = "a"
        sortname = _("Species A-Z", l)
    elif searchsort == 5:
        animalsort = "SPECIESNAME"
        personsort = "OWNERNAME"
        acsort = "SPECIESNAME"
        wlsort = "SPECIESNAME"
        lasort = "SPECIESNAME"
        lisort = "COMMENTS"
        fasort = "SPECIESNAME"
        vosort = "COMMENTS"
        losort = "RECORDDETAIL"
        sortdir = "d"
        sortname = _("Species Z-A", l)
    elif searchsort == 6:
        animalsort = "RELEVANCE"
        personsort = "RELEVANCE"
        wlsort = "RELEVANCE"
        acsort = "RELEVANCE"
        lasort = "RELEVANCE"
        lisort = "RELEVANCE"
        fasort = "RELEVANCE"
        vosort = "RELEVANCE"
        losort = "RELEVANCE"
        sortdir = "d"
        sortname = _("Most relevant", l)

    viewperson = asm3.users.check_permission_bool(session, asm3.users.VIEW_PERSON)
    viewanimal = asm3.users.check_permission_bool(session, asm3.users.VIEW_ANIMAL)
    viewstaff = asm3.users.check_permission_bool(session, asm3.users.VIEW_STAFF)
    viewvolunteer = asm3.users.check_permission_bool(session, asm3.users.VIEW_VOLUNTEER)
    user = session.user
    locationfilter = session.locationfilter
    siteid = session.siteid
    visibleanimalids = session.visibleanimalids

    # Special token searches
    if q == "onshelter" or q == "os":
        explain = _("All animals on the shelter.", l)
        if viewanimal:
            ar(asm3.animal.get_animal_find_simple(dbo, "", limit=limit, locationfilter=locationfilter, siteid=siteid, visibleanimalids=visibleanimalids), "ANIMAL", animalsort)

    elif q == "notforadoption":
        explain = _("All animals who are flagged as not for adoption.", l)
        if viewanimal:
            ar(asm3.animal.get_animals_not_for_adoption(dbo), "ANIMAL", animalsort)

    elif q == "longterm":
        explain = _("All animals who have been on the shelter longer than {0} months.", l).format(asm3.configuration.long_term_days(dbo) / 30)
        if viewanimal:
            ar(asm3.animal.get_animals_long_term(dbo), "ANIMAL", animalsort)

    elif q == "nevervacc":
        explain = _("All animals who do not have a vaccination of any type", l)
        if viewanimal:
            ar(asm3.animal.get_animals_never_vacc(dbo), "ANIMAL", animalsort)

    elif q == "notmicrochipped":
        explain = _("All animals who have not been microchipped", l)
        if viewanimal:
            ar(asm3.animal.get_animals_not_microchipped(dbo), "ANIMAL", animalsort)

    elif q == "norabies":
        explain = _("All animals who have not received a rabies vaccination", l)
        if viewanimal:
            ar(asm3.animal.get_animals_no_rabies(dbo), "ANIMAL", animalsort)

    elif q == "hold":
        explain = _("All animals who are currently held in case of reclaim.", l)
        if viewanimal:
            ar(asm3.animal.get_animals_hold(dbo), "ANIMAL", animalsort)

    elif q == "holdtoday":
        explain = _("All animals where the hold ends today.", l)
        if viewanimal:
            ar(asm3.animal.get_animals_hold_today(dbo), "ANIMAL", animalsort)

    elif q == "quarantine":
        explain = _("All animals who are currently quarantined.", l)
        if viewanimal:
            ar(asm3.animal.get_animals_quarantine(dbo), "ANIMAL", animalsort)

    elif q == "deceased":
        explain = _("Recently deceased shelter animals (last 30 days).", l)
        if viewanimal:
            ar(asm3.animal.get_animals_recently_deceased(dbo), "ANIMAL", animalsort)

    elif q == "forpublish":
        explain = _("All animals matching current publishing options.", l)
        if viewanimal:
            ar(asm3.publishers.base.get_animal_data(dbo), "ANIMAL", animalsort)

    elif q == "people":
        ar(asm3.person.get_person_find_simple(dbo, "", classfilter="all", includeStaff=viewstaff, includeVolunteers=viewvolunteer, limit=limit, siteid=siteid), "PERSON", personsort)
        explain = _("All people on file.", l)

    elif q == "vets":
        explain = _("All vets on file.", l)
        if viewperson:
            ar(asm3.person.get_person_find_simple(dbo, "", classfilter="vet", includeStaff=viewstaff, includeVolunteers=viewvolunteer, limit=limit, siteid=siteid), "PERSON", personsort)

    elif q == "retailers":
        explain = _("All retailers on file.", l)
        if viewperson:
            ar(asm3.person.get_person_find_simple(dbo, "", classfilter="retailer", includeStaff=viewstaff, includeVolunteers=viewvolunteer, limit=limit, siteid=siteid), "PERSON", personsort)

    elif q == "staff":
        explain = _("All staff on file.", l)
        if viewperson:
            ar(asm3.person.get_person_find_simple(dbo, "", classfilter="staff", includeStaff=viewstaff, includeVolunteers=viewvolunteer, limit=limit, siteid=siteid), "PERSON", personsort)

    elif q == "fosterers":
        explain = _("All fosterers on file.", l)
        if viewperson:
            ar(asm3.person.get_person_find_simple(dbo, "", classfilter="fosterer", includeStaff=viewstaff, includeVolunteers=viewvolunteer, limit=limit, siteid=siteid), "PERSON", personsort)

    elif q == "volunteers":
        explain = _("All volunteers on file.", l)
        if viewperson:
            ar(asm3.person.get_person_find_simple(dbo, "", classfilter="volunteer", includeStaff=viewstaff, includeVolunteers=viewvolunteer, limit=limit, siteid=siteid), "PERSON", personsort)

    elif q == "shelters":
        explain = _("All animal shelters on file.", l)
        if viewperson:
            ar(asm3.person.get_person_find_simple(dbo, "", classfilter="shelter", includeStaff=viewstaff, includeVolunteers=viewvolunteer, limit=limit, siteid=siteid), "PERSON", personsort)

    elif q == "aco":
        explain = _("All animal care officers on file.", l)
        if viewperson:
            ar(asm3.person.get_person_find_simple(dbo, "", classfilter="aco", includeStaff=viewstaff, includeVolunteers=viewvolunteer, limit=limit, siteid=siteid), "PERSON", personsort)

    elif q == "banned":
        explain = _("All banned owners on file.", l)
        if viewperson:
            ar(asm3.person.get_person_find_simple(dbo, "", classfilter="banned", includeStaff=viewstaff, includeVolunteers=viewvolunteer, limit=limit, siteid=siteid), "PERSON", personsort)

    elif q == "homechecked":
        explain = _("All homechecked owners on file.", l)
        if viewperson:
            ar(asm3.person.get_person_find_simple(dbo, "", classfilter="homechecked", includeStaff=viewstaff, includeVolunteers=viewvolunteer, limit=limit, siteid=siteid), "PERSON", personsort)

    elif q == "homecheckers":
        explain = _("All homecheckers on file.", l)
        if viewperson:
            ar(asm3.person.get_person_find_simple(dbo, "", classfilter="homechecker", includeStaff=viewstaff, includeVolunteers=viewvolunteer, limit=limit, siteid=siteid), "PERSON", personsort)

    elif q == "members":
        explain = _("All members on file.", l)
        if viewperson:
            ar(asm3.person.get_person_find_simple(dbo, "", classfilter="member", includeStaff=viewstaff, includeVolunteers=viewvolunteer, limit=limit, siteid=siteid), "PERSON", personsort)

    elif q == "donors":
        explain = _("All donors on file.", l)
        if viewperson:
            ar(asm3.person.get_person_find_simple(dbo, "", classfilter="donor", includeStaff=viewstaff, includeVolunteers=viewvolunteer, limit=limit, siteid=siteid), "PERSON", personsort)

    elif q == "drivers":
        explain = _("All drivers on file.", l)
        if viewperson:
            ar(asm3.person.get_person_find_simple(dbo, "", classfilter="driver", includeStaff=viewstaff, includeVolunteers=viewvolunteer, limit=limit, siteid=siteid), "PERSON", personsort)

    elif q == "reservenohomecheck":
        explain = _("People with active reservations, but no homecheck has been done.", l)
        if viewperson:
            ar(asm3.person.get_reserves_without_homechecks(dbo), "PERSON", personsort)

    elif q == "overduedonations":
        explain = _("People with overdue donations.", l)
        if viewperson:
            ar(asm3.person.get_overdue_donations(dbo), "PERSON", personsort)

    elif q == "signed":
        explain = _("Document signing requests received in the last week", l)
        if viewperson:
            ar(asm3.person.get_signed_requests(dbo, 7), "PERSON", personsort)
            ar(asm3.animal.get_signed_requests(dbo, 7), "ANIMAL", animalsort)

    elif q == "unsigned":
        explain = _("Document signing requests issued in the last month that are unsigned", l)
        if viewperson:
            ar(asm3.person.get_unsigned_requests(dbo, 31), "PERSON", personsort)
            ar(asm3.animal.get_unsigned_requests(dbo, 31), "ANIMAL", animalsort)

    elif q == "opencheckout":
        explain = _("Adoption checkout requests issued in the last week that are still open", l)
        if viewperson:
            ar(asm3.person.get_open_adoption_checkout(dbo, 7), "PERSON", personsort)

    elif q == "activelost":
        explain = _("Lost animals reported in the last 30 days.", l)
        if asm3.users.check_permission_bool(session, asm3.users.VIEW_LOST_ANIMAL):
            ar(asm3.lostfound.get_lostanimal_find_simple(dbo, "", limit=limit, siteid=siteid), "LOSTANIMAL", lasort)

    elif q == "activefound":
        explain = _("Found animals reported in the last 30 days.", l)
        if asm3.users.check_permission_bool(session, asm3.users.VIEW_FOUND_ANIMAL):
            ar(asm3.lostfound.get_foundanimal_find_simple(dbo, "", limit=limit, siteid=siteid), "FOUNDANIMAL", fasort)

    elif q.startswith("a:") or q.startswith("animal:"):
        q = q[q.find(":")+1:].strip()
        explain = _("Animals matching '{0}'.", l).format(q)
        if viewanimal:
            ar( asm3.animal.get_animal_find_simple(dbo, q, limit=limit, locationfilter=locationfilter, siteid=siteid, visibleanimalids=visibleanimalids), "ANIMAL", animalsort )

    elif q.startswith("ac:") or q.startswith("animalcontrol:"):
        q = q[q.find(":")+1:].strip()
        explain = _("Animal control incidents matching '{0}'.", l).format(q)
        if asm3.users.check_permission_bool(session, asm3.users.VIEW_INCIDENT):
            ar( asm3.animalcontrol.get_animalcontrol_find_simple(dbo, q, user, limit=limit, siteid=siteid), "ANIMALCONTROL", acsort )

    elif q.startswith("p:") or q.startswith("person:"):
        q = q[q.find(":")+1:].strip()
        explain = _("People matching '{0}'.", l).format(q)
        if viewperson:
            ar( asm3.person.get_person_find_simple(dbo, q, includeStaff=viewstaff, includeVolunteers=viewvolunteer, limit=limit, siteid=siteid), "PERSON", personsort )

    elif q.startswith("wl:") or q.startswith("waitinglist:"):
        q = q[q.find(":")+1:].strip()
        explain = _("Waiting list entries matching '{0}'.", l).format(q)
        if asm3.users.check_permission_bool(session, asm3.users.VIEW_WAITING_LIST):
            ar( asm3.waitinglist.get_waitinglist_find_simple(dbo, q, limit=limit, siteid=siteid), "WAITINGLIST", wlsort )

    elif q.startswith("la:") or q.startswith("lostanimal:"):
        q = q[q.find(":")+1:].strip()
        explain = _("Lost animal entries matching '{0}'.", l).format(q)
        if asm3.users.check_permission_bool(session, asm3.users.VIEW_LOST_ANIMAL):
            ar( asm3.lostfound.get_lostanimal_find_simple(dbo, q, limit=limit, siteid=siteid), "LOSTANIMAL", lasort )

    elif q.startswith("fa:") or q.startswith("foundanimal:"):
        q = q[q.find(":")+1:].strip()
        explain = _("Found animal entries matching '{0}'.", l).format(q)
        if asm3.users.check_permission_bool(session, asm3.users.VIEW_FOUND_ANIMAL):
            ar( asm3.lostfound.get_foundanimal_find_simple(dbo, q, limit=limit, siteid=siteid), "FOUNDANIMAL", fasort )

    elif q.startswith("li:") or q.startswith("license:"):
        q = q[q.find(":")+1:].strip()
        explain = _("License numbers matching '{0}'.", l).format(q)
        if asm3.users.check_permission_bool(session, asm3.users.VIEW_LICENCE):
            ar( asm3.financial.get_licence_find_simple(dbo, q, limit), "LICENCE", lisort )

    elif q.startswith("lo:") or q.startswith("log:"):
        q = q[q.find(":")+1:].strip()
        explain = _("Logs matching '{0}'.", l).format(q)
        if asm3.users.check_permission_bool(session, asm3.users.VIEW_LOG):
            ar( asm3.log.get_log_find_simple(dbo, q, limit), "LOG", losort )

    elif q.startswith("vo:") or q.startswith("voucher:"):
        q = q[q.find(":")+1:].strip()
        explain = _("Voucher codes matching '{0}'.", l).format(q)
        if asm3.users.check_permission_bool(session, asm3.users.VIEW_VOUCHER):
            ar( asm3.financial.get_voucher_find_simple(dbo, q, limit), "VOUCHER", vosort )

    # No special tokens, search everything and collate
    else:
        if viewanimal:
            ar( asm3.animal.get_animal_find_simple(dbo, q, limit=limit, locationfilter=locationfilter, siteid=siteid, visibleanimalids=visibleanimalids), "ANIMAL", animalsort )
        if asm3.users.check_permission_bool(session, asm3.users.VIEW_INCIDENT):
            ar( asm3.animalcontrol.get_animalcontrol_find_simple(dbo, q, user, limit=limit, siteid=siteid), "ANIMALCONTROL", acsort )
        if viewperson:
            ar( asm3.person.get_person_find_simple(dbo, q, includeStaff=viewstaff, includeVolunteers=viewvolunteer, limit=limit, siteid=siteid), "PERSON", personsort )
        if asm3.users.check_permission_bool(session, asm3.users.VIEW_WAITING_LIST):
            ar( asm3.waitinglist.get_waitinglist_find_simple(dbo, q, limit=limit, siteid=siteid), "WAITINGLIST", wlsort )
        if asm3.users.check_permission_bool(session, asm3.users.VIEW_LOST_ANIMAL):
            ar( asm3.lostfound.get_lostanimal_find_simple(dbo, q, limit=limit, siteid=siteid), "LOSTANIMAL", lasort )
        if asm3.users.check_permission_bool(session, asm3.users.VIEW_FOUND_ANIMAL):
            ar( asm3.lostfound.get_foundanimal_find_simple(dbo, q, limit=limit, siteid=siteid), "FOUNDANIMAL", fasort )
        if asm3.users.check_permission_bool(session, asm3.users.VIEW_LICENCE):
            ar( asm3.financial.get_licence_find_simple(dbo, q, limit), "LICENCE", lisort )
        # This pollutes search results too much, only allow log search with explicit lo:
        #if asm3.users.check_permission_bool(session, asm3.users.VIEW_LOG):
        #    ar( asm3.log.get_log_find_simple(dbo, q, limit=100), "LOG", losort )
        if asm3.users.check_permission_bool(session, asm3.users.VIEW_VOUCHER):
            ar( asm3.financial.get_voucher_find_simple(dbo, q, limit), "VOUCHER", vosort)
        explain = _("Results for '{0}'.", l).format(q)

    # Apply the sort to the results
    # We return a tuple to the sorted function which forces rows with None in the 
    # SORTON key to the end (True, None) for None values, (False, value) for items
    if sortdir == "a":
        sortresults = sorted(results, key=lambda k: (k["SORTON"] is None, k["SORTON"]))
    else:
        sortresults = sorted(results, reverse=True, key=lambda k: (k["SORTON"] is not None, k["SORTON"]))

    # stop the clock
    timetaken = (time.time() - starttime)

    # Return our final set of values
    return sortresults, timetaken, explain, sortname

