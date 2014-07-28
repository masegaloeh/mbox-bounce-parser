#!/usr/bin/env python3

import email
import re

class BounceEmail ():

    def  __init__ (self, email_string):
        self.__message = email.message_from_string(email_string)
        self.__payload = None
        self.__reject_type = None

    def __find_delivery_status(self):
        is_status = False

        if self.__message.is_multipart():
           #Walking Recursively to search header Diagnostic-Code
            for part in self.__message.walk():
                if part.get_content_type() == 'message/delivery-status':
                    for epart in part.walk():
                        if epart['Diagnostic-Code'] is not None:
                            is_status = True
                            result = re.sub('\s{2,}', ' ', epart['Diagnostic-Code'])

        
        if not is_status:
            result = self.__message.as_string()

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
                return " wanda "

    def parse(self):
        if self.__payload is None:
            self.__payload = self.__find_delivery_status()
        if self.__reject_type is None:
            self.__reject_type = self.__apply_rule(self.__payload, '')

    def get_reason(self):
        return self.__payload

    def get_type(self):
        return self.__reject_type


eemail = \
"""From MAILER-DAEMON  Tue Jul  1 05:02:05 2014
Return-Path: <>
X-Original-To: noreply-459284241475-1404165724-ryuzaki.arnold=gmail.com@karir.itb.ac.id
Delivered-To: noreply-459284241475-1404165724-ryuzaki.arnold=gmail.com@karir.itb.ac.id
Received: by mx.karir.itb.ac.id (Postfix)
        id 8DC5456440; Tue,  1 Jul 2014 05:02:05 +0700 (WIT)
Date: Tue,  1 Jul 2014 05:02:05 +0700 (WIT)
From: MAILER-DAEMON@karir.itb.ac.id (Mail Delivery System)
Subject: Undelivered Mail Returned to Sender
To: noreply-459284241475-1404165724-ryuzaki.arnold=gmail.com@karir.itb.ac.id
Auto-Submitted: auto-replied
MIME-Version: 1.0
Content-Type: multipart/report; report-type=delivery-status;
        boundary="BEF8D5644C.1404165725/mx.karir.itb.ac.id"
Content-Transfer-Encoding: 8bit
Message-Id: <20140630220205.8DC5456440@mx.karir.itb.ac.id>

This is a MIME-encapsulated message.

--BEF8D5644C.1404165725/mx.karir.itb.ac.id
Content-Description: Notification
Content-Type: text/plain; charset=us-ascii

This is the mail system at host mx.karir.itb.ac.id.

I'm sorry to have to inform you that your message could not
be delivered to one or more recipients. It's attached below.

For further assistance, please send mail to postmaster.

If you do so, please include this problem report. You can
delete your own text from the attached returned message.

                   The mail system

<ryuzaki.arnold@gmail.com>: host gmail-smtp-in.l.google.com[74.125.129.27]
    said: 550-5.1.1 The email account that you tried to reach does not exist.
    Please try 550-5.1.1 double-checking the recipient's email address for
    typos or 550-5.1.1 unnecessary spaces. Learn more at 550 5.1.1
    http://support.google.com/mail/bin/answer.py?answer=6596
    rn1si24597058pbc.172 - gsmtp (in reply to RCPT TO command)

--BEF8D5644C.1404165725/mx.karir.itb.ac.id
Content-Description: Delivery report
Content-Type: message/delivery-status

Reporting-MTA: dns; mx.karir.itb.ac.id
X-Postfix-Queue-ID: BEF8D5644C
X-Postfix-Sender: rfc822; noreply-459284241475-1404165724-ryuzaki.arnold=gmail.com@karir.itb.ac.id
Arrival-Date: Tue,  1 Jul 2014 05:02:04 +0700 (WIT)

Final-Recipient: rfc822; ryuzaki.arnold@gmail.com
Original-Recipient: rfc822;ryuzaki.arnold@gmail.com
Action: failed
Status: 5.1.1
Remote-MTA: dns; gmail-smtp-in.l.google.com
Diagnostic-Code: smtp; 550-5.1.1 The email account that you tried to reach does
    not exist. Please try 550-5.1.1 double-checking the recipient's email
    address for typos or 550-5.1.1 unnecessary spaces. Learn more at 550 5.1.1
    http://support.google.com/mail/bin/answer.py?answer=6596
    rn1si24597058pbc.172 - gsmtp

--BEF8D5644C.1404165725/mx.karir.itb.ac.id
Content-Description: Undelivered Message
Content-Type: message/rfc822
Content-Transfer-Encoding: 8bit

Return-Path: <noreply-459284241475-1404165724-ryuzaki.arnold=gmail.com@karir.itb.ac.id>
Received: from web.karir.itb.ac.id (unknown [202.51.235.100])
        by mx.karir.itb.ac.id (Postfix) with ESMTP id BEF8D5644C;
        Tue,  1 Jul 2014 05:02:04 +0700 (WIT)
DKIM-Signature: v=1; a=rsa-sha256; c=simple/simple; d=karir.itb.ac.id;
        s=nokeys; t=1404165724;
        bh=Z4nfzRmkB9Hq5xYpuylTHe+O6dMmWbFal2kRsMwbLlk=;
        h=Date:To:From:Reply-to:Subject;
        b=WmVdlo4EYueENEINjlnxBff9SZsm59x1nA/iSPN/W/c5NDXKY4+FyXbIECykTgt/n
         i+sayskO9X5yUnIGiEM1kxtJHw7eBGE19e4HR7jyGqOKVtETpAGy+/B3nuwoP/mbFM
         2Ya8eDKU4Rcv7BvjUnRXFPA/QGCKWkyUJDi3slnQ=
Date: Tue, 1 Jul 2014 05:02:04 +0700
To: ITB Career Center Newsletter <newsletter@karir.itb.ac.id>
From: ITB Career Center <career@karir.itb.ac.id>
Reply-to: ITB Career Center <career@itb.ac.id>
Subject: Event dan Artikel Terbaru
Message-ID: <46a47b8f0f6216e5d1d3848ae79e8562@web.karir.itb.ac.id>
X-Priority: 3
X-Mailer: PHPMailer 5.2 (http://code.google.com/a/apache-extras.org/p/phpmailer/)
Precedence: bulk
MIME-Version: 1.0
Content-Transfer-Encoding: 8bit
Content-Type: text/html; charset="iso-8859-1"


<p style="color: #00407f;"><span style="color:
#000000;">Pengumuman dan kegiatan seputar karier terbaru di
ITB:</span></p>
<ul style="color: #00407f;"><li><a target="_blank"
href="http://karir.itb.ac.id/events/detail/285">Psikotes PT.
Aisin Indonesia (Astra Group)</a></li></ul>
<ul style="color: #00407f;"><li>Announcement - <a target="_blank"
href="http://karir.itb.ac.id/articles/detail/322">PT Aisin
Indonesia (Astra Group): Peserta Psikotes 3 Juli
2014</a></li></ul>
<ul style="color: #00407f;"></ul>
<p style="color: #00407f;"><span style="color: #000000;">Ikuti
terus informasi peluang karier, magang, dan program kewirausahaan
mahasiswa dengan mengunjungi situs <a href="../../../"
target="_blank"><span style="color: #000000;">ITB Career
Center</span></a>.</span></p>
<p style="color: #00407f;">&nbsp;</p>
<p style="color: #00407f;">&nbsp;</p><p>Best regards,</p>
<p>ITB Career Center<br
/>----------------------------------------------------------------------------------</p>
<p><span style="color:
#000000;"><strong>Office</strong></span></p>
<p><span style="color: #000000;">GKU Timur Lantai Dasar, Kampus
ITB</span><br /><span style="color: #000000;"> Jl. Ganesa 10
Bandung, 40132</span></p>
<p><span style="color: #000000;"><strong>Ph/Fax</strong>: (62) 22
- 2509177</span><br /><span style="color:
#000000;"><strong>Email</strong>&nbsp; &nbsp;: <span
style="text-decoration:
underline;">career@itb.ac.id</span></span><br /><span
style="color:
#000000;">----------------------------------------------------------------------------------</span><br
/><span style="color: #000000;"><strong>Website and Social Media
Channel</strong></span></p>
<p><span style="color: #000000;">Website : <a
href="http://karir.itb.ac.id/">http://karir.itb.ac.id</a></span><br
/><span style="color: #000000;">FB Page : <a
href="https://www.facebook.com/itb.career.center">ITB Career
Center</a></span><br /><span style="color: #000000;">Twitter
&nbsp; : <a
href="https://twitter.com/ITBCareerCenter">@ITBCareerCenter</a></span><br
/><span style="color: #000000;">YouTube: <a
href="http://www.youtube.com/user/ITBCareerCenter/videos">ITB
Career Center</a></span><br /><span style="color:
#000000;">Google+: <a
href="https://plus.google.com/b/106590411857705007612/106590411857705007612/posts">ITB
Career Center</a></span><br /><span style="color:
#000000;">LinkedIn: <a
href="http://id.linkedin.com/in/itbcareercenter/">ITB Career
Center</a></span></p>



--BEF8D5644C.1404165725/mx.karir.itb.ac.id--
"""

firstbounce = BounceEmail(eemail)
firstbounce.parse()
print(firstbounce.get_reason())
print(firstbounce.get_type())