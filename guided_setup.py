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
force_keyring=True;
if force_keyring == True :
#
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
			#this is adapted from the msmtp-gnome-tool
			#probably the previous method could be adapted

		def set_credentials_msmtp(self,user,pw):
			# display name for password.
			display_name = '%s password for %s at %s' % ("MSMTP", user, self._server)
			usr_attrs = {'user':user, 'server':_server, 'protocol':smtp}
			# Now it gets ready to add into the keyring. Do it.
			# Its id will be returned if success or an exception will be raised
			gkey.item_create_sync(gkey.get_default_keyring_sync(), gkey.ITEM_NETWORK_PASSWORD, display_name, attrs, pw, False)

		def get_username(mail):
			keyring = Keyring("offlineimap", mail, "imap")
			(username, password) = keyring.get_credentials()
			return username

		def get_password(mail):
			keyring = Keyring("offlineimap", mail, "imap")
			(username, password) = keyring.get_credentials()
			return password
#
else:
	#write password to file ( not suggested )
	pass
msmtp=False
offlineimap=False
mutt=False

class account(object):

	def __init__(self):
		##support for legacy mpop
		self.mpop=False
		self.imap_url=""
		self.imap_port="995"
		self.pop_url=""
		self.pop_port="993"
		self.smtp_url=""
		self.smtp_port="587"
		self.account_type="IMAP" # or may be gmail
		self.notmuch=False
		self.password="dont fucking use this if you have no reason for it"
		##example
		self.fullname="Joe Smith"
		self.mail="joe@exampe.com"
		self.name="example_joe"
		self.user = self.mail
		#offlineimap
		self.conf_offlineimap="$HOME/.dotfiles/offlineimap.conf"
		self.helper_path = "$HOME/.dotfiles/offlineimap-helper.py"
		self.refresh = "6" #quicksyncs
		self.autorefresh = "5" # minutes
		##msmtp
		self.conf_msmtp="$HOME/.dotfiles/.msmtprc"
		##mpop
		self.guess_pop()
		##mutt
		self.maildir='$HOME/Mail'
		self.path_mutt='$HOME/.dotfiles/mutt'
		self.path_mailboxes=self.path_mutt+'/offlineimap.d/offlineimap_mailboxes'
		self.ask_type()
		configure="INIT"
		while True:
			if configure=="":
				break
			elif configure.lower() =="y":
				break
			else:
				self.configure()
				self.present()
				configure=raw_input(r'''
Is this what you expected ? (y | n )  : ''')
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

	def configure(self):
		while True:
			name=raw_input("Hi whats your name (" + self.fullname + ') :')
			if name =="":
				break
			else:
				self.fullname=name
		while True:
			mail=raw_input("Please enter the mail adress you would like to configure (" + self.mail + '): ')
			if mail == "":
				break
			else:
				self.mail = mail
		while True:
			name=raw_input('''
What name would you like your account to go by?
it should be unique and have enough information ( ''' + self.name + ') :')
			if name=="":
				break
			else:
				self.name=name
		while True:
			INPUT = raw_input("Username ( " + self.user + ") :" )
			if INPUT == "":
				break
			else:
						self.user = INPUT

		if self.offlineimap==True:
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

			while True:
				conf=raw_input("where will your  offlineimap.conf be saved (" + self.conf_offlineimap + ') : ')
				if conf =="":
					break
				else:
					self.conf_offlineimap=conf

		if self.msmtp==True:
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
			while True:
				conf=raw_input("where will your msmtprc be saved (" + self.conf_msmtp + ') : ')
				if conf =="":
					break
				else:
					self.conf_msmtp=conf

		if self.mpop==True:
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

		if self.mutt==True:
			while True:
				INPUT = raw_input("Maildir (" + self.maildir + '): ')
				if INPUT == "":
					break
				else:
					self.maildir=INPUT
			while True:
				INPUT=raw_input("Where will your mutt configs be (" + self.path_mutt + ') : ')
				if INPUT=="":
					break
				else:
					self.path_mutt=INPUT
			while True:
				INPUT=raw_input("Where should i save the list of Mailboxes (" + self.path_mailboxes + ')? : ')
				if INPUT =="":
					break
				else:
					self.path_mailboxes=INPUT
	def domain(self):
		pass
	def autodiscover(self):
		try:
			pass
			#import lxml
		except:
			print "i need lxml"
