---
title: Installing SIM for Development
---

# Installing SIM for Development

* toc
{:toc}

## Getting Started

If you are an experienced Django developer, you will already have an idea of how to get started. We have detailed instructions here to make sure you don't miss anything.

## Short Instructions -- Experts Only

First, install Ubuntu 14.04 Desktop (64-bit). Add the following to `~/.bashrc`:

        export WORKON_HOME=~/Envs
        mkdir -p $WORKON_HOME
        source /usr/local/bin/virtualenvwrapper.sh
        export SIMROOT=~/sms-immunization-manager

Add the following to a new file called `~/setup-sim.sh`:

        sudo apt-get install python2.7 -y
        sudo apt-get install git -y

        sudo apt-get install python-pip -y
        sudo pip install virtualenv
        sudo pip install virtualenvwrapper

        source ~/.bashrc

        cd ~/

        git clone https://github.com/ireynolds/sms-immunization-manager.git
        mkvirtualenv -r $SIMROOT/requirements.txt sms-immunization-manager

Then complete installation by running `source ~/setup-sim.sh`. 

## Installation Instructions

These instructions accomplish the same thing as above, but include explanation at each step along the way.

### Install PyPI

[PyPI](https://pypi.python.org/pypi) (`pip` at the terminal) is a tool for installing Python packages. Install it by running `sudo apt-get install python-pip`.

### Install VirtualEnv

VirtualEnv is a tool for managing what python packages are installed from the perspective of a particular instance of the Python process. We use it to ensure consistency between the Python libraries installed in our development and deployment environments. The VirtualEnvWrapper package adds some additional tools to VirtualEnv that make it more user-friendly.

Install [VirtualEnv](https://pypi.python.org/pypi/virtualenv) and [VirtualEnvWrapper](http://virtualenvwrapper.readthedocs.org/en/latest/) by running the following commands. Don't be alarmed if some warnings appear.

	sudo pip install virtualenv
	sudo pip install virtualenvwrapper

VirtualEnvWrapper requires some changes to your `~/.bashrc` file. Add the following to `~/.bashrc` (you will likely have to install a text editor, for example, `vim`, by running `sudo apt-get install vim`):

        export WORKON_HOME=~/Envs # Set up virtualenvwrapper directory
        mkdir -p $WORKON_HOME
        source /usr/local/bin/virtualenvwrapper.sh

This change to `~/.bashrc` creates a directory `Envs/` within your home directory, which will contain the Python libraries used by each virtual Python environment you create. After making changes to `.bashrc`, you must either launch a new terminal session, or re-load your bashrc file by running source `~/.bashrc`.

### Get SIM's Source

SIM's code is hosted in a [GitHub](https://github.com/ireynolds/sms-immunization-manager) repository, so you'll first install and configure Git and then clone the source to your computer.

#### Install and Configure Git

First, install Git by running `sudo apt-get install git`.

Next, define your name and email address using the following commands. This information will appear in Git's commit log next to commits you make.

	git config --global user.name "Your Name Here"
	git config --global user.email "your_netid@uw.edu"

You may use either your UW or CSE email address. If you mistype your name or email address, or wish to change this information in the future, simply re-execute the commands above.

#### Clone SIM from GitHub

You will need to decide on a location for SIM's source code within your file system. In the following commands, we assume you wish you wish to check out the source code into the root of your home directory (accessed using the path `~/` ). However, you may check out the code into any folder you wish, and modify the following commands accordingly to reference a different parent folder than `~`. Run:

	cd ~/
	git clone https://github.com/ireynolds/sms-immunization-manager.git

You will have to enter your username and password for GitHub. After this, a directory `sms-immunization-manager` should now exist within your home directory.

### Create a Convenient Environment Variable

To help simplify commands (and to allow convenient copy-pasting between teammates), define an environment variable `SIMROOT` that points to the root directory of SIM's Git repository. If you checked out our Git repository using the commands above, this can be accomplished by adding the following to your bashrc file:

	export SIMROOT=~/sms-immunization-manager

Again, you will need to either start a new terminal session or re-load your `.bashrc` file by running `source ~/.bashrc`

Once this environment variable is defined, you can use it to reference the repository root directory. For example, running `ls $SIMROOT` lists the files in the Git repository.

### Create a Virtual Environment

To create a new virtual environment named 'sms-immunization-manager' containing the Python packages needed to run SIM, run:

	mkvirtualenv -r $SIMROOT/requirements.txt sms-immunization-manager

This command will download the packages listed in `requirements.txt` and install them to a subdirectory of `~/Envs`. It will also activate the virtual environment (you will see the name of the current virtual environment in your terminal prompt).

#### Managing Virtual Environments

To enable SIM's virtual environment at any time, run `workon sms-immunization-manager`. To disable the currently enabled virtual environment, run `deactivate`. You can regenerate the virtual environment at any time by re-running the command that made it (`mkvirtualenv`, above).

Make sure to enable SIM's virtual environment before trying to run SIM. When run outside of its virtual environment, SIM will encounter an error when importing Django.