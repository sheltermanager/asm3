This is web.py 0.62

One minor fix was applied to application.py, the line reload_mapping() was commented out.

It was causing a reload that broke session functionality as Session().\_processor was being
removed from the list of processors after the reload.


