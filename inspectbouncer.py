from email import message

class BounceEmail (message.Message):

    def __find_payload(self):
        is_status = False

        if self.is_multipart():
           #Walking Recursively to search header Diagnostic-Code
            for part in self.walk():
                if part.get_content_type() == 'message/delivery-status':
                    for epart in part.walk():
                        if epart['Diagnostic-Code'] is not None:
                            is_status = True
                            result = re.sub('\s{2,}', ' ', epart['Diagnostic-Code'])

        
        if not is_status:
            result = self.as_string()

        return result

    def __apply_rule(self, payload, rules):
        dict_rules = [
            {'rules': '^smtp;\s*5\d{2}', 'reject_type':'hard'}, #postfix default reply code
            {'rules': '^smtp;\s*4\d{2}', 'reject_type':'soft'}, #postfix default reply code
            {'rules': 'delivery temporarily suspended', 'reject_type':'soft'},
            {'rules': 'over quota', 'reject_type':'soft'}, 
            {'rules': 'Malformed or unexpected name server reply', 'reject_type':'soft'},
            {'rules': '(Host|domain).*not found', 'reject_type':'soft'},
        ]

        for xrules in dict_rules:
            if re.search(xrules['rules'], payload) is not None:
                return xrules['reject_type']
            else:
                return "| " + message_part

    def get_status(self, rules):
        self.__find_payload(self)