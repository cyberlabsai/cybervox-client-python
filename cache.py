import glob
import logging
import os
import re
from datetime import datetime

import requests

handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s'))
logger = logging.getLogger("cache")
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


def getAccessToken(clientID, clientSecret):
    if accessToken := getCachedAccessToken():
        return accessToken

    if (accessToken := fetchAccessToken(clientID, clientSecret)) is None:
        return ""

    return saveAccessToken(accessToken)


digits_re = re.compile(r'\d+')


def getCachedAccessToken():
    matches = glob.glob("access-token-*.txt")
    if not len(matches):
        return ""
    logger.debug("found %d access token files", len(matches))

    cacheFilename = matches[-1]
    creationTime = int(digits_re.search(cacheFilename).group(0))

    cachedFor = (datetime.utcnow() - datetime.utcfromtimestamp(creationTime)).total_seconds() / (60 * 60)
    logger.debug("cache created %.2f hours ago", cachedFor)

    if cachedFor > 23.5:
        [os.remove(m) for m in matches]
        return ""

    logger.debug('reading access token from "%s"', cacheFilename)
    return open(cacheFilename).read()


def saveAccessToken(token):
    cacheFilename = "access-token-{0}.txt".format(int(datetime.now().timestamp()))
    logger.debug('saving access token to "%s"', cacheFilename)
    open(cacheFilename, "wt").write(token)
    return token


def fetchAccessToken(clientID, clientSecret):
    request = {
        'client_id':     clientID,
        'client_secret': clientSecret,
        'audience':      "https://api.cybervox.ai",
        'grant_type':    "client_credentials"
    }
    logger.debug("fetching new access token...")
    response = requests.post("https://cybervox-dev.us.auth0.com/oauth/token", json=request)
    if response.status_code != 200:
        return ""
    return response.json()['access_token']
