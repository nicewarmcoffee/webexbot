from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError

import json
import requests
from configparser import ConfigParser
from pydantic import BaseModel

app = FastAPI()

parser = ConfigParser()
parser.read('/etc/auth.conf')

session = requests.Session()
webhook_url = "https://webexapis.com/v1/webhooks"
message_url = "https://webexapis.com/v1/messages/"

webhook_request_header = {
    "Content-type": "application/json; charset=utf-8",
    "Authorization": "Bearer " + parser.get('gg_token', 'token')
    }

bot_id = 'GeneralGrievous@webex.bot'

webhook_payload = {
    "name": "General Grievous",
    "targetUrl": "https://nicewarm.coffee/webexhook",
    "resource": "messages",
    "event": "created"
    }


webhook = session.post(webhook_url, headers=webhook_request_header, json=webhook_payload)
print(webhook.content)

def get_webex_message(url):
    message_session = session.get(url, headers=webhook_request_header)
    return json.loads(message_session.text)


def send_message(resp_text, command):
    if command == 'kenobi':
        message = 'General Kenobi!'
    else:
        message = 'Time to abandon ship!'

    request_payload = { 'roomId': resp_text['roomId'], 'text': message }
    send_session = session.post(message_url, headers=webhook_request_header, json=request_payload)
    return send_session


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/webexhook")
async def webexhook(webex: Request):
#    body = b''
#    async for chunk in webex.stream():
#        body += chunk
    webex_data = await webex.json()
    message = get_webex_message(message_url + webex_data['data']['id'])
    print(message)
    if message['personEmail'] != bot_id:
        if message['text'].lower() == 'hello there':
            msg_session = send_message(message, 'kenobi')
        else:
            msg_session = send_message(message, 'random')
  
    return {"message": "got your post!"}


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(webex: Request, exc: RequestValidationError):
    exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
    print(f"{webex}: {exc_str}")
    return {'error': 'oh no!'}