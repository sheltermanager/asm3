#!/usr/bin/env python3

import os, sys

# Add our modules to the sys.path
sys.path.append(os.getcwd())

from asm3 import automail
from asm3 import animalcontrol
from asm3 import additional
from asm3 import al
from asm3 import audit
from asm3 import animal
from asm3 import cachedisk
from asm3 import clinic
from asm3 import configuration
from asm3 import db
from asm3 import dbfs
from asm3 import dbupdate
from asm3 import diary
from asm3 import financial
from asm3 import lostfound
from asm3 import media
from asm3 import medical
from asm3 import movement
from asm3 import onlineform
from asm3 import person
from asm3 import publish
from asm3 import reports as extreports
from asm3 import utils
from asm3 import waitinglist
from asm3.sitedefs import LOCALE, TIMEZONE, MULTIPLE_DATABASES, MULTIPLE_DATABASES_TYPE, MULTIPLE_DATABASES_MAP
from asm3.sitedefs import HTMLFTP_PUBLISHER_ENABLED
from asm3.typehints import Callable, Database

import time

def ttask(fn: Callable, dbo: Database) -> None:
    """ Runs a function and times how long it takes """
    x = time.time()
    fn(dbo)
    elapsed = time.time() - x
    if elapsed > 10:
        al.warn("complete in %0.2f sec" % elapsed, fn.__name__, dbo)
    else:
        al.debug("complete in %0.2f sec" % elapsed, fn.__name__, dbo)

def daily(dbo: Database):
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

        # Update news file
        ttask(utils.get_asm_news, dbo)

        # Update any reports that have newer versions available
        ttask(extreports.update_smcom_reports, dbo)

        # Update on shelter and foster animal location fields
        ttask(animal.update_on_shelter_animal_statuses, dbo)
        ttask(animal.update_foster_animal_statuses, dbo)
        ttask(animal.update_boarding_animal_statuses, dbo)

        # Update on shelter, foster and young animal variable data (age, time on shelter, etc)
        ttask(animal.update_on_shelter_variable_animal_data, dbo)
        ttask(animal.update_foster_variable_animal_data, dbo)
        ttask(animal.update_offshelter_young_variable_animal_data, dbo)

        # Update locations of arriving boarders
        ttask(financial.update_location_boarding_today, dbo)

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

        # auto anonymise expired personal data
        ttask(person.update_anonymise_personal_data, dbo)

        # auto remove people who only have a cancelled reserve
        ttask(person.remove_people_only_cancelled_reserve, dbo)

        # auto remove expired media items
        ttask(media.remove_expired_media, dbo)
        ttask(media.remove_media_after_exit, dbo)

        # auto update clinic statuses
        ttask(clinic.auto_update_statuses, dbo)

        # Update the generated looking for report
        ttask(person.update_lookingfor_report, dbo)

        # Update the generated lost/found match report
        ttask(lostfound.update_match_report, dbo)

        # Email any reports set to run with batch
        ttask(extreports.email_daily_reports, dbo)

        # Send automated person emails
        ttask(automail.send_all, dbo)

    except:
        em = str(sys.exc_info()[0])
        al.error("FAIL: running batch tasks: %s" % em, "cron.daily", dbo, sys.exc_info())

def reports_email(dbo: Database):
    """
    Batch email reports
    """
    try:
        # Email any daily reports for local time of now
        extreports.email_daily_reports(dbo, dbo.now())
    except:
        em = str(sys.exc_info()[0])
        al.error("FAIL: running daily email of reports_email: %s" % em, "cron.reports_email", dbo, sys.exc_info())

def publish_3pty(dbo: Database):
    try:
        publishers = configuration.publishers_enabled(dbo)
        freq = configuration.publisher_sub24_frequency(dbo)
        for p in publishers.split(" "):
            if p not in publish.PUBLISHER_LIST: continue
            # Services that we do more frequently than 24 hours are handled by 3pty_sub24
            if publish.PUBLISHER_LIST[p]["sub24hour"] and freq != 0: continue
            # We do html/ftp publishing separate from other publishers
            if p == "html": continue
            publish.start_publisher(dbo, p, user="system", newthread=False)
    except:
        em = str(sys.exc_info()[0])
        al.error("FAIL: uncaught error running third party publishers: %s" % em, "cron.publish_3pty", dbo, sys.exc_info())

