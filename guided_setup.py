#!/usr/bin/python
###this keyring implementation is from http://dev.gentoo.org/~tomka/mail-setup.tar.bz2
#with changes to accomodate multiple accounts on the same server
#therefor we identify the username and passwords by the mail adress and misuse the server field for that
#maybe someone has a better idea
##other elements are from URL: http://github.com/gaizka/misc-scripts/tree/master/msmtp


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

def ask_type():
	msmtp=false
	offlineimap=false
	mutt=false

	while True:
		print "Currently i will setup " 
		if mutt==true:
			print "Mutt"
		if offlineimap==true:
			print "offlineimap"
		if msmtp==true:
			print "MSMTP"
		print "What would you want to setup?"
		print "( MSMTP | offlineimap | MUTT )"
		INPUT=raw_input("Selecting an Option you already selected will disable it")
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
	imap_url=""
	imap_port="995"
	pop_url=""
	pop_port=""
	smtp_url=""
	smtp_port="587"
	account_type="IMAP" # or may be gmail
	notmuch=False
	def __init__(self,mail,name):
		self.mail = mail
		self.name = name
		self.user = mail
		self.imap_url=self.guess_imap()
		self.smtp_url=self.guess_smtp()
		self.pop_url=self.guess_pop()
	def configure(self):
		keyring_offlineimap=Keyring("offlineimap", self.mail, "imap")
		keyring_msmtp=Keyring("msmtp", self.smtp_url, "smtp")
		keyring_mpop=Keyring("mpop", self.pop_url, "pop3")
		ret=True #retry?
		while ret:
			msg = "Password for user '%s' as '%s' ? " %(user, mail)
	        	passwd = getpass.getpass(msg)
        		passwd_confirmation = getpass.getpass("Confirmation ? ")
			if passwd != passwd_confirmation:
        	        	print "ERR: password and password confirmation mismatch"
                		ret = False
            		else:
                		if keyring_offlineimap.has_credentials()==False:
					if keyring_offlineimap.set_credentials(user,password):
                   				print "Password successfully set for offlineimap"
               				else:
                   				print "ERR: Password failed to set for offlineimap"
                    				ret = False
				else:
                                	delete=raw_input("Password is already set for offlineimap \n if it is incorrect please use a keyringmanager to delete it ")
                                if keyring_offlineimap.has_credentials()==False:
                                        if keyring_msmtp.set_credentials(user,password):
                                                print "Password successfully set for msmtp"
                                        else:   
                                                print "ERR: Password failed to set for msmtp"
                                                ret = False
                                else:   
                                        delete=raw_input("Password is already set for msmtp \n if it is incorrect please use a keyringmanager to delete it ")

                                if keyring_offlineimap.has_credentials()==False:
                                        if keyring_mpop.set_credentials(user,password):
                                                print "Password successfully set for mpop"
                                        else:   
                                                print "ERR: Password failed to set for mpop"
                                                ret = False
                                else:   
                                        delete=raw_input("Password is already set for mpop \n if it is incorrect please use a keyringmanager to delete it ")



	def guess_imap(self):
		pass
	def guess_smtp(self):
		pass
	def guess_pop(self):
		pass
	def guess_type(self):
		pass
	def set_smtp(self,url):
		smtp_url=url
	def set_imap(self,url):	
		imap_url=url
	def set_pop(self,url):
		pop_url=url
	def set_type(self,string):
		account_type=string
	def get_imap(self):
		return imap_url
	def get_smtp(self):
		return smtp_url
	def get_pop(self):
		return pop_url
	def get_type(self):
		return account_type
	

