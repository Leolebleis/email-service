import base64
import os.path
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from googleapiclient import errors
from googleapiclient.discovery import build, Resource
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials


path_to_here = os.path.dirname(os.path.abspath(__file__))
token_path = os.path.join(path_to_here, 'google-credentials.json')

# If modifying these scopes, delete the file google-credentials.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

html_message = """
<html>
  <head></head>
  <body>
    <p>Hi!<br>
       How are you?<br>
       Here is the <a href="http://www.python.org">link</a> you wanted.
    </p>
  </body>
</html>
"""


def authenticate() -> Resource:
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file google-credentials.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if not creds.valid:
        creds.refresh(Request())
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)


def create_message(sender: str, to: str, subject: str, message_html: str):
    """
    Create a message for an email.
    :param sender: Email address of the sender.
    :param to: Email address of the receiver.
    :param subject: The subject of the email message.
    :param message_html: The text of the email message.
    :return: An object containing a base64url encoded email object.
    """
    message = MIMEMultipart('alternative')
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    part1 = MIMEText(message_html, 'html')
    message.attach(part1)
    return {'raw': base64.urlsafe_b64encode(message.as_string().encode()).decode()}


def send_message(service: Resource, user_id: str, message: dict[str, str]):
    """
    Send an email message.
    :param service: Authorized Gmail API service instance.
    :param user_id: User's email address. The special value "me" can be used to indicate the authenticated user.
    :param message: Message to be sent.
    :return: Sent Message.
    """
    try:
        message = (service.users().messages().send(userId=user_id, body=message)
                   .execute())
        print('Message Id: %s' % message['id'])
        return message
    except errors.HttpError as error:
        print('An error occurred: %s' % error)


if __name__ == '__main__':
    send_message(authenticate(), 'me',
                 create_message('me', 'leo.lebleis@gmail.com', 'test', html_message))
