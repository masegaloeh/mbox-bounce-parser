#!/usr/bin/env python3

import argparse
import email
import mailbox
import re

class BounceEmail ():

    def  __init__ (self, email_string):
        self.message = email.message_from_string(email_string)
        self.__payload = None
        self.__reject_type = None
        self.debug = False

    def __find_delivery_status(self):
        is_status = False

        if self.message.is_multipart():
           #Walking Recursively to search header Diagnostic-Code
            for part in self.message.walk():
                if part.get_content_type() == 'message/delivery-status':
                    for epart in part.walk():
                        if epart['Diagnostic-Code'] is not None:
                            is_status = True
                            result = re.sub('\s{2,}', ' ', epart['Diagnostic-Code'])

        if not is_status:
            result = self.message.as_string()

        return result

    def __apply_rule(self, payload, rules):
        dict_rules = [
            {'rules': '^smtp;\s*5\d{2}', 'reject_type':'hard'}, #postfix default reply code
            {'rules': '^smtp;\s*4\d{2}', 'reject_type':'soft'}, #postfix default reply code
            {'rules': 'delivery temporarily suspended', 'reject_type':'soft'},
            {'rules': 'over quota', 'reject_type':'soft'}, 
            {'rules': 'Malformed or unexpected name server reply', 'reject_type':'soft'},
            {'rules': '(Host|domain).*not found', 'reject_type':'soft'},
            {'rules': 'Operation timed out', 'reject_type':'soft'},
            {'rules': 'connectWithTimeout failed \[127.0.0.1:628\]: Connection refused', 'reject_type':'soft'},
            {'rules': 'Address rejected', 'reject_type':'hard'},
        ]

        for xrules in dict_rules:
            if self.debug:
                print('Matching regex \'{0}\' to string {1}'.format(xrules['rules'], payload))
            if re.search(xrules['rules'], payload) is not None:
                return xrules['reject_type']

        return "wanda"

    def parse(self):
        if self.__payload is None:
            self.__payload = self.__find_delivery_status()
        if self.__reject_type is None:
            self.__reject_type = self.__apply_rule(self.__payload, '')

    def get_reason(self):
        return self.__payload

    def get_type(self):
        return self.__reject_type

class BounceEmailITBCC (BounceEmail):
    def get_problematic_sender(self):
        valid_xoriginalto1 = 'vbounce@karir\.itb\.ac\.id'
        valid_xoriginalto2 = '^noreply-\d+-\d+-(.+=.+)?@karir\.itb\.ac\.id$'

        mygroup1 = re.match(valid_xoriginalto1, self.message['X-Original-To'])
        mygroup2 = re.match(valid_xoriginalto2, self.message['X-Original-To'])

        if  mygroup1 is not None:
            origin = 'vbounce' #will add additional parser later
        elif mygroup2 is not None:
            origin = mygroup2.groups()[0].replace('=', '@') + " "
        else:
            origin = False
        
        return origin

parser = argparse.ArgumentParser(description='Beware. This app will parse your bounce email.')
parser.add_argument('-i','--input', help='Input mbox file name',required=True)
args = parser.parse_args()

mbox = mailbox.mbox(args.input)

for message in mbox:
    firstbounce = BounceEmailITBCC(message.__str__())

    firstbounce.parse()
    reason = firstbounce.get_reason()

    try:
        firstbounce.get_reason().encode('ascii')
    except UnicodeEncodeError:
        reason = firstbounce.get_reason().encode('ascii', 'ignore').decode()

    print('Email: {2}; Reject Type: {0}; Reason: "{1}"'.format(firstbounce.get_type(), reason, firstbounce.get_problematic_sender()))