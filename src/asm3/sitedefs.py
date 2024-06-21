
"""
WARNING: YOU SHOULD NO LONGER EDIT THIS FILE BY HAND!
======================================================

Make changes at /etc/asm3.conf instead. If you do not have that file, 
copy it from scripts/asm3.conf.example
"""

# Provides site-wide definitions, reading them from a configuration file
import codecs, os, sys, json
from asm3.typehints import Dict

# The map of values loaded from the config file
cfg = None

def read_config_file() -> None:
    """
    Load the config file into cfg map. Looks for the config file in
    the following places in order:
    1. ASM3_CONF environment variable
    2. $INSTALL_DIR/asm3.conf
    3. $HOME/.asm3.conf
    4. /etc/asm3.conf
    """
    global cfg
    fname = ""
    insconf = os.path.dirname(os.path.abspath(__file__)) + os.sep + ".." + os.sep + "asm3.conf"
    homeconf = os.path.expanduser("~") + os.sep + ".asm3.conf"
    if "ASM3_CONF" in os.environ and os.environ["ASM3_CONF"] != "": fname = os.environ["ASM3_CONF"]
    elif os.path.exists(insconf): fname = insconf
    elif os.path.exists(homeconf): fname = homeconf
    elif os.path.exists("/etc/asm3.conf"): fname = "/etc/asm3.conf"
    if fname == "":
        sys.stderr.write("no config found, using defaults\n")
        cfg = {}
    else:
        sys.stderr.write("config: %s\n" % fname)
        cfg = {}
        with codecs.open(fname, 'r', encoding='utf8') as f:
            lines = f.readlines()
        for l in lines:
            if l.find("#") != -1 and l.find("{") == -1: 
                l = l[0:l.find("#")]
            if l.find("=") != -1:
                k, v = l.split("=", 1)
                cfg[k.strip()] = v.strip()

def get_string(k: str, dv: str = "") -> str:
    global cfg
    if cfg is None: read_config_file()
    if k not in cfg: return dv
    return cfg[k]

def get_boolean(k: str, dv: bool = False) -> bool:
    v = get_string(k)
    if v == "": return dv
    return v == "True" or v == "true"

def get_integer(k: str, dv: int = 0) -> int:
    v = get_string(k)
    if v == "": return dv
    return int(v)

def get_dict(k: str, dv: Dict = {}) -> Dict:
    v = get_string(k)
    if v == "": return dv
    return json.loads(v)

# The base URL to the ASM installation as seen by the client (should not end with /)
BASE_URL = get_string("base_url", "http://localhost:5000")

# The URL to asm's service endpoint to be shown in online forms screens in particular,
# but also used by animal_view_adoptable_js to link to animal_view etc
SERVICE_URL = get_string("service_url", "http://localhost:5000/service")

# The language to use before a locale has been configured 
# in the database
LOCALE = get_string("locale", "en")

# The timezone offset to use before one has been configured
# in the database (+/- server clock offset, NOT UTC)
TIMEZONE = get_integer("timezone", 0)

# Where ASM directs log output to, one of:
# stderr  - the standard error stream
# syslog  - the UNIX syslogger (to LOCAL3 facility)
# ntevent - the Windows event logger
# <file>  - The path to a file to log to
LOG_LOCATION = get_string("log_location", "syslog")

# Include debug messages when logging - set to False
# to disable debug messages
LOG_DEBUG = get_boolean("log_debug", True)

# Whether to reload the application when the code.py filestamp changes
AUTORELOAD = get_boolean("autoreload", False)

# Database info
# MYSQL, POSTGRESQL, SQLITE or DB2
DB_TYPE = get_string("db_type", "MYSQL")
DB_HOST = get_string("db_host", "localhost")
DB_PORT = get_integer("db_port", 3306)
DB_USERNAME = get_string("db_username", "robin")
DB_PASSWORD = get_string("db_password", "robin")
DB_NAME = get_string("db_name", "asm")

# If set, all calls to db.execute will be logged to the file
# named. Use {database} to substitute database name.
DB_EXEC_LOG = get_string("db_exec_log")

