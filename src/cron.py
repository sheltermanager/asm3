#!/usr/bin/python

import os, sys

# Add our modules to the sys.path
sys.path.append(os.getcwd())

import al
import audit
import animal
import configuration
import db
import dbfs
import dbupdate
import diary
import i18n
import lostfound
import media
import movement
import onlineform
import person
import publish
import reports as extreports
import smcom
import time
import utils
import waitinglist
from sitedefs import LOCALE, TIMEZONE, MULTIPLE_DATABASES, MULTIPLE_DATABASES_TYPE, MULTIPLE_DATABASES_MAP

def ttask(fn, dbo):
    """ Runs a function and times how long it takes """
    x = time.time()
    fn(dbo)
    elapsed = time.time() - x
    if elapsed > 10:
        al.warn("complete in %0.2f sec" % elapsed, fn.__name__, dbo)
    else:
        al.debug("complete in %0.2f sec" % elapsed, fn.__name__, dbo)

def daily(dbo):
    """
    Tasks to run once each day before users login for the day.
    """
    try:
        # The batch should never be run at a time when users may be
        # using the system, remove any database update locks as any
        # lock at this time should be erroneous
        configuration.db_unlock(dbo)

        # Check to see if any updates need performing on this database
        if dbupdate.check_for_updates(dbo):
            ttask(dbupdate.perform_updates, dbo)

        if dbupdate.check_for_view_seq_changes(dbo):
            ttask(dbupdate.install_db_views, dbo)
            ttask(dbupdate.install_db_sequences, dbo)
            ttask(dbupdate.install_db_stored_procedures, dbo)

        # Get the latest news from sheltermanager.com
        configuration.asm_news(dbo, update=True)

        # Update on shelter and foster animal location fields
        ttask(animal.update_on_shelter_animal_statuses, dbo)
        ttask(animal.update_foster_animal_statuses, dbo)

        # Update on shelter animal variable data (age, time on shelter, etc)
        ttask(animal.update_on_shelter_variable_animal_data, dbo)

        # Update animal figures for reports
        ttask(animal.update_animal_figures, dbo)
        ttask(animal.update_animal_figures_annual, dbo)

        # Update waiting list urgencies and auto remove
        ttask(waitinglist.auto_remove_waitinglist, dbo)
        ttask(waitinglist.auto_update_urgencies, dbo)

        # Email diary notes to users
        ttask(diary.email_uncompleted_upto_today, dbo)

        # Update animal litter counts
        ttask(animal.update_active_litters, dbo)

        # Find any missing person geocodes
        ttask(person.update_missing_geocodes, dbo)

        # Clear out any old audit logs
        ttask(audit.clean, dbo)

        # Remove old publisher logs
        ttask(publish.delete_old_publish_logs, dbo)

        # auto cancel any reservations
        ttask(movement.auto_cancel_reservations, dbo)

        # auto cancel animal holds
        ttask(animal.auto_cancel_holds, dbo)

        # auto remove online forms
        ttask(onlineform.auto_remove_old_incoming_forms, dbo)

        # Update the generated looking for report
        ttask(person.update_lookingfor_report, dbo)

        # Update the generated lost/found match report
        ttask(lostfound.update_match_report, dbo)

        # Email any reports set to run with batch
        ttask(extreports.email_daily_reports, dbo)

    except:
        em = str(sys.exc_info()[0])
        al.error("FAIL: running batch tasks: %s" % em, "cron.daily", dbo, sys.exc_info())

def reports_email(dbo):
    """
    Batch email reports
    """
    try:
        # Email any daily reports for local time of now
        extreports.email_daily_reports(dbo, i18n.now(dbo.timezone))
    except:
        em = str(sys.exc_info()[0])
        al.error("FAIL: running daily email of reports_email: %s" % em, "cron.reports_email", dbo, sys.exc_info())

def publish_3pty(dbo):
    try:
        publishers = configuration.publishers_enabled(dbo)
        for p in publishers.split(" "):
            if p != "html": # We do html/ftp publishing separate from others
                publish.start_publisher(dbo, p, user="system", async=False)
    except:
        em = str(sys.exc_info()[0])
        al.error("FAIL: uncaught error running third party publishers: %s" % em, "cron.publish_3pty", dbo, sys.exc_info())

def publish_html(dbo):
    try :
        if configuration.publishers_enabled(dbo).find("html") != -1:
            publish.start_publisher(dbo, "html", user="system", async=False)
    except:
        em = str(sys.exc_info()[0])
        al.error("FAIL: uncaught error running html publisher: %s" % em, "cron.publish_html", dbo, sys.exc_info())

