
import asm3.al
import asm3.audit
import asm3.cachemem
import asm3.configuration
import asm3.db
import asm3.dbupdate
import asm3.lookups
import asm3.i18n
import asm3.smcom
import asm3.utils

from asm3.sitedefs import BASE_URL

import os
import sys

# Security flags
ADD_ANIMAL                      = "aa"
CHANGE_ANIMAL                   = "ca"
VIEW_ANIMAL                     = "va"
DELETE_ANIMAL                   = "da"
CLONE_ANIMAL                    = "cloa"
MERGE_ANIMAL                    = "ma"

GENERATE_DOCUMENTS              = "gaf"
MODIFY_NAME_DATABASE            = "mand"
MAIL_MERGE                      = "mmeo"

ADD_REPO_DOCUMENT               = "ard"
DELETE_REPO_DOCUMENT            = "drd"
VIEW_REPO_DOCUMENT              = "vrd"

ADD_BOARDING                    = "abi"
VIEW_BOARDING                   = "vbi"
CHANGE_BOARDING                 = "cbi"
DELETE_BOARDING                 = "dbi"

ADD_CLINIC                      = "acl"
VIEW_CLINIC                     = "vcl"
CHANGE_CLINIC                   = "ccl"
DELETE_CLINIC                   = "dcl"

ADD_VACCINATION                 = "aav"
VIEW_VACCINATION                = "vav"
CHANGE_VACCINATION              = "cav"
DELETE_VACCINATION              = "dav"
BULK_COMPLETE_VACCINATION       = "bcav"

ADD_TEST                        = "aat"
VIEW_TEST                       = "vat"
CHANGE_TEST                     = "cat"
DELETE_TEST                     = "dat"

ADD_MEDICAL                     = "maam"
CHANGE_MEDICAL                  = "mcam"
VIEW_MEDICAL                    = "mvam"
DELETE_MEDICAL                  = "mdam"
BULK_COMPLETE_MEDICAL           = "bcam"

ADD_MEDIA                       = "aam"
CHANGE_MEDIA                    = "cam"
VIEW_MEDIA                      = "vam"
DELETE_MEDIA                    = "dam"

ADD_DIET                        = "daad"
CHANGE_DIET                     = "dcad"
DELETE_DIET                     = "ddad"
VIEW_DIET                       = "dvad"

ADD_COST                        = "caad"
CHANGE_COST                     = "ccad"
DELETE_COST                     = "cdad"
VIEW_COST                       = "cvad"

ADD_MOVEMENT                    = "aamv"
CHANGE_MOVEMENT                 = "camv"
VIEW_MOVEMENT                   = "vamv"
DELETE_MOVEMENT                 = "damv"

ADD_ACCOUNT                     = "aac"
VIEW_ACCOUNT                    = "vac"
CHANGE_ACCOUNT                  = "cac"
CHANGE_TRANSACTIONS             = "ctrx"
DELETE_ACCOUNT                  = "dac"

ADD_PERSON                      = "ao"
CHANGE_PERSON                   = "co"
VIEW_PERSON                     = "vo"
VIEW_STAFF                      = "vso"
VIEW_VOLUNTEER                  = "vvo"
DELETE_PERSON                   = "do"
EMAIL_PERSON                    = "emo"
MERGE_PERSON                    = "mo"
VIEW_PERSON_LINKS               = "volk"

ADD_INVESTIGATION               = "aoi"
CHANGE_INVESTIGATION            = "coi"
DELETE_INVESTIGATION            = "doi"
VIEW_INVESTIGATION              = "voi"

ADD_VOUCHER                     = "vaov"
CHANGE_VOUCHER                  = "vcov"
DELETE_VOUCHER                  = "vdov"
VIEW_VOUCHER                    = "vvov"

ADD_DONATION                    = "oaod"
CHANGE_DONATION                 = "ocod"
DELETE_DONATION                 = "odod"
VIEW_DONATION                   = "ovod"

ADD_LOG                         = "ale"
CHANGE_LOG                      = "cle"
DELETE_LOG                      = "dle"
VIEW_LOG                        = "vle"

ADD_ONLINE_FORMS                = "aof"
VIEW_ONLINE_FORMS               = "vof"
CHANGE_ONLINE_FORMS             = "eof"
DELETE_ONLINE_FORMS             = "dof"
VIEW_INCOMING_FORMS             = "vif"
DELETE_INCOMING_FORMS           = "dif"