# Produce an EXPLAIN for each query in the log before running it
DB_EXPLAIN_QUERIES = get_boolean("db_explain_queries", False)

# How many days to keep the audit trail and deletion log for
DB_RETAIN_AUDIT_DAYS = get_integer("db_retain_audit_days", 182)

# Record the time taken to run each query
DB_TIME_QUERIES = get_boolean("db_time_queries", False)

# If DB_TIME_QUERIES is on, only log queries that take longer 
# than X seconds to run (or 0 to log all queries)
DB_TIME_LOG_OVER = get_integer("db_time_log_over", 0)

# Time out queries that take longer than this (ms) to run
DB_TIMEOUT = get_integer("db_timeout", 0)

# URLs for ASM services
URL_NEWS = get_string("url_news", "https://sheltermanager.com/repo/asm_news.html")
URL_REPORTS = get_string("url_reports", "https://sheltermanager.com/repo/reports.txt")
URL_MICROCHIP_PREFIXES = get_string("url_microchip_prefixes", "https://sheltermanager.com/repo/chipprefixes.txt")

# Deployment type, wsgi or fcgi
DEPLOYMENT_TYPE = get_string("deployment_type", "wsgi")

# Whether the session cookie should be secure (only valid for https)
SESSION_SECURE_COOKIE = get_boolean("session_secure_cookie", False)

# Output debug info on sessions
SESSION_DEBUG = get_boolean("session_debug", False)

# The Content-Security-Policy header to send, or blank for no policy
# Include 'nonce-%(nonce)s' in any policy to prevent the bootstrap 
# inline script breaking
CONTENT_SECURITY_POLICY = get_string("content_security_policy", "")

# The host/port that memcached is running on if it is to be used.
# If memcache is not available, an in memory dictionary will be
# used instead.
#MEMCACHED_SERVER = "127.0.0.1:11211"
MEMCACHED_SERVER = get_string("memcached_server", "")

# Where to store media files.
# database - media files are base64 encoded in the dbfs.content db column
# file - media files are stored in a folder 
# s3 - media files are stored in S3 compatible storage
DBFS_STORE = get_string("dbfs_store", "database")

# DBFS_STORE = file: The folder where media files are stored.
# It must exist and ASM must have write permissions. It should never end with a /
DBFS_FILESTORAGE_FOLDER = get_string("dbfs_filestorage_folder", "/home/robin/tmp/dbfs")

# DBFS_STORE = s3: The S3 bucket and credentials, endpoint url is only necessary for non-AWS
# If no credentials are set, $HOME/.aws/credentials or env vars will be used.
DBFS_S3_BUCKET = get_string("dbfs_s3_bucket", "")
DBFS_S3_ACCESS_KEY_ID = get_string("dbfs_s3_access_key_id", "")
DBFS_S3_SECRET_ACCESS_KEY = get_string("dbfs_s3_secret_access_key", "")
DBFS_S3_ENDPOINT_URL = get_string("dbfs_s3_endpoint_url", "")

# If you are migrating away from one S3 provider to another, you can set the old provider's
# credentials here. The DBFS module will look in the new provider first, and if it doesn't
# find an object, look in the old provider and copy it to the new one.
# This allows you to switch to another provider straight away. You can then optionally
# use something like rclone to move objects from the old provider to the new one. 
DBFS_S3_MIGRATE_BUCKET = get_string("dbfs_s3_migrate_bucket", "")
DBFS_S3_MIGRATE_ACCESS_KEY_ID = get_string("dbfs_s3_migrate_access_key_id", "")
DBFS_S3_MIGRATE_SECRET_ACCESS_KEY = get_string("dbfs_s3_migrate_secret_access_key", "")
DBFS_S3_MIGRATE_ENDPOINT_URL = get_string("dbfs_s3_migrate_endpoint_url", "")

