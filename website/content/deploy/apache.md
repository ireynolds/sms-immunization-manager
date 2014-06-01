---
title: Setting Up Apache
---

# Setting Up Apache

* toc
{:toc}

Apache is the web server that hosts static elements (for example, images) and routes dynamic requests to SIM.

## Installing Apache

Run `sudo apt-get install apache2`.

You can run the following commands to control the `apache2` service.

    sudo service apache2 status
    sudo service apache2 restart
    # many others ...

Restarting Apache forces a re-compile of WSGI, and by extension Django and SIM. Restarting Apache can also help resolve any glitches that crop up when editing Apache's configuration on-the-fly, so don't be afraid to do so.

## Enabling SSL

Enabling SSL prevents malicious people from secretly inspecting or modifying messages to and from SIM. Without SSL, the moderation interface on SIM is essentially publicly-available (even if the moderation interface is password-protected, it can be bypassed easily if SSL isn't enabled).

First, get an SSL certificate. A public production instance should have an SSL purchased from a certificate authority. For demonstration purposes, or for private production-level instances, you may follow [our instructions for setting up a temporary self-signed certificate](../ssl-certificate).

Next, enable the Apache SSL mod by running `sudo a2enmod ssl`. You will have to restart Apache, so run `sudo service apache2 restart`.

## Configure Apache's to Host SIM

We will work with the following configuration files:

* `/etc/apache2/sites-available/000-default.conf`
* `/etc/apache2/sites-available/default-ssl.conf`

First, open the default HTTPS website configuration file at `/etc/apache2/sites-available/default-ssl.conf`.

In the VirtualHost that begins with `<VirtualHost _default_:443>`, make the following changes.

Add a line with your server name right below the Server Admin email:

	ServerName <SERVER FQDN or IP ADDRESS>:443

Alter or add the following lines:

	SSLEngine on
	SSLCertificateFile /etc/apache2/ssl/sim.crt
	SSLCertificateKeyFile /etc/apache2/ssl/sim.key

Now save and close the file and reload Apache settings by running `sudo service apache2 reload`.

Finally, WSGI, Apache, and the Django settings.py file must be configured properly serve requests for dynamic and static content. Follow Django's documentation on configuring Apache with WSGI and Django. For reference, here's a working Apache configuration without SSL:

	<VirtualHost *:80>
	    # Serve static files
	    Alias /static/ /var/git/sms-immunization-manager/static/

	    <Directory /var/git/sms-immunization-manager/static>
	        Order deny,allow
	        Allow from all
	    </Directory>

	    # Serve remaining paths using WSGI
	    WSGIDaemonProcess sms-immunization-manager \
	    	python-path=/var/git/sms-immunization-manager
	    WSGIProcessGroup sms-immunization-manager
	    WSGIScriptAlias / /var/git/sms-immunization-manager/sim/wsgi.py


	    <Directory /var/git/sms-immunization-manager/sim>
	        <Files wsgi.py>
	            Order allow,deny
	            Allow from all
	        </Files>
	    </Directory>

	    ErrorLog ${APACHE_LOG_DIR}/error.log

	    # Possible values include: debug, info, notice, warn, error, crit,
	    # alert, emerg.
	    LogLevel warn

	    CustomLog ${APACHE_LOG_DIR}/access.log combined
	</VirtualHost>

## Miscellaneous Information on Apache

* By default, `/var/www/` is the web root used by Apache. Files in that folder will be served via the web server, so don't leave anything private there. Django will override this behavior and handle most web requests via WSGI. Static files such as images, stylesheets and JavaScript, however, will still be served by Apache out of a directory in `/var/www`.
* Apache's configuration files live in `/etc/apache2`.
* Apache's logs live in `/var/log/apache2`. If WSGI is configured correctly and Django's DEBUG setting is set to False, Python tracebacks of errors encountered when serving web requests are written to `error.log` in this folder. Otherwise, tracebacks are returned via HTTP. If WSGI is incorrectly configured, tracebacks may fail to appear in Apache's error log.
