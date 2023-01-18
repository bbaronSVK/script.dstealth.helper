##############################

import json
import urllib.parse as ulibparse

import scripts.helper as H
import scripts.modules.cache as cache

from scripts.helper import Helper as HP
from scripts.plugin_helper import PluginHelper as PH
from scripts.api.imdb_parser import IMDBFilters as Filters
from scripts.api.imdb_parser import IMDBParser as IMDB
from scripts.api.tmdb_api import *

##############################

TVS_FILTER_LANG = "tvshows_filter_lang"
TVS_FILTER_LISTS = "tvshows_filter_lists"
TVS_FILTER_GENRE = "tvshows_filter_genre"
TVS_FILTER_RELEASE = "tvshows_filter_release"
TVS_FILTER_VOTES = "tvshows_filter_votes"
TVS_FILTER_SORT = "tvshows_filter_sort"
TVS_FILTER_RESULTS = "tvshows_filter_results"
TVS_EPISODES = "tvshows_episodes"
TVS_NEW = "tvshows_new"
TVS_POPULAR = "tvshows_popular"
TVS_TRENDING = "tvshows_trending"
TVS_UPCOMING = "tvshows_upcoming"
TVS_GENRE_ACTION = "tvshows_genre_action"
TVS_GENRE_COMEDY = "tvshows_genre_comedy"
TVS_GENRE_DRAMA = "tvshows_genre_drama"
TVS_GENRE_HORROR = "tvshows_genre_horror"
TVS_GENRE_THRILLER = "tvshows_genre_thriller"

MenuList = [
    TVS_FILTER_LANG,
    TVS_FILTER_LISTS,
    TVS_FILTER_GENRE,
    TVS_FILTER_RELEASE,
    TVS_FILTER_VOTES,
    TVS_FILTER_SORT,
    TVS_FILTER_RESULTS,
    TVS_EPISODES,
    TVS_NEW,
    TVS_POPULAR,
    TVS_TRENDING,
    TVS_UPCOMING,
    TVS_GENRE_ACTION,
    TVS_GENRE_COMEDY,
    TVS_GENRE_DRAMA,
    TVS_GENRE_HORROR,
    TVS_GENRE_THRILLER
]

##############################

def Router(req, params:dict) -> None:
    if req == TVS_FILTER_LANG:
        return __Filter_Lang(params)
    if req == TVS_FILTER_LISTS:
        return __Filter_Lists(params)
    if req == TVS_FILTER_GENRE:
        return __Filter_Genre(params)
    if req == TVS_FILTER_RELEASE:
        return __Filter_Release(params)
    if req == TVS_FILTER_VOTES:
        return __Filter_Votes(params)
    if req == TVS_FILTER_SORT:
        return __Filter_Sort(params)
    if req == TVS_FILTER_RESULTS:
        return __Filter_Results(params)

    if req == TVS_EPISODES:
        return __NewEpisodes(params)
    if req == TVS_NEW:
        return __New(params)
    if req == TVS_POPULAR:
        return __Popular(params)
    if req == TVS_TRENDING:
        return __Trending(params)
    if req == TVS_UPCOMING:
        return __Upcoming(params)

    if req == TVS_GENRE_ACTION:
        return __genre_action(params)
    if req == TVS_GENRE_COMEDY:
        return __genre_comedy(params)
    if req == TVS_GENRE_DRAMA:
        return __genre_drama(params)
    if req == TVS_GENRE_HORROR:
        return __genre_horror(params)
    if req == TVS_GENRE_THRILLER:
        return __genre_thriller(params)

    return
# end of Movie Router method

def List(params:dict) -> None:
    handle = PH.getHandle(params)

    menu = PH.Menu(handle)
    menu.addFolder(HP.lang(32500) + " " + HP.lang(32200), {'req':TVS_FILTER_LANG}, "filter.png", "filter.jpg")
    menu.addFolder(32205, {'req':TVS_UPCOMING}, "upcoming.png")
    menu.addFolder(32201, {'req':TVS_EPISODES}, "new.png")
    menu.addFolder(32202, {'req':TVS_NEW}, "new.png")
    menu.addFolder(32203, {'req':TVS_POPULAR}, "popular.png")
    menu.addFolder(32204, {'req':TVS_TRENDING}, "trending.png")
    menu.addFolder(32206, {'req':TVS_GENRE_ACTION}, "genres.png")
    menu.addFolder(32207, {'req':TVS_GENRE_COMEDY}, "genres.png")
    menu.addFolder(32208, {'req':TVS_GENRE_DRAMA}, "genres.png")
    menu.addFolder(32209, {'req':TVS_GENRE_HORROR}, "genres.png")
    menu.addFolder(32210, {'req':TVS_GENRE_THRILLER}, "genres.png")
    menu.finishMenu()
    return
