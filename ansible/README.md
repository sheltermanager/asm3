# Ansible Playbooks

Ansible is a configuration management system. For more information about ansible, see:

http://www.ansible.com/how-ansible-works

## Terminology

The primary machine used to issue those commands is called the control machine. Hosts are the remote machines that you configure with ansible. For more details about terms, see here:

http://docs.ansible.com/ansible/glossary.html

To use ansible, you'll need a *nix based control machine/server that is used to configure and deploy any number of hosts and services.

## Configure host machines

### Base OS installation on hosts

Ansible assumes you have already set up the new host/destination machine with a base OS installation. There are many options for where to put a base OS:

  - Install a base OS on an actual hardware instance of a machine.
  - Install a base OS on a virtual machine. VirtualBox or VMWare are common options.
      - VirtualBox is a free and capable solution for creating virtual machines on your local machine.
      - VMWare is a commercial solution that also makes the base OS install very straightforward.
  - Use Vagrant to spin up a base virtual machine. Vagrant does have the abilitiy to call a configuration management solution like ansible automatically. VirtualBox and VMWare are both options here too. If you're using VMWare for virtualization, you'll need the commercial version of Vagrant to work with VMWare.
  - Use a cloud service provider that provides the base system for you
  - Use Docker containers? (Still working on this...)

For VirtualBox, you'll need a "Host-only Adapter" in order to access the machine. When the VM is powered off, add another network interface:

    Virtual Box -> Devices -> Network -> Network Settings...
    Adapter 2 -> Enable Network Adapter
    Attached to: Host-only Adapter
    Name: vboxnet0

Then, when the machine is powered on, do:

    #find all adapters... should be a new one that is unconfigured
    ip addr
    #enp0s8 for me
    sudo vi /etc/network/interfaces
    #add new section for interface, adapting from lines already there

    # The local network interface
    auto enp0s8
    iface enp0s8 inet dhcp

    sudo /etc/init.d/networking restart
    #check for new ip with:
    ifconfig

Typically, openssh-server is available on server installations by default. Make sure that the host machine is accessible via SSH:

    sudo apt-get update
    sudo apt-get -y install openssh-server

Ansible requires Python installed on the host machine, as well:

    bash
    sudo apt-get install -y python

You'll also need a user account that can sudo.


## Install ansible on control machine

Up-to-date details for installing an ansible control machine are available here:

http://docs.ansible.com/ansible/intro_installation.html

If ansible is not installed on the local machine, it is a good idea to assign a static IP address to the control machine. It's easier to access the machine that way. See above for notes about configuring the network interface. In this case, we'll replace:

    iface enp0s8 inet dhcp

with:

    iface enp0s8 inet static
    address 192.168.56.22
    netmask 255.255.255.0

If ansible is being installed on a VM, it may make sense to update the hostname:

    sudo vi /etc/hostname
    sudo vi /etc/hosts
    sudo service hostname restart

Be sure to install any missing requirements:

    sudo apt-get install build-essential libssl-dev libffi-dev python-dev python-pip sshpass
    pip install --upgrade pip

Finally, install ansible with pip:

    pip install ansible


## Configure SSH public key connections

SSH public key connections allow you to configure a control machine with SSH access to a host machine without needing to supply a password every time.

https://help.ubuntu.com/community/SSH/OpenSSH/Keys

Generate local keys on the control machine:

    ssh-keygen -t rsa

then transfer the control machine's public key to the host/destination for the user that can sudo. See the link above for manual transfer process, or use ssh-copy-id. On OSX, this works:

https://github.com/beautifulcode/ssh-copy-id-for-OSX

    ssh-copy-id username@hostname

You can test this with:

    ssh username@hostname

If you're not prompted for a password, it worked!


## Ansible Configuration

### Tell ansible about hosts
When you start having more than one host, keeping track of all the host variables can get out of hand.  It's best to use an inventory directory, rather than just a single hosts file.  Take a look at the inventory_example directory.

You will pass your own inventory directory as a parameter ("-i") on the command line.

### Ansible configuration defaults

Ansible expects playbooks, roles, etc (e.g. this repository) to be in /etc/ansible by default.
However, we typically use a local ansible.cfg for running playbooks.  The ansible.cfg included in this repository should allow for running the playbooks directory from this directory.

Make sure to use ansible-vault to encrypt files that include passwords.

Documentation about the vault is available here:

http://docs.ansible.com/ansible/playbooks_vault.html

To encrypt an already existing, unencrypted file:

    ansible-vault encrypt foo.yml

For details about the vault:

[Variables and Vaults](group_vars/)

### Test ansible:

At this point, if you run:

    ansible all -m ping -i /path/to/inventory

it should be "success"!

If you're using a VM, this is a good chance to take a snapshot of your host so it's easy to revert back to this point for testing.

## Using ansible

### External Roles

This playbook utilized roles from Ansible Galaxy. These require using ansible-galaxy to pull them down and make them available locally.

To grab them all, in the main directory of this system-playbooks project, run the following:

    ansible-galaxy install -r roles.yml

These roles are then available for use by playbooks.

### Applying system configurations

Pick a playbook, review the configured roles, then give it a go:

    ansible-playbook asm_install.yml -i /path/to/inventory

If the playbook completes successfully, *congratulations!* The servers you specified in your inventory should be set up correctly.
