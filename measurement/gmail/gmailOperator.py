# TODO
# and data_folder


from gmailAPI import GmailClient
from time import sleep
from .. import utility
import pprint
pp = pprint.PrettyPrinter(indent=4)
# pretty-print dictionaries with pp.pprint(dict)



data_folder = 'D:\steelelab-nas\measurement_data\BlueFors\door_computer\Sal\Kurma6A_C\\2015_12_3_______17.28.54_____SingleTone__overnight_assp_zoom'

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
        utility.create_png(data_folder)

        png = None
        for file in os.listdir(data_folder):
            if file.endswith(".png"):
                png = file

        if png == None:
            g.send(subject = 'Re: '+message['subject'],
             message_text = 'Spyview did not generate a file', 
             file_dir = None, 
             filename = None,
             cc = message['cc'])
            raise RuntimeError('Spyview did not generate a file')
        else:
            g.send(subject = 'Re: '+message['subject'],
             message_text = 'Spyview did not generate a file', 
             file_dir = data_folder, 
             filename = png,
             cc = message['cc']) 




if __name__ == "__main__":
    EmailOperator()

    #body
    #from
    #cc
    #subject