SYSTEM_MENU                     = "asm"
SYSTEM_OPTIONS                  = "cso"
PUBLISH_OPTIONS                 = "cpo"
MODIFY_ADDITIONAL_FIELDS        = "maf"
MODIFY_LOOKUPS                  = "ml"
MODIFY_DOCUMENT_TEMPLATES       = "mdt"
EXPORT_ANIMAL_CSV               = "eav"
IMPORT_CSV_FILE                 = "icv"
TRIGGER_BATCH                   = "tbp"
ADD_USER                        = "asu"
EDIT_USER                       = "esu"
EDIT_DIARY_TASKS                = "edt"
RUN_DB_UPDATE                   = "rdbu"
RUN_DB_DIAGNOSTIC               = "rdbd"
USE_SQL_INTERFACE               = "usi"
USE_INTERNET_PUBLISHER          = "uipb"
VIEW_AUDIT_TRAIL                = "vatr"

ADD_REPORT                      = "ccr"
VIEW_REPORT                     = "vcr"
CHANGE_REPORT                   = "hcr"
DELETE_REPORT                   = "dcr"
EXPORT_REPORT                   = "excr"

ADD_DIARY                       = "adn"
VIEW_DIARY                      = "vdn"
EDIT_ALL_DIARY_NOTES            = "eadn"
EDIT_MY_DIARY_NOTES             = "emdn"
EDIT_COMPLETED_NOTES            = "ecdn"
BULK_COMPLETE_NOTES             = "bcn"
DELETE_DIARY                    = "ddn"
PRINT_DIARY                     = "pdn"
PRINT_VACCINATION_DIARY         = "pvd"

ADD_LOST_ANIMAL                 = "ala"
ADD_FOUND_ANIMAL                = "afa"
CHANGE_LOST_ANIMAL              = "cla"
CHANGE_FOUND_ANIMAL             = "cfa"
DELETE_LOST_ANIMAL              = "dla"
DELETE_FOUND_ANIMAL             = "dfa"
VIEW_LOST_ANIMAL                = "vla"
VIEW_FOUND_ANIMAL               = "vfa"
MATCH_LOST_FOUND                = "mlaf"

VIEW_TRANSPORT                  = "vtr"
ADD_TRANSPORT                   = "atr"
DELETE_TRANSPORT                = "dtr"
CHANGE_TRANSPORT                = "ctr"

VIEW_WAITING_LIST               = "vwl"
ADD_WAITING_LIST                = "awl"
DELETE_WAITING_LIST             = "dwl"
CHANGE_WAITING_LIST             = "cwl"
BULK_COMPLETE_WAITING_LIST      = "bcwl"

ADD_INCIDENT                    = "aaci"
VIEW_INCIDENT                   = "vaci"
CHANGE_INCIDENT                 = "caci"
DELETE_INCIDENT                 = "daci"
DISPATCH_INCIDENT               = "cacd"
RESPOND_INCIDENT                = "cacr"

ADD_CITATION                    = "aacc"
VIEW_CITATION                   = "vacc"
CHANGE_CITATION                 = "cacc"
DELETE_CITATION                 = "dacc"

ADD_TRAPLOAN                    = "aatl"
VIEW_TRAPLOAN                   = "vatl"
CHANGE_TRAPLOAN                 = "catl"
DELETE_TRAPLOAN                 = "datl"

ADD_LICENCE                     = "aapl"
VIEW_LICENCE                    = "vapl"
CHANGE_LICENCE                  = "capl"
DELETE_LICENCE                  = "dapl"

ADD_ROTA                        = "aoro"
VIEW_ROTA                       = "voro"
VIEW_STAFF_ROTA                 = "vsro"
CHANGE_ROTA                     = "coro"
DELETE_ROTA                     = "doro"

ADD_LITTER                      = "all"
VIEW_LITTER                     = "vll"
DELETE_LITTER                   = "dll"
CHANGE_LITTER                   = "cll"

ADD_STOCKLEVEL                  = "asl"
VIEW_STOCKLEVEL                 = "vsl"
DELETE_STOCKLEVEL               = "dsl"
CHANGE_STOCKLEVEL               = "csl"

ADD_EVENT                       = "ae"
VIEW_EVENT                      = "ve"
CHANGE_EVENT                    = "ce"
DELETE_EVENT                    = "de"
VIEW_EVENT_ANIMALS              = "vea"
CHANGE_EVENT_ANIMALS            = "cea"
LINK_EVENT_MOVEMENT             = "lem"

