import os, sys
sys.path.insert(0, "{{ asm_path }}/src")
os.environ["ASM3_CONF"] = "{{ asm_data }}/asm3.conf"
import main
application = main.application