# If a backup S3 bucket can provider is set, all files sent to the S3 service
# above will also be sent to this one too to maintain a synchronised backup.
DBFS_S3_BACKUP_BUCKET = get_string("dbfs_s3_backup_bucket", "")
DBFS_S3_BACKUP_ACCESS_KEY_ID = get_string("dbfs_s3_backup_access_key_id", "")
DBFS_S3_BACKUP_SECRET_ACCESS_KEY = get_string("dbfs_s3_backup_secret_access_key", "")
DBFS_S3_BACKUP_ENDPOINT_URL = get_string("dbfs_s3_backup_endpoint_url", "")

# The directory to use to cache elements on disk. Must already exist
# as the application will not attempt to create it.
DISK_CACHE = get_string("disk_cache", "/tmp/asm_disk_cache")

# Allow some non-critical queries to be cached for short periods in the 
# disk cache to help with performance. The majority of these are queries for
# to populate the home page so that it can load quickly. 
CACHE_COMMON_QUERIES = get_boolean("cache_common_queries", False)

# Cache service call responses on the server side according
# to their max-age headers in the disk cache
CACHE_SERVICE_RESPONSES = get_boolean("cache_service_responses", False)

# If EMAIL_ERRORS is set to True, all errors from the site
# are emailed to ADMIN_EMAIL and the user is given a generic
# error page. If set to False, debug information is output.
EMAIL_ERRORS = get_boolean("email_errors", False)
ADMIN_EMAIL = get_string("admin_email", "you@youraddress.com")

# If ROLLUP_JS is set to True, a single, rolled up and minified
# javascript file will be sent to the client
ROLLUP_JS = get_boolean("rollup_js", False)

# Only allow hotlinks to the animal_image and extra_image
# service calls from this domain, or comma separated list of domains
IMAGE_HOTLINKING_ONLY_FROM_DOMAIN = get_string("image_hotlinking_only_from_domain", "")

# Use Transfer-Encoding: chunked for large files. Note that
# this does not work with mod_wsgi. Turning it off will cause
# web.py to buffer the output, which can cause problems with
# dumps of large databases.
LARGE_FILES_CHUNKED = get_boolean("large_files_chunked", True)

# Maximum size a document template can be. Anything over this and the
# user has probably copied/pasted an image as a data-uri and it will cause
# tinymce to break and the doc to fail to load. Default 2M
MAX_DOCUMENT_TEMPLATE_SIZE = get_integer("max_document_template_size", 2097152)

# Whether to resize incoming images
RESIZE_IMAGES_DURING_ATTACH = get_boolean("resize_images_during_attach", True)
RESIZE_IMAGES_SPEC = get_string("resize_images_spec", "1024x1024")

# Shell command to use to compress PDFs
SCALE_PDF_DURING_ATTACH = get_boolean("scale_pdf_during_attach", False)
SCALE_PDF_CMD = get_string("scale_pdf_cmd", "convert -density 120 -quality 60 %(input)s -compress Jpeg %(output)s")
#SCALE_PDF_CMD = "pdftk %(input)s output %(output)s compress"
#SCALE_PDF_CMD = "gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/screen -dNOPAUSE -dQUIET -dBATCH -sOutputFile=%(output)s %(input)s"

# Shell command to convert HTML to PDF
HTML_TO_PDF = get_string("html_to_pdf", "wkhtmltopdf --orientation %(orientation)s %(papersize)s %(input)s %(output)s")
#HTML_TO_PDF = "html2pdf %(input)s %(output)s"

# Target for viewing an address on a map, {0} is the address
MAP_LINK = get_string("map_link", "https://www.openstreetmap.org/search?query={0}")

# Map provider for rendering maps on the client, can be "osm" or "google"
MAP_PROVIDER = get_string("map_provider", "osm")
MAP_PROVIDER_KEY = get_string("map_provider_key", "") # For google, the API key to use when making map requests
OSM_MAP_TILES = get_string("osm_map_tiles", "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png")

