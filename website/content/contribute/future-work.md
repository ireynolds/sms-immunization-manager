---
title: Future Work
---

# Future Work

* toc
{:toc}
#Next Steps for Laos Deployment
##Internationalization    
Translations of error messages and other Message Effects strings, messages sent to the user, and strings used in the web interface are also needed before SIM can be deployed to Laos. To this end, our group has contacted a translator who has offered to help us translate the necessary strings from English into Lao, and these translations are currently underway.

##DHIS2 Integration
The first major component that needs to be completed for the Laos deployment is integrating the existing project with the DHIS2 backend used by health facilities in Laos so that data reports can be periodically committed to DHIS2. This would involve implementing handlers for commit signals to send or retrieve data from DHIS2 as part of SIM’s commit stage.

##User Reminders
Sending reminders to users on a regular basis to ensure timely reporting of data about the cold chain is another important next step for the Laos deployment. This would involve sending SMS messages to data workers who have not submitted monthly reports until these reports are submitted, at a frequency determined by administrators. 

##Spam Filter Improvements
One suggestion that we received from feedback on a recent demo of SIM was to allow the spam filter to send a response to the user if their message was filtered due to an unrecognized number. Currently the spam filter logs the message and halts all processing of the message if the sender is not a recognized health worker or administrator, but does not send any response back to the sender. Sending a response to spam messages would be helpful in notifying health workers as soon as possible if they are not registered in the system so that they do not make the mistake of submitting reports before they are properly registered. 

A malicious user, however, could potentially waste funds by sending numerous SMS messages to the system, and should be blocked. It would be useful to have a way of distinguishing between malicious spammers and unregistered users by determining if the same unrecognized user is trying to send an inordinate number of messages. A more advanced filtering stage may also be useful for the detection of automatic response loops that potentially drain funds. Thus, it would be helpful to have a way to keep track of the number of messages sent by and to each user in the system. Keeping track of these counts would also be helpful for facilities in determining how much to reimburse health workers for sending and receiving SMS messages using their personal phones.

##Customizable User Roles
It would also be beneficial to allow for moderators to have more flexibility in customizing health worker roles and the operation codes that each user is allowed to submit via SMS. Currently, only two roles exist to represent the list of operation codes associated with administrators and data reporters, but the list of permitted operation codes has been hard-coded as part of the SIM project settings file. Allowing administrators to adjust these roles in a non-programmatic way would increase the adaptability of our system to potential future changes in the hierarchical structure of facility workers.

##Improved Test Infrastructure
There is much room for improvement in expanding the existing test framework for SIM. For one, there is a need for more systematic end-to-end testing to confirm expected behavior as a message moves through various SIM stages. In addition, it would be very useful to have more systematic integration tests in order to confirm proper behavior for text messages with multiple opcodes that require action from multiple apps within SIM. There is also room to add more thorough tests for Message Effects to ensure that the expected message effects are being returned to the user and the moderation interface, and to validate that it is possible to reach all possible cases where Message Effects are expected to be created and returned.

##Improved Error Messages
As discussed in the Evaluation section, it is very important to ensure that error messages and logged Message Effects contain useful information for both users and moderators that is easy to understand. All Message Effect text strings should be evaluated for their helpfulness in explaining the context of the Message Effect to the relevant user, and improved where necessary. 

One interesting case to note is that if a user sends a batch of SMS messages in rapid succession, some of which contain errors, the user will get a batch of SMS responses back from SIM, but may not be able to deduce the original text message that each response is associated with if some of these responses contain reports of syntactic or semantic errors. This kind of ambiguity in the logged error messages makes it difficult for a user to correct errors in their SMS reports. It may be useful to consider including more detailed information about the context of the original text message, so that a user can clearly identify the SMS reports that were successfully received, and those that need to be resent.

Thus, in addition to the technical improvements described above, it would be useful to meet with and demo our project for health workers, administrators, and other representatives from various health organizations located in and outside of Laos to gain more feedback on the perceived usability of our system, as well as the look and feel of the moderation interface.

#Potential directions for future work
##Querying DHIS2
Providing managers at the district and national levels with the ability to query the DHIS2 database for information regarding equipment status and stock distribution could help administrators to better assess the efficiency of the cold chain. An example use case is that such a querying system could allow managers to do analysis for a particular country and get information about how well each level of the cold chain is working. Receiving a high-level overview or comparison of the performance of various health facilities would help managers to pinpoint sections of the cold chain or specific facilities that are inefficient, and allow these managers to assess the frequency of failures and discover the reasons behind poor performance in such facilities. Thus, it would be useful for a district or national level manager to be able to send an SMS message asking about aspects of the cold chain such as equipment failures, equipment shortages, stock overflow or distribution levels, and receive a reply summarizing this information across multiple facilities for easy comparison and review.

##Location information
In addition to allowing district or national level managers to query the DHIS2 database, another potential direction for future work would be to include or make use of existing location information stored in DHIS2 to allow health workers in the field to query the database. One possible use case would be to allow a health worker out on an outreach trip to provide vaccinations at a nearby village or town, or perhaps even a patient who is looking to be vaccinated, to send an SMS asking for information about the nearest facilities such as location, hours, and current vaccine stock levels. Adding this ability would also aid in vaccine redistribution in cases where a facility has too much or too little stock. The ability to access accurate and up-to-date data about the stock levels at other facilities would allow facilities to communicate more efficiently with each other and collectively work to deal with stock outages and prevent waste. This feature would also help to build patient trust in the ability of the health center to meet their needs, especially for patients who may need to travel far distances just to reach the health center. Such patients could send an SMS to the system to ask for the nearest locations where they have the best chance of receiving a vaccination.

##Alternatives to RapidSMS
RapidSMS was designed to handle SMS messages that contain a single operation code, and the phases and message handlers defined for the RapidSMS router are not sufficient for dealing with messages that deal with messages containing multiple operation codes that may also depend on each other. The main benefit of RapidSMS is that the router is a convenient middleman between RapidSMS apps and the backend. However, one possible area for future work is to replace the RapidSMS router with a customized router implementation of our own to accommodate the more intricate stages for checking syntax, committing data, and responding to users that our system requires. 

##Improving the parser
The current implementation of the delimiter-based parser for incoming SMS messages to our system created extra requirements when defining operation codes because the delimiter-based approach meant that vaccine names or other strings that contained operation codes may be misinterpreted as representing actual operation codes. Thus, it may be beneficial to explore alternative implementation strategies for the parser, such as the possibility of a parser that is based on context free grammars and has some knowledge of the associated grammatical patterns for the arguments required for submission with each operation code

