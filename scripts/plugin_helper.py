##############################

import datetime
import re
import os

import xbmcaddon
import xbmcgui
import xbmcplugin

from scripts.helper import *

##############################

SCRIPT_ID = "dstealth-helper.py"
PLUGIN_ID = "plugin://script.dstealth.helper/"

ADDON = xbmcaddon.Addon()
ADDON_ID = ADDON.getAddonInfo('id')
ADDON_PATH = ADDON.getAddonInfo('path') # contains trailing \

RESOURCES_PATH = os.path.join(ADDON_PATH, 'resources') + os.sep
FANART_PATH = RESOURCES_PATH + "fanart" + os.sep
ICON_PATH = RESOURCES_PATH + "icons" + os.sep
THUMB_PATH = RESOURCES_PATH + "thumbs" + os.sep

ISFOLDER = True
ISFILE = False

##############################
   
class PluginHelper:
    
    resolve = xbmcplugin.setResolvedUrl
    
    DEFAULT_MOVIE_POSTER = THUMB_PATH + 'movie_poster.jpg'
    DEFAULT_TV_POSTER = THUMB_PATH + 'tv_poster.jpg'
    FANART_EMPTY = FANART_PATH + "empty.jpg"

    @staticmethod
    def cleanMetaData(metadata:dict):
        # Filter out non-existing/custom keys. Otherise there are tons of errors in Kodi log.
        if metadata is None:
            return metadata
        allowed = [
            'genre', 'country', 'year', 'episode', 'season', 'sortepisode', 'sortseason', 'episodeguide',
            'showlink', 'top250', 'setid', 'tracknumber', 'rating', 'userrating', 'watched', 'playcount',
            'overlay', 'cast', 'castandrole', 'director', 'mpaa', 'plot', 'plotoutline', 'title',
            'originaltitle', 'sorttitle', 'duration', 'studio', 'tagline', 'writer', 'tvshowtitle', 'premiered',
            'status', 'set', 'setoverview', 'tag', 'imdbnumber', 'code', 'aired', 'credits', 'lastplayed',
            'album', 'artist', 'votes', 'path', 'trailer', 'dateadded', 'mediatype', 'dbid']
        return {k: v for k, v in metadata.items() if k in allowed}

    def fillMetadataWorkers(items:list, function) -> list:
        # worker that uses threading to fill metadata of items
        import scripts.modules.cache as cache
        metadataList = []
        total = len(items)

        for i in range(0, total):
            dict(items[i]).update({cache.METACACHE: False})
        items = cache.getMetadata(items)

        for r in range(0, total, 40):
            threads = []
            for i in range(r, r+40):
                if i < total:
                    threads.append(Helper.createWorker(function, metadataList, items, i))
            # start the batch of threads
            [t.start() for t in threads]
            # then wait until they finish before moving on to the next batch
            [t.join() for t in threads]

        if metadataList != []:
            cache.storeMetadata(metadataList)

        items = [i for i in items if i['imdb'] != '0']
        return items
    # end of fillMetadata() function

    @staticmethod
    def getHandle(params):
        handle = params.get("handle", -999999)
        if (handle == -999999):
            raise Exception(ADDON.getLocalizedString(32013))
        return handle

    @staticmethod
    def getItemCount() -> int:
        return int(Settings.getSetting("items.per.page"))

    @staticmethod
    def parseDatesInUrl(url:str):
        # replace any date[#] with the actual date as yyyy-mm-dd
        dtnow = datetime.datetime.utcnow()
        for n in re.findall(r'date\[(\-?\d+)\]', url):
            logwarn(n)
            date = (dtnow + datetime.timedelta(int(n))).strftime('%Y-%m-%d')
            url = url.replace('date[%s]' % n, date)
        return url

    class Menu():
        def __init__(self, handle) -> None:
            self.handle = handle
            self.menuItems = []
            # more sort methods at: https://xbmc.github.io/docs.kodi.tv/master/kodi-dev-kit/group__python__xbmcplugin.html#ga85b3bff796fd644fb28f87b136025f40
            self.sortmethod = xbmcplugin.SORT_METHOD_NONE

        def addFolder(self, langLabel, req: dict, icon: str=None, thumb: str=None, fanart: str=None):
            label = ADDON.getLocalizedString(langLabel) if isinstance(langLabel, int) else langLabel

            item = PluginHelper.MenuItem(label)

            icon = ICON_PATH + icon if icon else None
            thumb = THUMB_PATH + thumb if thumb else None
            fanart = FANART_PATH + fanart if fanart else PluginHelper.FANART_EMPTY
            item.setArt(icon= icon, thumb= thumb, poster= thumb, fanart= fanart)
            
            self.addMenuItem(PLUGIN_ID +"?"+ Helper.urlEncodeDict(req), item, ISFOLDER)
            return item
        
        def addItem(self, label:str, url:str, infolabelsMeta:dict={}, infoType:str='Video', art:dict={}, contextMenu:list=[], properties={}, offscreen:bool=False):
            item = PluginHelper.MenuItem(label, offscreen=offscreen)
            if len(infolabelsMeta) > 0: item.setInfo(infoType, infolabelsMeta)
            if len(art) > 0: item.setArt(art)
            if len(contextMenu) > 0: item.setContextMenu(contextMenu)
            if len(properties) > 0: item.setProperties(properties)

            self.addMenuItem(url, item, ISFILE)
            return item

        def addMenuItem(self, url, menuitem, isFolder=False, totalItems=1):
            listitem = None
            if isinstance(menuitem, PluginHelper.MenuItem):
                listitem = menuitem.getListItem()
            elif isinstance(menuitem, xbmcgui.ListItem):
                listitem = menuitem
            else:
                raise Exception(ADDON.getLocalizedString(32014))
            
            item = {}
            item['url'] = url
            item['listitem'] = listitem
            item['isFolder'] = isFolder
            item['totalItems'] = totalItems
            self.menuItems.append(item)
            return
        
        def finishMenu(self, cacheToDisk:bool=True):
            for item in self.menuItems:
                try:
                    xbmcplugin.addDirectoryItem(self.handle, item.get('url'), item.get('listitem'), item.get('isFolder'), item.get('totalItems'))
                except:
                    pass
            xbmcplugin.addSortMethod(self.handle, self.sortmethod)
            xbmcplugin.endOfDirectory(self.handle, cacheToDisc=cacheToDisk)
            
        def setContent(self, content:str):
            """
            Sets the plugins content.

            :param content: string - content type (eg. movies or tvshows)

            Available content strings:

            ==================================================  
            files songs artists albums movies tvshows episodes musicvideos videos images games
            ==================================================

            Use **videos** for all videos which do not apply to the more specific mentioned ones like "movies", "episodes" etc. A good example is youtube.

            @python_v18 Added new **games** content
            """
            xbmcplugin.setContent(self.handle, content)

        def setView(self, content:str, view:int):
            for i in range(0, 200):
                # try every 100 miliseconds until view is loaded and then we succeed or fail
                if xbmc.getCondVisibility('Container.Content(%s)' % content):
                    try:
                        return xbmc.executebuiltin('Container.SetViewMode(%s)' % str(view))
                    except:
                        return
                Helper.sleep(100)
            return

        def sortByNone(self):
            self.sortmethod = xbmcplugin.SORT_METHOD_NONE
        def sortByDateAdded(self):
            self.sortmethod = xbmcplugin.SORT_METHOD_DATEADDED
        def sortByDuration(self):
            self.sortmethod = xbmcplugin.SORT_METHOD_DURATION
        def sortByLabel(self):
            self.sortmethod = xbmcplugin.SORT_METHOD_LABEL
        def sortByTitle(self):
            self.sortmethod = xbmcplugin.SORT_METHOD_TITLE
        
    # end of Menu class

    class MenuItem():
        def __init__(self, label="", label2="", path="", offscreen=False) -> None:
            self.ListItem = xbmcgui.ListItem(label, label2, path, offscreen)
        def getListItem(self) -> xbmcgui.ListItem:
            return self.ListItem
        def setArt(self, art:dict=None, icon="", thumb="", poster="", fanart="", landscape="", banner=""):
            if art == None:
                art = {'icon':icon, 'thumb':thumb, 'poster':poster, 'fanart':fanart, 'landscape':landscape, 'banner':banner}
            self.ListItem.setArt(art)
        def setContextMenu(self, cm:list):
            self.ListItem.addContextMenuItems(cm)
        def setDateTime(self, w3cDateTime):
            self.ListItem.setDateTime(w3cDateTime)
        def setInfo(self, type:str, infolabel:dict):
            self.ListItem.setInfo(type, infolabel) # infolabel is { key: value }
        def setLabel(self, text):
            self.ListItem.setLabel(text)
        def setLabel2(self, text):
            self.ListItem.setLabel2(text)
        def setPath(self, path):
            self.ListItem.setPath(path)
        def setProperties(self, props:dict):
            self.ListItem.setProperties(props)
        def setStreamInfo(self, stream:str, info:dict):
            self.ListItem.addStreamInfo(stream, info)
    # end of MenuItem class

# end of PluginHelper class
