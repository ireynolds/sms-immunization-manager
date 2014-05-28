---
title: Deploy
---

Deployment Instructions
=============

The following instructions are intended to be as helpful as possible and thus are rather detailed.

Configuration
-------------

These instructions will help you get a SIM server up and running. If you are familiar with deploying a Django website on an Apache server much of this will be familiar. SIM is dependent on the following software:

* Python 2.7.6
* Django
* RapidSMS
* Apahce
* modwsgi

### Configure SIM

For users that are unfamiliar with webhosting we have created these step-by-step instructions for deploying a SIM server using a hosted server from Amazon Web Services.

#### Starting an Amazon EC2 instance

1. Open up the EC2 dashboard for the US-West (Oregon) availability zone.
2. Click Launch Instance
3. Choose the host operating system ‘Ubuntu Server ‘Ubuntu Server 14.04 LTS (PV)’, with 64 bit selected.
4. Check that the Instance Type is micro (unless you wish to provision a larger instance)
5. Click ‘Next: Configure Instance Details’
6. Select ‘No Preference’ for the launch subnet.
7. Leave monitoring, user data, public IP, IAM role, shutdown behavior and tenancy in their default state.
8. Enable termination protection.
9. Select the default Kernel and RAM Disk IDs
10. click ‘Next: Add Storage’
11. Use the default storage device configuration, unless you have some specific reason to change it (e.g. would like to provision more disk space, and are allowed to).
12. Click ‘Next: Tag Instance’
13. Don’t add any tags.
14. Click ‘Next: Configure Security Group’
15. Either create a new security group that allows SSH connections (this is the default security group settings), or use an existing security group that you know to be configured correctly. Add inbound HTTP access as well.
16. Click ‘Review and Launch’.
17. Click ‘Launch’
18. Either generate a new keypair, or use an existing one. This keypair should only be used for our 403 project, and not for any personal EC2 instances you may have, since you may need to share it with other team members.
19. Make sure you have downloaded the keypair as a .pem file. Pace this file into your home directory and run chmod 400 on the file.

#### Viewing provisioned EC2 instances

1. Open the EC2 Management Console for the US-West availability zone.
2. Click on the Instances link in the menu on the left
3. To view details about an instance, click on it in the table. This data includes
  * The internal and external IP of the instance
  * The domain name provided by Amazon for the instance
  * Links to modify or terminate the instance.

#### Accessing an EC2 instance as root

This should only be used if individual user accounts are unavailable or broken. Whenever possible, use sudo to impersonate root instead of logging in as a root user.

If your keypair is installed, run the following command to ssh into an EC2 instance:

`ssh -i ~/.ssh/[keypair name].pem ubuntu@[instance domain or IP]`

The root user is also accessible, however its use is discouraged. Ubuntu Server comes pre-configured with an ubuntu user that is a sudoer.

### Configuring user permissions

#### Create an individual user

`sudo adduser [username]`

You will be prompted for a password, name, and other miscellaneous information that can be left blank.

#### Add a user to sudoers

`sudo adduser [username] sudo`

This adds the given user to the group ‘sudo’, which is configured to grant sudo access to its members. Do not manually edit `/etc/sudoers`unless absolutely necessary.


#### Enable SSH password authentication

By default, EC2 instances are configured to reject password authentication for SSH, and require a keypair instead. Though more secure, this is inconvenient and overkill for our needs. To enable password authentication:

Open `/etc/ssh/sshd_config` and set PasswordAuthentication to ‘yes’.
Reload sshd’s configuration data by running

`sudo service ssh reload`

Once SSH password authentication has been enabled, log out of the ubuntu user and into your personal user. Use your personal user when accessing the server unless you have a specific reason for using ubuntu or root.

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

#### EnvayaSMS

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