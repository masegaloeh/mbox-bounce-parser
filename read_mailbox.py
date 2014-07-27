#!/usr/bin/env python3
import argparse
import mailbox
import re

def apply_rule(message_part):
    dict_rules = [
    {'rules': 'This user doesn\'t.+have account', 'reject_type': 'hard'}
    ]

    for xrules in dict_rules:
        if re.match(xrules['rules'], message_part) is None:
            return xrules['reject_type']
    else:
        return False

def find_payload(message):
    if message.is_multipart():

        #Walking Recursively to search header Diagnostic-Code

        is_status = False
        for part in message.walk(): 
            if part.get_content_type() == 'message/delivery-status':
                for epart in part.walk():
                    if epart['Diagnostic-Code'] is not None:
                        is_status = True
                        givenstring = epart['Diagnostic-Code'].replace('\n', ' ')
                        result = apply_rule(givenstring)

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