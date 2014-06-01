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

By default, SIM sends and receives messages exclusively via SMS. It uses a "backend" called [EnvayaSMS](http://sms.envaya.org/), which translates between SMS messages and HTTP requests, to do so. However, any other set of backends could be used, including much higher-volume SMS-to-HTTP gateways than EnvayaSMS.

* Each message that SIM receives triggers a defined action. Messages can be used to set data in or retrieve data from a database, especially a remote database such as DHIS2.

* After handling a message, SIM can immediately send a response message to the original sender (typically thanking them for their report or reporting an error in their message) as well as other notifications sent to interested users (such as administrators).

* Administrators can observe and moderate all of these capabilities and actions through a web-based moderation interface. 

* A new deployment, with all-new SMS operations and behaviors, can be built by a single programmer in about two months. If the programmer uses SIM's message-parsing modules and adheres to [a strict policy on defining message syntax](/use/smsapis/#eliminating_ambiguous_syntax), then these SMS operations will be reliable even if users are careless or unfamiliar with English.

You can read a description of some major use cases on the [home page](/). Otherwise, read more about the supported SMS operations and the moderation interface below.


SMS Operations
------------------

SIM includes several [SMS operations](smsapis) that support SIM's initial Laos deployment and hopefully provide a usable base for future work. At minimum, these operations represent the capabilities that are well-supported by SIM's architecture.

SIM is, at its core, a framework for building reliable SMS operations, so the supporting Python code is designed to be configurable and pluggable. If necessary you can read about how to modify the SMS operations and add new ones by learning how to [contribute](/contribute).

Moderation Interface
------------------

The [moderation interface](moderation) was created to allow users to review the SMS messages sent by Community Health Workers. The moderation interface is designed to work well with whatever set of SMS operations you've implemented. However, if necessary you can read about how to modify the moderation interface by learning how to [contribute](/contribute). 