def maint_reinstall_default_media(dbo):
    try:
        dbupdate.install_default_media(dbo, True)
    except:
        em = str(sys.exc_info()[0])
        al.error("FAIL: uncaught error running maint_reinstall_default_media: %s" % em, "cron.maint_reinstall_default_media", dbo, sys.exc_info())

def maint_recode_all(dbo):
    try:
        animal.maintenance_reassign_all_codes(dbo)
    except:
        em = str(sys.exc_info()[0])
        al.error("FAIL: uncaught error running maint_recode_all: %s" % em, "cron.maint_recode_all", dbo, sys.exc_info())

def maint_variable_data(dbo):
    try:
        animal.update_all_variable_animal_data(dbo)
    except:
        em = str(sys.exc_info()[0])
        al.error("FAIL: uncaught error running maint_variable_data: %s" % em, "cron.maint_variable_data", dbo, sys.exc_info())

def maint_recode_shelter(dbo):
    try:
        animal.maintenance_reassign_shelter_codes(dbo)
    except:
        em = str(sys.exc_info()[0])
        al.error("FAIL: uncaught error running maint_recode_shelter: %s" % em, "cron.maint_recode_shelter", dbo, sys.exc_info())

def maint_animal_figures(dbo):
    try:
        animal.update_all_animal_statuses(dbo)
        animal.update_all_variable_animal_data(dbo)
        animal.maintenance_animal_figures(dbo, includeMonths = True, includeAnnual = True)
    except:
        em = str(sys.exc_info()[0])
        al.error("FAIL: uncaught error running maint_animal_figures: %s" % em, "cron.maint_animal_figures", dbo, sys.exc_info())

def maint_animal_figures_annual(dbo):
    try:
        animal.maintenance_animal_figures(dbo, includeMonths = False, includeAnnual = True)
    except:
        em = str(sys.exc_info()[0])
        al.error("FAIL: uncaught error running maint_animal_figures_annual: %s" % em, "cron.maint_animal_figures_annual", dbo, sys.exc_info())

def maint_db_diagnostic(dbo):
    try:
        d = dbupdate.diagnostic(dbo)
        for k, v in d.iteritems():
            print("%s: %s" % (k, v))
    except:
        em = str(sys.exc_info()[0])
        al.error("FAIL: uncaught error running maint_db_diagnostic: %s" % em, "cron.maint_db_diagnostic", dbo, sys.exc_info())

def maint_db_dump(dbo):
    try:
        for x in dbupdate.dump(dbo):
            print(utils.cunicode(x).encode("utf-8"))
    except:
        em = str(sys.exc_info()[0])
        al.error("FAIL: uncaught error running maint_db_dump: %s" % em, "cron.maint_db_dump", dbo, sys.exc_info())

def maint_db_dump_dbfs(dbo):
    try:
        dbupdate.dump_dbfs_stdout(dbo)
    except:
        em = str(sys.exc_info()[0])
        al.error("FAIL: uncaught error running maint_db_dump: %s" % em, "cron.maint_db_dump", dbo, sys.exc_info())

def maint_db_dump_merge(dbo):
    try:
        print(utils.cunicode(dbupdate.dump_merge(dbo)).encode("utf-8"))
    except:
        em = str(sys.exc_info()[0])
        al.error("FAIL: uncaught error running maint_db_dump_merge: %s" % em, "cron.maint_db_dump_merge", dbo, sys.exc_info())

def maint_db_dump_smcom(dbo):
    try:
        for x in dbupdate.dump_smcom(dbo):
            print(utils.cunicode(x).encode("utf-8"))
    except:
        em = str(sys.exc_info()[0])
        al.error("FAIL: uncaught error running maint_db_dump: %s" % em, "cron.maint_db_dump_smcom", dbo, sys.exc_info())

def maint_db_dump_animalcsv(dbo):
    try:
        print(utils.csv(dbo.locale, animal.get_animal_find_advanced(dbo, { "logicallocation" : "all", "includedeceased": "true", "includenonshelter": "true" })))
    except:
        em = str(sys.exc_info()[0])
        al.error("FAIL: uncaught error running maint_db_dump_animalcsv: %s" % em, "cron.maint_db_dump_animalcsv", dbo, sys.exc_info())

def maint_db_dump_personcsv(dbo):
    try:
        print(utils.csv(dbo.locale, person.get_person_find_simple(dbo, "", "all", True, True, 0)))
    except:
        em = str(sys.exc_info()[0])
        al.error("FAIL: uncaught error running maint_db_dump_personcsv: %s" % em, "cron.maint_db_dump_personcsv", dbo, sys.exc_info())

def maint_db_install(dbo):
    try:
        dbupdate.install(dbo)
    except:
        em = str(sys.exc_info()[0])
        al.error("FAIL: uncaught error running maint_db_install: %s" % em, "cron.maint_db_install", dbo, sys.exc_info())