# end of List() function

##############################

def __filter_menu(params:dict, newReq:str, suffix:int, firstItemLang, list:dict, filterkey:str, thumb='filter.jpg') -> None:
    handle = PH.getHandle(params)
    params.pop("handle", None)
    params.update({'req': newReq})

    suffix = HP.lang(suffix) + ": "

    menu = PH.Menu(handle)
    if firstItemLang is not None:
        menu.addFolder(suffix + HP.lang(firstItemLang), params, "filter.png", thumb)

    for key, val in list.items():
        req = params.copy()
        req.update({filterkey: key})
        menu.addFolder(suffix + HP.lang(val), req, "filter.png", thumb)

    menu.finishMenu()
    return
# end of __filter_menu() function

def __Filter_Lang(params:dict) -> None:
    __filter_menu(params, TVS_FILTER_LISTS, 32510, 32501, Filters.LangDict, Filters.F_LANG)
    return
# end of __Filter_Lang() function

def __Filter_Lists(params:dict) -> None:
    __filter_menu(params, TVS_FILTER_GENRE, 32590, 32501, Filters.ListsDict, Filters.F_LIST)
    return
# end of __Filter_Lists() function

def __Filter_Genre(params:dict) -> None:
    __filter_menu(params, TVS_FILTER_RELEASE, 32530, 32501, Filters.GenreDict, Filters.F_GENRE)
    return
# end of __Filter_Genre() function

def __Filter_Release(params:dict) -> None:
    __filter_menu(params, TVS_FILTER_VOTES, 32560, 32502, Filters.ReleaseDict, Filters.F_RELEASE)
    return
# end of __Filter_Release() function

def __Filter_Votes(params:dict) -> None:
    handle = PH.getHandle(params)
    params.pop("handle", None)
    params.update({'req': TVS_FILTER_SORT})

    suffix = HP.lang(32570) + ": "

    menu = PH.Menu(handle)
    menu.addFolder(suffix + HP.lang(32503), params, "filter.png", "filter.jpg")

    for val in Filters.VotesArr:
        req = params.copy()
        req.update({Filters.F_VOTES: str(val)})
        fmtStr = HP.lang(32571) % str(val)
        menu.addFolder(suffix + fmtStr, req, "filter.png", "filter.jpg")

    menu.finishMenu()
    return
# end of __Filter_Votes() function

def __Filter_Sort(params:dict) -> None:
    __filter_menu(params, TVS_FILTER_RESULTS, 32580, None, Filters.SortDict, Filters.F_SORTBY, None)
    return
# end of __Filter_Sort() function

def __Filter_Results(params:dict, url:str=IMDB.URL_TVS_FILTER) -> None:
    handle = PH.getHandle(params)
    params.pop("handle", None)
    start = params.get('start', '1')
    count = PH.getItemCount()
    
    cacheKey = "tvs_filter_%s_%s_" % (str(count), str(start))
    url = url.replace('{count}', str(count)).replace('{start}', str(start))
    urlParams = ""

    if Filters.F_LANG in params:
        lang = str(params.get(Filters.F_LANG))
        urlParams += Filters.FMT_LANG % lang
        cacheKey += lang + "_"
    if Filters.F_LIST in params:
        lists = str(params.get(Filters.F_LIST))
        urlParams += Filters.FMT_LIST % lists
        cacheKey += lists + "_"
    if Filters.F_GENRE in params:
        genre = str(params.get(Filters.F_GENRE))
        urlParams += Filters.FMT_GENRE % genre
        cacheKey += genre + "_"
    if Filters.F_RELEASE in params:
        rels = str(params.get(Filters.F_RELEASE))
        urlParams += Filters.FMT_RELEASE % rels
        cacheKey += rels + "_"
    if Filters.F_VOTES in params:
        votes = str(params.get(Filters.F_VOTES))
        urlParams += Filters.FMT_VOTES % votes
        cacheKey += votes + "_"
    if Filters.F_SORTBY in params:
        sortby = str(params.get(Filters.F_SORTBY))
        urlParams += Filters.FMT_SORTBY % sortby
        cacheKey += sortby + "_"

    url = url + urlParams
    url = PH.parseDatesInUrl(url)

    # overwrite cacheKey if a key was provided
    if 'key' in params:
        cacheKey = params.get('key')

    try: startNum = int(start)
    except: startNum = 1
    startNext = startNum + count
    params.update({'start': startNext})

    items = cache.get(cacheKey, H.Settings.getCacheTimeout(), IMDB.parseUrlContents, url)
    items = PH.fillMetadataWorkers(items, __getTmdbMetadata)
    __tvDirectory(handle, items, params)

    return
