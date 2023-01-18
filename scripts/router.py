##############################

import scripts.modules.cache as cache
import scripts.plugin_dirs.mainmenus as Plugin

from scripts.helper import *

##############################

def plugin_action(params):
    req = params.get("req", '').lower()

    if req == '':
        return Plugin.MainMenu.List(params)

    if req == "trakt_auth":
        from scripts.api.trakt import Trakt
        return Trakt.authTrakt()

    if req == Plugin.PLAY:
        return Plugin.Misc.play(params)

    if req == Plugin.TRAILER:
        return Plugin.Misc.playTrailer(params)

    if req == Plugin.MOVIES_MENU:
        return Plugin.MainMenu.Movies.List(params)
    
    if req in Plugin.MainMenu.Movies.MenuList:
        return Plugin.MainMenu.Movies.Router(req, params)

    if req in Plugin.TVSHOWS_MENU:
        return Plugin.MainMenu.TVShows.List(params)

    if req in Plugin.MainMenu.TVShows.MenuList:
        return Plugin.MainMenu.TVShows.Router(req, params)

    log("Plugin action failed for params: " + repr(params))    
    return
# end of plugin_action

def script_action_cache_clear(params=None):
    yes = DIALOG.yesno(ADDON.getLocalizedString(32893),ADDON.getLocalizedString(32894))
    if not yes:
        return
    cache.cache_clear()
    DIALOG.notification(ADDON.getLocalizedString(32000), ADDON.getLocalizedString(32895), time=3000, icon=ADDON_ICON)
    return
# end of clearAllCache action

def script_action_getkodisetting(params):
    if 'setting' not in params:
        DIALOG.ok(ADDON.getLocalizedString(32000), ADDON.getLocalizedString(32011))
        return

    debug = params.get('debug', False)
    setting = params.get('setting', '')
    prop = params.get('prop', setting)
    window_id = params.get('window_id', 10000)

    if (debug):
        log(f"trying... getkodisetting(): {setting} into Window({window_id}).Property: {prop}")

    try:
        json_query = Helper.json_call('Settings.GetSettingValue',
                                    params={'setting': setting},
                                    debug=debug)
        result = json_query['result']
        result = result.get('value')
        result = str(result)
        if result.startswith('[') and result.endswith(']'):
           result = result[1:-1]

        Helper.Window.setProp(prop, result, window_id)
        if (debug):
            log(f"Window({window_id}).Property '{prop}' set to '{result}'")
    except Exception as e:
        Helper.Window.clearProp(prop, window_id)
        if (debug):
            log(f"Window({window_id}).Property '{prop}' cleared")
        logerror(e)
    return
# end of getkodisetting action

def script_action_setkodisetting(params):
    if 'setting' not in params:
        DIALOG.ok(ADDON.getLocalizedString(32000), ADDON.getLocalizedString(32011))
        return
    if 'value' not in params:
        DIALOG.ok(ADDON.getLocalizedString(32000), ADDON.getLocalizedString(32012))
        return

    debug = params.get('debug', False)
    setting = params.get('setting', '')
    valueStr = params.get('value', '')

    try:
        value = int(valueStr)
    except Exception:
        if valueStr.lower() == 'true':
            value = True
        elif valueStr.lower() == 'false':
            value = False
        else:
            value = valueStr

    if(debug):
        log("trying... setkodisetting(): {} = {}".format(setting, str(value)))

    Helper.json_call('Settings.SetSettingValue',
              params={'setting': setting, 'value': value},
              debug=debug)
    return
# end of setkodisetting action
