from gmailAPI import GmailClient
from time import sleep
import pprint
from .. import utility
pp = pprint.PrettyPrinter(indent=4)
# pretty-print dictionaries with pp.pprint(dict)

class EmailOperator(object):
    """docstring for SetupGUI"""
    def __init__(self):
        self.g = GmailClient('TUD202834@gmail.com')
        self.g.read_all_unread_messages() #empty the inbox
        self.idle()

    def idle(self):
        while True:
            message_list = self.g.read_all_unread_messages()
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
        pass




# if __name__ == "__main__":
    # EmailOperator()

    #body
    #from
    #cc
    #subject