---
title: SMS Operations
---

{::options parse_block_html="true" /}

# SMS Operations

* toc
{:toc}

## Message Requirements

A "message" is the complete body of an incoming SMS message, which contains multiple SMS operations (except where noted below, a particular operation may appear multiple times in a single message.). Each SMS operation is a two-character "operation code" followed by some text (the "arguments"). The arguments usually encode some data, such as the stock level of a particular vaccine or the name and phone number of a new health worker to register.

Each message is executed in some context, usually related to the user who sent the message. For example, a message that reports stock level automatically applies to the facility to which the sending user is registered. Any message in the Contextual group, such as `FC`, modifies this context.

### Interpreting a Message

Upon receiving a message, all operations are interpreted before any is acted upon. If any operation contains an error, then no operation is acted upon. This reduces the chance of misinterpreting an operation, especially because some operations modify the context in which other operations execute.

If an error is detected in any operation, then all operations in that message are canceled. SIM makes an effort to detect errors as early as possible so that either all operations in a message succeed or none do--this, again, reduces the chances of misinterpreting a message.

### Eliminating Ambiguous Syntax

The overwhelming majority of these are a result of (a) alphabetic arguments that may contain an operation code inside them, which could confuse the parser as it identifies significant opcodes, and (b) the requirements that messages with no delimiters be allowed.

It is important that operation codes do not appear in the arguments to an operation (save `HE`, which is the only exception). For example, no vaccine can be labeled `SL` if there is also an `SL` operation code. If there were, the message `SL SL 10` would be ambiguous.

To further eliminate ambiguity, two operations may only appear together in one message if they are in the same group (Periodic Reporting, Spontaneous Reporting, Administration, Information). The Contextual group is an exception--any Contextual operation may appear with any other operation.

The definitions below are listed using spaces as delimiters. However, if delimiters are present at all, they may be spaces, semicolons, commas, plus signs, or minus signs. To accomodate for this, the format of each SMS operation is defined carefully so that no delimiters are necessary--for example, all alphabetic codes and labels are exactly two characters, and no variable-length numeric arguments are always separated by an alphabetic argument. These measures make it much less likely that a mistake in typing a message would go unnoticed.

Additionally, the system treats `o` and `0` as identical because of the difficulty many users have in distinguishing between them. This is done by converting all instances of `o` to `0` before interpreting the message. For this reason, all opcodes and arguments (including any labels and identifiers) must be written as if the letter `o` does not exist.

