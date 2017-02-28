import os
from flask import Flask, request
from twilio.util import TwilioCapability
import twilio.twiml

# Account Sid and Auth Token can be found in your account dashboard
ACCOUNT_SID = 'AC074af63c54728717d600a7b2641a1d72'
AUTH_TOKEN = 'dc43003c977409f3412be46cea0fa5c8'

# TwiML app outgoing connections will use
APP_SID = 'PN527d4b883ec6a2e743e4697ba81eb3bc'

CALLER_ID = '+919637793593'
CLIENT = 'jenny'

app = Flask(__name__)

@app.route('/token')
def token():
  account_sid = os.environ.get("ACCOUNT_SID", ACCOUNT_SID)
  auth_token = os.environ.get("AUTH_TOKEN", AUTH_TOKEN)
  app_sid = os.environ.get("APP_SID", APP_SID)

  capability = TwilioCapability(account_sid, auth_token)

  # This allows outgoing connections to TwiML application
  if request.values.get('allowOutgoing') != 'false':
     capability.allow_client_outgoing(app_sid)

  # This allows incoming connections to client (if specified)
  client = request.values.get('client')
 
  if client != None:
    capability.allow_client_incoming(client)

  # This returns a token to use with Twilio based on the account and capabilities defined above

  print(capability.generate())
  return capability.generate()

@app.route('/call', methods=['GET', 'POST'])
def call():
  """ This method routes calls from/to client                  """
  """ Rules: 1. From can be either client:name or PSTN number  """
  """        2. To value specifies target. When call is coming """
  """           from PSTN, To value is ignored and call is     """
  """           routed to client named CLIENT                  """
  resp = twilio.twiml.Response()  
  from_value = request.args.get('From')
  print "sarufrom"
  print (from_value)
  to = request.values.get('To')
  print "saruto"
  print (to)
  if not (from_value and to):
    resp.say("Message without number")
    return str(resp)
  from_client = from_value.startswith('client')
  caller_id = os.environ.get("CALLER_ID", CALLER_ID)
  if not from_client:
    # PSTN -> client
    resp.dial(callerId=from_value).client(CLIENT)
  elif to.startswith("client:"):
    # client -> client
    resp.dial(callerId=from_value).client(to[7:])
  else:
    # client -> PSTN
    resp.dial(to, callerId=caller_id)
  return str(resp)

@app.route('/', methods=['GET', 'POST'])
def welcome():
  resp = twilio.twiml.Response()
  resp.say("Welcome to Twilio")
  return str(resp)

if __name__ == "__main__":
  port = int(os.environ.get("PORT", 5000))
  app.run(host='0.0.0.0', port=port, debug=True)
