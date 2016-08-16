#!/usr/bin/python

msmtp=false
offlineimap=false
mutt=false
def ask_type():
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
	smtP-url=""
	def __init__(self,mail,name):
		self.mail = mail
		self.name = name
		self.user = mail
	def guess_imap(self):
		pass
	def guess_smtp(self):
		pass
	def set_smtp(self,url):
		smtp_url=url
	def set_imap(self,url):	
		imap_url=url
	def get_imap(self):
		return imap_url
	def get_smtp(self):
		return smtp_url
ask_type()
