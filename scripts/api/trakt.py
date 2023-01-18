##############################

import json
import requests
import time

from urllib import parse

from scripts.helper import *

##############################

class Trakt:
    __BASE_URL = 'https://api.trakt.tv'
    __CLIENT_ID = '7a9eb5e1316a18cd580e20bcacc8841da1b817376df07e88e5fbd4442a8cfc8a'
    __CLIENT_SECRET = 'f7afd66d18582ff9588976f90d7d97fb815237fbe02748884d1d20870b7e1180'
    __REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'
    __timestamp = None
    
    @staticmethod
    def __getTrakt(url:str, post=None):
        try:
            url = parse.urljoin(Trakt.__BASE_URL, url)
            post = json.dumps(post) if post else None
            headers = {
                'Content-Type': 'application/json',
                'trakt-api-key': Trakt.__CLIENT_ID,
                'trakt-api-version': str(2)
            }

            if Trakt.hasTraktCredentialsInfo():
                headers.update({'Authorization': 'Bearer %s' % Settings.getSetting("trakt.token")})
            
            if DEBUG:
                log("Attempting Trakt call to URL: " + repr(url))

            if Trakt.isCallsSupressed():
                if DEBUG:
                    log('Trakt call supressed by DS Helper, wait and try again in a bit.')
                return {}

            if post:
                request = requests.post(url, data=post, headers=headers)
            else:
                request = requests.get(url, headers=headers)

            if DEBUG:
                log("Trakt Response: " + repr(request))

            if request is None or not request.status_code:
                return {}
            
            resp_code = request.status_code

            if resp_code in [500, 502, 503, 504, 520, 521, 522, 524]:
                logwarn('Temporary Trakt error, Service Unavailable: ' + repr(request))
                logwarn('Supressing calls for 30 seconds...')
                Trakt.setCallsSupressed(30)
            elif resp_code in [401, 403]:
                logwarn('Unauthorized or Forbidden Trakt request: ' + repr(request))
            elif resp_code in [404, 405]:
                logwarn('Trakt record/method Not Found: ' + repr(request))
            elif resp_code in [429]:
                logwarn('Trakt rate Limit Reached: ' + repr(request))
                logwarn('Supressing calls for 30 seconds...')
                Trakt.setCallsSupressed(30)

            try:
                response = request.json()
            except Exception as ex:
                if DEBUG:
                    logerror(ex)
                response = {}
            request.close()
            return response
        except Exception as e:
            logerror(e)
        return {}

    @staticmethod
    def authTrakt():
        try:
            if Trakt.hasTraktCredentialsInfo() is True:
                if DIALOG.yesno(
                    Helper.lang(32301),
                    Helper.lang(32302)
                ):
                    Settings.setSetting("trakt.user", '')
                    Settings.setSetting("trakt.token", '')
                    Settings.setSetting("trakt.refresh", '')
                raise Exception()

            post = {'client_id': Trakt.__CLIENT_ID}
            result = Trakt.__getTrakt('/oauth/device/code', post)

            if not result.get('user_code') or not result.get('device_code'):
                DIALOG.ok(Helper.lang(32000), Helper.lang(32303))
                raise Exception("Did not get proper response from trakt when requesting device code.")

            progress = 0
            interval = result.get('interval', 5)
            expires_in = result.get('expires_in', 0)
            authDeviceUrl = (Helper.lang(32304) % result.get('verification_url'))
            user_code = (Helper.lang(32305) % result.get('user_code'))
            device_code = result.get('device_code')

            dialog = PROGRESS_DIALOG()
            dialog.create(Helper.lang(32300), f"{authDeviceUrl}[CR]{user_code}")
            auth = Trakt.authPoll(dialog, progress, interval, expires_in, device_code)
            
            access_token = auth.get('access_token').strip()
            refresh_token = auth.get('refresh_token').strip()
            Settings.setSetting("trakt.token", access_token)
            Settings.setSetting("trakt.refresh", refresh_token)

            r2 = Trakt.__getTrakt('/users/me')

            username = r2.get('username').strip()
            Settings.setSetting("trakt.user", username)

            dialog.close()
            raise Exception("Trakt successfully authorized!")
        except Exception as e:
            if DEBUG:
                logerror(str(e))
            Settings.openSettings(1,0)
        return
        
    @staticmethod
    def authPoll(dialog: PROGRESS_DIALOG, progress, interval, expires_in, device_code):
        if DEBUG:
            log(f"----- Polling Trakt Auth(): progress:{str(progress)}, interval:{str(interval)}, expires:{str(expires_in)} -----")
        if dialog.iscanceled():
            dialog.close()
            raise Exception("Trakt Auth dialog cancelled.")
        
        if expires_in <= progress:
            dialog.close()
            raise Exception("Trakt Auth dialog expired.")

        xbmc.Monitor().waitForAbort(interval)
        if xbmc.Monitor().abortRequested():
            dialog.close()
            raise Exception("Trakt Auth dialog aborted.")
        
        post = {'code': device_code, 'client_id': Trakt.__CLIENT_ID, 'client_secret': Trakt.__CLIENT_SECRET}
        auth = Trakt.__getTrakt('/oauth/device/token', post)
        if auth and ('access_token' in auth):
            return auth

        progress += interval
        percentage = int((progress / expires_in) * 100)
        dialog.update(percentage)
        return Trakt.authPoll(dialog, progress, interval, expires_in, device_code)

    @staticmethod
    def hasTraktCredentialsInfo() -> bool:
        tkn = Settings.getSetting("trakt.token")
        rfr = Settings.getSetting("trakt.refresh")
        if tkn == '' or rfr == '':
            return False
        return True

    @staticmethod
    def isCallsSupressed() -> bool:
        if not Trakt.__timestamp:
            return False

        now = time.time()
        waitUntil = Trakt.__timestamp
        if now > waitUntil:
            Trakt.__timestamp = None
            return False

        return True

    @staticmethod
    def setCallsSupressed(wait_time_seconds:int):
        Trakt.__timestamp = time.time() + wait_time_seconds

# end of Trakt class