##############################

import json
import os
import traceback
import threading
import urllib.parse

import xbmc
import xbmcaddon
import xbmcgui

##############################

SCRIPT_ID = "dstealth-helper.py"
PLUGIN_ID = "plugin://script.dstealth.helper/"

ADDON = xbmcaddon.Addon()
ADDON_ICON = ADDON.getAddonInfo('icon')
ADDON_ID = ADDON.getAddonInfo('id')
ADDON_PATH = ADDON.getAddonInfo('path') # contains trailing \
DATA_PATH = ADDON.getAddonInfo('profile')
RESOURCES_PATH = os.path.join(ADDON_PATH, 'resources') + os.sep

XBMC_DEBUG = xbmc.LOGDEBUG       # 0
XBMC_INFO = xbmc.LOGINFO         # 1
XBMC_WARNING = xbmc.LOGWARNING   # 2
XBMC_ERROR = xbmc.LOGERROR       # 3

DIALOG = xbmcgui.Dialog()
PROGRESS_DIALOG = xbmcgui.DialogProgress

DEBUG = True if xbmcaddon.Addon().getSetting("debug.enabled").lower() == 'true' else False

##############################

def log(txt, loglevel=XBMC_INFO):
    message = u'[%s] %s' % (ADDON_ID, repr(txt))
    xbmc.log(msg=message, level=loglevel)

def logdebug(txt):
    if DEBUG:
        log("DEBUG: " + repr(txt), XBMC_INFO)

def logwarn(txt):
    log("WARNING: " + repr(txt), XBMC_WARNING)

def logerror(txt):
    log("ERROR: " + repr(txt), XBMC_ERROR)
    if isinstance(txt, Exception):
        traceback.print_exc()

##############################
        
class Helper:

    @staticmethod
    def createWorker(targetFunc, *args) -> threading.Thread:
        return threading.Thread(target=targetFunc, args=args)

    @staticmethod
    def debugMsg(debug=False, ex=None, msg="", prefix=""):
        if (debug):
            log("Displaying DebugMsg()")
            errMsg = ""
            if ex != None:
                logerror(ex)
                errMsg = "ErrMsg: " + repr(ex) + "\n"
            if (prefix != ""):
                prefix = prefix + ":\n"
            if (ex == None and prefix == "" and msg == ""):
                msg = "No message provided."
            DIALOG.ok(ADDON.getLocalizedString(32001), prefix + errMsg + msg)
        return
        
    @staticmethod    
    def getKodiVersion(as_str=False):
        if as_str:
            return xbmc.getInfoLabel('System.BuildVersion').split()[0]
        return int(xbmc.getInfoLabel('System.BuildVersion').split('.')[0])

    @staticmethod
    def json_call(method, properties=None, sort=None,
                query_filter=None, limit=None, params=None,
                item=None, options=None, limits=None, debug=False):
        if (debug):
            log("Helper.json_call()")

        json_string = {
            'jsonrpc': '2.0',
            'id': 1,
            'method': method,
            'params': {}
            }

        if properties is not None:
            json_string['params']['properties'] = properties

        if limit is not None:
            json_string['params']['limits'] = {'start': 0, 'end': int(limit)}

        if sort is not None:
            json_string['params']['sort'] = sort

        if query_filter is not None:
            json_string['params']['filter'] = query_filter

        if options is not None:
            json_string['params']['options'] = options

        if limits is not None:
            json_string['params']['limits'] = limits

        if item is not None:
            json_string['params']['item'] = item

        if params is not None:
            json_string['params'].update(params)

        try:
            jsonrpc_call = json.dumps(json_string)
            result = xbmc.executeJSONRPC(jsonrpc_call)
            result = json.loads(result)
        except Exception as e:
            Helper.debugMsg(debug, e, prefix="Helper.json_call()")
            debug = True

        if debug or ('error' in result):
            log('Helper.json_call() JSON STRING: ' + repr(json_string))
            log('Helper.json_call() JSON RESULT: ' + repr(result))

        return result
        
    @staticmethod
    def json_prettyprint(string):
        return json.dumps(string, sort_keys=True, indent=4, separators=(',', ': '))

    @staticmethod
    def lang(code: int) -> str:
        return ADDON.getLocalizedString(code)

    @staticmethod
    def removeDuplicatesFromListOfDict(l:list) -> list:
        # Only keep elements that are not in the rest of the initial list.
        return [i for n,i in enumerate(l) if i not in l[n + 1:]]

    @staticmethod
    def sleep(time):
        """ Modified `sleep` command that honors a user exit request. """
        while time > 0 and not xbmc.Monitor().abortRequested():
            xbmc.sleep(min(100, time))
            time = time - 100

    @staticmethod
    def urlEncodeDict(dict):
        return urllib.parse.urlencode(dict)

    @staticmethod
    def wrapDict(x:dict) -> dict:
        return x

    @staticmethod
    def wrapList(x:list) -> list:
        return x

    class Window:
        @staticmethod
        def clearProp(key, window_id=10000):
            window = xbmcgui.Window(window_id)
            window.clearProperty(key)

        @staticmethod
        def getProp(key, window_id=10000):
            window = xbmcgui.Window(window_id)
            result = window.getProperty(key.replace('.json','').replace('.bool',''))
            if result:
                if key.endswith('.json'):
                    result = json.loads(result)
                elif key.endswith('.bool'):
                    result = result in ('true', '1')
            return result
        
        @staticmethod
        def setProp(key, value, window_id=10000):
            window = xbmcgui.Window(window_id)
            if key.endswith('.json'):
                key = key.replace('.json', '')
                value = json.dumps(value)
            elif key.endswith('.bool'):
                key = key.replace('.bool', '')
                value = 'true' if value else 'false'
            window.setProperty(key, value)
    # end of Window class

# end of Helper class

##############################
        
class Settings:
    @staticmethod
    def getCacheTimeout() -> int:
        return int(Settings.getSetting("cache.timeout")) * 60

    @staticmethod
    def getSetting(setting: str) -> str:
        return xbmcaddon.Addon().getSetting(setting)

    @staticmethod
    def setSetting(setting: str, value):
        xbmcaddon.Addon().setSetting(setting, str(value))
        return
    
    @staticmethod
    def openSettings(categoryPos: int = 0, settingPos: int = 0):
        try:
            exec = xbmc.executebuiltin
            exec('Addon.OpenSettings(%s)' % ADDON_ID)
            exec('SetFocus(%i)' % (categoryPos - 100))
            exec('SetFocus(%i)' % (settingPos - 80))
        except Exception as e:
            logerror(e)
            return
# end of Settings class