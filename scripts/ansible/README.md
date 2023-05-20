# Ansible Playbooks

Ansible is a configuration management system. For more information about ansible, see:

http://www.ansible.com/how-ansible-works
http://docs.ansible.com/ansible/glossary.html

This playbook requires Ansible 2.4 or newer.

## TLDR
* Copy the compressed archive for the version you want to deploy into `archives/`
* Update the ansible variables in your inventory
* Run the playbook to deploy to all hosts

    ansible-playbook asm_install.yml -i /path/to/inventory

Sometimes it is convenient to limit the deployment to a particular host
    ansible-playbook asm_install.yml -i /path/to/inventory --limit=some_host

## Configure host machines

Currently, this playbook relies on roles from City of Bloomington, that only support Ubuntu.  Contributions to the ansible roles are welcome!

https://github.com/City-of-Bloomington/ansible-role-linux
https://github.com/City-of-Bloomington/ansible-role-apache
https://github.com/City-of-Bloomington/ansible-role-postgresql


## Ansible Configuration

### Tell ansible about your hosts
When you start having many hosts, keeping track of all the variables can get out of hand.  It's best to use an inventory directory, rather than just a single hosts file.  The inventory_example gives an idea of how we organize our inventory for City of Bloomington.

You will pass your own inventory directory as a parameter ("-i") on the command line.

Make sure to use ansible-vault to encrypt files that include passwords.

http://docs.ansible.com/ansible/playbooks_vault.html

To encrypt an already existing, unencrypted file:

    ansible-vault encrypt something_secret.yml

### Ansible configuration defaults

Ansible expects playbooks, roles, etc (e.g. this repository) to be in /etc/ansible by default.
However, we typically use a local ansible.cfg for running playbooks.  The ansible.cfg included in this repository should allow for running the playbooks directory from this directory.


## Using ansible

### External Roles

This playbook utilized roles from Ansible Galaxy. These require using ansible-galaxy to pull them down and make them available locally.

To grab them all, in the main directory of this system-playbooks project, run the following:

    ansible-galaxy install -r roles.yml

These roles are then available for use by playbooks.

### Applying system configurations

Give it a go:

    ansible-playbook asm_install.yml -i /path/to/inventory

If the playbook completes successfully, *congratulations!* The servers you specified in your inventory should be set up correctly.
