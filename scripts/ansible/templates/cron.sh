#!/bin/bash
/usr/bin/python {{ asm_path }}/src/cron.py daily &> /var/log/cron/asm