def publish_3pty_sub24(dbo: Database):
    try:
        publishers = configuration.publishers_enabled(dbo)
        freq = configuration.publisher_sub24_frequency(dbo)
        hournow = dbo.now().hour
        al.debug("chosen freq %s, current hour %s" % (freq, hournow), "cron.publish_3pty_sub24", dbo)
        if freq == 0: return # 24 hour mode is covered by regular publish_3pty with the batch
        elif freq == 2 and hournow not in [0,2,4,6,8,10,12,14,16,18,20,22]: return
        elif freq == 4 and hournow not in [1,5,9,13,17,21]: return
        elif freq == 6 and hournow not in [3,9,13,19]: return
        elif freq == 8 and hournow not in [1,9,17]: return
        elif freq == 12 and hournow not in [0,12]: return
        for p in publishers.split(" "):
            if p in publish.PUBLISHER_LIST and publish.PUBLISHER_LIST[p]["sub24hour"]:
                publish.start_publisher(dbo, p, user="system", newthread=False)
    except:
        em = str(sys.exc_info()[0])
        al.error("FAIL: uncaught error running sub24 third party publishers: %s" % em, "cron.publish_3pty_sub24", dbo, sys.exc_info())

def publish_html(dbo: Database):
    try :
        if HTMLFTP_PUBLISHER_ENABLED and configuration.publishers_enabled(dbo).find("html") != -1:
            publish.start_publisher(dbo, "html", user="system", newthread=False)
    except:
        em = str(sys.exc_info()[0])
        al.error("FAIL: uncaught error running html publisher: %s" % em, "cron.publish_html", dbo, sys.exc_info())

def maint_import_report(dbo: Database):
    try:
        extreports.install_smcom_report_file(dbo, "system", os.environ["ASM3_REPORT"])
        print("OK")
    except:
        em = str(sys.exc_info()[0])
        print(em) # This one is designed to be run from the command line rather than cron
        al.error("FAIL: uncaught error running import report: %s" % em, "cron.maint_import_report", dbo, sys.exc_info())

def maint_recode_all(dbo: Database):
    try:
        animal.maintenance_reassign_all_codes(dbo)
    except:
        em = str(sys.exc_info()[0])
        al.error("FAIL: uncaught error running maint_recode_all: %s" % em, "cron.maint_recode_all", dbo, sys.exc_info())

def maint_variable_data(dbo: Database):
    try:
        animal.update_all_variable_animal_data(dbo)
    except:
        em = str(sys.exc_info()[0])
        al.error("FAIL: uncaught error running maint_variable_data: %s" % em, "cron.maint_variable_data", dbo, sys.exc_info())

def maint_recode_shelter(dbo: Database):
    try:
        animal.maintenance_reassign_shelter_codes(dbo)
    except:
        em = str(sys.exc_info()[0])
        al.error("FAIL: uncaught error running maint_recode_shelter: %s" % em, "cron.maint_recode_shelter", dbo, sys.exc_info())

def maint_animal_figures(dbo: Database):
    try:
        animal.update_all_animal_statuses(dbo)
        animal.update_all_variable_animal_data(dbo)
        animal.maintenance_animal_figures(dbo, includeMonths = True, includeAnnual = True)
    except:
        em = str(sys.exc_info()[0])
        al.error("FAIL: uncaught error running maint_animal_figures: %s" % em, "cron.maint_animal_figures", dbo, sys.exc_info())

def maint_animal_figures_annual(dbo: Database):
    try:
        animal.maintenance_animal_figures(dbo, includeMonths = False, includeAnnual = True)
    except:
        em = str(sys.exc_info()[0])
        al.error("FAIL: uncaught error running maint_animal_figures_annual: %s" % em, "cron.maint_animal_figures_annual", dbo, sys.exc_info())

def maint_db_diagnostic(dbo: Database):
    try:
        d = dbupdate.diagnostic(dbo)
        for k, v in d.items():
            print("%s: %s" % (k, v))
    except:
        em = str(sys.exc_info()[0])
        al.error("FAIL: uncaught error running maint_db_diagnostic: %s" % em, "cron.maint_db_diagnostic", dbo, sys.exc_info())

