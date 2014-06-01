---
title: Getting a Self-Signed Certificate
---

# Getting a Self-Signed Certificate

* toc
{:toc}

Visiting a website with a self-signed certificate causes a security warning in the browser, so don't use a self-signed certificate on a real production instance. A self-signed certificate is useful for demonstration purposes and for internal staging (production-level, but private) instances.

## Create the Certificate

First, create a folder to store the certificate: `sudo mkdir /etc/apache2/ssl`.

Next, create the certificate. This certificate will expire in 1770 days (5 years):

	sudo openssl req -x509 -nodes -days 1770 -newkey rsa:2048 \
		-keyout /etc/apache2/ssl/sim.key -out /etc/apache2/ssl/sim.crt

Fill in the following values when prompted:

    Country Name: US
    State or Province Name: Washington
    Locality Name: Seattle
    Organization Name: University of Washington
    Organizational Unit Name: Dept. of Computer Science and Engineering
    Common Name: <SERVER FQDN or IP ADDRESS>
    Email Address: <WEBMASTER EMAIL>


## Set Permissions

The certificate is only usable if it is marked as read-only, so run:

    chmod u-w sim.crt
    chmod u-w sim.key