def check_permission(session, flag, message = ""):
    """
    Throws an ASMPermissionError if the flag is not in the map
    """
    if "superuser" not in session or "securitymap" not in session: raise asm3.utils.ASMPermissionError("Invalid session")
    l = session.locale
    if session.superuser == 1: return
    if not has_security_flag(session.securitymap, flag):
        if message == "":
            message = asm3.i18n._("Forbidden", l)
        raise asm3.utils.ASMPermissionError(message)

def check_permission_bool(session, flag):
    """
    Returns True if a user has permission to do something
    """
    if "superuser" not in session or "securitymap" not in session: return False
    if session.superuser == 1: return True
    if has_security_flag(session.securitymap, flag): return True
    return False

def check_permission_map(l, superuser, securitymap, flag):
    """
    Throws an ASMPermissionError if the flag is not in the map
    """
    if superuser == 1: return
    if not has_security_flag(securitymap, flag):
        raise asm3.utils.ASMPermissionError(asm3.i18n._("Forbidden", l))

def has_security_flag(securitymap, flag):
    """
    Returns true if the given flag is in the given map
    """
    perms = securitymap.split("*")
    return flag + " " in perms

def add_security_flag(securitymap, flag):
    """
    Adds a security flag to a map and returns the new map
    """
    if not has_security_flag(securitymap, flag):
        securitymap += flag + " *"
    return securitymap

def authenticate(dbo, username, password):
    """
    Authenticates whether a username and password are valid.
    Returns None if authentication failed, or a user row
    """
    username = username.upper()
    # Do not use any login inputs directly in database queries
    for u in dbo.query("SELECT ID, UserName, Password FROM users"):
        if username == u.USERNAME.upper():
            dbpassword = u.PASSWORD.strip()
            if verify_password(password, dbpassword):
                u = dbo.query("SELECT * FROM users WHERE ID=?", [u.ID])
                if len(u) == 1: return u[0]
    return None

def authenticate_ip(user, remoteip):
    """
    Tests whether the user's remoteip fits into any IP restriction
    set on the user object.
    If IP restriction is not present or blank, we let them through.
    Returns true for successful authentication.
    user: A row from the user table
    remoteip: The user's remote ip address
    """
    if "IPRESTRICTION" not in user:
        return True
    if user.IPRESTRICTION is None or user.IPRESTRICTION == "":
        return True
    # Restriction is a space separated list of addresses in CIDR
    # notation.
    restrictions = user.IPRESTRICTION.split(" ")
    for r in restrictions:
        if r.find(".") != -1:
            # IPv4 restriction
            address = r
            size = "32"
            # if there's a slash, extract CIDR size
            if r.count("/") == 1:
                address, size = r.split("/")
            # We should have 4 numbers for the dotted quads
            if address.count(".") != 3:
                continue
            q1, q2, q3, q4 = address.split(".")
            # Depending on the size selected, we check a smaller or
            # larger chunk of the remote ip for a match.
            if size == "32" and remoteip == address:
                return True
            if size == "24" and remoteip.startswith("%s.%s.%s." % (q1, q2, q3)):
                return True
            if size == "16" and remoteip.startswith("%s.%s." % (q1, q2)):
                return True
            if size == "8" and remoteip.startswith("%s." % q1):
                return True
        elif r.find(":") != -1:
            # IPv6 restriction
            # This is much simpler, treat the restriction as a prefix
            # and verify that the remoteip we've been given starts
            # with the prefix
            if remoteip.startswith(r):
                return True
    return False

def hash_password(plaintext, scheme = "pbkdf2"):
    """
    Returns a one-way hash of a password string.
    plaintext: The password to hash
    scheme:    md5, md5java, pbkdf2 or plain (no hash)
    """
    if scheme is None or scheme == "" or scheme == "plain":
        return "plain:%s" % plaintext
    elif scheme == "pbkdf2":
        PBKDF2_ITERATIONS = 10000
        PBKDF2_ALGORITHM = "sha1"
        salt = asm3.utils.base64encode(os.urandom(16))
        h = asm3.utils.pbkdf2_hash_hex(plaintext, salt, PBKDF2_ALGORITHM, PBKDF2_ITERATIONS)
        return "pbkdf2:%s:%s:%d:%s" % (PBKDF2_ALGORITHM, asm3.utils.bytes2str(salt), PBKDF2_ITERATIONS, h)
    elif scheme == "md5" or scheme == "md5java":
        h = asm3.utils.md5_hash_hex(plaintext)
        if scheme == "md5java" and h.startswith("0"): h = h[1:]
        return "%s:%s" % (scheme, h)