def maint_db_fix_preferred_photos(dbo: Database):
    try:
        d = dbupdate.fix_preferred_photos(dbo)
        print("Fixed %d" % d)
    except:
        em = str(sys.exc_info()[0])
        al.error("FAIL: uncaught error running maint_db_fix_preferred_photos: %s" % em, "cron.maint_db_fix_preferred_photos", dbo, sys.exc_info())

def maint_db_dump(dbo: Database):
    try:
        for x in dbupdate.dump(dbo):
            print(x)
    except:
        em = str(sys.exc_info()[0])
        al.error("FAIL: uncaught error running maint_db_dump: %s" % em, "cron.maint_db_dump", dbo, sys.exc_info())

def maint_db_dump_hsqldb(dbo: Database):
    try:
        for x in dbupdate.dump_hsqldb(dbo):
            print(x)
    except:
        em = str(sys.exc_info()[0])
        al.error("FAIL: uncaught error running maint_db_dump_hsqldb: %s" % em, "cron.maint_db_dump_hsqldb", dbo, sys.exc_info())

def maint_db_dump_dbfs_base64(dbo: Database):
    try:
        for x in dbupdate.dump_dbfs_base64(dbo):
            print(x)
    except:
        em = str(sys.exc_info()[0])
        al.error("FAIL: uncaught error running maint_db_dump_dbfs_base64: %s" % em, "cron.maint_db_dump_dbfs_base64", dbo, sys.exc_info())

def maint_db_dump_dbfs_files(dbo: Database):
    try:
        for x in dbupdate.dump_dbfs_files(dbo):
            print(x)
    except:
        em = str(sys.exc_info()[0])
        al.error("FAIL: uncaught error running maint_db_dump_dbfs_files: %s" % em, "cron.maint_db_dump_dbfs_files", dbo, sys.exc_info())

def maint_db_dump_lookups(dbo: Database):
    try:
        for x in dbupdate.dump_lookups(dbo):
            print(x)
    except:
        em = str(sys.exc_info()[0])
        al.error("FAIL: uncaught error running maint_db_dump_lookups: %s" % em, "cron.maint_db_dump_lookups", dbo, sys.exc_info())

def maint_db_dump_merge(dbo: Database):
    try:
        for x in dbupdate.dump_merge(dbo):
            print(x)
    except:
        em = str(sys.exc_info()[0])
        al.error("FAIL: uncaught error running maint_db_dump_merge: %s" % em, "cron.maint_db_dump_merge", dbo, sys.exc_info())

def maint_db_dump_smcom(dbo: Database):
    try:
        for x in dbupdate.dump_smcom(dbo):
            print(x)
    except:
        em = str(sys.exc_info()[0])
        al.error("FAIL: uncaught error running maint_db_dump_smcom: %s" % em, "cron.maint_db_dump_smcom", dbo, sys.exc_info())

def maint_db_dump_animalcsv(dbo: Database):
    try:
        print(utils.bytes2str(utils.csv(dbo.locale, animal.get_animal_find_advanced(dbo, { "logicallocation" : "all", "includedeceased": "true", "includenonshelter": "true" }))))
    except:
        em = str(sys.exc_info()[0])
        al.error("FAIL: uncaught error running maint_db_dump_animalcsv: %s" % em, "cron.maint_db_dump_animalcsv", dbo, sys.exc_info())

def maint_db_dump_personcsv(dbo: Database):
    try:
        print(utils.bytes2str(utils.csv(dbo.locale, person.get_person_find_simple(dbo, "", classfilter="all", includeStaff=True, includeVolunteers=True, limit=0))))
    except:
        em = str(sys.exc_info()[0])
        al.error("FAIL: uncaught error running maint_db_dump_personcsv: %s" % em, "cron.maint_db_dump_personcsv", dbo, sys.exc_info())

