# TODO
# and data_folder

import os
from gmailAPI import GmailClient
from time import sleep
from .. import utility
import pprint
pp = pprint.PrettyPrinter(indent=4)
# pretty-print dictionaries with pp.pprint(dict)



data_folder = r'D:\steelelab-nas\measurement_data\BlueFors\door_computer\Sal\Kurma6A_C\2015_12_14_______16.48.27_____SingleTone__rabi_pow_dep'

class GmailOperator(object):
    """docstring for SetupGUI"""
    def __init__(self):
        self.g = GmailClient('TUD202834@gmail.com')
        self.g.read_all_unread_messages() #empty the inbox
        self.idle()

    def idle(self):
        while True:
            try:
                message_list = self.g.read_all_unread_messages()
            except Exception, e:
                print 'Fetching mail failed.'
                print str(e)
            if message_list == None:
                sleep(5)
            else:
                for message in message_list:
                    try:
                        self.treat(message)
                    except Exception, e:
                        print "Treating message failed with error: "+str(e)
                        print "The message was: "
                        pp.pprint(message)

    def treat(self,message):
        if 'status' in message['subject']:
            self.status(message)

    def status(self, message):
        utility.create_png(data_folder)
 
        pdf = ''
        for f in os.listdir(data_folder):
            if f.endswith(".pdf"):
                pdf = f

        if pdf == '':
            self.g.send(to = message['from'],
             subject = 'Re: '+message['subject'],
             message_text = 'Spyview did not generate a file', 
             file_dir = None, 
             filename = None,
             cc = message['cc'])
            raise RuntimeError('Spyview did not generate a file')
        else:
            self.g.send(to = message['from'],
             subject = 'Re: '+message['subject'],
             message_text = '', 
             file_dir = data_folder, 
             filename = pdf,
             cc = message['cc']) 



    #body
    #from
    #cc
    #subject