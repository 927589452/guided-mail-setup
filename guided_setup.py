#!/usr/bin/python
###this keyring implementation is from http://dev.gentoo.org/~tomka/mail-setup.tar.bz2
#with changes to accomodate multiple accounts on the same server
#therefor we identify the username and passwords by the mail adress and misuse the server field for that
#maybe someone has a better idea
##other elements are from URL: http://github.com/gaizka/misc-scripts/tree/master/msmtp

import getpass
import re
import sys
import gtk
try:
    import gnomekeyring as gkey
except ImportError:
    print """Unable to import gnome keyring module
On Debian like systems you probably need to install the following package(s):
python-gnomekeyring"""
    sys.exit(-1)

class Keyring(object):
    def __init__(self, name, server, protocol): #instead of server we use mail for offlineimap
        self._name = name
        self._server = server
        self._protocol = protocol
        self._keyring = gkey.get_default_keyring_sync()

    def has_credentials(self):
        try:
            attrs = {"server": self._server, "protocol": self._protocol}
            items = gkey.find_items_sync(gkey.ITEM_NETWORK_PASSWORD, attrs)
            return len(items) > 0
        except gkey.DeniedError:
            return False

    def get_credentials(self):
        attrs = {"server": self._server, "protocol": self._protocol}
        items = gkey.find_items_sync(gkey.ITEM_NETWORK_PASSWORD, attrs)
        return (items[0].attributes["user"], items[0].secret)

    #def set_credentials(self, (user, pw)):
    def set_credentials(self, (user, pw)):
        
	attrs = {
                "user": user,
                "server": self._server,
                "protocol": self._protocol,
            }
        gkey.item_create_sync(gkey.get_default_keyring_sync(),
                gkey.ITEM_NETWORK_PASSWORD, self._name, attrs, pw, True)

def get_username(mail):
    keyring = Keyring("offlineimap", mail, "imap")
    (username, password) = keyring.get_credentials()
    return username

def get_password(mail):
    keyring = Keyring("offlineimap", mail, "imap")
    (username, password) = keyring.get_credentials()
    return password

msmtp=False
offlineimap=False
mutt=False

def ask_type():
	msmtp=False
	offlineimap=False
	mutt=False

	while True:
		print "Currently i will setup " 
		if mutt==True:
			print "Mutt"
		if offlineimap==True:
			print "offlineimap"
		if msmtp==True:
			print "MSMTP"
		INPUT = raw_input(""" \
What would you want to setup? \
( MSMTP | offlineimap | MUTT )\n \
Selecting an Option you already selected will disable it""") # it would be nice if i could higlight options here
		if INPUT.lower()=="mutt": 
			mutt=(bool(mutt)^(bool(1) )) 
			#this operation toggles the bool state
		elif INPUT.lower()=="msmtp":
			msmtp=(bool(mutt)^(bool(1)))
		elif INPUT.lower()=="offlineimap":
			offlineimap=(bool(mutt)^(bool(1)))
		elif INPUT == "":
			break
		else:
			print "Sorry" , INPUT, "is not a valid input"