def maint_db_dump_zip(dbo: Database):
    try:
        l = dbo.locale
        dbname = dbo.database
        if dbname.find("/") != -1: dbname = dbname[dbname.rfind("/")+1:]
        dbomysql = db.get_dbo("MYSQL")
        dbopg = db.get_dbo("POSTGRESQL")
        dbodb2 = db.get_dbo("DB2")
        dbosqlite = db.get_dbo("SQLITE")
        PATH = f"/tmp/dbdump_{dbname}"
        utils.mkdir(PATH)
        utils.write_text_file(f"{PATH}/dump.sql", utils.generator2str(dbupdate.dump, dbo))
        utils.write_text_file(f"{PATH}/ddl_sqlite.sql", dbupdate.sql_structure(dbosqlite))
        utils.write_text_file(f"{PATH}/ddl_mysql.sql", dbupdate.sql_structure(dbomysql))
        utils.write_text_file(f"{PATH}/ddl_postgresql.sql", dbupdate.sql_structure(dbopg))
        utils.write_text_file(f"{PATH}/ddl_db2.sql", dbupdate.sql_structure(dbodb2))
        utils.write_text_file(f"{PATH}/asm2.sql", utils.generator2str(dbupdate.dump_hsqldb, dbo))
        rows = animal.get_animal_find_advanced(dbo, { "logicallocation" : "all", "filter" : "includedeceased,includenonshelter" })
        additional.append_to_results(dbo, rows, "animal")
        utils.write_binary_file(f"{PATH}/animal.csv", utils.csv(l, rows))
        utils.write_binary_file(f"{PATH}/media.csv", utils.csv(l, media.get_media_export(dbo)))
        utils.write_binary_file(f"{PATH}/medical.csv", utils.csv(l, medical.get_medical_export(dbo)))
        rows = person.get_person_find_simple(dbo, "", includeStaff=True, includeVolunteers=True)
        additional.append_to_results(dbo, rows, "person")
        utils.write_binary_file(f"{PATH}/person.csv", utils.csv(l, rows))
        rows = animalcontrol.get_animalcontrol_find_advanced(dbo, { "filter" : "" }, "system")
        additional.append_to_results(dbo, rows, "incident")
        utils.write_binary_file(f"{PATH}/incident.csv", utils.csv(l, rows))
        utils.write_binary_file(f"{PATH}/licence.csv", utils.csv(l, financial.get_licence_find_simple(dbo, "")))
        utils.write_binary_file(f"{PATH}/payment.csv", utils.csv(l, financial.get_donations(dbo, "m10000")))
        utils.zip_directory(PATH, f"/tmp/{dbname}.zip")
        utils.rmdir(PATH)
        print(f"All data files exported to /tmp/{dbname}.zip")
    except:
        em = str(sys.exc_info()[0])
        al.error("FAIL: uncaught error running maint_db_dump_zip: %s" % em, "cron.maint_db_dump_zip", dbo, sys.exc_info())

def maint_db_install(dbo: Database):
    try:
        dbupdate.install(dbo)
    except:
        em = str(sys.exc_info()[0])
        al.error("FAIL: uncaught error running maint_db_install: %s" % em, "cron.maint_db_install", dbo, sys.exc_info())

def maint_db_reinstall(dbo: Database):
    try:
        dbupdate.reinstall_default_data(dbo)
    except:
        em = str(sys.exc_info()[0])
        al.error("FAIL: uncaught error running maint_db_reinstall: %s" % em, "cron.maint_db_reinstall", dbo, sys.exc_info())

def maint_db_reinstall_default_templates(dbo: Database):
    try:
        dbupdate.install_default_templates(dbo, True)
    except:
        em = str(sys.exc_info()[0])
        al.error("FAIL: uncaught error running maint_db_reinstall_default_templates: %s" % em, "cron.maint_db_reinstall_default_templates", dbo, sys.exc_info())

def maint_db_reinstall_default_onlineforms(dbo: Database):
    try:
        dbupdate.install_default_onlineforms(dbo, True)
    except:
        em = str(sys.exc_info()[0])
        al.error("FAIL: uncaught error running maint_db_reinstall_default_onlineforms: %s" % em, "cron.maint_db_reinstall_default_onlineforms", dbo, sys.exc_info())