def verify_password(plaintext, passwordhash):
    """
    Verifies whether or not password "plaintext" hashes to the same 
    value as passwordhash.
    Hash scheme is auto detected from passwordhash itself.
    """
    if passwordhash.startswith("pbkdf2:"):
        scheme, algorithm, salt, iterations, phash = passwordhash.split(":")
        return asm3.utils.pbkdf2_hash_hex(plaintext, salt, algorithm, int(iterations)) == phash
    elif passwordhash.startswith("plain:"):
        return plaintext == passwordhash[passwordhash.find(":")+1:]
    elif passwordhash.startswith("md5:"):
        return hash_password(plaintext, "md5") == passwordhash
    elif passwordhash.startswith("md5java:"):
        return hash_password(plaintext, "md5java") == passwordhash
    else:
        # Fall back to assuming historic undecorated md5
        md5py = asm3.utils.md5_hash_hex(plaintext)
        md5java = md5py
        if md5java.startswith("0"): md5java = md5java[1:]
        return passwordhash == md5py or passwordhash == md5java

def change_password(dbo, username, oldpassword, newpassword):
    """
    Changes the password for a user
    """
    l = dbo.locale
    if None is authenticate(dbo, username, oldpassword):
        raise asm3.utils.ASMValidationError(asm3.i18n._("Password is incorrect.", l))
    dbo.execute("UPDATE users SET Password = ? WHERE UserName LIKE ?", (hash_password(newpassword), username))

def get_real_name(dbo, username):
    """
    Returns a user's real name
    """
    return dbo.query_string("SELECT RealName FROM users WHERE UserName LIKE ?", [username])

def get_roles(dbo):
    """
    Returns a list of all system roles
    """
    return dbo.query("SELECT * FROM role ORDER BY Rolename")

def get_roles_ids_for_user(dbo, username):
    """
    Returns a list of role ids a user is in
    """
    rolesd = dbo.query("SELECT RoleID FROM userrole INNER JOIN users ON users.ID = userrole.UserID WHERE users.UserName = ?", [username])
    roles = []
    for r in rolesd:
        roles.append(r.ROLEID)
    return roles

def get_roles_for_user(dbo, user):
    """
    Returns a list of roles a user is in
    """
    rows = dbo.query("SELECT r.Rolename FROM role r " \
        "INNER JOIN userrole ur ON ur.RoleID = r.ID " \
        "INNER JOIN users u ON u.ID = ur.UserID " \
        "WHERE u.UserName LIKE ? " \
        "ORDER BY r.Rolename", [user])
    roles = []
    for r in rows:
        roles.append(r.ROLENAME)
    return roles

def get_security_map(dbo, userid):
    """
    Returns the security map for a user by id, which is an aggregate of all
    the roles they have.
    """
    rv = ""
    maps = dbo.query("SELECT role.SecurityMap FROM role " \
        "INNER JOIN userrole ON role.ID = userrole.RoleID " \
        "WHERE userrole.UserID = ?", [userid])
    for m in maps:
        rv += str(m.SECURITYMAP)
    return rv

def get_site(dbo, username):
    """
    Returns a user's site or 0 if it doesn't have one.
    If this is being called as part of a CSV import, or incoming form, 
    we remove those prefixes from the username first.
    """
    try:
        if username.startswith("import/"): username = username[7:]
        if username.startswith("form/"): username = username[5:]
        return dbo.query_int("SELECT SiteID FROM users WHERE UserName LIKE ?", [username])
    except:
        return 0

def get_diary_forlist(dbo):
    """
    Returns a list of all roles, plus users who are valid targets for diary notes
    (ie. have the VIEW_DIARY permission)
    List returned contains USERNAME which is both roles and users
    """
    users = get_users_and_roles(dbo)
    out = []
    for u in users:
        # We only need to look up the security flags for non-super users and non-roles
        securitymap = ""
        if u.ISROLE == 0 or u.SUPERUSER == 0: 
            securitymap = get_security_map(dbo, u.ID)
        if u.ISROLE == 1 or u.SUPERUSER == 1 or has_security_flag(securitymap, VIEW_DIARY):
            out.append(u)
    return out

