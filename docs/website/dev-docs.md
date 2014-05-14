styles: styles.css
title: Developer Documentation
home: homepage.html

# Install SIM #

This section describes how to install the unmodified application.

1. Add the following to ```~/.bashrc```.

		export WORKON_HOME=~/Envs
		mkdir -p $WORKON_HOME 
		source /usr/local/bin/virtualenvwrapper.sh 
		export SIMROOT=~/sms-immunization-manager

1. Add the following to a new script ```~/setup-sim.sh```.

		sudo apt-get install python2.7 -y
		sudo apt-get install git -y

		sudo apt-get install python-pip -y
		sudo pip install virtualenv
		sudo pip install virtualenvwrapper

		source ~/.bashrc

		cd ~/
		git clone https://github.com/ireynolds/sms-immunization-manager.git
		
		cd $SIMROOT
		mkvirtualenv -r requirements.txt sms-immunization-manager
		workon sms-immunization-manager

		python manage.py syncdb
		python manage.py migrate

1. Run this script with ```source ~/setup-sim.sh```. You will need to enter the contact 
   information for the first admin user.

## Architecture

The root of the repository is a [Django](https://www.djangoproject.com/) application. Below is a
brief description of the files and directories in the root of the repository.

You can also read about our [major design decisions](design-decisions.html).

* **sim**: This is the top-level package that includes, for example, the main settings
	for SIM.
* **utils**: This module includes helper classes and methods useful throughout SIM.
* **dhis2**: This module sends data to and from DHIS2.
* **equipment**: The module interprets the syntax of equipment-related operations.
* **moderation**: This module module implements the logging and moderation back-end and UI.
* **notifications**: This module sends notifications to users via SMS or emails.
* **operation_parser**: This module contains the top-level parser that splits an incoming message into
	its constituent operations before any individual operation is parsed.
* **permissions**: This module models, stores, and verifies each user's permission to use
	some set of operations.
* **registration**: This module interprets the syntax of user-related operations.
* **stock**: This module interprets the syntax of vaccine stock-related operations.

It also contains the following files:

* **manage.py**: The Django automation tool, similar to [make](http://www.gnu.org/software/make/) 
	and other tools.
* **requirements.txt**: A list of Python dependencies to be installed in SIM's 
	[virtualenv](https://pypi.python.org/pypi/virtualenv).

# Build and run SIM #

Run SIM by running ```python $SIMROOT/manage.py runserver```. You can access the site in your web 
browser at ```http://localhost:8000/```.

# Test SIM #

## Manual testing #

The web UI for administrators can be tested by running SIM in development mode (above). The 
SMS operations are best tested by writing unit and integration tests. 

## Automated testing #

Run the automated tests by running ```python manage.py simtest```.

# Continuous Integration #

This section left intentionally and temporarily blank.

# Bug Tracking #

This section left intentionally and temporarily blank.

# Releasing a new version #

This section left intentionally and temporarily blank.