GEO_PROVIDER = get_string("geo_provider", "nominatim")  # Geocode provider to use - nominatim or google
GEO_PROVIDER_KEY = get_string("geo_provider_key", "")   # For google, the API key to use when making geocoding requests
GEO_SMCOM_URL = get_string("geo_smcom_url", "")
GEO_SMCOM_ADDRESS_URL = get_string("geo_smcom_address_url", "")
GEO_BATCH = get_boolean("geo_batch", False)             # Whether or not to try and lookup geocodes as part of the batch
GEO_LIMIT = get_integer("geo_limit", 100)               # How many geocodes to lookup as part of the batch
GEO_LOOKUP_TIMEOUT = get_integer("geo_lookup_timeout", 5) # Timeout in seconds when doing geocode lookups
GEO_SLEEP_AFTER = get_integer("geo_sleep_after", 1)     # Sleep for seconds after a request to throttle (nominatim has a 1/s limit)

# Enable the database field on login and allow login to multiple databases
MULTIPLE_DATABASES = get_boolean("multiple_databases", False)
MULTIPLE_DATABASES_TYPE = get_string("multiple_databases_type", "map")
# { "alias": { "dbtype": "MYSQL", "host": "localhost", "port": 3306, "username": "root", "password": "root", "database": "asm" } }
MULTIPLE_DATABASES_MAP = get_dict("multiple_databases_map")

# Whether the old HTML/FTP publisher of static files is enabled
HTMLFTP_PUBLISHER_ENABLED = get_boolean("htmlftp_publisher_enabled", True)

# FTP connection timeout value in seconds
FTP_CONNECTION_TIMEOUT = get_integer("ftp_connection_timeout", 60)

# FTP hosts and URLs for third party publishing services
ADOPTAPET_FTP_HOST = get_string("adoptapet_ftp_host", "autoupload.adoptapet.com")
AKC_REUNITE_BASE_URL = get_string("akc_reunite_base_url", "")
AKC_REUNITE_USER = get_string("akc_reunite_user", "")
AKC_REUNITE_PASSWORD = get_string("akc_reunite_password", "")
ANIBASE_BASE_URL = get_string("anibase_base_url", "")
ANIBASE_API_USER = get_string("anibase_api_user", "")
ANIBASE_API_KEY = get_string("anibase_api_key", "")
BUDDYID_BASE_URL = get_string("buddyid_base_url", "")
BUDDYID_EMAIL = get_string("buddyid_email", "")
BUDDYID_PASSWORD = get_string("buddyid_password", "")
FOUNDANIMALS_FTP_HOST = get_string("foundanimals_ftp_host", "")
FOUNDANIMALS_FTP_USER = get_string("foundanimals_ftp_user", "")
FOUNDANIMALS_FTP_PASSWORD = get_string("foundanimals_ftp_password", "")
HOMEAGAIN_BASE_URL = get_string("homeagain_base_url", "")
MADDIES_FUND_TOKEN_URL = get_string("maddies_fund_token_url", "")
MADDIES_FUND_UPLOAD_URL = get_string("maddies_fund_upload_url", "")
PETCADEMY_FTP_HOST = get_string("petcademy_ftp_host", "")
PETCADEMY_FTP_USER = get_string("petcademy_ftp_user", "")
PETCADEMY_FTP_PASSWORD = get_string("petcademy_ftp_password", "")
PETFBI_FTP_HOST = get_string("petfbi_ftp_host", "petfiles.petfbi.org")
PETFINDER_FTP_HOST = get_string("petfinder_ftp_host", "members.petfinder.com")
PETFINDER_SEND_PHOTOS_BY_FTP = get_boolean("petfinder_send_photos_by_ftp", True)
PETRESCUE_URL = get_string("petrescue_url", "")
RESCUEGROUPS_FTP_HOST = get_string("rescuegroups_ftp_host", "ftp.rescuegroups.org")
SAVOURLIFE_API_KEY = get_string("savourlife_api_key", "")
SAVOURLIFE_URL = get_string("savourlife_url", "")
SAC_METRICS_URL = get_string("sac_metrics_url", "")
SAC_METRICS_API_KEY = get_string("sac_metrics_api_key", "")
SMARTTAG_FTP_HOST = get_string("smarttag_ftp_host", "ftp.idtag.com")
SMARTTAG_FTP_USER = get_string("smarttag_ftp_user", "")
SMARTTAG_FTP_PASSWORD = get_string("smarttag_ftp_password", "")
PETTRAC_UK_POST_URL = get_string("pettrac_uk_post_url", "https://online.pettrac.com/registration/onlineregistration.aspx")
PETLINK_BASE_URL = get_string("petlink_base_url", "")
PETSLOCATED_FTP_HOST = get_string("petslocated_ftp_host", "ftp.petslocated.com")
PETSLOCATED_FTP_USER = get_string("petslocated_ftp_user", "")
PETSLOCATED_FTP_PASSWORD = get_string("petslocated_ftp_password", "")
VETENVOY_US_VENDOR_USERID = get_string("vetenvoy_us_vendor_userid", "")
VETENVOY_US_VENDOR_PASSWORD = get_string("vetenvoy_us_vendor_password", "")
VETENVOY_US_BASE_URL = get_string("vetenvoy_us_base_url", "")
VETENVOY_US_SYSTEM_ID = get_string("vetenvoy_us_system_id", "20")
VETENVOY_US_HOMEAGAIN_RECIPIENTID = get_string("vetenvoy_us_homeagain_recipientid", "")
VETENVOY_US_AKC_REUNITE_RECIPIENTID = get_string("vetenvoy_us_akc_reunite_recipientid", "")

