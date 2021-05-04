import asyncio
import logging
import os
import sys

import requests
import uvloop as uvloop
import websockets

import cybervox

handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s'))
logger = logging.getLogger("main")
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

clientID = os.getenv("CLIENT_ID", "")
clientSecret = os.getenv("CLIENT_SECRET", "")


def getAccessToken(clientID, clientSecret):
    request = {
        'client_id':     clientID,
        'client_secret': clientSecret,
        'audience':      "https://api.cybervox.ai",
        'grant_type':    "client_credentials"
    }
    logger.info("fetching access token...")
    response = requests.post("https://api.cybervox.ai/auth", json=request)
    if response.status_code != 200:
        return ""
    return response.json()['access_token']


async def main():
    if not clientID or not clientSecret:
        logger.fatal('abort: check "CLIENT_ID" and "CLIENT_SECRET" env vars')
        return

    if len(sys.argv) < 2:
        audio_file = "ola-mundo.wav"
        logger.warning("no audio file was given, using default '%s'", audio_file)
    else:
        audio_file = sys.argv[1]

    if not os.path.exists(audio_file):
        logger.fatal('file "%s" not found.', audio_file)
        return

    access_token = getAccessToken(clientID, clientSecret)
    if not access_token:
        logger.fatal('abort: invalid access token')
        return

    async with websockets.connect("wss://api.cybervox.ai/ws?access_token=" + access_token) as websocket:
        # --- UPLOAD ---
        upload_response = await cybervox.upload(websocket, audio_file)
        upload_payload = upload_response['payload']
        logger.info('upload id: %s', upload_payload['upload_id'])

        # --- STT ---
        stt_response = await cybervox.stt(websocket, upload_payload['upload_id'])
        stt_payload = stt_response['payload']
        if not stt_payload['success']:
            logger.fatal('abort: reason: %s', stt_payload['reason'])
            return
        logger.info('%s', stt_payload['text'])


if __name__ == '__main__':
    uvloop.install()
    asyncio.run(main())