# end of __Filter_Results() function

##############################

def __NewEpisodes(params:dict) -> None:
    start = params.get('start', '1')
    count = PH.getItemCount()
    key = "tvs_newepisodes_%s_%s" % (str(count), str(start))
    params.update({
        'key': key,
        Filters.F_LANG: 'en',
        Filters.F_RELEASE: "date[-7],date[0]",
        Filters.F_SORTBY: "release_date,desc"
    })
    __Filter_Results(params, IMDB.URL_TVS_AIRING)
    return
# end of __NewEpisodes() function

def __New(params:dict) -> None:
    start = params.get('start', '1')
    count = PH.getItemCount()
    key = "tvs_newshows_%s_%s" % (str(count), str(start))
    params.update({
        'key': key,
        Filters.F_LANG: 'en',
        Filters.F_RELEASE: "date[-365],date[0]",
        Filters.F_VOTES: 250,
        Filters.F_SORTBY: "release_date,desc"
    })
    __Filter_Results(params)
    return
# end of __New() function

def __Popular(params:dict) -> None:
    start = params.get('start', '1')
    count = PH.getItemCount()
    key = "tvs_popular_%s_%s" % (str(count), str(start))
    params.update({
        'key': key,
        Filters.F_LANG: 'en',
        Filters.F_RELEASE: "date[-365],date[0]",
        Filters.F_VOTES: 500,
        Filters.F_SORTBY: "user_rating,desc"
    })
    __Filter_Results(params)
    return
# end of __Popular() function

def __Trending(params:dict) -> None:
    start = params.get('start', '1')
    count = PH.getItemCount()
    key = "tvs_trending_%s_%s" % (str(count), str(start))
    params.update({
        'key': key,
        Filters.F_LANG: 'en',
        Filters.F_RELEASE: "date[-365],date[0]",
        Filters.F_VOTES: 500,
        Filters.F_SORTBY: "moviemeter,asc"
    })
    __Filter_Results(params)
    return
# end of __Trending() function

def __Upcoming(params:dict) -> None:
    start = params.get('start', '1')
    count = PH.getItemCount()
    key = "tvs_upcoming_%s_%s" % (str(count), str(start))
    params.update({
        'key': key,
        Filters.F_LANG: 'en',
        Filters.F_RELEASE: "date[1],",
        Filters.F_SORTBY: "moviemeter,asc"
    })
    __Filter_Results(params)
    return
# end of __Upcoming() function

def __genre_action(params:dict) -> None:
    start = params.get('start', '1')
    count = PH.getItemCount()
    key = "tvs_genre_action_%s_%s" % (str(count), str(start))
    params.update({
        'key': key,
        Filters.F_LANG: 'en',
        Filters.F_GENRE: "action",
        Filters.F_RELEASE: "date[-365],date[0]",
        Filters.F_VOTES: 1000,
        Filters.F_SORTBY: "release_date,desc"
    })
    __Filter_Results(params)
    return
# end of __genre_action() function

def __genre_comedy(params:dict) -> None:
    start = params.get('start', '1')
    count = PH.getItemCount()
    key = "tvs_genre_comedy_%s_%s" % (str(count), str(start))
    params.update({
        'key': key,
        Filters.F_LANG: 'en',
        Filters.F_GENRE: "comedy",
        Filters.F_RELEASE: "date[-365],date[0]",
        Filters.F_VOTES: 1000,
        Filters.F_SORTBY: "release_date,desc"
    })
    __Filter_Results(params)
    return
# end of __genre_comedy() function

def __genre_drama(params:dict) -> None:
    start = params.get('start', '1')
    count = PH.getItemCount()
    key = "tvs_genre_drama_%s_%s" % (str(count), str(start))
    params.update({
        'key': key,
        Filters.F_LANG: 'en',
        Filters.F_GENRE: "drama",
        Filters.F_RELEASE: "date[-365],date[0]",
        Filters.F_VOTES: 1000,
        Filters.F_SORTBY: "release_date,desc"
    })
    __Filter_Results(params)
    return
# end of __genre_drama() function