def get_users_and_roles(dbo):
    """
    Returns a single list of all users and roles together, with USERNAME containing the
    name of both roles and users.
    """
    return dbo.query("SELECT ID, UserName, 0 AS IsRole, SuperUser FROM users " \
        "UNION SELECT ID, Rolename AS UserName, 1 AS IsRole, 0 AS SuperUser FROM role ORDER BY UserName")

def get_users(dbo, user=""):
    """
    Returns a list of all (or a list with a single) system users and a pipe separated list of their roles
    """
    users = dbo.query("SELECT * FROM users ORDER BY UserName")
    roles = dbo.query("SELECT ur.*, r.RoleName FROM userrole ur INNER JOIN role r ON ur.RoleID = r.ID")
    out = []
    for u in users:
        if user != "" and user.upper() != u.USERNAME.upper(): continue
        roleids = []
        rolenames = []
        for r in roles:
            if r.USERID == u.ID:
                roleids.append(str(r.ROLEID))
                rolenames.append(str(r.ROLENAME))
        u.ROLEIDS = "|".join(roleids)
        u.ROLES = "|".join(rolenames)
        out.append(u)
    return out

def get_user(dbo, user):
    """
    Returns a single user account by name. Returns None if no user account is found.
    """
    return dbo.first_row( get_users(dbo, user) )

def get_active_users(dbo):
    """
    Returns a string containing the active/logged in users on the system
    USERNAME, SINCE, MESSAGES
    """
    return asm3.utils.nulltostr(asm3.cachemem.get("activity_%s" % dbo.database))

def is_user_valid(dbo, user):
    """
    Returns True if user both exists in the database and does not have DisableLogin set.
    This function is called by ASMEndpoint.is_loggedin for nearly every request
    so it uses a 24 hour memory cache to keep the list rather than going to the database.
    The functions in here that add, change or delete users will invalidate that cache.
    """
    users = asm3.cachemem.get("usernames_%s" % dbo.database)
    if users is None:
        ul = dbo.query("SELECT UserName FROM users WHERE (DisableLogin Is Null OR DisableLogin=0)")
        users = []
        for u in ul:
            users.append(u.USERNAME)
        asm3.cachemem.put("usernames_%s" % dbo.database, users, 86400)
    return user in users

def logout(session, remoteip = "", useragent = ""):
    """
    Logs the user session out
    """
    try:
        asm3.al.info("%s logged out" % session.user, "users.logout", session.dbo)
        asm3.audit.logout(session.dbo, session.user, remoteip, useragent)
        session.user = None
        session.kill()
    except:
        pass

def update_user_activity(dbo, user, timenow = True):
    """
    If timenow is True, updates this user's last activity time to now.
    If timenow is False, removes this user from the active list.
    """
    if dbo is None or user is None: return
    ac = asm3.utils.nulltostr(asm3.cachemem.get("activity_%s" % dbo.database))
    # Prune old activity and remove the current user
    nc = []
    for a in ac.split(","):
        # If there are any errors reading or parsing
        # the entry, skip it
        try:
            if a != "":
                u, d = a.split("=")
                # if the last seen value was more than an hour ago, 
                # don't bother adding that user
                p = asm3.i18n.parse_date("%Y-%m-%d %H:%M:%S", d)
                if asm3.i18n.subtract_hours(dbo.now(), 1) > p:
                    continue
                # Don't add the current user
                if u == user:
                    continue
                nc.append(a)
        except:
            continue
    # Add this user with the new time 
    if timenow: 
        nc.append("%s=%s" % (user, asm3.i18n.format_date(dbo.now(), "%Y-%m-%d %H:%M:%S")))
    asm3.cachemem.put("activity_%s" % dbo.database, ",".join(nc), 3600 * 8)

def get_personid(dbo, user):
    """
    Returns the personid for a user or 0 if it doesn't have one
    """
    return dbo.query_int("SELECT OwnerID FROM users WHERE UserName LIKE ?", [user])

def get_location_filter(dbo, user):
    """
    Returns the location filter (comma separated list of IDs) 
    for a user, or "" if it doesn't have one.
    """
    return dbo.query_string("SELECT LocationFilter FROM users WHERE UserName LIKE ?", [user])

