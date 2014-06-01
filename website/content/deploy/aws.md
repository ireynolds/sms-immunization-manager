---
title: Configuring Amazon AWS
---

# Configuring Amazon AWS

* toc
{:toc}

## Provisioning an AWS EC2 Instance

1. Open up the EC2 dashboard for the US-West (Oregon) availability zone.
2. Click Launch Instance.
3. Choose the host operating system "Ubuntu Server 'Ubuntu Server 14.04 LTS (PV)'", with 64-bit selected.
4. Check that the Instance Type is micro (unless you wish to provision a larger instance).
5. Click "Next: Configure Instance Details".
6. Select "No Preference" for the launch subnet.
7. Leave monitoring, user data, public IP, IAM role, shutdown behavior and tenancy in their default state.
8. Enable termination protection.
9. Select the default Kernel and RAM Disk IDs.
10. click "Next: Add Storage".
11. Use the default storage device configuration, unless you have some specific reason to change it (e.g. would like to provision more disk space, and are allowed to).
12. Click "Next: Tag Instance".
13. Don't add any tags.
14. Click "Next: Configure Security Group".
15. Either create a new security group that allows SSH connections (this is the default security group settings), or use an existing security group that you know to be configured correctly. Add inbound HTTP access as well.
16. Click "Review and Launch".
17. Click "Launch".
18. Either generate a new keypair, or use an existing one. Keep in mind that you may have to share with keypair with other developers on this project.
19. Make sure you have downloaded the keypair as a .pem file. Pace this file into your home directory and run `chmod 400` on the file.

## Enabling external HTTP and HTTPS access

If the security group for this instance does not permit inbound HTTP (port 80) and HTTPS (port 443) traffic, add these ports via AWS's web console.

## Viewing Provisioned EC2 Instances

1. Open the EC2 Management Console for the US-West availability zone.
2. Click on the Instances link in the menu on the left.
3. To view details about an instance, click on it in the table. This data includes.
	* The internal and external IP of the instance.
	* The domain name provided by Amazon for the instance.
	* Links to modify or terminate the instance.

## Enabling SSH password authentication

By default, EC2 instances are configured to reject password authentication for SSH, and require a keypair instead. Though more secure, this is inconvenient and overkill for our needs. To enable password authentication:

Open `/etc/ssh/sshd_config` and set `PasswordAuthentication` to `yes`. Then reload `sshd`'s configuration data by running `sudo service ssh reload`.

## Accessing an EC2 Instance as Root

This should only be used if individual user accounts are unavailable or broken. Whenever possible, use sudo to impersonate root instead of logging in as a root user.

If your keypair is installed, run the following command to ssh into an EC2 instance:

	ssh -i ~/.ssh/[keypair name].pem ubuntu@[instance domain or IP]

The root user is also accessible, however its use is discouraged. Ubuntu Server comes pre-configured with an ubuntu user that is a sudoer.

## Configuring user permissions

### Create an individual user

Run `sudo adduser [username]`. You will be prompted for a password, name, and other miscellaneous information that can be left blank.

### Add a user to sudoers

Run `sudo adduser [username] sudo`. This adds the given user to the group "sudo", which is configured to grant sudo access to its members. Do not manually edit `/etc/sudoers` unless absolutely necessary.