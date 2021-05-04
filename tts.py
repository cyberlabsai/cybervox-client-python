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

    text = ' '.join(sys.argv[1:])
    if len(text) == 0:
        text = "Olá Mundo!"
        logger.warning("no text was given, using default '%s'", text)

    access_token = getAccessToken(clientID, clientSecret)
    if not access_token:
        logger.fatal('abort: invalid access token')
        return

    async with websockets.connect("wss://api.cybervox.ai/ws?access_token=" + access_token) as websocket:
        tts_response = await cybervox.tts(websocket, text, "perola")
        tts_payload = tts_response['payload']
        if not tts_payload['success']:
            logger.fatal('abort: reason: %s', tts_payload['reason'])
            return
        logger.info('https://api.cybervox.ai%s', tts_payload['audio_url'])


if __name__ == '__main__':
    uvloop.install()
    asyncio.run(main())