# Config for payment processing services
PAYPAL_VALIDATE_IPN_URL = get_string("paypal_validate_ipn_url", "")

# Options available under the share button
SHARE_BUTTON = get_string("share_button", "shareweb,sharepic,shareemail")

# Type of electronic signing device available
ELECTRONIC_SIGNATURES = get_string("electronic_signatures", "")

# If you have an emergency notice you'd like displaying on the
# login and home screens, set a filename here for the content
# (if the file does not exist or has no content, nothing will
# be displayed).
EMERGENCY_NOTICE = get_string("emergency_notice", "")

# SMTP_SERVER = { "sendmail": False, "host": "mail.yourdomain.com", "port": 25, "username": "userifauth", "password": "passifauth", "usetls": False }
# SMTP_SERVER = { "sendmail": False, "host": "mail.yourdomain.com", "port": 25, "username": "", "password": "", "usetls": False }
SMTP_SERVER = get_dict("smtp_server", { "sendmail": True })

# The from address for all outgoing emails. The email address configured
# in the database will be used as the Reply-To header to avoid
# any issues with DKIM/SPF/DMARC spoofing
# substitutions: 
# {organisation} organisation name
# {database} database name
# {alias} database alias
FROM_ADDRESS = get_string("from_address", "you@yourdomain.com")

# URLs to access manuals and help documentation
MANUAL_HTML_URL = get_string("manual_html_url", "static/pages/manual/index.html")
MANUAL_FAQ_URL = get_string("manual_faq_url", "static/pages/manual/faq.html")
MANUAL_PDF_URL = get_string("manual_pdf_url", "")
MANUAL_VIDEO_URL = get_string("manual_video_url", "")

# The file containing names to be used by the random name function
RANDOM_NAME_FILE = get_string("random_name_file", os.path.dirname(os.path.abspath(__file__)) + os.sep + ".." + os.sep + "static" + os.sep + "pages" + os.sep + "names.txt")

SMCOM_PAYMENT_LINK = get_string("smcom_payment_link", "")
SMCOM_LOGIN_URL = get_string("smcom_login_url", "")