#		domain= domain(self)
#		try get autoconfig.domain/mail/config-v1.1.xml
#		except
#			try domain/.well-known/autoconfig/mail/config-v1.1.xml
		#parse xml else do generic

		pass

	def present(self):
		if self.mutt==True:
			 #config_mutt=raw_input("Where should I put your mutt config")
			 print self.gen_mutt()
			 print "Is this correct"
		if self.msmtp==True:
			 #config_msmtp=raw_input("Where should I put your msmtp config")
			 print self.gen_msmtp()
			 print "Is this correct"
		if self.offlineimap==True:
			 #config_offlineimap=raw_input("Where should I put your offlineimap config")
			 print self.gen_offlineimap()
			 print "Is this correct"


	def passwords(self):
		keyring_offlineimap=Keyring("offlineimap", self.mail, "imap")
		keyring_msmtp=Keyring("msmtp", self.smtp_url, "smtp")
		keyring_mpop=Keyring("mpop", self.pop_url, "pop3")
		ret = True
		while ret:
			msg = "Password for user '%s' as '%s' on '%s'? " %(self.user, self.mail,self.smtp_url)
			passwd = getpass.getpass(msg)
			passwd_confirmation = getpass.getpass("Confirmation ? ")
			if passwd != passwd_confirmation:
				print "ERR: password and password confirmation mismatch"
			else:
				if force_keyring==True:

					if self.offlineimap==True:
						try:
							keyring_offlineimap.set_credentials(self.user,passwd)
					 		print "Password successfully set for offlineimap"
							ret_offlineimap = False
			   			except:
				   			print "ERR: Password failed to set for offlineimap"
							try:
								keyring_offlineimap.has_credentials()
								delete=raw_input(r'''Password is already set for offlineimap
if it is incorrect please use a keyringmanager to delete it ''')
								ret_offlineimap = False
							except:
								ret = True
					if self.msmtp==True:
						try:
							keyring_msmtp.set_credentials_msmtp(self.user,password)
							print "Password successfully set for msmtp"
							ret_msmtp=False
						except:
							print "ERR: Password failed to set for msmtp"
							try:
								keyring_msmtp.has_credentials()
								delete=raw_input(r'''
Password is already set for  msmtp
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
Password is already set for mpop
if it is incorrect please use a keyringmanager to delete it ''')
								ret_mpop=False
							except:
								ret=True
					break
				else:
					self.password=passwd
					break

	def guess_imap(self):
		#will use self.imap_url =
		#and self.imap_port =
		self.imap_url=""
		self.imap_port=""
	def guess_smtp(self):
		#see above
		self.smtp_url=""
		self.smtp_port=""
	def guess_pop(self):
		#see above
		self.pop_url=""
		self.pop_port=""

	def guess_type(self):
		#seeabove
		pass
	def ask_type(self):
			self.msmtp=False
			self.offlineimap=False
			self.mutt=False
			self.mpop=False
 		   	while True:
				print r'''
Currently i will setup '''
				msg=""
				if self.msmtp==True:
					msg=msg + r'''
1 MSMTP'''
				if self.offlineimap==True:
					msg=msg+r'''
2 offlineimap'''
				if self.mutt==True:
					msg=msg+ r'''
3 MUTT'''
				if self.mpop==True:
					msg=msg+r'''
4 mpop'''
				print msg
				INPUT = raw_input(r'''
What would you want to setup?

1 MSMTP |
2 offlineimap |
3 MUTT |
4 mpop

Selecting an Option you already selected will disable it
Pressing enter will end the selection : ''') # it would be nice if i could higlight options here
				if INPUT.lower()=="mutt" or INPUT.lower()=="3":
					self.mutt=(bool(self.mutt)^(bool(1) ))
					#this operation toggles the bool state
				elif INPUT.lower()=="msmtp" or INPUT.lower()=="1" :
					self.msmtp=(bool(self.msmtp)^(bool(1)))
				elif INPUT.lower()=="offlineimap" or INPUT.lower()=="2":
					self.offlineimap=(bool(self.offlineimap)^(bool(1)))
				elif INPUT.lower()=="mpop" or INPUT.lower() == "4":
					self.mpop=(bool(self.mpop)^(bool(1)))
				elif INPUT:lower()=="all" or INPUT.lower() == "0":
					if self.mpop OR self.msmtp OR self.offlineimap OR self.mutt:
						self.msmtp=False
						self.offlineimap=False
						self.mutt=False
						self.mpop=False
					else:
						self.msmtp=True
						self.offlineimap=True
						self.mutt=True
						self.mpop=True
				elif INPUT == "":
					break
				else:
					print "Sorry" , INPUT, "is not a valid input"

	def write_offlineimap(self):
		file=open(self.config,"r+")
		file.write(gen_offlineimap(self))
		file.close()

	def get_offlineimap_accounts(self):
		#this will scrape all accountnames from the offlineimap config
		return [] #similiar to pass

	def check_offlineimap_helper(self):
		if force_keyring:

			helper =  r'''
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
	def __init__(self, name, server, protocol):
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

###this may be outsourced and imported with
#################################################################################
#pythonfile =  $HOME/Development/offlineimap/offlineimap-helpers.py
'''
		f=open(self.helper_path) #should create if not existing
		f.write ( helper )
		f.close
		return r'pythonfile = %s ' % (helper_path)


	def gen_offlineimap(self):
		accounts=[]
		accounts=self.get_offlineimap_accounts()
		header= "\n"
		if False: #header_undefinded:
			header = header + "[general]\n"
			header = header + "metadata = $HOME/.offlineimap \n"
			header = header +  "accounts = " + ",".join(accounts,account) + "\n"
			header = header + self.check_offlineimap_helper()
			header = header + r'''
maxsyncaccounts = 20
ui = quieti #other options are syslog,ttyui
fsync = false #fast but insecure sync
ignore-readonly = no


'''

		mbnames = ""
		if False: #mbnames_undefined:
			mbnames = mbnames + r'''
[mbnames]
enabled = yes'''
			self.path_mailboxes='$HOME/.dotfiles/mutt/offlineimap.d/offlineimap_mailboxes'
			while True:
				INPUT=raw_input("Where should i save the list of Mailboxes (" + self.path_mailboxes + ')? : ')
				if INPUT =="":
					break
				else:
					self.path_mailboxes=INPUT
			mbnames = mbnames + "filename = " + path_mailboxes
			mbnames =  mbnames + r'''
"mailboxes "
peritem = "+%(accountname)s/%(foldername)s"
sep = " "
footer = "\n"
incremental = yes
'''
		conf = header + mbnames
		conf= "[Account " + self.name + "]\n"
		conf= conf + "localrepository = " + self.name + "_local\n"
		conf= conf +"remoterepository = " + self.name + "_remote\n"
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
		conf = conf + "\n[Repository " + self.name + "_local]"
		conf = conf + "type = Maildir"
		conf = conf + "localfolders = " + maildir + "/" + account.name
		conf = conf + r'''sep = .
restoreatime = no
maxconnections = 5'''
		if self.type=="IMAP":
			#Foldertranslation happens here; maybe we should have an interactive menu herefore
			conf =conf + r'''
#nametrans = lambda folder: re.sub('spam', '[Gmail].Spam',
#						   re.sub('drafts', '[Gmail].Drafts',
#						   re.sub('sent', '[Gmail].Sent Mail',
#						   re.sub('flagged', '[Gmail].Starred',
#						   re.sub('trash', '[Gmail].Trash',
#						   re.sub('archive', '[Gmail].All Mail', folder))))))'''
		else:
			conf = conf +r'''
nametrans = lambda folder: re.sub('spam', '[Gmail].Spam',
						   re.sub('drafts', '[Gmail].Drafts',
						   re.sub('sent', '[Gmail].Sent Mail',
						   re.sub('flagged', '[Gmail].Starred',
						   re.sub('trash', '[Gmail].Trash',
						   re.sub('archive', '[Gmail].All Mail', folder))))))'''
		conf = conf +"\n[Repository " + self.name + "_remote]\n"
		if self.type=="IMAP":
			conf = conf + "type = IMAP"
		else:
			conf = conf + "type = GMAIL"
		conf=conf + r'''ssl = yes
sslcacertfile = /etc/ssl/certs/ca-certificates.crt
remoteusereval = get_username("%s")
remotepasseval = get_password("%s")
remotehost = %s
realdelete = no
maxconnections = 5
folderfilter = lambda folder: \"important\" not in folder.lower()''' % (self.email,self.email,self.imap_url)
		if self.type=="IMAP":
			conf = conf + r'''
#nametrans = lambda folder: re.sub('.*Spam$', 'spam',
#						  re.sub('.*Drafts$', 'drafts',
#						  re.sub('.*Sent Mail$', 'sent',
#						  re.sub('.*Starred$', 'flagged',
#						  re.sub('.*Trash$', 'trash',2)
#						  re.sub('.*All Mail$', 'archive', folder))))))'''
		else:
			conf = conf + r'''
nametrans = lambda folder: re.sub('.*Spam$', 'spam',
						  re.sub('.*Drafts$', 'drafts',
						  re.sub('.*Sent Mail$', 'sent',
						  re.sub('.*Starred$', 'flagged',
						  re.sub('.*Trash$', 'trash',2)
						  re.sub('.*All Mail$', 'archive', folder))))))'''