class account(object):
	##support for legacy mpop
	mpop=False
	imap_url=""
	imap_port="995"
	pop_url=""
	pop_port=""
	smtp_url=""
	smtp_port="587"
	account_type="IMAP" # or may be gmail
	notmuch=False
	autorefresh=5
	refresh=6
	def __init__(self):
		mail=raw_input("Please enter the mail adress you would like to configure: ")
		self.mail = mail
		name=raw_input("""\
What name would you like your account to go by? \n \
it should be unique and have enough information""")
		self.name = name
		self.user = mail
		while True:
			INPUT = raw_input("Username ( " + mail + "  ) :" )
			if INPUT == "":
				break
			else:
				self.user = INPUT
		if self.offlineimap==True:
			self.guess_imap()
			while True:
				INPUT = raw_input("IMAP URL (" + self.imap_url + ") : ")
				if INPUT =="":
					break
				else:
					self.imap_url=INPUT
			while True:
                        	INPUT = raw_input("IMAP Port (" + self.imap_port + ") : ")
                        	if INPUT =="":
                                	break
                       	 	else:   
                                	self.imap_port=INPUT
		if self.msmtp==True:
			self.guess_smtp()
			while True:
                	        INPUT = raw_input("SMTP URL (" + self.smtp_url + ") : ")
				if INPUT =="":
                                	break
	                        else:
        	                        self.smtp_url=INPUT
			while True:
                        	INPUT = raw_input("SMTP Port (" + self.smtp_port + ") : ")
                        	if INPUT =="":
                                	break
	                        else:   
        	                        self.smtp_port=INPUT
		if self.mpop==True:
                	self.guess_pop()
			while True:
                        	INPUT = raw_input("POP URL (" + self.pop_url + ") : ")
	                        if INPUT =="":
        	                        break
                	        else:   
                        	        self.pop_url=INPUT
	                while True:
        	                INPUT = raw_input("POP Port (" + self.pop_port + ") : ")
                	        if INPUT =="":
                        	        break
                        	else:   
                               		self.pop_port=INPUT
		
		self.passwords()
		if self.offlineimap==True:
			while True:
				INPUT = raw_input("Autrefresh after " +self.autorefresh +" min:")
				if INPUT=="":
					break
				else:
					self.autorefresh=INPUT
			while True:
				INPUT = raw_input("Full refresh after " +self.refresh + "quickrefresh: ")
				if INPUT =="":
					break
				else:
					self.refresh=INPUT
	def passwords(self):
		keyring_offlineimap=Keyring("offlineimap", self.mail, "imap")
		keyring_msmtp=Keyring("msmtp", self.smtp_url, "smtp")
		keyring_mpop=Keyring("mpop", self.pop_url, "pop3")
		ret = True
		while ret:
			msg = "Password for user '%s' as '%s' ? " %(self.user, self.mail)
	        	passwd = getpass.getpass(msg)
        		passwd_confirmation = getpass.getpass("Confirmation ? ")
			if passwd != passwd_confirmation:
				print "ERR: password and password confirmation mismatch"
                	else:	
				if self.offlineimap==True:
					try:
						keyring_offlineimap.set_credentials(self.user,passwd)
                	   			print "Password successfully set for offlineimap"
						ret_offlineimap = False
               				except:
                   				print "ERR: Password failed to set for offlineimap"
	                    			try:
							keyring_offlineimap.has_credentials()
							delete=raw_input(r'''
Password is already set for offlineimap
if it is incorrect please use a keyringmanager to delete it ''')
							ret_offlineimap = False
						except:
							ret = True
                                if self.msmtp==True:
					try:
						keyring_msmtp.set_credentials(self.user,password)
        	                                print "Password successfully set for msmtp"
                	                	ret_msmtp=False
					except:
                                	        print "ERR: Password failed to set for msmtp"
                                        	try:  
							keyring_msmtp.has_credentials()
        	                                        delete=raw_input(r'''
Password is already set for offlineimap 
if it is incorrect please use a keyringmanager to delete it ''')
							ret_msmtp=False
                	                        except:
                                	                ret=True
				if self.mpop==True:
					try:  
						keyring_mpop.set_credentials(self.user,password)
        	                                print "Password successfully set for mpop"
						ret_mpop=False
                        	        except: 
                                	        print "ERR: Password failed to set for mpop"
                                        	try:
							keyring_mpop.has_credentials()
        	                                        delete=raw_input(r'''
Password is already set for offlineimap 
if it is incorrect please use a keyringmanager to delete it ''')
							ret_mpop=False
                        	                except: 
                                	                ret=True

				break

	def guess_imap(self):
		#will use self.imap_url =
		#and self.imap_port =
		pass
	def guess_smtp(self):
		#see above
		pass
	def guess_pop(self):
		#see above
		pass
	def guess_type(self):
		#seeabove
		pass
	def ask_type(self):
        	self.msmtp=False
        	self.offlineimap=False
        	self.mutt=False

 	       	while True:
                	print "Currently i will setup "
                	msg=""
			if self.mutt==True:
                        	msg=msg+ "Mutt"
                	if self.offlineimap==True:
                        	msg=msg+"offlineimap"
                	if self.msmtp==True:
                        	msg=msg "MSMTP"
			if self.mpop==True:
				msg=msg+"mpop"
			print msg
                	INPUT = raw_input(r''' 
What would you want to setup? 
( MSMTP | offlineimap | MUTT | mpop)
Selecting an Option you already selected will disable it: ''') # it would be nice if i could higlight options here
                	if INPUT.lower()=="mutt":
                        	self.mutt=(bool(self.mutt)^(bool(1) ))
                        	#this operation toggles the bool state
                	elif INPUT.lower()=="msmtp":
                        	self.msmtp=(bool(self.msmtp)^(bool(1)))
                	elif INPUT.lower()=="offlineimap":
                        	self.offlineimap=(bool(self.offlineimap)^(bool(1)))
			elif INPUT.lower()=="mpop":
                        	self.mpop=(bool(self.mpop)^(bool(1)))

                	elif INPUT == "":   
                        	break
                	else:
                        	print "Sorry" , INPUT, "is not a valid input"
	
