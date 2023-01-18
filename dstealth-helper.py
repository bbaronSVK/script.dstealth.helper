#!/usr/bin/python

# Replacement for the old script.skin.helper
# Written by: DStealth
# Inspired by Embuary Helper: https://github.com/sualfred/script.embuary.helper/wiki
# Kodi Docs: https://xbmc.github.io/docs.kodi.tv/master/kodi-base/
# Kodi Dev: https://xbmc.github.io/docs.kodi.tv/master/kodi-dev-kit/

##############################
#       Documentation        #
##############################
"""

USAGE:
    RunScript(script.dstealth.helper,
              action=<action>,
              [parameters as key=value]
             )

    OPTIONAL Parameters:
        debug
            - passing this as a parameter will do two things:
                1) display more verbose INFO logs
                2) display Dialog.OK prompts if errors occur

ACTIONS:
    getkodisetting
        - gets the value of the Kodi setting asked for and sets it the window property
        - if no property "prop" is given, the property will be the full setting name
        - if no window_id is given, will default to home aka 10000
        - (refer to guisettings.xml in Kodi userdata folder)
        PARAMS:
            setting=<kodi.setting>
            [prop=<name_of_window_property_to_receive_value>]
            [window_id=<window_id_to_set_value_to_to>]
        EXAMPLE:
            action=getkodisettings
            setting=input.enablemouse
            prop=my_mouse
            window_id=1130

    setkodisetting
        - sets the value of various Kodi Settings
        - (refer to guisettings.xml in Kodi userdata folder)
        PARAMS:
            setting=<kodi.setting>
            value=<value>
        EXAMPLE:
            action=setkodisettings,
            setting=input.enablemouse
            value=false

"""
##############################

import xbmcgui
import sys

import scripts.modules.cache as cache
from scripts.helper import *
from scripts.router import *

##############################

class Main:
    def __init__(self):
        self.pluginMode = False
        self.debug = DEBUG
        self.action = False

        self.parseArgs()

        mode = "Plugin" if self.pluginMode else "Script"
        log(f"DStealth Helper ran in {mode} mode.")        
        if (self.debug):
            log("DSH args: " + repr(sys.argv))
            log("DSH params: " + repr(self.params))

        for err in self.errors:
            logerror(err)

        if self.action:
            self.runAction()
        else:
            DIALOG.ok(ADDON.getLocalizedString(32002), ADDON.getLocalizedString(32010))
        return

    def parseArgs(self):
        self.params = {}
        self.errors = []
        args = sys.argv
        
        i = -1
        for arg in args:
            i += 1
            if arg.lower() == SCRIPT_ID:
                continue
            if arg.lower() == PLUGIN_ID:
                self.pluginMode = True
                self.action = "plugin"
                continue

            # this is debug for the Script feature, Plugin feature passes debug as a param
            if arg.lower().strip() == "debug":
                self.params['debug'] = True
                self.debug = True
                continue

            if arg.lower().startswith('action='):
                self.action = arg[7:].lower()
            else:
                try:
                    if self.pluginMode:
                        if i == 1:
                            # plugin:// handle
                            self.params["handle"] = int(arg)
                        if (i == 2 and arg.startswith('?')):
                            # plugin://script.dstealth.helper?paramstring
                            paramstring = arg[1:].replace('&amp;', '&') # incase xml string
                            for param in paramstring.split('&'):
                                if '=' not in param: continue                                
                                key = param.split("=")[0].lower().strip()
                                vals = param.split("=")[1:]
                                val = "=".join(vals).strip()
                                from urllib.parse import unquote_plus
                                self.params[unquote_plus(key)] = unquote_plus(val)
                    elif ('=' in arg):
                        key = arg.split("=")[0].lower().strip()
                        vals = arg.split("=")[1:]
                        val = "=".join(vals).strip()
                        self.params[key] = val
                except Exception as e:
                    self.errors.append(e)
                    continue
        return

    def runAction(self):
        try:
            if (self.pluginMode):
                action = globals()["plugin_action"]
            else:
                action = globals()["script_action_" + self.action]
            action(self.params)
        except Exception as e:
            Helper.debugMsg(self.debug, e, prefix="Helper.runAction()")
            raise e
        return

# This "if" Allows you to execute code when the file runs
#   as a Script but not when it's imported as a Module.
if __name__ == '__main__':
    cache.CleanupIfRequired()
    Main()