#	file.close()


	def write_msmtp(self):
		file=open(config,"r + ")
		file.write(gen_msmtp(self))
		file.close()

	def gen_msmtp(account):
		conf= ""
		conf = r'''
# %s
account %s
host %s
from %s
tls_starttls on
port %s
auth on
user %s
''' % (account.name,account.name,account.smtp_url,account.mail,account.smtp_port,account.user)

		return conf

	def write_mutt(self):
		pass
	def gen_mutt(self):
		#will generate/modify a offlineimap.d/offlineimap file containing the hooks and source commands
		d_offlineimap=""
		if False: #offlineimap.d/offlineimap does not exist
			d_offlineimap = d_offlineimap + r'''
# IMAP: offlineimap
set folder = "%s" #"$HOME/Mail"
source "%s" #$HOME/.dotfiles/mutt/offlineimap.d/offlineimap_mailboxes
''' %(account.maildir,account.path_mailboxes)
		d_offlineimap=d_offlineimap+r'''
##ACCOUNT "%s"
folder-hook ="%s"/*  'source "%s"/offlineimap.d/"%s"' ''' %(account.name,account.name,account.path_mutt,account.name)
		#will generate a offlineimap.d/account.name file containing standard spool settings from etc
		d_account=""
		d_account=d_account+r'''
##ACCOUNT "%s" #account.name
# source with folder-hook $folder/imap.d/"%s"/*  #account.name
source "%s" # account.path_mailboxes $HOME/.dotfiles/mutt/offlineimap.d/offlineimap_mailboxes
set spoolfile = "+"%s"/INBOX" #account.name
set record = "+"%s"/Sent\ Items" #account.name
set postponed = "+"%s"/Drafts" #account.name
set pgp_autosign
set postponed="+"%s"/Drafts" #account.name
set record="+"%s"/Sent\ Items" #account.name
set from="%s <%s>" #account.fullname  account.mail
set signature=""%s"/.signature-"%s"" #account.path_mutt account.name
#random signature
#set signature="fortune pathtofortunefile|"
set sendmail="/bin/msmtp-enqueue.sh -C "%s" -a "%s""# account.conf_msmtp,account.name

##defining custom header
unmy_hdr *
unset use_from
unset use_domain
unset user_agent


set certificate_file="%s"/importedcerts #account.path_mutt

## Extra info.
my_hdr X-Info: Keep It Simple, Stupid.

## OS Info.
my_hdr X-Operating-System: `uname -s`, kernel `uname -r`

## This header only appears to MS Outlook users
my_hdr X-Message-Flag: WARNING!! Microsoft sucks

## Custom Mail-User-Agent ID.
my_hdr User-Agent: Every email client sucks, this one just sucks less.

my_hdr Cc:	  "%s" <"%s"> #account.fullname,account.mail
my_hdr From:	"%s" <"%s"> #account.fullname,account.mail


''' % (account.name,account.name,account.path_mailboxes,account.name,account.name,account.name,account.name,account.name,account.fullname,account.mail,account.path_mutt,account.name,account.conf_msmtp,account.name,account.path_mutt,account.fullname,account.mail,account.fullname,account.mail)

	def gen_configs(self):
		if self.mutt==True:
			#config_mutt=raw_input("Where should I put your mutt config")
			print self.gen_mutt()
			print "Is this correct"

		if self.msmtp==True:
			#config_msmtp=raw_input("Where should I put your msmtp config")
			print self.gen_msmtp()
			print "Is this correct"
		if self.offlineimap==True:
			#config_offlineimap=raw_input("Where should I put your offlineimap config")
			print self.gen_offlineimap()
			print "Is this correct"

def main():
	print """\
###################################################################################
################ Welcome to my configuration wizard ###############################
################ I hope it can help you			 ###############################
################ My ASCII Skills suck !!!		   ###############################
###################################################################################"""

#	ask_type()
	acc=account()
	acc.gen_configs()


main()

