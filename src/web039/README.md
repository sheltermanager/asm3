This is web.py 0.39-20181101

One minor fix was applied to httpserver.py \_\_init\_\_ to add self.directory = os.getcwd() 



web.py 0.62 is currently available, but seems to have major issues with sessions that I
don't have time to work out currently. This version is what we've used in production without
any issues for the last 2 years.

Last time I investigated (25/10/21) I found that even though the session.py/Session.\_\_init\_\_() 
was correctly calling app.add_processor() to register itself, adding breakpoint() to the top of 
session.py/Session().\_processor() never got hit and when putting a breakpoint into 
application.py/application.handle_with_processors() the Session processor disappeared from the
list (if you check the list from the breakpoint in Session.\_\_init\_\_ with app.processors, it
is there initially, so the processor list is being rebuilt/cleared).

This means that \_load() was never called, so no session cookie was set or the session initialised.