def insert_user_from_form(dbo, username, post):
    """
    Creates a user record from posted form data. Uses
    the roles key (which should be a comma separated list of
    role ids) to create userrole records.
    """
    # Verify the username is unique
    l = dbo.locale
    if 0 != dbo.query_int("SELECT COUNT(*) FROM users WHERE LOWER(UserName) LIKE LOWER(?)", [post["username"]]):
        raise asm3.utils.ASMValidationError(asm3.i18n._("Username '{0}' already exists", l).format(post["username"]))

    nuserid = dbo.insert("users", {
        "UserName":             post["username"],
        "RealName":             post["realname"],
        "EmailAddress":         post["email"],
        "Password":             hash_password(post["password"]),
        "EnableTOTP":           0,
        "OTPSecret":            asm3.utils.otp_secret(),
        "SuperUser":            post.integer("superuser"),
        "DisableLogin":         post.integer("disablelogin"),
        "RecordVersion":        0,
        "SecurityMap":          "dummy",
        "OwnerID":              post.integer("person"),
        "SiteID":               post.integer("site"),
        "LocationFilter":       post["locationfilter"],
        "IPRestriction":        post["iprestriction"]
    }, username, setCreated=False)

    dbo.delete("userrole", "UserID=%d" % nuserid)
    roles = post["roles"].strip()
    if roles != "":
        for rid in roles.split(","):
            if rid.strip() != "":
                dbo.insert("userrole", { "UserID": nuserid, "RoleID": rid }, generateID=False)

    # Invalidate the cache of usernames
    asm3.cachemem.delete("usernames_%s" % dbo.database)

    # If the option was set, email these new credentials to the user
    # Note: we do not audit the actual email content to prevent plaintext passwords appearing in the audit log
    if post.boolean("emailcred") and post["email"] != "":
        fromaddress = asm3.configuration.email(dbo)
        subject = asm3.i18n._("New user account", l)
        url = "%s/login" % BASE_URL
        if asm3.smcom.active(): url = asm3.smcom.get_login_url(dbo)
        bodynopass = "%s:\n\n%s: {url}\n%s: {user}\n%s: {pass}" % (
            asm3.i18n._("A new ASM user account has been set up for you", l), 
            asm3.i18n._("URL", l), asm3.i18n._("Username", l), asm3.i18n._("Password", l) )
        bodynopass = bodynopass.replace("{url}", url)
        bodynopass = bodynopass.replace("{user}", post["username"])
        body = bodynopass.replace("{pass}", post["password"])
        asm3.utils.send_email(dbo, fromaddress, post["email"], "", "", subject, body, "plain", exceptions=False)
        if asm3.configuration.audit_on_send_email(dbo): 
            asm3.audit.email(dbo, username, fromaddress, post["email"], "", "", subject, bodynopass)

    return nuserid

def update_user_settings(dbo, username, email = "", realname = "", locale = "", theme = "", signature = "", enable_totp = 0):
    """
    Updates the user account settings for email, name, locale, theme and signature
    """
    userid = dbo.query_int("SELECT ID FROM users WHERE Username = ?", [username])
    dbo.update("users", userid, {
        "RealName":         realname,
        "EmailAddress":     email,
        "ThemeOverride":    theme,
        "LocaleOverride":   locale,
        "EnableTOTP":       enable_totp,
        "Signature":        signature
    }, username, setLastChanged=False)

def update_user_otp_secret(dbo, userid, secret):
    """
    Updates the OTP secret for a user account
    """
    dbo.update("users", userid, { "OTPSecret": secret })

def update_user_from_form(dbo, username, post):
    """
    Updates a user record from posted form data
    Uses the roles key (which should be a comma separated list of
    role ids) to create userrole records.
    """
    userid = post.integer("userid")
    dbo.update("users", userid, {
        "RealName":         post["realname"],
        "EmailAddress":     post["email"],
        "EnableTOTP":       post.boolean("enabletotp"),
        "SuperUser":        post.integer("superuser"),
        "DisableLogin":     post.integer("disablelogin"),
        "OwnerID":          post.integer("person"),
        "SiteID":           post.integer("site"),
        "LocationFilter":   post["locationfilter"],
        "IPRestriction":    post["iprestriction"]
    }, username, setLastChanged=False)

    dbo.delete("userrole", "UserID=%d" % userid)
    roles = post["roles"].strip()
    if roles != "":
        for rid in roles.split(","):
            if rid.strip() != "":
                dbo.insert("userrole", { "UserID": userid, "RoleID": rid }, generateID=False)

    # Invalidate the cache of usernames
    asm3.cachemem.delete("usernames_%s" % dbo.database)

