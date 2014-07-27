#!/usr/bin/env python3

import argparse
import mailbox
import re

def apply_rule(message_part):
    dict_rules = [
    {'rules': '^smtp;\s*5\d{2}', 'reject_type':'hard'}, #postfix default reply code
    {'rules': '^smtp;\s*4\d{2}', 'reject_type':'soft'}, #postfix default reply code
    {'rules': 'delivery temporarily suspended', 'reject_type':'soft'},
    {'rules': 'over quota', 'reject_type':'soft'}, 
    {'rules': 'Malformed or unexpected name server reply', 'reject_type':'soft'},
    {'rules': '(Host|domain).*not found', 'reject_type':'soft'},
    #{'rules': 'This user doesn\'t.+have.+account', 'reject_type': 'hard'},
    #{'rules': 'Recipient address rejected', 'reject_type': 'hard'},
    #{'rules': ' The email account that you tried to reach does not exist', 'reject_type': 'hard'},
    #{'rules': 'connectWithTimeout failed \[127\.0.\0\.1:628]\: Connection refused', 'reject_type': 'soft'}
    ]

    #print(message_part)
    for xrules in dict_rules:
        if re.search(xrules['rules'], message_part) is not None:
            return xrules['reject_type']
            #return "| " + message_part
    else:
        return "| " + message_part

def find_payload(message):
    is_status = False

    if message.is_multipart():
        #Walking Recursively to search header Diagnostic-Code
        for part in message.walk():
            if part.get_content_type() == 'message/delivery-status':
                for epart in part.walk():
                    if epart['Diagnostic-Code'] is not None:
                        is_status = True
                        givenstring = re.sub('\s{2,}', ' ', epart['Diagnostic-Code'])
                        #givenstring = epart['Diagnostic-Code'].replace('\n', ' ')
                        result = apply_rule(givenstring)

    #else:
        #result = apply_rule(message.as_string())

    if not is_status:
        return False
    else:
        return result
                


def bounce_parser(message):
    valid_getfrom = 'MAILER-DAEMON'
    if re.match(valid_getfrom, message.get_from()) is None:
        return False

    valid_xoriginalto1 = 'vbounce@karir\.itb\.ac\.id'
    valid_xoriginalto2 = '^noreply-\d+-\d+-(.+=.+)?@karir\.itb\.ac\.id$'

    mygroup1 = re.match(valid_xoriginalto1, message['X-Original-To'])
    mygroup2 = re.match(valid_xoriginalto2, message['X-Original-To'])

    if  mygroup1 is not None:
        origin = 'vbounce '
    elif mygroup2 is not None:
        origin = mygroup2.groups()[0].replace('=', '@') + " "
    else:
        print("EMBUH")
        return False

    result = find_payload(message)
    if not result:
        print(origin + "RA KETEMU")
    else:
        print(origin + result)

    return True


parser = argparse.ArgumentParser(description='Beware. This app will parse your mbox files.')
parser.add_argument('-i','--input', help='Input mbox file name',required=True)
args = parser.parse_args()

mbox = mailbox.mbox(args.input)
for message in mbox:
    bounce_parser(message)

#user
# email_verified
# subscribe
# subscribe_article

# del all