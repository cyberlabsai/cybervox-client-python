import asyncio
import logging
import os
import time

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
    logger.debug("fetching access token...")
    response = requests.post("https://api.cybervox.ai/auth", json=request)
    if response.status_code != 200:
        return ""
    return response.json()['access_token']


async def main():
    if not clientID or not clientSecret:
        logger.fatal('abort: check "CLIENT_ID" and "CLIENT_SECRET" env vars')
        return

    access_token = getAccessToken(clientID, clientSecret)
    if not access_token:
        logger.fatal('abort: invalid access token')
        return

    async with websockets.connect("wss://api.cybervox.ai/ws?access_token=" + access_token) as websocket:
        # --- PING ---
        ping_response = await cybervox.ping(websocket)
        ping_payload = ping_response['payload']
        delta = time.time() - ping_payload['timestamp']
        logger.debug("   PING: Round-trip: %9.2f ms, Success: %s", delta * 1000.0, ping_payload['success'])

        # --- TTS ---
        tts_response = await cybervox.tts(websocket, "Olá Mundo!")
        tts_payload = tts_response['payload']
        delta = time.time() - tts_payload['timestamp']
        logger.debug('    TTS: Round-trip: %9.2f ms, Success: %s, Reason: "%s", AudioURL: https://api.cybervox.ai%s',
                     delta * 1000.0,
                     tts_payload['success'],
                     tts_payload['reason'],
                     tts_payload['audio_url'])

        # --- UPLOAD ---
        upload_response = await cybervox.upload(websocket, 'ola-mundo.wav')
        upload_payload = upload_response['payload']
        delta = time.time() - upload_payload['timestamp']
        logger.debug(' UPLOAD: Round-trip: %9.2f ms, UploadID: %s',
                     delta * 1000.0,
                     upload_payload['upload_id'])

        # --- STT ---
        stt_response = await cybervox.stt(websocket, upload_payload['upload_id'])
        stt_payload = stt_response['payload']
        delta = time.time() - stt_payload['timestamp']
        logger.debug('    STT: Round-trip: %9.2f ms, Success: %s, Reason: "%s", Text: "%s"',
                     delta * 1000.0,
                     stt_payload['success'],
                     stt_payload['reason'],
                     stt_payload['text'])


if __name__ == '__main__':
    uvloop.install()
    asyncio.run(main())
