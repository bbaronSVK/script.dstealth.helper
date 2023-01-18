##############################

import re
import requests

from bs4 import BeautifulSoup, Tag

import scripts.helper as H

##############################

class IMDBFilters:
    """
    Primary Language:
        - Any:                          None
        - <list others>:                &primary_language={lang}
       
    Lists:
        - Any:                          None
        - Top <val>:                    &groups=top_{val}

    Genres:
        - Any:                          None
        - <list genres>:                &genres={genre}

    Release Date:
        - All time:                     None
        - Date Range:                   &release_date=date[{fr}],date[{to}]

    Number of Votes:
        - Any or no votes:              None
        - <val>+ votes:                 &num_votes={val}

    Sort By:
        - Popularity, highest first:    &sort=moviemeter,asc
        - Popularity, lowest first:     &sort=moviemeter,desc
        - Release Date, descending:     &sort=release_date,desc
        - Release Date, ascending:      &sort=release_date,asc
        - User Rating, highest first:   &sort=user_rating,desc
        - User Rating, lowest first:    &sort=user_rating,asc  
    """

    F_LANG = 'lang'
    FMT_LANG = '&primary_language=%s'
    LangDict = {
        'en': 32511,
        'yue': 32512,
        'fr': 32513,
        'de': 32514,
        'hi': 32515,
        'it': 32516,
        'ja': 32517,
        'ko': 32518,
        'cmn': 32519,
        'pa': 32520,
        'ru': 32521,
        'es': 32522
    }

    F_LIST = 'list'
    FMT_LIST = '&groups=%s'
    ListsDict = {
        "top_100": 32591,
        "top_250": 32592,
        "top_1000": 32593
    }

    F_GENRE = 'genre'
    FMT_GENRE = '&genres=%s'
    GenreDict = {
        "action": 32531,
        "adventure": 32532,
        "animation": 32533,
        "biography": 32534,
        "comedy": 32535,
        "crime": 32536,
        "documentary": 32537,
        "drama": 32538,
        "family": 32539,
        "fantasy": 32540,
        "film-noir": 32541,
        "game-show": 32542,
        "history": 32543,
        "horror": 32544,
        "music": 32545,
        "musical": 32546,
        "mystery": 32547,
        "news": 32548,
        "reality-tv": 32549,
        "romance": 32550,
        "sci-fi": 32551,
        "sport": 32552,
        "talk-show": 32553,
        "thriller": 32554,
        "war": 32555,
        "western": 32556
    }

    F_RELEASE = 'release'
    FMT_RELEASE = '&release_date=%s'
    ReleaseDict = {
        "date[-365],date[0]": 32561,
        "date[-365],date[-60]": 32562,
        "date[-182],date[0]": 32566,
        "date[-60],date[0]": 32563,
        "date[-30],date[0]": 32564,
        "date[1],": 32565
    }

    F_VOTES = 'votes'
    FMT_VOTES = '&num_votes=%s,'
    VotesArr = [1000, 750, 500, 250, 100, 1]

    F_SORTBY = 'sortby'
    FMT_SORTBY = '&sort=%s'
    SortDict = {
        "moviemeter,asc": 32581,
        "moviemeter,desc": 32582,
        "release_date,desc": 32583,
        "release_date,asc": 32584,
        "user_rating,desc": 32585,
        "user_rating,asc": 32586
    }

# end of IMDBFilters class

