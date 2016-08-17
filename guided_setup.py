#!/usr/bin/python
###this keyring implementation is from http://dev.gentoo.org/~tomka/mail-setup.tar.bz2
#with changes to accomodate multiple accounts on the same server
#therefor we identify the username and passwords by the mail adress
import re
import sys
import gtk
import gnomekeyring as gkey

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

msmtp=false
offlineimap=false
mutt=false
def ask_type():
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
			mutt=(bool(mutt)^(bool(1) )#this operation toggles the bool state
		elif INPUT.lower()=="msmtp":
			msmtp=(bool(mutt)^(bool(1))
		elif INPUT.lower()=="offlineimap":
			offlineimap=(bool(mutt)^(bool(1))
		elif INPUT == "":
			break
		else:
			print "Sorry" , INPUT, "is not a valid input"

class account(object):
	imap_url=""
	smtp_url=""
	account_type="IMAP" # or may be gmail
	def __init__(self,mail,name):
		self.mail = mail
		self.name = name
		self.user = mail
		self.imap_url=self.guess_imap()
		self.smtp_url=self.guess_smtp()
	def guess_imap(self):
		pass
	def guess_smtp(self):
		pass
	def guess_type(self):
		pass
	def set_smtp(self,url):
		smtp_url=url
	def set_imap(self,url):	
		imap_url=url
	def set_type(self,string):
		account_type=string
	def get_imap(self):
		return imap_url
	def get_smtp(self):
		return smtp_url
	def get_type(self):
		return account_type

def write_offlineimap(account,config,notmuch,autorefresh):
	file=open(config,"r+")
	file.write("[Account " + account.name + "]")
	file.write("localrepository = " account.name+"_local")
	file.write("remoterepository = " +account.name+"_remote")
	file.write("status_backend = sqlite")
	if notmuch==True:
		file.write("postsynchook = notmuch new")
	else:
		file.write("#postsynchook = notmuch new")
	if autorefresh != 0:
		file.write("autorefresh = "+autorefresh)
		file.write("quick = 5")
	else:
		file.write("#autorefresh = "+autorefresh)
                file.write("#quick = 5")
	
	file.write("\n[Repository "+account.name+"_local]")
        file.write("type = Maildir")
        file.write("localfolders = "maildir+"/"+account.name)
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

        file.write("\n[Repository "+account.name+"_remote]\n"
        if account.type=="IMAP":
		file.write("type = IMAP")
        else:
                file.write("type = GMAIL")
	file.write("ssl = yes")
        file.write("sslcacertfile = /etc/ssl/certs/ca-certificates.crt")
        file.write("remoteusereval = get_username(\""+account.email+"\")")
        file.write("remotepasseval = get_password(\""+account.email+"\")")
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


def write_msmtp(account):
	pass

def write_mutt(account)
	pass

ask_type()