def delete_user(dbo, username, uid):
    """
    Deletes the selected user
    """
    dbo.delete("userrole", "UserID=%d" % uid)
    dbo.delete("users", uid, username)
    # Invalidate the cache of usernames
    asm3.cachemem.delete("usernames_%s" % dbo.database)

def insert_role_from_form(dbo, username, post):
    """
    Creates a role record from posted form data. 
    """
    return dbo.insert("role", {
        "Rolename":     post["rolename"],
        "SecurityMap":  post["securitymap"]
    }, username, setCreated=False)

def update_role_from_form(dbo, username, post):
    """
    Updates a role record from posted form data
    """
    dbo.update("role", post.integer("roleid"), {
        "Rolename":     post["rolename"],
        "SecurityMap":  post["securitymap"]
    }, username, setLastChanged=False)

def delete_role(dbo, username, rid):
    """
    Deletes the selected role. If it's in use, throws an ASMValidationError
    """
    l = dbo.locale
    if dbo.query_int("SELECT COUNT(*) FROM userrole WHERE RoleID = ?", [rid]) > 0:
        raise asm3.utils.ASMValidationError(asm3.i18n._("Role is in use and cannot be deleted.", l))

    dbo.delete("accountsrole", "RoleID=%d" % rid)
    dbo.delete("animalcontrolrole", "RoleID=%d" % rid)
    dbo.delete("customreportrole", "RoleID=%d" % rid)
    dbo.delete("role", rid, username)

def reset_password(dbo, userid, password):
    """
    Resets the password for the given user to "password".
    Also, clears 2FA from the account.
    """
    dbo.update("users", userid, { "Password": hash_password(password), "EnableTOTP": 0 })

def update_session(dbo, session, username):
    """
    Loads the session data for the username given.
    Triggers reloading of config.js by changing config_ts
    """
    user = get_user(dbo, username)
    session.dbo = dbo
    session.user = user.USERNAME
    session.userid = user.ID
    session.superuser = user.SUPERUSER
    locale = asm3.configuration.locale(dbo)
    if "LOCALEOVERRIDE" in user and user.LOCALEOVERRIDE and user.LOCALEOVERRIDE != "": 
        asm3.al.debug("%s: locale override of %s" % (session.user, user.LOCALEOVERRIDE), "users.update_session", dbo)
        locale = user.LOCALEOVERRIDE
    session.locale = locale
    dbo.locale = session.locale
    theme = "asm"
    if "THEMEOVERRIDE" in user and user.THEMEOVERRIDE and user.THEMEOVERRIDE != "":
        asm3.al.debug("%s:theme override of %s" % (session.user, user.THEMEOVERRIDE), "users.update_session", dbo)
        theme = user.THEMEOVERRIDE
    session.theme = theme
    if not dbo.is_large_db:
        dbo.is_large_db = dbo.query_int("SELECT COUNT(*) FROM owner") > 4000 or \
            dbo.query_int("SELECT COUNT(*) FROM animal") > 2000
    session.securitymap = get_security_map(dbo, user.ID)
    session.roles = ""
    session.roleids = ""
    session.siteid = 0
    session.locationfilter = ""
    session.visibleanimalids = ""
    if "ROLES" in user: session.roles = user.ROLES
    if "ROLEIDS" in user: session.roleids = user.ROLEIDS
    if "SITEID" in user: session.siteid = asm3.utils.cint(user.SITEID)
    if "LOCATIONFILTER" in user: session.locationfilter = asm3.utils.nulltostr(user.LOCATIONFILTER)
    if "OWNERID" in user: session.staffid = user.OWNERID
    # If the user has a location filter that involves a filtered list of animals linked to them, load them now.
    if "LOCATIONFILTER" in user and user.LOCATIONFILTER != "":
        af = []
        # My Fosters
        if user.LOCATIONFILTER.find("-12") != -1:
            af += dbo.query("SELECT AnimalID FROM adoption WHERE MovementType=2 AND OwnerID=? AND MovementDate<=? AND (ReturnDate Is Null OR ReturnDate>?)", \
                ( user.OWNERID, dbo.today(), dbo.today() ))
        # My Coordinated Animals
        if user.LOCATIONFILTER.find("-13") != -1:
            af += dbo.query("SELECT ID AS AnimalID FROM animal WHERE Archived=0 AND AdoptionCoordinatorID=?", [user.OWNERID])
        va = []
        for r in af:
            va.append(str(r.ANIMALID))
        session.visibleanimalids = ",".join(va)
    session.config_ts = asm3.i18n.format_date(asm3.i18n.now(), "%Y%m%d%H%M%S")

