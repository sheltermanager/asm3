# Ansible Playbook
This playbook deploys a pre-built copy of ASM, instead of a source tarball.
You will likely need to build the tarball yourself.  The Makefile contains commands for the various build tasks.

To do a build you will need to have the dependencies installed:
https://github.com/sheltermanager/asm3#dependencies

Then run:

```bash
make dist
```

## Deploy
```bash
cd asm3/scripts/ansible
ansible-playbook asm_install.yml -i /path/to/inventory --limit=shelter.domain.org
```

## Ansible Configuration
In your ansible inventory, you must create the asm variables used in this playbook.

```yml
apache_serveradmin: 'someone@domain.org'

asm_path: "/srv/sites/asm"
asm_data: "/srv/data/asm"

asm_base_uri: "/asm"
asm_base_url: "https://{{ ansible_host }}/asm"

asm_db:
  type: "POSTGRESQL" # MYSQL POSTGRESQL
  port: 5432         # 3306    5432
  host: "localhost"
  name: "asm"
  user: "asm"
  pass: "{{ vault_asm_db.password }}"

asm_smtp:
  host: 'smtp.domain.org'
  port: 25
  user: ''
  pass: ''
  tls:  'false'

asm_sitedefs:
    timezone: "-5"
    log_location: "stderr"
    # Where to store media files.
    # database - media files are base64 encoded in the dbfs.content db column
    # file - media files are stored in a folder
    # s3 - media files are stored in amazon s3
    dbfs_store: "file"
    admin_email: "asm@domain.org"
    # Map provider for rendering maps on the client, can be "osm" or "google"
    map_provider: "google"
    map_provider_key: ""
    # Client side geocode provider for mapping address to lat/lng in the browser
    # can be "mapquest", "nominatim" or "google"
    geo_provider:     "google"
    geo_provider_key: ""
    # FTP hosts and URLs for third party publishing services
    petlink_base_url: "https://www.petlink.net/us/"
```


