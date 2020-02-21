GitReporter
===========
This is a simple tool to track changes of a GIT repository. It's design purpose is to track changes in  configurations of network appliances or Ansible setups, and report changes to the resposible staff.

It supports censoring of sensitive data as IP-addresses or password-hashes, to avoid leakage in the untrusted zones such as public clouds or e-mail providers.

It may be used to create a simple HTML page with same information without sending e-mail.


Requirements
-----------
  * GIT
  * Python 3.x
  * ansiconv (`pip3 install ansiconv`)
  * configparser (`pip3 install ansiconv`)
  * Local SMTP service or remote server


How to run
----------
Create an configuration file then simply run `gitreporter.py my-custom-config.conf`