def write_offlineimap(account,config,autorefresh):
	file=open(config,"r+")
	file.write(gen_offlineimap(account,config,autorefresh))
	file.close()
def gen_offlineimap(account,config):
	accounts=[]
#	accounts=get_offlineimap_accounts(config)
	header= "\n"
	if False: #header_undefinded:
		header = header + "[general]\n"
		header = header + "metadata = $HOME/.offlineimap \n"
		header = header +  "accounts = " + ",".join(accounts,account) + "\n" 
		header = header +  r'''
#################################################################################
\#this keyring implementation is from http://dev.gentoo.org/~tomka/mail-setup.tar.bz2
\#with changes to accomodate multiple accounts on the same server
\#therefor we identify the username and passwords by the mail adress and misuse the server field for that
\#maybe someone has a better idea
\##other elements are from URL: http://github.com/gaizka/misc-scripts/tree/master/msmtp


import re
import sys
import gtk
try:
    import gnomekeyring as gkey
except ImportError:
    print """Unable to import gnome keyring module
On Debian like systems you probably need to install the following package(s):
python-gnomekeyring"""
    sys.exit(-1)

class Keyring(object):
    def __init__(self, name, mail, protocol):
        self._name = name
        self._mail = mail
        self._protocol = protocol
        self._keyring = gkey.get_default_keyring_sync()

    def has_credentials(self):
        try:
            attrs = {"mail": self._mail, "protocol": self._protocol}
            items = gkey.find_items_sync(gkey.ITEM_NETWORK_PASSWORD, attrs)
            return len(items) > 0
        except gkey.DeniedError:
            return False

    def get_credentials(self):
        attrs = {"mail": self._mail, "protocol": self._protocol}
        items = gkey.find_items_sync(gkey.ITEM_NETWORK_PASSWORD, attrs)
        return (items[0].attributes["user"], items[0].secret) 

    def set_credentials(self, (user, pw)):
        attrs = {
                "user": user,
                "mail": self._mail,
                "protocol": self._protocol,
            }
        gkey.item_create_sync(gkey.get_default_keyring_sync(),
                gkey.ITEM_NETWORK_PASSWORD, self._name, attrs, pw, True)

def get_username(mail):
    keyring = Keyring("offlineimap", mail, "imap")
    (username, password) = keyring.get_credentials()
    return username

def get_password(mail):
    keyring = Keyring("offlineimap", mail, "imap")
    (username, password) = keyring.get_credentials()
    return password

###this may be outsourced and imported with
#################################################################################
#pythonfile =  $HOME/Development/offlineimap/offlineimap-helpers.py  '''

		header = header + "maxsyncaccounts = 20 \n"
		header = header + "ui = quieti #other options are syslog,ttyui \n"
		header = header + "fsync = false #fast but insecure sync \n"
		header = header + "ignore-readonly = no \n \n"
	
	mbnames = ""
	if False: #mbnames_undefined:
		mbnames = mbnames + r'''
[mbnames]
enabled = yes'''
		path_mailboxes=raw_input("Where should i save the list of mailboxes? ")
		mbnames = mbnames + "filename = " + path_mailboxes
		mnames =  mbnames + r'''
"mailboxes "
peritem = "+%(accountname)s/%(foldername)s"
sep = " "
footer = "\n"
incremental = yes
'''	
	conf = header + mbnames
	conf= "[Account " + account.name + "]\n"
	conf= conf + "localrepository = " + account.name + "_local\n"
	conf= conf +"remoterepository = " + account.name + "_remote\n"
	conf = conf +"status_backend = sqlite\n"
	if account.notmuch==True:
		conf=conf +"postsynchook = notmuch new\n"
	else:
		conf = conf +"#postsynchook = notmuch new\n"
	if autorefresh != 0:
		conf = conf + "autorefresh = " + autorefresh + "\n"
		conf = conf + "quick = 5 \n"
	else:
		conf = conf + "#autorefresh = " + autorefresh + "\n"
                conf = conf + "#quick = 5\n"
	
	conf = conf + "\n[Repository " + account.name + "_local]"
        conf = conf + "type = Maildir"
        conf = conf + "localfolders = " + maildir + "/" + account.name
	conf = conf + r'''sep = .
restoreatime = no
maxconnections = 5'''
	if account.type=="IMAP":
        	conf =conf + r'''
#nametrans = lambda folder: re.sub('spam', '[Gmail].Spam',
#                           re.sub('drafts', '[Gmail].Drafts',
#                           re.sub('sent', '[Gmail].Sent Mail',
#                           re.sub('flagged', '[Gmail].Starred',
#                           re.sub('trash', '[Gmail].Trash',
#                           re.sub('archive', '[Gmail].All Mail', folder))))))'''
	else:
		conf = conf +r'''
nametrans = lambda folder: re.sub('spam', '[Gmail].Spam',
                           re.sub('drafts', '[Gmail].Drafts',
                           re.sub('sent', '[Gmail].Sent Mail',
                           re.sub('flagged', '[Gmail].Starred',
                           re.sub('trash', '[Gmail].Trash',
                           re.sub('archive', '[Gmail].All Mail', folder))))))'''

        conf = conf +"\n[Repository " + account.name + "_remote]\n"
        if account.type=="IMAP":
		conf = conf + "type = IMAP"
        else:
                conf = conf + "type = GMAIL"
	conf=conf + r'''ssl = yes
sslcacertfile = /etc/ssl/certs/ca-certificates.crt
remoteusereval = get_username("'''+account.email + r'''")
remotepasseval = get_password("''' +account.email + r'''")
remotehost = ''' + account.imap_url +r'''
realdelete = no
maxconnections = 5
folderfilter = lambda folder: \"important\" not in folder.lower()'''
        if account.type=="IMAP":
		conf = conf + r'''
#nametrans = lambda folder: re.sub('.*Spam$', 'spam',
#                          re.sub('.*Drafts$', 'drafts',
#                          re.sub('.*Sent Mail$', 'sent',
#                          re.sub('.*Starred$', 'flagged',
#                          re.sub('.*Trash$', 'trash',2)
#                          re.sub('.*All Mail$', 'archive', folder))))))'''
	else:
		conf = conf + r'''
nametrans = lambda folder: re.sub('.*Spam$', 'spam',
                          re.sub('.*Drafts$', 'drafts',
                          re.sub('.*Sent Mail$', 'sent',
                          re.sub('.*Starred$', 'flagged',
                          re.sub('.*Trash$', 'trash',2)
                          re.sub('.*All Mail$', 'archive', folder))))))'''

	file.close()