def maint_db_reinstall(dbo):
    try:
        dbupdate.reinstall_default_data(dbo)
    except:
        em = str(sys.exc_info()[0])
        al.error("FAIL: uncaught error running maint_db_reinstall: %s" % em, "cron.maint_db_reinstall", dbo, sys.exc_info())

def maint_db_reset(dbo):
    try:
        dbupdate.reset_db(dbo)
    except:
        em = str(sys.exc_info()[0])
        al.error("FAIL: uncaught error running maint_db_reset: %s" % em, "cron.maint_db_reset", dbo, sys.exc_info())

def maint_deduplicate_people(dbo):
    try:
        person.merge_duplicate_people(dbo, "cron")
    except:
        em = str(sys.exc_info()[0])
        al.error("FAIL: uncaught error running maint_deduplicate_people: %s" % em, "cron.maint_deduplicate_people", dbo, sys.exc_info())

def maint_scale_animal_images(dbo):
    try:
        media.scale_all_animal_images(dbo)
    except:
        em = str(sys.exc_info()[0])
        al.error("FAIL: uncaught error running maint_scale_animal_images: %s" % em, "cron.maint_scale_animal_images", dbo, sys.exc_info())

def maint_scale_odts(dbo):
    try:
        media.scale_all_odt(dbo)
    except:
        em = str(sys.exc_info()[0])
        al.error("FAIL: uncaught error running maint_scale_odts: %s" % em, "cron.maint_scale_odts", dbo, sys.exc_info())

def maint_scale_pdfs(dbo):
    try:
        media.scale_all_pdf(dbo)
    except:
        em = str(sys.exc_info()[0])
        al.error("FAIL: uncaught error running maint_scale_pdfs: %s" % em, "cron.maint_scale_pdfs", dbo, sys.exc_info())

def maint_switch_dbfs_storage(dbo):
    try:
        dbfs.switch_storage(dbo)
    except:
        em = str(sys.exc_info()[0])
        al.error("FAIL: uncaught error running maint_dbfs_switch_storage: %s" % em, "cron.maint_switch_dbfs_storage", dbo, sys.exc_info())

def run(dbo, mode):
    # If the task is maint_db_install, then there won't be a 
    # locale or timezone to read
    x = time.time()
    al.info("start %s" % mode, "cron.run", dbo)
    if mode == "maint_db_install":
        dbo.locale = LOCALE
        dbo.timezone = TIMEZONE
    else:
        # Get the locale and timezone from the system 
        dbo.locale = configuration.locale(dbo) 
        dbo.timezone = configuration.timezone(dbo)
    dbo.installpath = os.getcwd() + os.sep
    al.debug("set locale and timezone for database: %s, %d" % (dbo.locale, dbo.timezone), "cron", dbo)
    if mode == "all":
        daily(dbo)
        reports_email(dbo)
        publish_html(dbo)
        publish_3pty(dbo)
    elif mode == "daily":
        daily(dbo)
    elif mode == "reports_email":
        reports_email(dbo)
    elif mode == "publish_3pty":
        publish_3pty(dbo)
    elif mode == "publish_html":
        publish_html(dbo)
    elif mode == "maint_recode_all":
        maint_recode_all(dbo)
    elif mode == "maint_recode_shelter":
        maint_recode_shelter(dbo)
    elif mode == "maint_scale_animal_images":
        maint_scale_animal_images(dbo)
    elif mode == "maint_scale_odts":
        maint_scale_odts(dbo)
    elif mode == "maint_scale_pdfs":
        maint_scale_pdfs(dbo)
    elif mode == "maint_switch_dbfs_storage":
        maint_switch_dbfs_storage(dbo)
    elif mode == "maint_variable_data":
        maint_variable_data(dbo)
    elif mode == "maint_animal_figures":
        maint_animal_figures(dbo)
    elif mode == "maint_animal_figures_annual":
        maint_animal_figures_annual(dbo)
    elif mode == "maint_db_diagnostic":
        maint_db_diagnostic(dbo)
    elif mode == "maint_db_dump":
        maint_db_dump(dbo)
    elif mode == "maint_db_dump_dbfs":
        maint_db_dump_dbfs(dbo)
    elif mode == "maint_db_dump_merge":
        maint_db_dump_merge(dbo)
    elif mode == "maint_db_dump_smcom":
        maint_db_dump_smcom(dbo)
    elif mode == "maint_db_dump_animalcsv":
        maint_db_dump_animalcsv(dbo)
    elif mode == "maint_db_dump_personcsv":
        maint_db_dump_personcsv(dbo)
    elif mode == "maint_db_install":
        maint_db_install(dbo)
    elif mode == "maint_reinstall_default_media":
        maint_reinstall_default_media(dbo)
    elif mode == "maint_db_reinstall":
        maint_db_reinstall(dbo)
    elif mode == "maint_db_reset":
        maint_db_reset(dbo)
    elif mode == "maint_deduplicate_people":
        maint_deduplicate_people(dbo)
    elapsed = time.time() - x
    al.info("end %s: elapsed %0.2f secs" % (mode, elapsed), "cron.run", dbo)

