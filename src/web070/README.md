This is web.py 0.70 taken from the github release

Search the code for "RRT" to find changes made.

1. Added multipart.py to the package so it does not have to be a separate
dependency (and the version packaged in Debian 12 was old and incompatible)

2. webapi.py - imports the parse_form_data method from multipart.py in the
current package instead of the whole module from path.

3. application.py - stops reload_mapping() being called on first load as it
breaks sessions in debug mode. I reported this upstream with a fix in 2021, but
it has not been merged.

4. session.py - allows you to set session.send_cookie = False to prevent your
endpoint including the Set-Cookie header to send the session cookie.  Useful if
you use CDNs as Cloudflare won't honour cache control directives when
Set-Cookie is in the response headers. PR was submitted upstream in 2023, but
it has not been merged.