def __genre_horror(params:dict) -> None:
    start = params.get('start', '1')
    count = PH.getItemCount()
    key = "tvs_genre_horror_%s_%s" % (str(count), str(start))
    params.update({
        'key': key,
        Filters.F_LANG: 'en',
        Filters.F_GENRE: "horror",
        Filters.F_RELEASE: "date[-365],date[0]",
        Filters.F_VOTES: 1000,
        Filters.F_SORTBY: "release_date,desc"
    })
    __Filter_Results(params)
    return
# end of __genre_horror() function

def __genre_thriller(params:dict) -> None:
    start = params.get('start', '1')
    count = PH.getItemCount()
    key = "tvs_genre_thriller_%s_%s" % (str(count), str(start))
    params.update({
        'key': key,
        Filters.F_LANG: 'en',
        Filters.F_GENRE: "thriller",
        Filters.F_RELEASE: "date[-365],date[0]",
        Filters.F_VOTES: 1000,
        Filters.F_SORTBY: "release_date,desc"
    })
    __Filter_Results(params)
    return
# end of __genre_thriller() function

##############################

def __getTmdbMetadata(metadataList:list, items:list, i:int):
    try:
        itemmeta = HP.wrapDict(items[i])

        if itemmeta.get(cache.METACACHE) == True:
            return
        
        fullmeta = TMDBApi.getTVShowDetails(itemmeta)
        if fullmeta is None:
            return

        HP.wrapDict(items[i]).update(fullmeta)
        metadataList.append(fullmeta)
    except Exception as e:
        if H.DEBUG:
            H.logerror(e)
        pass
# end of __getMetadata() function

def __tvDirectory(handle, items:list, nextPageReq:dict = None):
    menu = PH.Menu(handle)
    created = 0
    errored = 0
    errors = []
    listed_already = []
    for i in items:
        try:
            i = HP.wrapDict(i)

            title, year, imdb, tmdb = i['title'], i['year'], i['imdb'], i.get('tmdb', '0')
            label = '%s (%s)' % (title, year)

            if label in listed_already:
                continue
            else:
                listed_already.append(label)

            urllabel = ulibparse.quote_plus(label)
            urltitle = ulibparse.quote_plus(title)
            urlinfo = 'name=%s&title=%s&year=%s&imdb=%s&tmdb=%s' % (urllabel, urltitle, year, imdb, tmdb)

            meta = {}
            meta = dict((k, v) for k, v in i.items() if not v == '0')
            meta.update({'code': imdb, 'imdbnumber': imdb, 'imdb_id': imdb})
            meta.update({'mediatype': 'movie'})
            meta.update({'trailer': '%s?req=trailer&%s&autoplay=false' % (H.PLUGIN_ID, urlinfo)})
            
            if 'duration' not in meta:
                meta.update({'duration': '0'})
            # convert minutes to seconds
            meta.update({'duration': str(int(meta['duration']) * 60)})
            
            if 'poster' not in meta:
                meta.update({'poster': PH.DEFAULT_TV_POSTER})
            poster = meta.get('poster')

            if 'fanart' not in meta:
                meta.update({'fanart': PH.FANART_EMPTY})
            fanart = meta.get('fanart')

            contextMenu = []
            addToLibrary_str = HP.lang(32015)
            addToLibrary_act = 'RunPlugin(%s?req=movieToLibrary&%s)' % (H.PLUGIN_ID, urlinfo)
            contextMenu.append((addToLibrary_str, addToLibrary_act))

            art = {'icon':poster, 'thumb':poster, 'poster':poster, 'fanart': fanart}
            properties = {'IsPlayable': 'true', 'imdb_id': imdb}

            onclickurl = '%s?req=play&%s' % (H.PLUGIN_ID, urlinfo)

            item = menu.addItem(label, onclickurl, PH.cleanMetaData(meta), art=art, contextMenu=contextMenu, properties=properties, offscreen=True)

            castWithThumb = i.get('castwiththumb')
            if castWithThumb and castWithThumb != '0':
                item.getListItem().setCast(castWithThumb)

            created += 1
        except Exception as e:
            errored += 1
            errors.append(e)

    if (nextPageReq is not None) and (len(items) >= PH.getItemCount()):
        menu.addFolder(HP.lang(32017), nextPageReq, "next.png", "next_page.jpg")

    menu.setContent('tvshows')
    menu.finishMenu(cacheToDisk=False)
    # give it a second for the menu page to load before we try to change the view
    HP.sleep(1000)
    menu.setView('movies', 50)
    
    if H.DEBUG:
        H.log(f"TVShowsDirectory created {created} items.")
        H.log(f"TVShowsDirectory encountered {errored} errors.")
        for e in errors:
            H.logerror(e)
# end of __tvDirectory() function