def write_msmtp(account,config):
        file=open(config,"r + ")
	file.write(gen_conf(account))
	file.close()

def gen_msmtp(account):
	conf= ""
	conf = conf + "#"+account.name +"\n"
        conf = conf + "account "+account.name +"\n"
        conf = conf + "host " + account.smtp_url +"\n"
        conf = conf + "from " + account.mail +"\n"
        conf = conf + "tls_starttls on" +"\n"
        conf = conf + "port " + account.smtp_port +"\n"
        conf = conf + "auth on" +"\n"
        conf = conf + "user " + account.user +"\n"
	return conf

def write_mutt(account):
	pass	

def gen_configs(account):
	if account.mutt==True:
		#config_mutt=raw_input("Where should I put your mutt config")
		print gen_mutt(account,config_mutt)
		print "Is this correct"
		
	if True: # account.msmtp==True:
		#config_msmtp=raw_input("Where should I put your msmtp config")
		print gen_msmtp(account)
		print "Is this correct"
	if True: # account.offlineimap==True:
		#config_offlineimap=raw_input("Where should I put your offlineimap config")
		print gen_offlineimap(account,config_offlineimap)
		print "Is this correct"

def main():
	print """\
###################################################################################
################ Welcome to my configuration wizard ###############################
################ I hope it can help you             ###############################
################ My ASCII Skills suck !!!           ###############################
###################################################################################"""

#	ask_type()
	acc=account()
	gen_configs(acc)


main()

