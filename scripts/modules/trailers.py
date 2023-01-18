##############################

import requests

import scripts.helper as H
import scripts.modules.cache as cache

from scripts.helper import Helper as HP

##############################

class Trailers:
    __KEY_FMT = "trailers_%s_%s"
    __CACHE_LIFE = H.Settings.getCacheTimeout()
    __URL_IMDB_VIDEO = 'https://www.imdb.com/_json/video/'

    @staticmethod
    def getIMDBTrailers(imdb:str) -> list:
        key = Trailers.__KEY_FMT % ('imdb', imdb)

        items = cache.get(key, Trailers.__CACHE_LIFE, Trailers.__getImdbVideos, imdb)
        if not items or items == []:
            raise Exception("No IMDB trailers available.")
        return items
    # end of getIMDBTrailers() function

    @staticmethod
    def __getImdbVideos(imdb:str) -> list:
        """
        Returns a list of dictionaries: [{title, duration, icon, video}]
        """
        url = Trailers.__URL_IMDB_VIDEO + imdb
        
        request = requests.get(url)
        if request.status_code != 200:
            raise Exception(f"IMDB Trailer not found for '{imdb}'.")
        response = dict(request.json())
        request.close()

        videos = []
        listItems = response.get('playlists', {}).get(imdb, {}).get('listItems', [])
        for item in listItems:
            try:
                vidID = item.get('videoId')
                metadata = HP.wrapDict(response.get('videoMetadata', {}).get(vidID))
                title = metadata.get('title')
                duration = metadata.get('duration')
                icon = metadata.get('smallSlate', {}).get('url2x')
                related_to = metadata.get('primaryConst', imdb)
                if (related_to != imdb):
                    continue
                encodings = metadata.get('encodings', [])
                qualities = ['1080p', '720p', '480p', '360p', 'SD']
                video = None
                for q in qualities:
                    for e in encodings:
                        e = HP.wrapDict(e)
                        vidUrl = e.get('videoUrl')
                        defn = e.get('definition')
                        if defn == q:
                            video = vidUrl
                            break
                    if video is not None:
                        break
                if video is None:
                    continue
                videos.append({
                    'title': title,
                    'duration': duration,
                    'icon': icon,
                    'video': video
                })
            except:
                pass

        return videos
    # end of __getImdbVideos() function
# end of Trailers class