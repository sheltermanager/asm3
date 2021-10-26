This is web.py 0.62

Changes:

application.py

The line reload_mapping() at the bottom of application.\_\_init\_\_  was commented out.

It was causing a reload that broke session functionality as Session().\_processor was being
removed from the list of processors after the reload.

session.py

The \_save function was updated to check the session_id and ip elements exist in the session dict 
before trying to delete them to avoid a KeyError 

(think this was only necesssary for "ip" and because it wasn't in sessions from web.py 0.39
that were still active in memcache)

    def _save(self):
        current_values = dict(self._data)
        if "session_id" in current_values: del current_values["session_id"]
        if "ip" in current_values: del current_values["ip"]

