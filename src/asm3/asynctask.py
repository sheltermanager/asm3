
"""
Module for helping run tasks asynchronously and updating/getting progress.
Only allows one async task per database to be run at a time.

For many tasks, it should be as simple as calling their function as
an argument to function_task, and having the function code call 
async.set_progress_value(>100) or async.increment_progress_value()
"""

import asm3.cachedisk

from asm3.typehints import Any, Callable, Database

import threading

lc = {}

def get(dbo: Database, k: str) -> Any:
    """ Retrieve a task value for this database """
    return asm3.cachedisk.get(k, dbo.name())

def put(dbo: Database, k: str, v: Any) -> None:
    """ Store a task value for this database """
    asm3.cachedisk.put(k, dbo.name(), v, 3600)

def is_task_running(dbo: Database) -> bool:
    """ Returns True if a task is running """
    name = get(dbo, "taskname")
    mx = get(dbo, "taskmax")
    v = get(dbo, "taskval")
    if v is not None and v == mx:
        return False
    if name is not None and name != "":
        return True
    return False

def reset(dbo: Database) -> None:
    """ Clear all task related values (except lasterror and returnvalue) """
    put(dbo, "taskname", "")
    put(dbo, "taskmax", 0)
    put(dbo, "taskval", 0)
    put(dbo, "taskcancel", False)
    # tasklasterror, taskreturnvalue deliberately not cleared

def get_task_name(dbo: Database) -> str:
    """ Get the task name """
    v = get(dbo, "taskname")
    if v is None or v == "":
        return "NONE"
    return v

def set_task_name(dbo: Database, v: str) -> None:
    """ Set the task name """
    put(dbo, "taskname", v)

def get_progress_max(dbo: Database) -> int:
    """ Get the max value for the progress meter """
    return get(dbo, "taskmax")
   
def set_progress_max(dbo: Database, progressmax: int) -> None:
    """ Set a value for the maximum progress meter """
    put(dbo, "taskmax", progressmax)

def get_progress_value(dbo: Database) -> int:
    """ Get a value for the progress meter """
    return get(dbo, "taskval")

def get_progress_percent(dbo: Database) -> int:
    m = get_progress_max(dbo)
    v = get_progress_value(dbo)
    if m is not None and v is not None and m != 0:
        return int((float(v) / float(m)) * 100)
    return 0

def set_progress_value(dbo, v: int) -> None:
    """ Set a value for the progress meter """
    return put(dbo, "taskval", v)

def increment_progress_value(dbo: Database) -> None:
    """ Adds one to the progress value """
    v = get_progress_value(dbo)
    if v is not None: 
        v += 1
        set_progress_value(dbo, v)

def get_cancel(dbo: Database) -> bool:
    """ Returns whether the running task should stop """
    v = get(dbo, "taskcancel")
    if v is None: return False
    return v

def set_cancel(dbo, v: bool) -> None:
    """ Set to True to tell the running task to stop """
    put(dbo, "taskcancel", v)

def get_return_value(dbo: Database) -> str:
    """ Get the return value """
    v = get(dbo, "taskreturnvalue")
    if v is None: return ""
    return v

def set_return_value(dbo: Database, v: str) -> None:
    """ Set the return value """
    put(dbo, "taskreturnvalue", v)

def get_last_error(dbo: Database) -> str:
    """ Get the last error message """
    v = get(dbo, "tasklasterror")
    if v is None: return ""
    return v

def set_last_error(dbo: Database, e: str) -> None:
    """ Set the last error message """
    put(dbo, "tasklasterror", e)

class FuncThread(threading.Thread):
    """ Class that wraps calling a function in a new thread.
        Calls our reset method after the task is done, 
        handles putting exceptions in lasterror and storing the returnvalue too.
    """
    def __init__(self, dbo: Database, target: Callable, *args):
        self.target = target
        self.args = args
        self.dbo = dbo
        threading.Thread.__init__(self)
 
    def run(self):
        try:
            set_return_value(self.dbo, self.target(*self.args))
        except Exception as err:
            set_last_error(self.dbo, str(err))
        finally:
            reset(self.dbo)

def function_task(dbo: Database, taskname: str, fn: Callable, *args):
    """ Runs the function fn with tuple of args, wrapping it as an async task 
        taskname: a name for the task
        fn: The function to call
        *args: arguments to pass to the function.

        functions can still call async.set_progress_value, but they don't
        need any other boiler plate async code and will work just as well sync.
    """
    if is_task_running(dbo): return # do nothing if a task is already going
    set_last_error(dbo, "")
    set_return_value(dbo, "")
    set_task_name(dbo, taskname)
    set_cancel(dbo, False)
    set_progress_max(dbo, 100) # override in called function
    set_progress_value(dbo, 0)
    FuncThread(dbo, fn, *args).start()

