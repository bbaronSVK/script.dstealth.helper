##############################

import scripts.helper as H

from scripts.plugin_helper import PluginHelper as PH

##############################

MOVIES_MENU = "movies_main"
TVSHOWS_MENU = "tvshows_main"
TRAKT_MENU = "trakt_main"
SEARCH_MENU = "search_main"
PLAY = 'play'
TRAILER = 'trailer'

##############################

class MainMenu:
    @staticmethod
    def List(params:dict) -> None:
        handle = PH.getHandle(params)
        
        menu = PH.Menu(handle)
        menu.addFolder(32100, {'req':MOVIES_MENU}, "movies.png", "movies.jpg", "empty.jpg")
        menu.addFolder(32200, {'req':TVSHOWS_MENU}, "tv.png", "tv.jpg", "empty.jpg")
        menu.addFolder(32300, {'req':TRAKT_MENU}, "trakt.png", "trakt.jpg", "empty.jpg")
        menu.addFolder(32400, {'req':SEARCH_MENU}, "search.png", "search.jpg", "empty.jpg")
        menu.finishMenu()
        return
    
    # leave these imports here as the Router will make use of them
    import scripts.plugin_dirs.moviesmenu as Movies
    import scripts.plugin_dirs.tvshowsmenu as TVShows
    
# end of MainMenu class

class Misc:
    @staticmethod
    def play(params:dict) -> None:
        handle = PH.getHandle(params)
        name = params.get('name', '')
        title = params.get('title', '')
        year = params.get('year', '')
        imdb = params.get('imdb', '')
        tmdb = params.get('tmdb', '')

        # TODO: if scraper available, provide scraped url's instead of trailer

        # autoplay trailer
        params.update({'autoplay': 'true'})
        Misc.playTrailer(params)

        return
    # end of play() function

    @staticmethod
    def playTrailer(params:dict) -> None:
        handle = PH.getHandle(params)
        name = params.get('name', '')
        title = params.get('title', '')
        year = params.get('year', '')
        imdb = params.get('imdb', '')
        tmdb = params.get('tmdb', '')
        autoplay = True if params.get('autoplay', '').lower() == 'true' else False

        tlist = None
        try:
            from scripts.modules.trailers import Trailers as T
            tlist = T.getIMDBTrailers(imdb)
        except:
            pass

        """
        TODO:
        try: IMDB trailer
        catch, try: TMDB trailer
        catch, try: YouTube trailer
        catch dialog "Could not find any trailers"
        """

        if not tlist or tlist == []:
            H.DIALOG.ok(H.Helper.lang(32000), H.Helper.lang(32016) + name)
            return

        # sort the list by official trailers first
        tlist = [v for v in tlist if 'official' in v['title'].lower()] + \
                [v for v in tlist if 'trailer' in v['title'].lower() and 'official' not in v['title'].lower()] + \
                [v for v in tlist if 'trailer' not in v['title'].lower() and 'official' not in v['title'].lower()]

        if autoplay:
            selected = tlist[0]
        else:
            vids = []
            for t in tlist:
                mi = PH.MenuItem(t['title'], t['duration'])
                icon = t['icon']
                mi.setArt(icon=icon, thumb=icon, poster=icon)
                vids.append(mi.getListItem())

            response = H.DIALOG.select("Select a Trailer", vids, useDetails=True)
            if response == -1:
                return # cancelled
            selected = tlist[response]
        
        icon = selected['icon']
        menuitem = PH.MenuItem(selected['title'], selected['duration'], selected['video'])
        menuitem.setArt(icon=icon, thumb=icon, poster=icon)
        menuitem.setProperties({'IsPlayable': 'true'})
        PH.resolve(handle, succeeded=True, listitem = menuitem.getListItem())

        return
    # end of playTrailer() function
# end of Misc class