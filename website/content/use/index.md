---
title: Use
---

Usage Instructions
==================

There are two ways to interact with a SIM deployment. Administrative users interact with SIM via a web interface while report sending users send text based SMS messages.

Features and Capabilities
------------------


...

...

...

Admin Interface
------------------

The Admin Interface was created to allow users to moderate the messages that are being sent in by reporting users in the field. The moderation interface is built on Django and is easy to customize further. If other features are needed for your project, please help by [contributing to the project](/contribute).

...

...

...

SMS Operations
------------------

These operations were designed to support the initial Laos deployment and hopefully provide a usable base for future work. They have been designed to be configurable and pluggable. If other operations are needed for your project, please help by [contributing to the project](/contribute).

### Requirements
A “message” is the complete body of an incoming SMS message, which consists of one or more (opcode, arguments) pairs. An opcode is two alphabetic characters.

A LABEL, a common argument, is two alphabetic characters (not so--see implemented Laos-specific hacks).

All message are case-insensitive. Also, because users can’t distinguish between Latin “o” and “0”, they are treated as identical for all purposes.

Where below spaces are used as delimiters, in reality delimiters may are character in the set `[\s;,;+-]`. A single message or operation may use any mix of delimiters or none at all.

All operations apply to the user’s registered facility, unless their message also contains an FC operation (see below for more information).

If an error is detected in any operation during the syntax or semantics stages, then all operations in that message are canceled.
Two opcodes may only appear together in one message if they are in the same group (Periodic Reporting, Spontaneous Reporting, Administration, Information). The Contextual group is an exception--any Contextual operation may appear with any other operation.

Except where noted below, a particular opcode may appear multiple times in a single message.

#### Modified/Additional Requirements for Laos Only

***Implemented*** A LABEL, a common argument, is one alphabetic character.

***Not Implemented*** Periodic reports contain SL and FT operations, but not necessarily FT and SL opcodes. The following mappings must be supported:

        CHARS sl STOCK+             ==>     ft CHARS sl STOCK+
        ALARMS STOCK+               ==>     ft ALARMS sl STOCK+
        ALARMS sl STOCK+            ==>     ft ALARMS sl STOCK+
        (LABEL ALARMS)+ sl STOCK+   ==>     ft (LABEL ALARMS)+ SL


SL and FT must appear together, and FT must come first.

#### Unhandled Errors
If a single message reports conflicting data (for example, a message simultaneously reports that equipment A is both failing and working or a SL message reports two different values for the same vaccine), then the system makes no guarantees about the system’s behavior.

### Codes
Codes are organized into groups by usage and/or functionality (below).

#### Periodic Reporting

***Fridge Tag*** For periodic reporting. The argument ALARMS is a pair of digits, which may or may not be delimited. The first digit is the number of high-temperature events, and the second is the number of low-temperature events. If the value of ALARMS is a single “0”, then it is treated as if it were “0 0”.

May only appear once in a message.

`ft (LABEL ALARMS)+` For all given fridges, updates the backend with the given number of low-temperature and high-temperature events. Any unreported fridges are assumed to have zero low-temperature and zero high-temperature events.

`ft ALARMS` If ALARMS is 0 or 0 0, updates the backend with zero low- and high-temperature events for all of the facility’s fridges.

If either or both of NUM_HIGH and NUM_LOW is non-zero, updates the backend with zero low- and high-temperature events for the facility’s only fridge if the facility has only one fridge, or raises an error otherwise.

***Stock Level*** For periodic reporting. May only appear once in a message.

`sl STOCK+` Where STOCK is (LABEL INTEGER). For all given vaccines, sets stock balance to the given count. Any unreported vaccines are assumed to have zero stock.

#### Spontaneous Reporting

***Stock Out*** For spontaneous use.

`se LABEL` For the given vaccine, sets stock balance to zero and sends notifications that the facility is out of that vaccine.
Equipment Repaired
For spontaneous use, generally following a NF command.

`re LABEL` Sends notifications that the given equipment is in working order.

***Equipment Failure*** For spontaneous use.

`nf LABEL` Sends notifications that the given equipment has failed or is about to.

#### Administration

***Register User/Number*** For basic administration.

`rg PHONE_NUMBER (NAME )+` PHONE_NUMBER is defined as `\d{8}` or `\d{4}-\d{4}` or `+\d{13}`. An existing user registers a new user with the given name and phone number at the sending user’s facility. (However, in the presence of the FC code, registers the new user for the given facility.)
Set Preferred Language
For basic administration. May only appear once in a message.

`pl DIGIT` Sets the user’s preferred language according to the mapping (1: English, 2: Karaoke, 3: Lao).
#### Information

***Help*** For information. May only appear once in a message.

`he OPCODE` Returns a brief description of the requested opcode.

#### Contextual

***Facility Code*** Modifies the context of the incoming message. May only appear once in a message.

`fc INTEGER` Instead of applying each operation in the message to the user’s facility, applies it to the given facility. Note that the argument is of variable length.