---
title: Home
---

# SMS Immunization Server

SMS Immunization Server (SIM) is an extensible system for interpreting and acting upon structured SMS 
messages. It is tailored for use in cold chain data reporting in developing countries. 

Unlike other SMS-based data reporting systems, SIM isn't married to any particular cold 
chain information manager for its data storage, is simple to deploy and maintain, and is easy to 
modify for your deployment (it's written in [Python](https://www.python.org/) and is based on the 
well-known [Django](https://www.djangoproject.com/) and [RapidSMS](https://www.rapidsms.org/) frameworks).

If you're interesting in learning more about something in specific, you can 

* Learn __[what SIM can do for you](/use)__
* Learn __[how to deploy SIM](/deploy/)__
* Learn __[how to contribute to SIM's development](/contribute/)__

Otherwise, continue reading to get an overview of what SIM can do.

## Data Reporting ##

In the primary use case, a health worker registered to a facility has some permission to report 
data, such as vaccine stock or fridge temperature, for that facility. When they want to, for 
example, report vaccine stock for their facility, they might send a message such as 

	SL P 100 D 1770

In this message, ```SL``` is the "operation code" ("opcode") that identifies the "Stock Level" SMS 
operation. The identifier is followed by two pairs, here ```P 100``` and ```D 1770```. In this 
case, ```P 100``` means that the facility has 100 doses of the HPV vaccine. 

The data is backed up to a cold chain information manager such as [DHIS2](http://www.dhis2.org/) 
and the user immediately receives a message in their language thanking them for their report.

Every deployment can easily configure its own opcode and vaccine identifiers for this and other 
operations.

## Equipment Status Reporting ##

In a secondary use case, a health worker notices that the facility's fridge is about to have a 
mechanical failure. The user sends the code
		
	NF B

In this message, ```NF``` is the opcode for "non-functional", and ```A``` is the identifier 
assigned to one of the facility's vaccine storage fridges. When SIM receives the message, it sends 
a notification by email and/or SMS to a technician who's responsible for maintaining that equipment. 

SIM keeps information about what equipment exists at each facility by automatically importing it 
from its configured cold chain information manager.

## Other Operations ##

It's easy to either (a) remove or change the operations that ship with the product or (b) add new 
operations that suit your deployment. Although SIM ships with several useful operations built-in, 
it's designed to allow you, the user, to easily implement the operations that best suit your 
deployment.

## How does the system handle invalid inputs? ##

Typically, users

* Haven't received training in months. 
* Typically only send a few messages a month.
* Aren't familiar with English.
* Aren't familiar with Latin characters. 
* Don't have a good way to remember the English codes for various equipment or vaccines. 
* Are using a T-9 keypad on a phone to type messages.

For these reasons and more, it's common for users to enter invalid messages. Based on the mistakes 
made in a trial deployment in Laos, SIM is designed to parse messages correctly even if

* No delimiters between atoms in messages (for example, receiving ```SLP100D1770``` rather than 
```SL P 100 D 1770```).
* Users can't tell the difference between the Latin ```O``` (Oh) and ```0``` (zero) characters.

If a message can't be parsed correctly, SIM replies promptly via SMS with a descriptive error 
message that helps the user understand why the message was invalid. 

## Moderation

The system keeps a log of incoming and outgoing messages for each user and each facility, as well 
as a log of side effects caused by each message (such as updates to DHIS2, parsing error, 
notifications sent to technicians, user information updated, or any other side effect). 

Administrators can see these logs by logging into a web interface. They can use it to manually 
review and act on any messages the system receives but can't understand. 
