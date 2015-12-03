import httplib2
import os

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import message_from_string
import mimetypes
from googleapiclient.errors import HttpError
from base64 import urlsafe_b64encode,urlsafe_b64decode
from HTMLParser import HTMLParser
import os



try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None


#Debugging uses
import pprint
pp = pprint.PrettyPrinter(indent=4)
# pretty-print dictionaries with pp.pprint(dict)


SCOPES = 'https://mail.google.com/'
CLIENT_SECRET_FILE = os.path.join(os.path.dirname(__file__),'client_secret.json')
APPLICATION_NAME = 'Gmail API Python'

class GmailClient(object):
  """docstring for Gmail_client"""
  def __init__(self,gmail_adress):
    self.service = self.create_service()
    self.gmail_adress = gmail_adress
      
  def get_credentials(self):
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    credential_dir = os.path.join(os.path.dirname(__file__),'.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'gmail-python-quickstart.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

  def create_service(self):
    """Returns a Gmail API service object.
    """
    credentials = self.get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)
    return service

  def create_message(self, to, subject, message_text, file_dir = None, filename = None,cc = ''):
    """Create a message for an email.

    Args:
      to: Email address of the receiver.
      subject: The subject of the email message.
      message_text: The text of the email message.
      file_dir: The directory containing the file to be attached.
      filename: The name of the file to be attached.
      cc: str in the format "adress@bla.com, adress2@bla.com"

    Returns:
      An object containing a base64url encoded email object.
    """
    # No attachement
    if file_dir == None:
      message = MIMEText(message_text)
      message['to'] = to
      message['cc'] = cc
      message['from'] = self.gmail_adress
      message['subject'] = subject
      return {'raw': urlsafe_b64encode(message.as_string())}

    # With attachment
    else:
      message = MIMEMultipart()
      message['to'] = to
      message['cc'] = cc
      message['from'] = self.gmail_adress
      message['subject'] = subject

      msg = MIMEText(message_text)
      message.attach(msg)

      path = os.path.join(file_dir, filename)
      content_type, encoding = mimetypes.guess_type(path)

      if content_type is None or encoding is not None:
        content_type = 'application/octet-stream'
      main_type, sub_type = content_type.split('/', 1)
      if main_type == 'text':
        fp = open(path, 'rb')
        msg = MIMEText(fp.read(), _subtype=sub_type)
        fp.close()
      elif main_type == 'image':
        fp = open(path, 'rb')
        msg = MIMEImage(fp.read(), _subtype=sub_type)
        fp.close()
      elif main_type == 'audio':
        fp = open(path, 'rb')
        msg = MIMEAudio(fp.read(), _subtype=sub_type)
        fp.close()
      else:
        fp = open(path, 'rb')
        msg = MIMEBase(main_type, sub_type)
        msg.set_payload(fp.read())
        fp.close()

      msg.add_header('Content-Disposition', 'attachment', filename=filename)
      message.attach(msg)

      return {'raw': urlsafe_b64encode(message.as_string())}

  def send(self, subject, message_text, file_dir = None, filename = None,cc = ''):
    """Send an email message.

    Args:
      to: Email address of the receiver.
      subject: The subject of the email message.
      message_text: The text of the email message.
      file_dir: The directory containing the file to be attached.
      filename: The name of the file to be attached.
      cc: str in the format "adress@bla.com, adress2@bla.com"

    Returns:
      Sent Message.
    """

    message = self.create_message(to, subject, message_text, file_dir = None, filename = None,cc = '')
    try:
      message = (self.service.users().messages().send(userId='me', body=message)
                 .execute())
      print 'Message Id: %s' % message['id']
      return message
    except HttpError, error:
      print 'An error occurred when sending the message: %s' % error

  def get_message(self, msg_id):
    """Get a Message with given ID.

    Args:
      msg_id: The ID of the Message required.

    Returns:
      A Message.
    """
    try:
      message = self.service.users().messages().get(userId='me', id=msg_id).execute()
      message = {
      'body': parse(message['snippet']),
      'subject': parse(get_value_in_header(message, 'Subject')),
      'cc': parse(get_value_in_header(message, 'Cc')),
      'from': parse(get_value_in_header(message, 'From'))
      } 

      return message
    except HttpError, error:
      print 'An error occurred: %s' % error

  def mark_as_read(self,msg_id):
    msg_labels = {"addLabelIds": [],"removeLabelIds": ['UNREAD']}
    try:
      message = self.service.users().messages().modify(userId='me', id=msg_id,body=msg_labels).execute()
    except HttpError, error:
      print 'An error occurred: %s' % error

  def read_all_unread_messages(self):
    try:
      messages_to_go_through = self.service.users().messages().list(userId='me', q = "is:unread").execute()['messages']
    except KeyError:
      return None
    
    all_messages = []
    for message in messages_to_go_through:
      all_messages.append(self.get_message(message['id']))
      self.mark_as_read(message['id'])

    return all_messages

def get_value_in_header(message, name): 
  for item in message['payload']['headers']:
    if item['name'] == name: 
      return item['value']

def parse(string):
  try:
    return HTMLParser().unescape(string)
  except TypeError:
    return string