class IMDBParser:
    URL_MOV_THEATRES = "https://www.imdb.com/showtimes/location?ref_=inth_ov_sh_sm"
    URL_MOV_FILTER   = "https://www.imdb.com/search/title/?count={count}&start={start}&view=advanced&title_type=feature,tv_movie,tv_special"
    URL_TVS_AIRING   = "https://www.imdb.com/search/title/?count={count}&start={start}&view=advanced&title_type=tv_episode"
    URL_TVS_FILTER   = "https://www.imdb.com/search/title/?count={count}&start={start}&view=advanced&title_type=tv_series,tv_miniseries"

    # list of different user agents: https://www.useragentstring.com/pages/useragentstring.php
    # Chrome 104 User-Agent:
    __user_agent = 'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'

    @staticmethod
    def parseUrlContents(url):
        """ Attempts to parse the given URL and returns a list of parsed items [dict] or empty list []. """
        try:
            if H.DEBUG:
                H.log("imdb.parseUrlContents(%s)" % repr(url))

            # PART 1: Get HTML Data
            html = IMDBParser.__getHTML(url)

            # PART 2: Parse DOM
            return IMDBParser.__parseDOM(html)

        except Exception as e:
            if H.DEBUG:
                H.logerror(e)
        
        return []
    # end of parseUrlContents method

    @staticmethod
    def __getHTML(url:str) -> str:
        """
        Attemps to GET html from url. Returns str if successfull otherwise empty str.
        """
        try:
            # spoof that we're a web-browser
            header = {'User-Agent': IMDBParser.__user_agent}
            # send the request, not going to pass headers as it causes imdb to error
            request = requests.get(url, headers=header)
            response = request.text
            request.close()
            return response
        except Exception as e:
            if H.DEBUG:
                H.logerror(e)
            return ''
    # end of __getHTML method
    
    @staticmethod
    def __parseDOM(html):
        # Using python BeautifulSoup v4: https://tedboy.github.io/bs4_doc/generated/bs4.html
        soup = BeautifulSoup(html, "html.parser")
        listitems = soup.find_all("div", attrs={'class': 'lister-item'})

        created = 0
        errored = 0
        errors = []
        createdItems = []
        for li in listitems:
            try:
                if isinstance(li, Tag):
                    # set none-existant's to '0' so we can filter them out in the controller calls

                    img = li.find('img')
                    
                    try:
                        _h3 = li.find('h3', {'class': 'lister-item-header'})
                        _a = _h3.find('a', href=True)
                        _href = _a['href']
                        title = _a.text.strip()
                        imdbID = 'tt' + str(re.compile('tt(\d*)\/').findall(_href)[0])
                    except:
                        title = img['alt']
                        imdbID = img['data-tconst']
                        imdbID = 'tt' + str(re.compile('tt(\d*)').findall(imdbID)[0])

                    try:
                        poster = img['loadlate'] # src is replaced with loadlate
                        if poster == 'https://m.media-amazon.com/images/S/sash/NapCxx-VwSOJtCZ.png':
                            # default "no poster" image
                            raise Exception()
                    except:
                        poster = '0'

                    try:
                        year = li.find('span', {'class': 'lister-item-year'}).text
                        year = re.compile('(\d{4})').findall(year)[0]
                    except:
                        year = '0'

                    genres = li.find('span', {'class': 'genre'}).text.strip()
                    genres = ' / '.join([i.strip() for i in genres.split(',')])

                    try:
                        duration = li.find('span', {'class': 'runtime'}).text
                        duration = re.findall('(\d+?) min(?:s|)', duration)[-1]
                        duration = str(int(duration)) # make sure it's a number before saving as string
                    except:
                        duration = '0'

                    rating = li.find('div', {'class': 'ratings-imdb-rating'})
                    if rating is None or rating == '' or rating == '-':
                        rating = '0'
                    else:
                        rating = rating['data-value']

                    try:
                        votes = li.find('div', {'class': 'rating-list'})
                        votes = re.findall('\((.+?) vote(?:s|)\)', votes['title'])[0]
                    except:
                        votes = '0'
                    if votes == '':
                        votes = '0'

                    try:
                        mpaa = li.find('span', {'class': 'certificate'}).text
                        mpaa = mpaa.replace('_', '-')
                    except:
                        mpaa = '0'

                    try:
                        allp = li.find_all('p')
                        director = []
                        cast = None
                        for p in allp:
                            if "Director" in p.text:
                                cast = p
                                for child in p.findChildren():
                                    # get all the names from anchors until not an anchor anymore
                                    if child.name != 'a':
                                        break
                                    director.append(str(child.text).strip())
                            if cast is not None: break
                    except:
                        director = []
                    director = ' / '.join(director)
                    if director == '': director = '0'

                    try:
                        actors = []
                        start = False
                        for child in cast.findChildren():
                            if start:
                                actors.append(str(child.text).strip())
                            if child.name == 'span':
                                start = True
                    except:
                        actors = []
                    if actors == []: actors = '0'

                    # no reliable way to get the plot, tagline, tvdb

                    item = {'title':title, 'originaltitle':title, 'year':year, 'genre':genres, 'duration':duration,
                            'rating':rating, 'votes':votes, 'mpaa':mpaa, 'director':director, 'cast':actors,
                            'plot':'', 'tagline':'', 'imdb':imdbID, 'tvdb':'', 'poster':poster}
                    createdItems.append(item)
                    created += 1
            except Exception as e:
                errored += 1
                errors.append(str(e))
                pass

        if H.DEBUG:
            H.log(f"IMDBParser: Created {created} parsed items.")
            H.log(f"IMDBParser: {errored} errors encountered.")
            for e in errors:
                H.logerror(e)
        return createdItems
    # end of __parseDOM method

# end of IMDBParser class