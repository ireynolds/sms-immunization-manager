---
title: Use
---

Usage Instructions
==================

* toc
{:toc}

There are two users who interact with a SIM deployment: 

* Administrative users, who interact with SIM via a web interface to configure the software and moderate messages.
* Community Health Workers and other staff members, who report cold chain information via SMS. 

Features and Capabilities
------------------

* SIM accepts text-based messages from user-defined backends. A "backend" is just a way of sending and receiving messages, such as HTTP or a cellular modem. SIM comes with a backend for [EnvayaSMS](http://sms.envaya.org/), but any other backends could be used as well or instead.

* Each message that SIM receives triggers a defined action. Messages can be used to set or retrieve data from a database, especially a remote database such as DHIS2.

* After handling a message, SIM can immediately send a response SMS message to the original sender (typically thanking them for their report or reporting an error in their message) as well as other notifications sent to interested users (such as administrators).

* Administrators can observe and moderate all of these capabilities and actions through a web-based moderation interface. 

You can read a description of some major use cases on the [home page](/). Otherwise, read more about the supported SMS operations and the moderation interface below.


SMS Operations
------------------

These operations were designed to support the initial Laos deployment and hopefully provide a usable base for future work. At minimum, these operations represent the capabilities that are well-supported by SIM's architecture.

SIM is, at its core, a framework for building reliable SMS operations, so the supporting Python code is designed to be configurable and pluggable. If necessary you can read about how to modify the SMS operations and add new ones by learning how to [contribute](/contribute).

Learn more about the built-in [SMS operations](smsapis).

Moderation Interface
------------------

The moderation interface was created to allow users to review the SMS messages sent by Community Health Workers. The moderation interface is designed to work well with whatever set of SMS operations you've implemented. However, if necessary you can read about how to modify the moderation interface by learning how to [contribute](/contribute). 

Learn more about the [moderation interface](moderation).
