# TODO movies.py
#  Searches for movies based on name through command.
#  User can choose to filter out specific qualities.
#  Shows amount of seeds per torrent.
#  Returns list of movies for the command.cog to shift through.
#  Sends API requests to website to allow room creation.
#  Generates a key for a user to authenticate room ownership.
#  Sends an optional password key in case the user wants room auth.
# NEVERMIND: Does NOT send direct torrents or URI (to not break Discord ToS). Was told this does not break ToS.

# TODO
#  Function: get_movies(searchBy='Title of Movie',quality='720p',minimum_rating='0',genre=None)
import requests


class MovieHandler:
    endpoint = "https://yts.mx/api/v2/list_movies.json"

    def __init__(self, name, quality):
        self.name = name
        self.quality = quality
        self.movies = {}
        self.load_movies()
        return

    def load_movies(self):
        res = requests.get(self.endpoint, params={'query_term': self.name, 'quality': self.quality, 'limit': 50,
                                                  'sort_by': 'seeds', 'with_rt_ratings': True}).json()
        if res['data']['movie_count'] > 0:
            self.movies = res['data']['movies']
            print(*self.movies)
        return

    def get(self, index=None):
        if index is None:
            return self.movies
        else:
            return self.movies[index]

    def has_quality(self, index, quality):
        has_flag = False
        for torrent in self.movies[index]['torrents']:
            if torrent['quality'] == quality:
                has_flag = True
                break
        return has_flag

    def set_quality(self, quality):
        self.quality = quality

    def get_quality(self):
        return self.quality

    def get_uri(self, index):
        for torrent in self.movies[index]['torrents']:
            if torrent['quality'] == self.quality or self.quality == 'All':
                return f"magnet:?xt=urn:btih:{torrent['hash']}"

    def count(self):
        return len(self.movies)
