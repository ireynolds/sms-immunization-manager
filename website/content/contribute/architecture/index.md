---
title: Architecture
---

# Architecture

* toc
{:toc}

SIM's architecture is based on [Django's architecture](https://docs.djangoproject.com/en/1.6/intro/overview/) and [RapidSMS's architecture](http://rapidsms.readthedocs.org/en/v0.17.0/topics/architecture.html). You should read and understand these archictures and terms before reading the following documentation.

## RapidSMS Phases vs. SIM Stages

RapidSMS's architecture is unsuitable because it requires that each SMS message has one operation. SIM, however, allow multiple SMS operations per message (and it allows each operation to affect others).

This diagram expresses the relationship between RapidSMS phases and SIM stages. Both RapidSMS phases and SIM stages are used at various points in SIM.

<img alt="Diagram of RapidSMS phases versus SIM stages" src="/static/images/phase-and-stage-architecture-diagram.png" />

The Syntax, Semantic, and Commit stages implement the independent behavior of each SMS operation. That is, to implement a new SMS operation, you will probably define handlers only for the following three stages.

__Syntax__
: The code that parses an operation's arguments into a useful Python representation. If syntactic errors are reported for an operation, then that operation does not proceed to the Semantic stage, and no operations in that message proceed to the Commit stage. An example of a syntactic error is when an argument should be a number but the sender supplied a word.

__Semantic__
: The code that verifies that an operation's arguments are valid. If semantic errors are reported for any operation, then no operations in that message proceed to the Commit stage. An example of a semantic error is when the message tries to report data for a fridge labeled C when the facility has no fridge labeled C.

__Commit__
: Any side effects are performed (for example, updating a local or remote database). The purpose of previous stages is to guarantee that the Commit stage will succeed for all operations.

The Filter, Parse, and Cleanup phases from RapidSMS are used in a few unusual circumstances, typically for code that has global effects. For example:

* The permissions module uses the Filter phase to reject messages from unrecognized numbers and to attach a valid contact to each message.
* The global message parser, which splits a message into its constituent operations, uses the Parse phase (operating before any SMS operations) to prepare the operations to be handled independently.
* The responder module uses the Cleanup phase, after all SMS operations have been handled, to choose a response to send back to the user.

## Create New SMS Operations or Side Effects

SIM apps subclass `utils.operations.OperationBase`, which subclasses `rapidsms.apps.base.AppBase`. The `OperationBase` class adapts RapidSMS's Parse and Handle phases to SIM's Syntax, Semantic, and Commit stages and passes all other phases directly through.

To implement a new SMS operation, first read the [rules for SMS operations](/use/smsapis) to prevent syntactic ambiguity. Then register the new operation in `sim/settings.py` as necesary (read about [SIM's custom fields in `settings.py`](#sims_modifications_to_)).

Next, define the Syntax stage.

	#!python
	def ExampleSIMApp(utils.operations.OperationBase):
	    '''Parses the example 'EX' SMS operation.'''

	    '''Returned by the Help SMS operation.'''
	    helptext = "For example, 'EX'. Implements a behaviorless " +
	        "Example operation."

	    def parse_arguments(self, opcode, arg_string, message):
	        '''
	        Parses the given message into a Python representation of its
	        syntactical meaning. Returns the 2-tuple (effects, args), where

	        effects
	            A list of MessageEffects representing the results of parsing.

	        args
	            A dictionary of keyword arguments to the semantic and commit
	            stage receivers for this operation.
	        '''
	        return [], {}

You may read about MessageEffects [here](#sims_modifications_to_).

Finally, define the Semantic and Commit stages. There is no restriction on the number of handlers implementing each of the Semantic and Commit stages. This minimizes coupling between syntax and behavior and leaves you free to easily add and remove behaviors without interfering with existing ones.

As an illustration of the loose coupling between Syntax, Semantic, and Commit code: these three stages, for one SMS operations, are often distributed across several modules and packages.

	#!python
	django.dispatch.dispatcher.receiver(utils.operations.semantic_signal,
	    sender=ExampleSIMApp)
	def example_semantic(self, message, opcode, *args, **kwargs):
	    '''Implements the SIM Semantic stage.'''
	    return []

	django.dispatch.dispatcher.receiver(utils.operations.commit_signal,
	    sender=ExampleSIMApp)
	def example_commit(self, message, opcode, *args, **kwargs):
	    '''Implements the SIM commit stage.'''
	    return []

## SIM's Modifications to `settings.py`

SIM adds several fields to Django's `settings.py` file. These fields are documented in `settings.py`, which can be viewed in [the repository](https://github.com/ireynolds/sms-immunization-manager).

## The MessageEffect Class

MessageEffects log the effects of each operation performed on a message or on behalf of one. They are used to report their outcome to the signal sender, as well as log the outcome for moderation purposes. The following types are provided to categorize the effect. Of note, ERROR effects will block later processing of the message.

| Message Effect | Description |
|---|---|
| DEBUG | Debug effects are developer information of no relevance to users. |
| INFO | Info effects document successes or other non-errors. |
| WARN | Warning effects document minor or non-user-actionable errors. Warnings are not typically returned to users, and do not prevent later processing from taking place. |
| ERROR | Error effects document user-actionable errors. Their messages may be returned to users and prevent later processing from taking place. |
| URGENT | Urgent effects are critically important information that must be seen and acted upon immediately. Their messages are always returned to users and do not halt further message processing. Use sparingly, if ever. |
| NOTIFY | Notify effects are critically important information that require human interventions and must be seen and acted upon by a moderator. Their messages are sent to moderators and do not halt further message processing. |

## Operation Code Groups

The operation codes in a message sometimes interact with each other to form different semantic meanings. For this reason there are some operation codes that are not permitted in the presence of others. Operation codes are defined to be permissible in certain  groups. The groups are as follows:

| Op-Code Group | Description |
|---|---|
| PERIODIC | Periodic codes are used in a repeating manner for tasks like monthly, or weekly reporting. |
| SPONTANEOUS | Spontaneous codes represent some important information needs to be sent outside of a typical reporting schedule. |
| ADMINISTRATION | Administration codes handle the setup and configuration tasks. |
| INFORMATION | Information codes represent informative support codes such as a help system. |
| CONTEXTUAL | Contextual codes are intended to change some meaning of a message that might be derived from the sender. |

## Spam Filter

The spam filter, `permissions.apps.SpamFilter`, acts in RapidSMS's Filter phase. It is registered in `settings.SIM_PRE_APPS` because it must come before any OperationBase classes. Within `settings.SIM_PRE_APPS`, it is also registered first, before other classes such as `operation_parser.apps.OperationParser`, so that these later classes may assume that the `message.connections[0].contact` field is not `None` (the spam filter rejects all messages for which this field is `None`).

## Global Message Parser

The global message parser, `operation_parser.apps.OperationParser` acts during the RapidSMS Parse phase and creates MessageEffects in the Syntax stage. It is responsible for finding the registered operation codes in an incoming message. The parser annotates the message with the discovered operation codes their arguments. These annotations will be used by the individual apps that support each operation code. The annotations are created in the order they are found in the message.

The global parser discovers every non-overlapping, contiguous opcode in an incoming message. Here are some examples:

* Given `NF C`, it finds `NF`.
* Given `N F C`, it finds nothing.
* Given `NFC`, it finds `NF` (rather than `NF` and `FC` or just `FC`).
* Given `NF C SL P 100`, it finds `NF` and `SL`.

It is possible that alphabetic arguments (such as names) contain operation code sequences. When it's impossible to avoid this problem, such as with `RG`, add the operation code that contains the offending argument to `settings.SIM_OPCODES_MUST_APPEAR_LAST`. The global parser ignores any opcode it detects in a message after an opcode in this collection. For example:

* Given `RG 1111-2222 Heather`, it finds `RG` (rather than `RG` and `HE`).

It is also possible that an undelimited sequence of arguments produces an operation code sequence (such as the message `NFC`). This is avoided with careful attention when defining messages' formats. This is possible at the boundaries of any pair of alphabetic atoms (including between alphabetic arguments and opcodes).

There is no module that detects messages from registered users that don't make use of defined operations (for example, if a user tries to send SMS messages to the system as if they're talking to a human being). However, if the global parser finds a message with no operation codes, it responds with an error message along the lines of "Message must submit or request information".

## Responder

The Responder app acts during the Cleanup RapidSMS phase and creates Message Effects in the Response stage. It is responsible for sending a message back to the sender of an incoming SMS message. Hopefully this message will typically be a "Thank You" response. In the event of one or more `ERROR`s, the responder will select an error as the basis of the response.

The Responder selects the first `ERROR` attached to the message to use as the base of the response. This is by design, so that the sender can correct multiple errors one at a time in the order that they appeared in the original message. Since the size of an SMS message is limited, it was decided that trying to report multiple errors in one message would be too difficult.

The Responder will **always** send the description of an `URGENT` message effect to the sender, as well as an error if any were found. If the message was marked in the group `INFORMATION` then no "Thank You" response will be sent for a well formed message. Messages in all other groups will receive "Thank You" response in addition to any `URGENT` messages.

The Responder creates an `INFO` message effect to document any instance when a message was sent back to the sender.