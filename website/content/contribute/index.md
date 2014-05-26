---
title: Contribute
---

Contribute
==========

Getting Started
---------------
<!-- repos w/ organization, branching strategies; build; run; automated tests; bug-tracking -->
SIM source code can be found on GitHub [github.com/ireynolds/sms-immunization-manager](https://github.com/ireynolds/sms-immunization-manager).

The repository is layed out in the following structure:

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

`contextual` ...

`dhis2` stores the SIM app that communicates with a DHIS2 server. This app performs the semantic checks for permissions as well as retrieving from and saving to a DHIS2 database.

`equipment` ...

`info` ...

`moderation` ...

`notifications` ...

`operation_parser` ...

`permisions` ...

`project_report` ... THIS MIGHT BE REMOVED BEFORE END OF QUARTER?

`prototype` ... THIS MIGHT BE REMOVED BEFORE END OF QUARTER?

`registration` ...

`response` ...

`sim` ...

`stock` ...

`user_registration` ...

`utils` ...

`website` contains the version controlled content used to generate this web site.


Typically development of a new feature is done in a new branch. During development, it is recommended to periodically pull and merge master into your branch to ensure that the rest of the code stays current. Once development of a feature is complete and it is fully tested a pull request will alert the rest of the development team to take a look.

Our Languages, Libraries, and Frameworks
---------------

The SIM server is written in [Python](https://www.python.org/) and is based on the well-known [Django](https://www.djangoproject.com/) and [RapidSMS](https://www.rapidsms.org/) frameworks.

The administrator moderation interface is built upon [bootstrap](http://www.getbootstrap.com) for layout and styling.

This documentation page is created with [nanoc](http://nanoc.ws/).

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