def maint_db_replace_html_entities(dbo: Database):
    try:
        dbupdate.replace_html_entities(dbo)
    except:
        em = str(sys.exc_info()[0])
        al.error("FAIL: uncaught error running maint_db_replace_html_entities: %s" % em, "cron.maint_db_replace_html_entities", dbo, sys.exc_info())

def maint_db_reset(dbo: Database):
    try:
        dbupdate.reset_db(dbo)
    except:
        em = str(sys.exc_info()[0])
        al.error("FAIL: uncaught error running maint_db_reset: %s" % em, "cron.maint_db_reset", dbo, sys.exc_info())

def maint_db_delete_orphaned_media(dbo: Database):
    try:
        dbfs.delete_orphaned_media(dbo)
    except:
        em = str(sys.exc_info()[0])
        al.error("FAIL: uncaught error running maint_db_delete_orphaned_media: %s" % em, "cron.maint_db_delete_orphaned_media", dbo, sys.exc_info())

def maint_db_update(dbo: Database):
    """
    Check and run any outstanding database updates
    """
    try:
        # This should never be run at a time when users may be
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

    except:
        em = str(sys.exc_info()[0])
        al.error("FAIL: running db updates: %s" % em, "cron.maint_db_update", dbo, sys.exc_info())

def maint_deduplicate_people(dbo: Database):
    try:
        person.merge_duplicate_people(dbo, "cron")
    except:
        em = str(sys.exc_info()[0])
        al.error("FAIL: uncaught error running maint_deduplicate_people: %s" % em, "cron.maint_deduplicate_people", dbo, sys.exc_info())

def maint_disk_cache(dbo: Database):
    try:
        cachedisk.remove_expired(dbo.database)
    except:
        em = str(sys.exc_info()[0])
        al.error("FAIL: uncaught error running remove_expired: %s" % em, "cron.maint_disk_cache", dbo, sys.exc_info())

def maint_scale_animal_images(dbo: Database):
    try:
        media.scale_all_animal_images(dbo)
    except:
        em = str(sys.exc_info()[0])
        al.error("FAIL: uncaught error running maint_scale_animal_images: %s" % em, "cron.maint_scale_animal_images", dbo, sys.exc_info())

def maint_scale_odts(dbo: Database):
    try:
        media.scale_all_odt(dbo)
    except:
        em = str(sys.exc_info()[0])
        al.error("FAIL: uncaught error running maint_scale_odts: %s" % em, "cron.maint_scale_odts", dbo, sys.exc_info())

def maint_scale_pdfs(dbo: Database):
    try:
        media.scale_all_pdf(dbo)
    except:
        em = str(sys.exc_info()[0])
        al.error("FAIL: uncaught error running maint_scale_pdfs: %s" % em, "cron.maint_scale_pdfs", dbo, sys.exc_info())

def maint_switch_dbfs_storage(dbo: Database):
    try:
        dbfs.switch_storage(dbo)
    except:
        em = str(sys.exc_info()[0])
        al.error("FAIL: uncaught error running maint_dbfs_switch_storage: %s" % em, "cron.maint_switch_dbfs_storage", dbo, sys.exc_info())

