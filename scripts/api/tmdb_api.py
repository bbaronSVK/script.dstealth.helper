##############################

import base64
import re
import requests
import scripts.helper as H

from scripts.helper import Helper as HP
from scripts.plugin_helper import PluginHelper as PH

##############################

class TMDBApi:
    """
        WARNING/LEGAL:
        You are NOT allowed to use this TMDB Api Key for your own purposes.
        If you need a TMDB Api Key please get one for free
        from the offocial TMDB API site.
    """
    __API_KEY = base64.b64decode(b'ZjhhZjg4OThlYjAwNWEwMmZiNWM5NjI4MTE0MzZhNjA=').decode('ascii')
    __IMG_LINK = "https://image.tmdb.org/t/p/w%s%s" # (size(width), path)
    __URL_FIND_IMDB = "https://api.themoviedb.org/3/find/%s?api_key=%s&external_source=imdb_id" % ('%s', __API_KEY)
    __URL_GET_MOVIE_DETAILS = "https://api.themoviedb.org/3/movie/%s?api_key=%s&append_to_response=credits,external_ids" % ('%s', __API_KEY)
    __URL_GET_TVSHOW_DETAILS = "https://api.themoviedb.org/3/tv/%s?api_key=%s&append_to_response=credits,external_ids" % ('%s', __API_KEY)

    @staticmethod
    def getMovieDetails(itemMeta:dict):
        try:
            # PART 1: get TMDB ID via the IMDB ID
            imdb_id = itemMeta.get('imdb')
            tmdb_id = TMDBApi.__getTmdbFromImdb(imdb_id, 'movie')
            
            # PART 2: Get movie details metadata
            urlDetails = TMDBApi.__URL_GET_MOVIE_DETAILS % str(tmdb_id)
            details = TMDBApi.__apiRequest(urlDetails)

            meta = {}
            meta.update({'imdb': imdb_id})
            meta.update({'tmdb': tmdb_id})

            TMDBApi.__ifDetailUpdateMeta(itemMeta, meta, 'rating', 'rating')
            TMDBApi.__ifDetailUpdateMeta(itemMeta, meta, 'votes', 'votes')
            TMDBApi.__ifDetailUpdateMeta(itemMeta, meta, 'mpaa', 'mpaa')

            TMDBApi.__ifDetailUpdateMeta(details, meta, 'title', 'title')
            TMDBApi.__ifDetailUpdateMeta(details, meta, 'original_title', 'originaltitle')
            TMDBApi.__ifDetailUpdateMeta(details, meta, 'tagline', 'tagline')
            TMDBApi.__ifDetailUpdateMeta(details, meta, 'overview', 'plot')
            TMDBApi.__ifDetailUpdateMeta(details, meta, 'release_date', 'premiered')
            TMDBApi.__ifDetailUpdateMeta(details, meta, 'status', 'status')
            TMDBApi.__ifDetailUpdateMeta(details, meta, 'runtime', 'duration')

            try:
                _ppath = details.get('poster_path', '')
                if _ppath and _ppath != '':
                    poster = TMDBApi.__IMG_LINK % ('500', _ppath)
                else:
                    poster = PH.DEFAULT_MOVIE_POSTER
                    #_imdbPoster = itemMeta.get('poster', '0')
            except:
                poster = '0'
            meta.update({'poster': poster})

            try:
                _fpath = details.get('backdrop_path', '')
                fanart = TMDBApi.__IMG_LINK % ('1280', _fpath) if _fpath and _fpath != '' else '0'
            except:
                fanart = '0'
            meta.update({'fanart': fanart})

            try: year = re.findall('(\d{4})', meta.get('premiered'))[0]
            except: year = '0'
            meta.update({'year': year})

            try: studio = details.get('production_companies', [{}])[0].get('name', '0')
            except: studio = '0'
            meta.update({'studio': studio})

            try:
                genres = details.get('genres', [])
                genres = [HP.wrapDict(g).get('name') for g in genres]
                genres = ' / '.join(genres)
            except:
                genres = '0'
            meta.update({'genre': genres})
            
            try:
                castWithThumb = []
                cast = details['credits']['cast'][:30]
                for person in cast:
                    try:
                        person = HP.wrapDict(person)
                        _cpath = person.get('profile_path', '').strip()
                        thumb = TMDBApi.__IMG_LINK % ('185', _cpath) if _cpath and _cpath != '' else ''
                        name = person.get('name')
                        role = person.get('character')
                        castWithThumb.append({
                            'name': name,
                            'role': role,
                            'thumbnail': thumb
                        })
                    except: pass
                if castWithThumb == []:
                    castWithThumb = '0'
            except:
                castWithThumb = '0'
            meta.update({'castwiththumb': castWithThumb})

            try:
                crew = HP.wrapList(details['credits']['crew'])
                director = ', '.join([d['name'] for d in [x for x in crew if x['job'] == 'Director']])
                writer = ', '.join([w['name'] for w in [y for y in crew if y['job'] in ['Writer', 'Screenplay', 'Author', 'Novel']]])
            except:
                director = writer = '0'
            meta.update({'director': director})
            meta.update({'writer': writer})

            # filter out empty values
            meta = dict((k,v) for k,v in meta.items() if v != '0')
            return meta
        except Exception as e:
            if H.DEBUG:
                H.logerror(e)
            return None
    # end of getMovieDetails() function

    @staticmethod
    def getTVShowDetails(itemMeta:dict):
        imdb_id = '?'
        tmdb_id = '?'
        try:
            # PART 1: get TMDB ID via the IMDB ID
            imdb_id = itemMeta.get('imdb')
            tmdb_id = TMDBApi.__getTmdbFromImdb(imdb_id, 'tv')
            
            # PART 2: Get movie details metadata
            urlDetails = TMDBApi.__URL_GET_TVSHOW_DETAILS % str(tmdb_id)
            details = TMDBApi.__apiRequest(urlDetails)

            meta = {}
            meta.update({'imdb': imdb_id})
            meta.update({'tmdb': tmdb_id})

            TMDBApi.__ifDetailUpdateMeta(itemMeta, meta, 'mpaa', 'mpaa')

            TMDBApi.__ifDetailUpdateMeta(details, meta, 'name', 'title')
            TMDBApi.__ifDetailUpdateMeta(details, meta, 'original_name', 'originaltitle')
            TMDBApi.__ifDetailUpdateMeta(details, meta, 'tagline', 'tagline')
            TMDBApi.__ifDetailUpdateMeta(details, meta, 'overview', 'plot')
            TMDBApi.__ifDetailUpdateMeta(details, meta, 'first_air_date', 'premiered')
            TMDBApi.__ifDetailUpdateMeta(details, meta, 'status', 'status')
            
            try:
                last_aired = details.get("last_episode_to_air")
                next_aired = details.get("next_episode_to_air")
                runtime = None
                if next_aired is not None:
                    runtime = HP.wrapDict(next_aired).get('runtime')
                elif last_aired is not None:
                    runtime = HP.wrapDict(last_aired).get('runtime')

                if runtime is not None:
                    meta.update({'duration': runtime})
                elif 'duration' in itemMeta:
                    meta.update({'duration': itemMeta.get('duration')})
            except: pass

            try:
                _ppath = details.get('poster_path', '')
                if _ppath and _ppath != '':
                    poster = TMDBApi.__IMG_LINK % ('500', _ppath)
                else:
                    poster = PH.DEFAULT_TV_POSTER
                    #_imdbPoster = itemMeta.get('poster', '0')
            except:
                poster = '0'
            meta.update({'poster': poster})

            try:
                _fpath = details.get('backdrop_path', '')
                fanart = TMDBApi.__IMG_LINK % ('1280', _fpath) if _fpath and _fpath != '' else '0'
            except:
                fanart = '0'
            meta.update({'fanart': fanart})

            try: year = re.findall('(\d{4})', meta.get('premiered'))[0]
            except: year = '0'
            meta.update({'year': year})

            try: studio = details.get('networks', [{}])[0].get('name', '0')
            except: studio = '0'
            meta.update({'studio': studio})

            try:
                genres = details.get('genres', [])
                genres = [HP.wrapDict(g).get('name') for g in genres]
                genres = ' / '.join(genres)
            except:
                genres = '0'
            meta.update({'genre': genres})
            
            try:
                castWithThumb = []
                cast = details['credits']['cast'][:30]
                for person in cast:
                    try:
                        person = HP.wrapDict(person)
                        _cpath = person.get('profile_path', '').strip()
                        thumb = TMDBApi.__IMG_LINK % ('185', _cpath) if _cpath and _cpath != '' else ''
                        name = person.get('name')
                        role = person.get('character')
                        castWithThumb.append({
                            'name': name,
                            'role': role,
                            'thumbnail': thumb
                        })
                    except: pass
                if castWithThumb == []:
                    castWithThumb = '0'
            except:
                castWithThumb = '0'
            meta.update({'castwiththumb': castWithThumb})

            try:
                crew = HP.wrapList(details['credits']['crew'])
                director = ', '.join([d['name'] for d in [x for x in crew if x['job'] == 'Director']])
                writer = ', '.join([w['name'] for w in [y for y in crew if y['job'] in ['Writer', 'Screenplay', 'Author', 'Novel']]])
            except:
                director = writer = '0'
            meta.update({'director': director})
            meta.update({'writer': writer})

            # filter out empty values
            meta = dict((k,v) for k,v in meta.items() if v != '0')
            return meta
        except Exception as e:
            if H.DEBUG:
                msg = str(e) + f" for imdb:{imdb_id}, tmdb:{tmdb_id}"
                H.logwarn(msg)
            return None
    # end of getTVShowDetails() function

    @staticmethod
    def __apiRequest(url:str) -> dict:
        try:
            request = requests.get(url)
            response = request.json()
            request.close()
            return dict(response)
        except Exception as e:
            try:
                request.close()
            except:
                pass
            if H.DEBUG:
                H.logerror(e)
            return {}
    # end of __apiRequest() function

    @staticmethod
    def __getTmdbFromImdb(imdb_id:str, type:str) -> str:
        """
        @param imdb_id: str
        @param type: str = 'movie', 'tv', 'person', 'tv_season' or 'tv_episode'
        @returns str or throws exception
        """
        urlFind = TMDBApi.__URL_FIND_IMDB % str(imdb_id)
        response = TMDBApi.__apiRequest(urlFind)
        
        resultsField = type + "_results"

        if resultsField not in response:
            raise Exception("TMDBApi.__getTmdbFromImdb(): could not find [%s]" % resultsField)
        results = HP.wrapList(response.get(resultsField))
        
        if len(results) < 1:
            raise Exception("TMDBApi.__getTmdbFromImdb(): [%s] empty" % resultsField)
        result = HP.wrapDict(results[0])
        if "id" not in result:
            raise Exception("TMDBApi.__getTmdbFromImdb(): id does not exist in [%s]" % resultsField)

        return result.get('id')
    # end of __getTmdbFromImdb() function
        
    @staticmethod
    def __ifDetailUpdateMeta(details:dict, meta:dict, dKey:str, mKey:str):
        if dKey in details:
            meta.update({mKey: details.get(dKey)})
        else:
            meta.update({mKey: '0'})

    @staticmethod
    def __logd(self, msg:str):
        if H.DEBUG:
            H.log("TMDBApi(): " + repr(msg))


# end of TMDBApi class