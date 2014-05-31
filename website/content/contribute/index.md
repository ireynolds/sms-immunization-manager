---
title: Contribute
---

Contribute
==========

* toc
{:toc}

This project started at the University of Washington Computer Science department but we are happy to work with developers anywhere. If you need to modify SIM for your deployment, work with us so that useful changes can be merged in with the core development.

Getting Started
---------------
<!-- repos w/ organization, branching strategies; build; run; automated tests; bug-tracking -->

Our source code is divided into small modules that can easily be included or removed from your deployment.

### GitHub Repo

SIM source code can be found on [GitHub](https://github.com/ireynolds/sms-immunization-manager).

### Directory Structure

In the repository you will find the following structure:

    .
    ├── contextual
    ├── dhis2
    ├── equipment
    ├── info
    ├── moderation
    |   ├── locale
    |   └── templates
    ├── notifications
    ├── operation_parser
    ├── permissions
    |   └── locale
    ├── project_report
    ├── prototype
    ├── registration
    ├── response
    ├── sim
    |   ├── static
    |   |   ├── css
    |   |   ├── fonts
    |   |   └── js
    |   └── templates
    |       ├── include
    |       └── rapidsms
    ├── stock
    ├── user_registration
    ├── utils
    |  └── management
    |      └── commands
    └── website
        ├── content
        └── layouts

The folders are:

`contextual`: ...

`dhis2`: app that communicates with a DHIS2 server. This app performs the semantic checks for permissions as well as retrieving from and saving to a DHIS2 database.

`equipment`: app that reacts to SMS messages that include reports on equipment status.

`info`: app that responds to SMS messages that include help requests.

`moderation`: contains code for the admin moderation web interface.

`notifications`: app that sends notifications to different users based on registered intrest.

`operation_parser`: app that parses the different operation codes and their block of arguments from a single message.

`permisions`: app that verifies permissions of the user that is sent an incoming SMS message.

`project_report`: ... THIS MIGHT BE REMOVED BEFORE END OF QUARTER?

`prototype`: ... THIS MIGHT BE REMOVED BEFORE END OF QUARTER?

`registration`: ...

`response`: app that sends the response to the sender of a message.

`sim`: main Django app settings

`stock`: app that reacts to SMS messages that include reports about inventory stock levels.

`user_registration`: ...

`utils`: utility classes that are used throughout SIM.

`website`: contains the version controlled content used to generate this web site.

Typically, developers create new features in a separate "feature branch". Developers regularly merge the master branch into their feature branch to keep it up-to-date. Once development of a feature is complete and fully-tested, the developer submits a pull request to alert the rest of the development team to do a code review.

Our Languages, Libraries, and Frameworks
---------------

The SIM server is written in [Python](https://www.python.org/) 2.7.6.

SIM is built using the well known frameworks:

* [Django](http://www.djangoproject.com)
* [RapidSMS](http://www.rapidsms.org)
* [Bootstrap](http://www.getbootstrap.com)

Tools helpful to development:

* [PyPI: The Python Package Index](https://pypi.python.org/pypi/pip)
* [virtualenvwrapper](http://virtualenvwrapper.readthedocs.org/en/latest/index.html)

This documentation page is created with [nanoc](http://nanoc.ws/). You will need it if you want to edit these pages.

Getting Started
---------------

If you are an experience Django developer you will already have an idea of how to get started. We have detailed instructions here to make sure you don't miss anything.

### Short Instructions -- Experts Only

First, install Ubuntu 13.04 Desktop (32- or 64-bit). Add the following to `~/.bashrc`:

        export WORKON_HOME=~/Envs
        mkdir -p $WORKON_HOME
        source /usr/local/bin/virtualenvwrapper.sh
        export SIMROOT=~/sms-immunization-manager

Add the following to a new file called `~/setup-sms-immunization-manager.sh`:

        sudo apt-get install python2.7 -y
        sudo apt-get install git -y

        sudo apt-get install python-pip -y
        sudo pip install virtualenv
        sudo pip install virtualenvwrapper

        source ~/.bashrc

        cd ~/

        git clone https://github.com/ireynolds/sms-immunization-manager.git
        mkvirtualenv -r $SIMROOT/requirements.txt sms-immunization-manager
        workon sms-immunization-manager

Then run `source ~/setup-sms-immunization-manager.sh`. To run the server, run `python $SIMROOT/manage.py runserver 0.0.0.0:8000`. Then you can access the server either by running `wget localhost:8000` or by visiting `localhost:8000` in your browser.

### Extended Instructions

#### Install PyPI

PyPI (`pip` at the terminal) is a tool for installing Python packages. Install it by running `sudo apt-get install python-pip`.

#### Install VirtualEnv

VirtualEnv is a tool for managing what python packages are installed from the perspective of a particular instance of the Python process. We use it to ensure consistency between the Python libraries installed in our development and deployment environments. The VirtualEnvWrapper package adds some additional tools to VirtualEnv that make it more user-friendly.

Install VirtualEnv and VirtualEnvWrapper by running the following commands. Don’t be alarmed if some warnings appear.

`sudo pip install virtualenv`

`sudo pip install virtualenvwrapper`

VirtualEnvWrapper requires some changes to your `~/.bashrc` file. Add the following to `~/.bashrc` (you will likely have to install vim, for example, by running `sudo apt-get install vim`):

        export WORKON_HOME=~/Envs #Set up virtualenvwrapper directory
        mkdir -p $WORKON_HOME
        source /usr/local/bin/virtualenvwrapper.sh

This change to `~/.bashrc` creates a directory Envs within your home directory, which will contain the Python libraries used by each virtual Python environment you create. After making changes to .bashrc, you must either launch a new terminal session, or re-load your bashrc file by running source `~/.bashrc`.

### Check out SIM’s source code

#### Install Git

`sudo apt-get install git`

#### Configure User Information in Git

Define your name and email address using the following commands. This information will appear in Git’s commit log next to commits you make.

`git config --global user.name "Your Name Here"`

`git config --global user.email "your_netid@uw.edu"`

You may use either your UW or CSE email address. If you mistype your name or email address, or wish to change this information in the future, simply re-execute the commands above.

#### Check out SIM from Github

You will need to decide on a location to keep SIM’s source code within your VM’s file system. In the following commands, we assume you wish you wish to check out the source code into the root of your home directory (accessed using the path `~/` ). However, you may check out the code into any folder you wish, and modify the following commands accordingly to reference a different parent folder than `~`.

`cd ~/`

`git clone https://github.com/ireynolds/sms-immunization-manager.git`

You will have to enter your username and password for GitHub. After this, a directory `sms-immunization-manager` should now exist within your home directory.

#### Create an environment variable pointing to the repository root

To help simplify commands (and to allow convenient copy-pasting between teammates), define an environment variable SIMROOT that points to the root directory of SIM’s Git repository. If you checked out our Git repository using the commands above, this can be accomplished by adding the following to your bashrc file:

`export SIMROOT=~/sms-immunization-manager`

Again, you will need to start a new terminal session, or re-load your bashrc file by running `source ~/.bashrc`

Once this environment variable is defined, you can use it to reference the repository root directory. For example, this command lists the files in the Git repository:

`ls $SIMROOT`

#### Create a Virtual Environment for SIM

To create a new virtual environment named ‘sms-immunization-manager’ containing the Python packages needed to run SIM, run the following:

`mkvirtualenv -r $SIMROOT/requirements.txt sms-immunization-manager`

This command will download the packages listed in `requirements.txt`, and install them to a subdirectory of `~/Envs`.

### Running SIM

#### Enabling and disabling virtual environments

To enable SIM’s virtual environment, run:

`workon sms-immunization-manager`

To disable the currently enabled virtual environment, run:

`deactivate`

Make sure to enable SIM’s virtual environment before trying to run SIM. When run outside of its virtual environment, SIM will encounter an error when importing Django.

#### Initializing a testing database

SIM is configured to use a sqlite3 database at `$SIMROOT/db.sqlite3` by default. Before running SIM, this database must be initialized (by creating tables and installing any initial data). To sync the database, run the following commands:

`python $SIMROOT/manage.py syncdb`

`python $SIMROOT/manage.py migrate`

#### Start an interactive shell session

`python $SIMROOT/manage.py shell`

You can exit the shell by typing Ctrl-D.

#### Start Django’s built-in development server

`python $SIMROOT/manage.py runserver`

To interact with the server, visit [http://localhost:8000](http://localhost:8000) in a web browser. You can exit the server by typing Ctrl-C.

### Celebrate
That’s it! Your VM is ready to be used for development!


Core Architecture
---------------
<!-- overview of Django, RapidSMS, SIM; class-level implementation with UML class/sequence diagrams; assumptions/requirements for syntax and I/O -->

Modiying SIM
---------------
<!-- How, if at all, do these modifications make it back into our repos? -->

Modify Existing Syntaxes
---------------
<!-- remove; rename arguments -->

Create New Syntaxes
---------------

Modify Existing Operations
---------------

Create new Operations
---------------

Releasing
---------------
<!-- Code and docs -->

In the Future
---------------
<!-- Unimplemented; Half-assed; Next priorities -->
