---
title: Setting Up SIM
---

# Setting Up SIM

* toc
{:toc}

## Download SIM

SIM's source is published on GitHub. On our production server, it will be in `/var/git/sms-immunization-manager`. Run the following commands.
    
    sudo apt-get install git -y
    sudo git clone https://github.com/ireynolds/sms-immunization-manager.git \
        /var/git/sms-immunization-manager/

And assign the correct permissions to the source's folder.

    sudo chown -R www-data /var/git/sms-immunization-manager

## Install SIM's Dependencies

Now install SIM's major dependencies, including any required Python packages (stored in requirements.txt in the root of the source folder).

    sudo apt-get install python2.7
    sudo apt-get install libapache2-mod-wsgi

    sudo apt-get install python-pip
    sudo pip install -r /var/git/sms-immunization-manager/requirements.txt

Note that the production server does not use VirtualEnv.

## Synchronize a Deployment Database

First, create an empty database for SIM by running

	sudo python /var/git/sms-immunization-manager/manage.py syncdb

This will prompt you to create a first user. This first user will have complete access to the features of SIM, DJango, and RapidSMS, so make sure this user account is secure. 

Next, make sure Apache can write to this database and the RapidSMS log file:

	sudo chown www-data /var/git/sms-immunization-manager/db.sqlite3
	sudo chgrp www-data /var/git/sms-immunization-manager/db.sqlite3
	sudo chmod 664 db.sqlite3
	sudo chown www-data /var/git/sms-immunization-manager/sim/rapidsms.log
	sudo chgrp www-data /var/git/sms-immunization-manager/sim/rapidsms.log
	sudo chmod 664 /var/git/sms-immunization-manager/sim/rapidsms.log