Some operations, such as HE and RG, have inherently ambiguous arguments; they are variable-length and alphabetic, so many valid values for the arguments contain opcodes (for example, HE's argument is intended to contain opcodes!). To eliminate this ambiguity, these operations must be last in the message. If they are not last, then a possibly-confusing error message will be returned.

When defining a syntax, be careful to consider the full range of possible interactions between operation codes. For example, the message "NFC", which is correct if treated as "NF C" (reports broken equipment) without delimiters, may be incorrect if treated as "N FC" (finding the FC opcode rather than the NF). This particular message is interpreted correctly, but similar ones may not be.

## Modified/Additional Requirements for Laos Only

***Implemented***
All labels are one character rather than two. This produces ambiguity that can be reduced by using two-character labels (the same length as opcodes).

***Not Implemented*** 
Periodic reports contain SL and FT operations, but not necessarily FT and SL operation codes. The following mappings must be supported:

* `CHARS sl STOCK+`             should be interpreted as     `ft CHARS sl STOCK+`
* `ALARMS STOCK+`               should be interpreted as     `ft ALARMS sl STOCK+`
* `ALARMS sl STOCK+`            should be interpreted as     `ft ALARMS sl STOCK+`
* `(LABEL ALARMS)+ sl STOCK+`   should be interpreted as     `ft (LABEL ALARMS)+ SL`

SL and FT must appear together, and FT must come first.

Facility codes are variable-length alphanumeric strings. Introducing this feature would dramatically increase the potential for ambiguity by risking that the facility code contains an opcode. Fixed-length alphanumeric strings and variable-length integers are unambiguous.

## Unhandled Errors

If a single message reports conflicting data (for example, a message simultaneously reports that equipment A is both failing and working or a SL message reports two different values for the same vaccine), then the system makes no guarantees about the system’s behavior.

## Supported Operation Codes
Codes are organized into groups by usage and/or functionality (below).

### Periodic Reporting

These operations are reported on a schedule (for example, monthly).

***Fridge Tag*** 
The argument `ALARMS` is a pair of digits, which may or may not be delimited. The first digit is the number of high-temperature events (`NUM_HIGH`), and the second is the number of low-temperature events (`NUM_LOW`). If the value of `ALARMS` is a single `0`, then it is treated as if it were `0 0`. May only appear once in a message.

<div class="sms-api-syntax" markdown="1">
`ft (LABEL ALARMS)+` For all given fridges, updates the backend with the given number of low-temperature and high-temperature events. Any unreported fridges are assumed to have zero low-temperature and zero high-temperature events.

`ft ALARMS` If `ALARMS` is `0` or `0 0`, updates the backend with zero low- and high-temperature events for all of the facility’s fridges.

If either or both of `NUM_HIGH` and `NUM_LOW` is non-zero, updates the backend with zero low- and high-temperature events for the facility’s only fridge if the facility has only one fridge, or raises an error otherwise.

__Examples__
* `FT 1 2`
* `FT A 1 0`
* `FT A 1 0B21`
* `FT A 1 0B0C43`
* `FT A 0 B 0 1 C 3 4 D 0`
</div>

***Stock Level*** 

The argument `STOCK` is (`LABEL INTEGER`). May only appear once in a message.

<div class="sms-api-syntax" markdown="1">
`sl STOCK+` For all given vaccines, sets stock balance for the given vaccine to the given number of doses. Any unreported vaccines are assumed to have zero stock.

__Examples__
* `SLA1`
* `SL A 1`
* `SLAB1`
* `SL ABC 12`
* `SL ABC12E3FG63H4`
* `SL ABC12 E 3 FG 63H4`
</div>

### Spontaneous Reporting

These operations are used at irregular intervals. For example, a facility would report that it's out of stock as soon as it happens rather than waiting for the scheduled reporting date.

***Stock Out*** 

<div class="sms-api-syntax" markdown="1">
`se LABEL` For the given vaccine, sets stock balance to zero and sends notifications that the facility is out of that vaccine.

__Examples__
* `SE A`
</div>

***Equipment Repaired*** Generally follows a `NF` command.

<div class="sms-api-syntax" markdown="1">
`re LABEL` Sends notifications that the given equipment is in working order.

__Examples__
* `RE  ;, A`
* `REA ;, `
</div>

***Equipment Failure***

<div class="sms-api-syntax" markdown="1">
`nf LABEL` Sends notifications that the given equipment has failed or is about to.

__Examples__
* `NF  ;, A`
* `NFA ;, `
</div>

### Administration

These operations affect the registered users.

***Register User/Number*** 

The argument `PHONE_NUMBER` is defined as `\d{8}` or `\d{4}-\d{4}` or `+\d{13}`. May only appear once in a message. Must appear last in the message.

<div class="sms-api-syntax" markdown="1">
`rg PHONE_NUMBER (NAME )+` An existing user registers a new user with the given name and phone number at the sending user’s facility. (However, in the presence of the `FC` code, registers the new user for the given facility.)

__Examples__
* `RG 11112222`
* `RG1111-2222`
* `RG 0000022222222`
</div>

***Set Preferred Language***
May only appear once in a message.

<div class="sms-api-syntax" markdown="1">
`pl DIGIT` Sets the user’s preferred language according to the mapping (`1`: English, `2`: Karaoke, `3`: Lao).

__Examples__
* `PL 1`
* `PL2`
</div>

### Information

***Help*** 
For information. May only appear once in a message. Must appear last in the message.

<div class="sms-api-syntax" markdown="1">
`he OPCODE` Returns a brief description of the requested opcode.

__Examples__
* `HE SL`
* `HEHE`
</div>

### Contextual

These operations modify the context of the other operations in their message.

***Facility Code*** 
May only appear once in a message.

<div class="sms-api-syntax" markdown="1">
`fc INTEGER` Instead of applying each operation in the message to the user’s facility, applies it to the given facility. Note that the `INTEGER` argument is of variable length. 

__Examples__
* `FC 0`
* `FC1102`
</div>