# Script and css references for dependencies (can be substituted for separate CDN here)
ASMSELECT_CSS = get_string("asmselect_css", 'static/lib/asmselect/1.0.4a/jquery.asmselect.css')
ASMSELECT_JS = get_string("asmselect_js", 'static/lib/asmselect/1.0.4a/jquery.asmselect.js')
BASE64_JS = get_string("base64_js", 'static/lib/base64/0.3.0/base64.min.js')
BOOTSTRAP_JS = get_string("bootstrap_js", 'static/lib/bootstrap/5.1.0/js/bootstrap.min.js')
BOOTSTRAP_CSS = get_string("bootstrap_css", 'static/lib/bootstrap/5.1.0/css/bootstrap.min.css')
BOOTSTRAP_GRID_CSS = get_string("bootstrap_grid_css", 'static/lib/bootstrap/5.1.0/css/bootstrap-grid.min.css')
BOOTSTRAP_ICONS_CSS = get_string("bootstrap_icons_css", 'static/lib/bootstrap-icons/1.5.0/bootstrap-icons.css')
CODEMIRROR_JS = get_string("codemirror_js", 'static/lib/codemirror/5.65.2.asm/lib/codemirror.js')
CODEMIRROR_CSS = get_string("codemirror_css", 'static/lib/codemirror/5.65.2.asm/lib/codemirror.css')
CODEMIRROR_BASE = get_string("codemirror_base", 'static/lib/codemirror/5.65.2.asm/')
FLOT_JS = get_string("flot_js", 'static/lib/flot/0.8.3/jquery.flot.min.js')
FLOT_PIE_JS = get_string("flot_pie_js", 'static/lib/flot/0.8.3/jquery.flot.pie.min.js')
FULLCALENDAR_CSS = get_string("fullcalendar_css", 'static/lib/fullcalendar/3.10.2/fullcalendar.min.css')
FULLCALENDAR_JS = get_string("fullcalendar_js", 'static/lib/fullcalendar/3.10.2/fullcalendar.min.js')
JQUERY_UI_CSS = get_string("jquery_ui_css", 'static/lib/jqueryui/jquery-ui-themes-1.13.0/themes/%(theme)s/jquery-ui.css')
JQUERY_UI_JS = get_string("jquery_ui_js", 'static/lib/jqueryui/jquery-ui-1.13.2/jquery-ui.min.js')
JQUERY_JS = get_string("jquery_js", 'static/lib/jquery/3.7.0/jquery.min.js')
JQUERY_MOBILE_CSS = get_string("jquery_mobile_css", 'static/lib/jquerymobile/1.4.5/jquery.mobile.min.css')
JQUERY_MOBILE_JS = get_string("jquery_mobile_js", 'static/lib/jquerymobile/1.4.5/jquery.mobile.min.js')
JQUERY_MOBILE_JQUERY_JS = get_string("jquery_mobile_jquery_js", 'static/lib/jquery/2.2.4/jquery.min.js')
LEAFLET_CSS = get_string("leaflet_css", 'static/lib/leaflet/1.3.1/leaflet.css')
LEAFLET_JS = get_string("leaflet_js", 'static/lib/leaflet/1.3.1/leaflet.js')
MOMENT_JS = get_string("moment_js", 'static/lib/moment/2.29.1/moment.min.js')
MOUSETRAP_JS = get_string("mousetrap_js", 'static/lib/mousetrap/1.4.6/mousetrap.min.js')
PATH_JS = get_string("path_js", 'static/lib/pathjs/0.8.4.asm-2/path.min.js')
QRCODE_JS = get_string("qrcode_js", 'static/lib/qrcodejs/1.0.0/qrcode.min.js')
SIGNATURE_JS = get_string("signature_js", 'static/lib/signature/1.2.1-asm03/jquery.signature.min.js')
TABLESORTER_CSS = get_string("tablesorter_css", 'static/lib/tablesorter/2.31.3-asm/dist/css/theme.asm.css')
TABLESORTER_JS = get_string("tablesorter_js", 'static/lib/tablesorter/2.31.3-asm/dist/js/jquery.tablesorter.min.js')
TABLESORTER_WIDGETS_JS = get_string("tablesorter_widgets_js", 'static/lib/tablesorter/2.31.3-asm/dist/js/jquery.tablesorter.widgets.min.js')
TIMEPICKER_CSS = get_string("timepicker_css", 'static/lib/timepicker/0.3.3/jquery.ui.timepicker.css')
TIMEPICKER_JS = get_string("timepicker_js", 'static/lib/timepicker/0.3.3/jquery.ui.timepicker.js')
TINYMCE_5_JS = get_string("tinymce_4_js", 'static/lib/tinymce/5.5.1/tinymce/js/tinymce/tinymce.min.js')

# Directory where font files are located for use with image watermarking
WATERMARK_FONT_BASEDIRECTORY = get_string("watermark_font_basedirectory", "/usr/share/fonts/truetype/")

