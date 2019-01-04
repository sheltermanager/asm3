#!/usr/bin/env python

# Set these according to your install
INSTALL_DIR = "/path/to/asm/install"
CONF_FILE = "/path/to/asm3.conf"

import os, sys
sys.path.insert(0, INSTALL_DIR)
os.environ["ASM3_CONF"] = CONF_FILE

import code
application = code.application
