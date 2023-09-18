
"""
Contains all aliased types for type hinting.

Current state of affairs: Python 3.7 on all database servers, Python 3.11 on dev machines.
Type hints were added in Python 3.5, they are treated as annotations/decorations on function parameters and variables.

Type hint annotations have issues because annotations are evaluated immediately. 

This was initially fixed by making the annotations strings (eg: dbo: "Database" instead of dbo: Database) so that they
can be evaluated later by static checking tools and not the interpreter. 

3.7 added "from __future__ import annotations", which basically stringified all annotations so that they were
evaluated later.

3.10 added the ability for types to be used instead of classes from the typing module (eg: list[dict] instead of List[Dict])

A new PEP aims to evaluate annotations with code and an __annotations__ dunder for a "best of all worlds" situation, but 
this has not happened yet as of 3.11

Rather than importing the typing module in all of our modules and having the future import, and a test for typing.TYPE_CHECKING,
I've opted for now to declare aliases for our most commonly used classes. This allows us to make use of type hints, but
with just a single from "asm3.typehints import ..." in modules, and in a way that is compatible with Python 3.5 onwards.

When Python 3.12+ is available everywhere, we can look at writing out this module and using the "real" references. Or something
better might be available, we'll see.
"""

import typing

Any = typing.Any
Callable = typing.Callable
Generator = typing.Generator
List = typing.List
Dict = typing.Dict
Tuple = typing.Tuple

datetime = "datetime.datetime" # this can be used if the only reason you're pulling datetime in is for type checking

Database = "asm3.dbms.base.Database"
ResultRow = "asm3.dbms.base.ResultRow"
Results = "List[asm3.dbms.base.ResultRow]"

PaymentProcessor = "asm3.paymentprocessor.base.PaymentProcessor"
PostedData = "asm3.utils.PostedData"

MemcacheClient = "memcache.Client"
S3Client = "S3.Client"
Session = "web.session.Session"

# ReportParams are a list of the 3 values extracted from report SQL and used to ask the user for criteria (report.py)
ReportParams = List[Tuple[str, str, str]] # variablename, type, question
# CriteriaParams are a list of the 4 values extracted from user input of criteria used to run the query for the report (report.py)
CriteriaParams = List[Tuple[str, str, str, str]] # variablename, questiontext, substitutionvalue, displayvalue
# List of sortable columns returned by column functions for find screens (html.py)
ColumnList = List[Tuple[str, str]] # fieldname, displaytext
# MenuItems are a list of tuples for items in a menu (menu.py, reports.py)
MenuItems = List[Tuple[str, str, str, str ,str ,str]] # permissions, hotkey, classes, url, icon, text
# MenuStructure is a tuple of top level menus with menu items (html.py)
MenuStructure = Tuple[str, str, str, MenuItems] # permissions, name, text, menuitems
# ServiceResponse is tuple used by service.py
ServiceResponse = Tuple[str, int, int, bytes | str] # mimetype, clientcachettl, edgecachettl, content
