#!/usr/bin/python

from os.path import dirname, basename, isfile
import glob

# Allow use of from locales import *
modules = glob.glob(dirname(__file__)+"/*.py")
__all__ = [ basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')]