def run_all_map_databases(mode):
    for alias in MULTIPLE_DATABASES_MAP.iterkeys():
        dbo = db.get_multiple_database_info(alias)
        dbo.timeout = 0
        dbo.connection = dbo.connect()
        run(dbo, mode)

def run_default_database(mode):
    dbo = db.get_database()
    dbo.timeout = 0
    dbo.connection = dbo.connect()
    run(dbo, mode)

def run_alias(mode, alias):
    if MULTIPLE_DATABASES_TYPE == "smcom":
        dbo = smcom.get_database_info(alias)
    elif MULTIPLE_DATABASES_TYPE == "map" and alias != "%":
        dbo  = db.get_multiple_database_info(alias)
    dbo.alias = alias
    if dbo.database == "FAIL":
        print("Invalid database alias '%s'" % (alias))
        return
    else:
        dbo.timeout = 0
        dbo.connection = dbo.connect()
        run(dbo, mode)

def run_override_database(mode, dbtype, host, port, username, password, database, alias):
    dbo = db.get_database(dbtype)
    dbo.dbtype = dbtype
    dbo.host = host
    dbo.port = port
    dbo.username = username
    dbo.password = password
    dbo.database = database
    dbo.alias = alias
    dbo.timeout = 0
    dbo.connection = dbo.connect()
    run(dbo, mode)

def print_usage():
    print("Usage: cron.py mode [alias]")
    print("")
    print("           alias is a database alias to find info from. If none is given")
    print("           in multi database/map mode, the task is run for all databases")
    print("")
    print("   Or: cron.py mode dbtype host port username password database alias")
    print("")
    print("mode is one of:")
    print("       all - runs daily and all publish_* tasks")
    print("       daily - daily batch tasks")
    print("       reports_email - email reports with dailyemail set (run this target once per hour)")
    print("       publish_html - publish html/ftp")
    print("       publish_3pty - run all 3rd party publishers")
    print("       maint_animal_figures - calculate all monthly/annual figures for all time")
    print("       maint_animal_figures_annual - calculate all annual figures for all time")
    print("       maint_db_diagnostic - run database diagnostics")
    print("       maint_db_dump - produce a dump of INSERT statements to recreate the db")
    print("       maint_db_dump_dbfs - produce a dump of INSERT statements to recreate the dbfs")
    print("       maint_db_dump_merge - produce a dump of INSERT statements, renumbering IDs to +100000")
    print("       maint_db_dump_animalcsv - produce a CSV of animal/adoption/owner data")
    print("       maint_db_dump_personcsv - produce a CSV of person data")
    print("       maint_db_dump_smcom - produce an SQL dump for import into sheltermanager.com")
    print("       maint_db_install - install structure/data into a new empty database")
    print("       maint_db_reinstall - wipe the db and reinstall default data")
    print("       maint_deduplicate_people - automatically merge duplicate people records")
    print("       maint_recode_all - regenerate all animal codes")
    print("       maint_recode_shelter - regenerate animals codes for all shelter animals")
    print("       maint_reinstall_default_media - re-adds default document/publishing templates")
    print("       maint_scale_animal_images - re-scales all the animal images in the database")
    print("       maint_scale_odts - re-scales all odt files attached to records (remove images)")
    print("       maint_scale_pdfs - re-scales all the PDFs in the database")
    print("       maint_switch_dbfs_storage - moves all existing dbfs files to the current DBFS_STORE")
    print("       maint_variable_data - recalculate all variable data for all animals")

if __name__ == "__main__": 
    if len(sys.argv) == 2 and not MULTIPLE_DATABASES:
        # mode argument given and we have a single database
        run_default_database(sys.argv[1])
    elif len(sys.argv) == 2 and MULTIPLE_DATABASES and MULTIPLE_DATABASES_TYPE == "map":
        # mode argument given and we have multiple map databases
        run_all_map_databases(sys.argv[1])
    elif len(sys.argv) == 3 and MULTIPLE_DATABASES:
        # mode and alias given
        run_alias(sys.argv[1], sys.argv[2])
    elif len(sys.argv) == 9:
        # mode and database information given
        run_override_database(sys.argv[1], sys.argv[2], sys.argv[3], utils.cint(sys.argv[4]), sys.argv[5], sys.argv[6], sys.argv[7], sys.argv[8])
    else:
        # We didn't get a valid combination of args
        print_usage()
        sys.exit(1)