def run(dbo: Database, mode: str) -> None:
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
        dbo.timezone_dst = configuration.timezone_dst(dbo)
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
    elif mode == "publish_3pty_sub24":
        publish_3pty_sub24(dbo)
    elif mode == "publish_html":
        publish_html(dbo)
    elif mode == "maint_import_report":
        maint_import_report(dbo)
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
    elif mode == "maint_db_fix_preferred_photos":
        maint_db_fix_preferred_photos(dbo)
    elif mode == "maint_db_dump":
        maint_db_dump(dbo)
    elif mode == "maint_db_dump_dbfs_base64":
        maint_db_dump_dbfs_base64(dbo)
    elif mode == "maint_db_dump_dbfs_files":
        maint_db_dump_dbfs_files(dbo)
    elif mode == "maint_db_dump_lookups":
        maint_db_dump_lookups(dbo)
    elif mode == "maint_db_dump_merge":
        maint_db_dump_merge(dbo)
    elif mode == "maint_db_dump_smcom":
        maint_db_dump_smcom(dbo)
    elif mode == "maint_db_dump_zip":
        maint_db_dump_zip(dbo)
    elif mode == "maint_db_dump_animalcsv":
        maint_db_dump_animalcsv(dbo)
    elif mode == "maint_db_dump_personcsv":
        maint_db_dump_personcsv(dbo)
    elif mode == "maint_db_dump_hsqldb":
        maint_db_dump_hsqldb(dbo)
    elif mode == "maint_db_install":
        maint_db_install(dbo)
    elif mode == "maint_db_reinstall":
        maint_db_reinstall(dbo)
    elif mode == "maint_db_reinstall_default_onlineforms":
        maint_db_reinstall_default_onlineforms(dbo)
    elif mode == "maint_db_reinstall_default_templates":
        maint_db_reinstall_default_templates(dbo)
    elif mode == "maint_db_replace_html_entities":
        maint_db_replace_html_entities(dbo)
    elif mode == "maint_db_reset":
        maint_db_reset(dbo)
    elif mode == "maint_db_update":
        maint_db_update(dbo)
    elif mode == "maint_db_delete_orphaned_media":
        maint_db_delete_orphaned_media(dbo)
    elif mode == "maint_deduplicate_people":
        maint_deduplicate_people(dbo)
    elif mode == "maint_disk_cache":
        maint_disk_cache(dbo)

    elapsed = time.time() - x
    al.info("end %s: elapsed %0.2f secs" % (mode, elapsed), "cron.run", dbo)

def run_all_map_databases(mode: str) -> None:
    for alias in MULTIPLE_DATABASES_MAP.keys():
        dbo = db.get_database(alias)
        dbo.timeout = 0
        dbo.connection = dbo.connect()
        run(dbo, mode)

def run_default_database(mode: str) -> None:
    dbo = db.get_database()
    dbo.timeout = 0
    dbo.connection = dbo.connect()
    run(dbo, mode)

def run_alias(mode: str, alias: str) -> None:
    dbo = db.get_database(alias)
    dbo.alias = alias
    if dbo.database == "FAIL":
        print("Invalid database alias '%s'" % (alias))
    else:
        dbo.timeout = 0
        dbo.connection = dbo.connect()
        run(dbo, mode)

def run_override_database(mode: str, dbtype: str, host: str, port: int, username: str, password: str, database: str, alias: str) -> None:
    dbo = db.get_dbo(dbtype)
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

def print_usage() -> None:
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
    print("       maint_db_dump_dbfs_base64 - dump the dbfs table and include all content as base64")
    print("       maint_db_dump_dbfs_files - dump the dbfs table, output as files to /tmp/dump_dbfs_files")
    print("       maint_db_dump_merge - produce a dump of INSERT statements, renumbering IDs to +100000")
    print("       maint_db_dump_animalcsv - produce a CSV of animal/adoption/owner data")
    print("       maint_db_dump_personcsv - produce a CSV of person data")
    print("       maint_db_dump_hsqldb - produce a complete HSQLDB file for ASM2")
    print("       maint_db_dump_lookups - produce an SQL dump of lookup tables only")
    print("       maint_db_dump_smcom - produce an SQL dump for import into sheltermanager.com")
    print("       maint_db_dump_zip - produce a zip file containing all export/dump files")
    print("       maint_db_fix_preferred_photos - fix/reset preferred flags for all photo media to latest")
    print("       maint_db_install - install structure/data into a new empty database")
    print("       maint_db_reinstall - reinstall default lookup data and templates to current locale")
    print("       maint_db_reinstall_default_onlineforms - reloads default online forms")
    print("       maint_db_reinstall_default_templates - reloads default document/publishing templates")
    print("       maint_db_replace_html_entities - substitutes html entities for unicode in all text fields")
    print("       maint_db_reset - wipe the db of all but lookup data")
    print("       maint_db_delete_orphaned_media - delete all entries from the dbfs not in media")
    print("       maint_db_update - run any outstanding database updates")
    print("       maint_deduplicate_people - automatically merge duplicate people records")
    print("       maint_disk_cache - remove expired entries from the disk cache")
    print("       maint_import_report - import report txt set file in ASM3_REPORT env")
    print("       maint_recode_all - regenerate all animal codes")
    print("       maint_recode_shelter - regenerate animals codes for all shelter animals")
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

