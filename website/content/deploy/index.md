---
title: Deploy
---

# Deploying SIM

* toc
{:toc}

The following instructions are intended to be as helpful as possible and thus are rather detailed.

## Configuration

These instructions will help you get a SIM server up and running. If you are familiar with deploying a Django website on an Apache server much of this will be familiar. SIM is dependent on the following software:

* [Python 2.7.6](https://www.python.org/)
* [Django](https://www.djangoproject.com/)
* [RapidSMS](https://www.rapidsms.org/)
* [Apache](http://httpd.apache.org/)
* [modwsgi](https://code.google.com/p/modwsgi/)
* [Ubuntu 14.04 LTS](http://releases.ubuntu.com/14.04/)

### Setting Up a Web Host

First you must get root access to a publicly-available webserver. If you are unfamiliar with webhosting, we have created step-by-step instructions for [configuring a compatible hosted server from Amazon Web Services](aws).

### Setting Up SIM

Next, we'll [download and install SIM](sim).

### Setting Up Apache

Apache is the web server that hosts static elements (for example, images) and routes dynamic requests to SIM. Now that SIM is installed, we'll [install Apache and configure it to work with SIM](apache).
 
### Setting Up a SMS-HTTP Gateway And Backend

In order to communicate with users via SMS, SIM requires an SMS-HTTP gateway device and a corresponding backend (a RapidSMS module that communicates with the gateway via HTTP). [Read more about how to configure gateways and backends](gateway-config).

## Getting Started

### Adding Users

The first user was created when you [installed SIM](sim/#synchronize_a_deployment_database). This user is responsible for creating all moderators using the Django Admin Site. The moderators are responsible for creating new Administrator SMS users for every facility by visiting that facility's page and clicking the 'Add' button. Administrator SMS users can use the [`RG` operation](/use/smsapis/#administration) to register any new Data Reporter SMS users. The Data Reporter SMS users may not register any new users, however.

### Adding Facilities and Equipment

The canonical representation of the country's cold chain system, including the facility hierarchy and equipment registered to each facility, is stored in a remote database such as DHIS2. However, SIM keeps a copy of some of this data in order to verify each SMS operation's validity and provide a more useful moderation interface.

This information is automatically synced from the remote database periodically by a Python module in SIM. No such module currently exists, so its implementation is left to future engineers.

## Tailoring SMS Operations for Your Deployment

It's unlikely that the SMS operations that ship with SIM will satisfy your needs. To configure these operations, remove them, or build your own, you should read about how to [contribute to SIM](/contribute). You will need to have programming experience.