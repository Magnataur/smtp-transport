#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import json
import base64
import smtplib
import collections

import poplib
# poplib has the limit of maximum string length red from pop3 server
# so we need to increase it
# we can't read out decoded image without increasing, because it
# stored in email as very long string
poplib._MAXLINE = 1000000000

from email.mime.text import MIMEText


# Some global variables
me = 'test@mail.ru'
to = 'hello@mail.ru'
server = 'mail.ru'
password = '12345'


class Message(collections.UserDict):
    def __init__(self, dict=None, **kwargs):
        initial_dict = {
            'subject': '',
            'message': '',
            'binary': '',
        }
        if dict is not None:
            initial_dict.update(dict)

        super().__init__(initial_dict, **kwargs)

    @property
    def subject(self):
        return self.data['subject']

    @subject.setter
    def subject(self, subject):
        self.data['subject'] = subject

    @property
    def message(self):
        return self.data['message']

    @message.setter
    def message(self, message):
        self.data['message'] = message

    @property
    def binary(self):
        return base64.standard_b64decode(self.data['binary'].encode())

    @binary.setter
    def binary(self, binary):
        """
        Encode binary data to base64 format, convert it to unicode string and store to self._message
        """
        self.data['binary'] = base64.standard_b64encode(binary).decode()

    def to_json(self):
        return json.dumps(self.data)


def main():
    global me
    global to
    global server
    global password

    m = Message()
    m.subject = 'Hello world'
    m.message = 'Proof of concept'

    with open('buttheart.png', 'rb') as fp:
        binary_data = fp.read()
    m.binary = binary_data

    mail = MIMEText(m.to_json())
    mail['Subject'] = 'Proof of concept'
    mail['From'] = me
    mail['To'] = to

    s = smtplib.SMTP(server)
    s.sendmail(me, [to, ], mail.as_string())
    s.quit()

    pop = poplib.POP3(server)
    pop.user(to)
    pop.pass_(password)

    response, lst, octets = pop.list()

    for n in lst:
        msg_number, msg_size = n.split()
        reply, message, size = pop.retr(int(msg_number))
        # message[-1] contains our Message as byte string,
        # so we need to decode it to unicode string before
        # convert it to python structure
        incoming = json.loads(message[-1].decode())

        print(incoming['subject'])
        print(incoming['message'])

        with open('out.png', 'wb') as fp:
            # incoming['binary'] is a unicode string
            # so we need to convert it to byte string before decoding
            # from base64 format and writing it to output file
            fp.write(base64.standard_b64decode(incoming['binary'].encode()))


if __name__ == '__main__':
    sys.exit(main())