def write_offlineimap(account,config,autorefresh):
	file=open(config,"r + ")
	if mbnames_undefined:
		file.write("[mbnames]")
		file.write("enabled = yes")
		file.write("filename = ~/.dotfiles/mutt/offlineimap/offlineimap_mailboxes")
		file.write("header = \"mailboxes \"")
		file.write("peritem = \"+%(accountname)s/%(foldername)s\"")
		file.write("sep = \" \"")
		file.write("footer = \"\n\"")

	file.write("[Account " + account.name + "]")
	file.write("localrepository = " + account.name + "_local")
	file.write("remoterepository = " + account.name + "_remote")
	file.write("status_backend = sqlite")
	if account.notmuch==True:
		file.write("postsynchook = notmuch new")
	else:
		file.write("#postsynchook = notmuch new")
	if autorefresh != 0:
		file.write("autorefresh = " + autorefresh)
		file.write("quick = 5")
	else:
		file.write("#autorefresh = " + autorefresh)
                file.write("#quick = 5")
	
	file.write("\n[Repository " + account.name + "_local]")
        file.write("type = Maildir")
        file.write("localfolders = " + maildir + "/" + account.name)
        file.write("sep = .")
        file.write("restoreatime = no")
        file.write("maxconnections = 5")
	if account.type=="IMAP":
        	file.write("#nametrans = lambda folder: re.sub('spam', '[Gmail].Spam',")
	        file.write("#                           re.sub('drafts', '[Gmail].Drafts',")
        	file.write("#                           re.sub('sent', '[Gmail].Sent Mail',")
	        file.write("#                           re.sub('flagged', '[Gmail].Starred',")
        	file.write("#                           re.sub('trash', '[Gmail].Trash',")
        	file.write("#                           re.sub('archive', '[Gmail].All Mail', folder))))))")
	else:
		file.write("nametrans = lambda folder: re.sub('spam', '[Gmail].Spam',")
                file.write("                           re.sub('drafts', '[Gmail].Drafts',")
                file.write("                           re.sub('sent', '[Gmail].Sent Mail',")
                file.write("                           re.sub('flagged', '[Gmail].Starred',")
                file.write("                           re.sub('trash', '[Gmail].Trash',")
                file.write("                           re.sub('archive', '[Gmail].All Mail', folder))))))")

        file.write("\n[Repository " + account.name + "_remote]\n")
        if account.type=="IMAP":
		file.write("type = IMAP")
        else:
                file.write("type = GMAIL")
	file.write("ssl = yes")
        file.write("sslcacertfile = /etc/ssl/certs/ca-certificates.crt")
        file.write("remoteusereval = get_username(\""+account.email + "\")")
        file.write("remotepasseval = get_password(\""+account.email + "\")")
        file.write("remotehost = account.imap_url")
        file.write("realdelete = no")
        file.write("maxconnections = 5")
        file.write("folderfilter = lambda folder: \"important\" not in folder.lower()")
        if account.type=="IMAP":
		file.write("#nametrans = lambda folder: re.sub('.*Spam$', 'spam',")
        	file.write("#                          re.sub('.*Drafts$', 'drafts',")
	        file.write("#                          re.sub('.*Sent Mail$', 'sent',")
        	file.write("#                          re.sub('.*Starred$', 'flagged',")
        	file.write("#                          re.sub('.*Trash$', 'trash',2)")
        	file.write("#                          re.sub('.*All Mail$', 'archive', folder))))))")
	else:
                file.write("nametrans = lambda folder: re.sub('.*Spam$', 'spam',")
                file.write("                          re.sub('.*Drafts$', 'drafts',")
                file.write("                          re.sub('.*Sent Mail$', 'sent',")
                file.write("                          re.sub('.*Starred$', 'flagged',")
                file.write("                          re.sub('.*Trash$', 'trash',2)")
                file.write("                          re.sub('.*All Mail$', 'archive', folder))))))")

	file.close()


def write_msmtp(account,config):
        file=open(config,"r + ")
	file.write("#"+account.name)
	file.write("account "+account.name)
	file.write("host " + account.smtp_url)
	file.write("from " + account.mail)
	file.write("tls_starttls on")
	file.write("port " + account.smtp_port)
	file.write("auth on")
	file.write("user " + account.user)
	
	file.close()

def write_mutt(account):
	pass	

