"all functions necessary to talk to the CyberVox api platform."

import json
import time


async def ping(ws):
    """Send a ping request on an established websocket connection.

    :param ws: an established websocket connection
    :return: the ping response
    """
    ping_request = {
        'emit':    "ping",
        'payload': {
            'timestamp': int(time.time())
        }
    }
    await ws.send(json.dumps(ping_request))
    return json.loads(await ws.recv())


async def tts(ws, text):
    """Send a text-to-speech request on an established websocket connection.

    :param ws: an established websocket connection
    :param text: the text to be converted to an WAVE file
    :return: the TTS response.
       >>> if resp['payload']['success'] is True then resp['payload']['audio_url']  # contains the converted audio URL.
       >>> if resp['payload']['success'] is False then resp['payload']['reason']  # contains the failure reason.
    """
    tts_request = {
        'emit':    "tts",
        'payload': {
            'text':      text,
            'timestamp': int(time.time())
        }
    }
    await ws.send(json.dumps(tts_request))
    return json.loads(await ws.recv())


async def upload(ws, filename):
    """Send an upload request followed by a bytes stream on an established websocket connection.

    :param ws: an established websocket connection
    :param filename: the file name to be uploaded
    :return: the Upload response.
       >>> resp['payload']['upload_id']  # contains the upload identifier.
    """
    upload_request = {
        'emit':    "upload",
        'payload': {
            'max_uploads': 1,
            'timestamp':   int(time.time())
        }
    }
    await ws.send(json.dumps(upload_request))
    await ws.send(bytes(open(filename, 'rb').read()))
    return json.loads(await ws.recv())


async def stt(ws, upload_id):
    """Send a speech-to-text request on an established websocket connection.

    :param ws: an established websocket connection
    :param upload_id: the upload identifier returned by upload().
    :return: the STT response.
       >>> if resp['payload']['success'] is True then resp['payload']['text']  # contains the transcribed audio.
       >>> if resp['payload']['success'] is False then resp['payload']['reason']  # contains the failure reason.
    """
    stt_request = {
        'emit':    "stt",
        'payload': {
            'upload_id': upload_id,
            'timestamp': int(time.time())
        }
    }
    await ws.send(json.dumps(stt_request))
    return json.loads(await ws.recv())
