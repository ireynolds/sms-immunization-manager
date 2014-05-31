import re


def spamNumber(phoneNumber):
	prefix = '+856'
	return phoneNumber.strip().startswith(prefix)

def spamMsg(msg):
	max_length = 100
	if not msgLonger(msg,max_length):
		return False
	if not hasDigitFilter(msg):
		return False 
	return True
	
def msgLonger(s,l):
	if len(s) > l:
		return False
	return True

_digits = re.compile('\d')	
def hasDigitFilter(s):
	return bool(_digits.search(s))
