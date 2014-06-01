---
title: Deploy
---

# Deployment Instructions

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

### Configure SIM

First you must get root access to a publicly-available webserver. If you are unfamiliar with webhosting, we have created step-by-step instructions for [configuring a compatible hosted server from Amazon Web Services](aws).



### Setting up Apache

Apache acts as the web server that will be hosting static elements and routing dynamic requests the the python code.

#### Installing Apache

`sudo apt-get install apache2`

Starting, stopping, restarting or reloading Apache

    sudo service apache2 status
    sudo service apache2 start
    sudo service apache2 stop

etc…

Restarting Apache forces a re-compile of WSGI, and by extension Django and SIS. It can also help resolve any glitches that crop up when editing Apache’s configuration on-the-fly.

#### Enabling external HTTP and HTTPS access

If the security group for this instance does not permit inbound HTTP (port 80) and HTTPS (port 443) traffic, add this port via AWS’s web console.

#### Miscellaneous Information on Apache
* By default, `/var/www/` is the web root used by Apache. Files in that folder will be served via the web server. Django will override this behavior and handle most web requests via WSGI. Static files such as images, stylesheets and javascript will still be served by Apache out of a directory in `/var/www`.

* Apache’s configuration files live in `/etc/apache2`

* Apache’s logs live in `/var/log/apache2`. If WSGI is configured correctly and Django’s DEBUG setting is set to False, Python tracebacks of errors encountered when serving web requests are written to error.log. Otherwise, tracebacks are returned via HTTP. If WSGI is incorrectly configured, tracebacks may fail to appear in Apache’s error log.

### Installing Git

`sudo apt-get install git`

### Checking out SIS’s code

SIS’s repository lives at `/var/git/sms-immunization-manager`.  Clone it from GitHub:

`sudo git clone https://github.com/ireynolds/sms-immunization-manager.git /var/git/sms-immunization-manager/`

And give it the correct permissions:

`sudo chown -R www-data /var/git/sms-immunization-manager`

### Installing Python

`sudo apt-get install python2.7`

`sudo apt-get install python-pip`

Install any packages needed by SIS. Note that the production server does not use VirtualEnv:

`sudo pip install -r /var/git/sms-immunization-manager/requirements.txt`

### Installing WSGI

`sudo apt-get install libapache2-mod-wsgi`

### Creating a self signed certificate

In a full production instance an SSL certificate should be purchased from a certificate authority. For demonstration purposes we are going to create and self sign a certificate. When visiting a website with a self signed certificate will cause a security warning in the browser until it is installed manually.

#### Create a new directory to store the ssl certificate and key:

`sudo mkdir /etc/apache2/ssl`

To create the certificate select the number of days until it will expire. In this case, 1770 days (5 years):

`sudo openssl req -x509 -nodes -days 1770 -newkey rsa:2048 -keyout /etc/apache2/ssl/sim.key -out /etc/apache2/ssl/sim.crt`

    -----
    You are about to be asked to enter information that will be incorporated
    into your certificate request. What you are about to enter is what is
    called a Distinguished Name or a DN. There are quite a few fields but you
    can leave some blank For some fields there will be a default value,
    If you enter '.', the field will be left blank.
    -----
    Country Name (2 letter code) [AU]:US
    State or Province Name (full name) [Some-State]:Washington
    Locality Name (eg, city) []:Seattle
    Organization Name (eg, company) [Internet Widgits Pty Ltd]:CSE 481K
    Organizational Unit Name (eg, section) []:SIM
    Common Name (e.g. server FQDN or YOUR name) []:<SERVER FQDN or IP ADDRESS>
    Email Address []:<WEBMASTER EMAIL>


#### Set the key and certificate you just created to be read only:

    chmod u-w sim.crt
    chmod u-w sim.key


### Enable Apache SSL support

#### Enable the Apache SSL mod:

`sudo a2enmod ssl`

#### Restart the server after enabling SSL:

`sudo service apache2 restart`

...

...

...


### Configure a SMS-HTTP Gateway

To learn how to configure gateways, go [here](gateway-config).

### Configure a Back-End

#### DHIS2

Getting Started
-------------

### Add Users
<!-- Bootstrapping admins and then regular -->

### Add Facilities and Equipment
<!-- unimplemented back-end module handles this -->

Tailoring Operations for Your Deployment
-------------