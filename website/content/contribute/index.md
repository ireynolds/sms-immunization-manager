---
title: Contributing to SIM
---

# Contributing to SIM

* toc
{:toc}

SIM's development is overseen by the University of Washington's Department of Computer Science and Engineering, but any other interested developers are welcome to contribute. If you need to modify SIM for your deployment, please work with us so that useful changes can be merged into the core product ([contact us](/about) and read about [merging your changes into trunk](#merging_your_changes_into_trunk)).

## Tools and Frameworks

The SIM server is written in [Python](https://www.python.org/) 2.7.6 and uses well-known frameworks such as:

* [Django](http://www.djangoproject.com): A Python web framework.
* [RapidSMS](http://www.rapidsms.org): An extension of Django that helps send and receive SMS messages.
* [Bootstrap](http://www.getbootstrap.com): A UI library.
* [nanoc](http://nanoc.ws/): A static site generator (used to build this documentation site). Depends on [Ruby](https://www.ruby-lang.org/en/) and several other [gems](http://guides.rubygems.org/) (including [Slim](http://slim-lang.com/) and [Maruku](http://maruku.rubyforge.org/maruku.html)).

Tools helpful to development:

* [PyPI: The Python Package Index](https://pypi.python.org/pypi/pip): A package manager for Python.
* [virtualenv](https://pypi.python.org/pypi/virtualenv) and [virtualenvwrapper](http://virtualenvwrapper.readthedocs.org/en/latest/index.html): A tool that isolates the installation of Python packages to prevent interference with other software.

## Source Code Repository

You can find our source repository on [GitHub](https://github.com/ireynolds/sms-immunization-manager). Our source code is divided into small modules that can easily be included or removed from your deployment. In the repository you will find the following structure:

    .
    ├── contextual
    ├── dhis2
    ├── envaya
    |   ├── migrations
    |   └── templates
    ├── equipment
    ├── info
    ├── messagelog
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

The folders are briefly described below:

`contextual`: The syntax for contextual SMS operations such as FacilityCode.

`dhis2`: Sends data to and syncs data from the DHIS2 remote database. Currently unimplemented.

`equipment`: The syntax for SMS operations that relate to equipment status such as EquipmentFailure.

`info`: The syntax for SMS operations that return information, such as Help.

`moderation`: Views, templates, and models for the moderation interface. 

`notifications`: Sends notifications in response to certain SMS operations such as EquipmentFailure.

`operation_parser`: Parses the different operation codes and their block of arguments from a single message.

`permisions`: Verifies permissions of the user that sends an incoming SMS message.

`project_report`: Contains the LaTeX source of the original CSE 481 project report.

`response`: Sends a response to the sender of an SMS message.

`sim`: Main Django app settings.

`stock`: Syntax for SMS operations related to vaccine stock, such as StockLevel and StockOut.

`user_registration`: The syntax for registration SMS operations such as UserRegistration and PreferredLanguage.

`utils`: Utility classes that are used throughout SIM.

`website`: The source of this documentation website. Learn more about [contributing to the website](docs).

## Architecture

SIM's major architectural decisions are documented [here](architecture). It's critical that you read all of this information before working on SIM in earnest. You can also find a more complete and precise definition of the content of each folder in the repository's root.

## Getting Started

You can find our source repository on [GitHub](https://github.com/ireynolds/sms-immunization-manager). Our source code is divided into small modules that can easily be included or removed from your deployment.

### Installing SIM

Read [these instructions](install) to prepare to run SIM's tests and a development instance.

### Syncing a Development Database

SIM is configured to use a [SQLite](http://www.sqlite.org/) database at `$SIMROOT/db.sqlite3`. Before running SIM, this database must be initialized (by creating tables and installing any initial data). To sync the database, run `python $SIMROOT/manage.py syncdb --migrate`.

The `syncdb` command creates the necessary tables, and the `--migrate` command runs necessary [database migrations](http://south.readthedocs.org/en/latest/tutorial/part1.html#changing-the-model) for all tables.

You can also run these the `syncdb` command to clear the database and ensure a consistent state. This is especially helpful when you're creating, removing, or redefining models during development.

### Running a Development Instance

To run a development instance of SIM, run `python $SIMROOT/manage.py runserver`. This will run the SIM instance on port 8000.

If you are running SIM inside a virtual machine, you will need to run, for example, `python $SIMROOT/manage.py runserver 0.0.0.0:8000`. Setting the IP to `0.0.0.0` configures Django to accept requests from the host machine. 

In either case, you can interact with SIM at [http://localhost:8000](http://localhost:8000) in a web browser. You can exit the server by typing `Ctrl-C`. 

Any `print` statements executed as part of interacting with the development instance will print their output here. This is an incredibly useful tool for debugging.

### Running an Interactive Shell Session

To run a Python shell in the same context as SIM, run `python $SIMROOT/manage.py shell` (you can exit the shell by typing `Ctrl-D`). This shell allows you to, among other things, query and modify SIM's database.

### Running Tests

SIM includes automated tests that you can run with `python manage.py simtest`. 

You can also run manual end-to-end tests by opening the moderation interface, navigating to the RapidSMS dashboard, and then navigating to the Message Tester interface; this allows you to send fake SMS messages through SIM and see the side effects, including any responses.

### Reviewing Bugs

We use [GitHub's built-in bug tracker](https://github.com/ireynolds/sms-immunization-manager/issues?state=open).

## Releasing SIM

TODO

## Future Work

TODO

### Merging Your Changes Into Trunk

TODO How, if at all, do these modifications make it back into our repos?

## The Google Drive Repository

The team also has content in Google Drive. Read more about [the Google Drive repository](google-drive).

## The Product Documentation Site

The source of this documentation site is in the `website/` directory of the repository. The published content is generated from that source using [nanoc](http://nanoc.ws/). You can read our [overview of how the site works](docs) to get started or the nanoc documentation, which is excellent, to learn even more. 