def web_login(post, session, remoteip, useragent, path):
    """
    Performs a login and sets up the user's session.
    NOTE: ASM3 will no longer allow login on ASM2 databases due to update_session above calling
          get_user (which relies on the role tables existing). You should run cron.maint_db_update
          to update the database before attempting to login.
    Returns the username on successful login, or:
        FAIL        - problem with user/pass/account/ip
        DISABLED    - The database is disabled
        WRONGSERVER - The database is not on this server
        ASK2FA      - User has 2FA enabled, challenge for code
        BAD2FA      - 2FA enabled and OTP does not match
    """
    database = post["database"]
    username = post["username"]
    password = post["password"]
    onetimepass = post["onetimepass"]
    mobileapp = post["mobile"] == "true"
    rememberme = post["rememberme"] == "on"
    nologconnection = post["nologconnection"] == "true"
    if len(username) > 100:
        username = username[0:100]

    dbo = asm3.db.get_database(database)

    if dbo.database in ("FAIL", "DISABLED", "WRONGSERVER"):
        return dbo.database

    # Connect to the database and authenticate the username and password
    user = authenticate(dbo, username, password)

    if user is None:
        asm3.al.error("database:%s username:%s password:%s failed authentication from %s [%s]" % (database, username, password, remoteip, useragent), "users.web_login", dbo)
        return "FAIL"

    if not authenticate_ip(user, remoteip):
        asm3.al.error("user %s from %s [%s] failed ip restriction check '%s'" % (username, remoteip, useragent, user.IPRESTRICTION), "users.web_login", dbo)
        return "FAIL"

    # Check if this user has been disabled from logging in
    if "DISABLELOGIN" in user and user.DISABLELOGIN == 1:
        asm3.al.error("user %s from %s [%s] failed as account has logins disabled" % (username, remoteip, useragent), "users.web_login", dbo)
        return "FAIL"

    # If the user has 2FA enabled, check it
    if "ENABLETOTP" in user and "OTPSECRET" in user and user.ENABLETOTP == 1:
        if onetimepass == "":
            asm3.al.debug("user %s has 2FA enabled and no code has been given" % username, "users.web_login", dbo)
            return "ASK2FA"
        if onetimepass != str(asm3.utils.totp(user.OTPSECRET)):
            asm3.al.error("user %s failed OTP check" % username, "users.web_login", dbo)
            return "BAD2FA"

    asm3.al.info("%s successfully authenticated from %s [%s]" % (username, remoteip, useragent), "users.web_login", dbo)

    try:
        dbo.locked = asm3.configuration.smdb_locked(dbo)
        dbo.timezone = asm3.configuration.timezone(dbo)
        dbo.timezone_dst = asm3.configuration.timezone_dst(dbo)
        dbo.installpath = path
        dbo.locale = asm3.configuration.locale(dbo)
        session.nologconnection = nologconnection
        session.mobileapp = mobileapp 
        update_session(dbo, session, user.USERNAME)
    except:
        asm3.al.error("failed setting up session: %s" % str(sys.exc_info()[0]), "users.web_login", dbo, sys.exc_info())
        return "FAIL"

    try:
        # Mark the user logged in
        if not nologconnection: 
            asm3.audit.login(dbo, username, remoteip, useragent)
        asm3.al.info("%s logged in" % user.USERNAME, "users.login", dbo)
        update_user_activity(dbo, user.USERNAME)
    except:
        asm3.al.error("failed updating user activity: %s" % str(sys.exc_info()[0]), "users.web_login", dbo, sys.exc_info())

    try:
        # Did the user request "remember me"? If so, generate a token
        # for them and remember the user for 2 weeks
        if rememberme:
            token = asm3.utils.uuid_str()
            asm3.cachemem.put(token, "%s|%s|%s" % (database, username, password), 86400*14)
            return "%s|%s" % (user.USERNAME, token)
    except:
        asm3.al.error("failed getting remember me: %s" % str(sys.exc_info()[0]), "users.web_login", dbo, sys.exc_info())

    return user.USERNAME

