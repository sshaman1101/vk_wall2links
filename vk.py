import json
import urllib2
import eyed3
from eventlet.green import urllib


class Parser():
    app_id = ''
    client_key = ''
    api_url = 'https://api.vk.com/method/'
    token = ''
    group_id = None
    group_name = ''

    def __init__(self, app_id, client_key, group_name=''):
        self.app_id = app_id
        self.client_key = client_key

        self.token = self._check_credentials()

        if group_name != '':
            self.group_id, self.group_name = self._get_group_id_by_name(group_name)

    def _check_credentials(self):
        """ gets vk access token """
        auth_url = 'https://oauth.vk.com/access_token?' + \
                   'client_id=' + self.app_id + \
                   '&client_secret=' + self.client_key + \
                   '&grant_type=client_credentials'

        # todo: raise exception if app or client keys is wrong.
        return json.loads(urllib2.urlopen(auth_url).read())['access_token']

    def _get_group_id_by_name(self, group_name):
        """ method converts group name to ID and name """
        url = self.api_url + 'groups.getById?' + \
              'gid=' + group_name
        response = urllib2.urlopen(url)
        response_data = json.loads(response.read())['response'][0]

        gid = response_data['gid']
        name = response_data['name']

        return str(-gid), name

    def _get_wall_messages(self, count=100, offset=0):
        """ downloads messages from wall with given count and offset """
        if count < 1 or count > 100:
            count = 100

        if self.group_id is None or self.group_id == "":
            raise Exception("Set group name first!")

        filter = 'owner'

        url = self.api_url + 'wall.get?' + \
              '&owner_id=' + self.group_id + \
              '&count=' + str(count) + \
              '&offset=' + str(offset) + \
              '&filter=' + filter

        response = urllib2.urlopen(url).read()
        json_resp = json.loads(response)
        return json_resp['response']

    def _format_audio(self, attachment):
        """
            format audio attachment as dict like
            {'artist': performer, 'title': title, 'url': url}
        """
        performer = attachment['performer'].replace('/', '_').replace('\\', '_')
        title = attachment['title'].replace('/', '_').replace('\\', '_')
        url = attachment['url'].split('?', 1)[0]

        return {'artist': performer, 'title': title, 'url': url, 'album': self.group_name}

    def _parse_message(self, message):
        """
            Get wall message, extract audio attachments, format them
            according to self._format_audio() and return as array.
        """
        audio = []
        if 'attachments' in message:
            have_audio = False
            attachments = message['attachments']

            for i in range(0, len(attachments)):
                if 'audio' in attachments[i]:
                    have_audio = True
                    break

            if have_audio:
                for i in range(0, len(attachments)):
                    if 'audio' in attachments[i]:
                        audio.append(self._format_audio(attachments[i]['audio']))

        return audio

    def _get_wall_count(self):
        """ Returns total records count from wall """
        url = self.api_url + 'wall.get?' + \
              '&owner_id=' + self.group_id + \
              '&count=1' + \
              '&offset=0' + \
              '&filter=' + 'owner'

        response = urllib2.urlopen(url).read()
        json_resp = json.loads(response)
        count = json_resp['response'][0]

        return int(count)

    def set_group_name(self, name):
        """
            Gets group name and loads its ID and name via vk api """
        self.group_id, self.group_name = self._get_group_id_by_name(name)

    def get_audio(self, count, offset):
        """
            Loads wall messages with given count and offset and
            turns them into array of dicts (not dicks!)
        """
        audios = []
        wall = self._get_wall_messages(count=count, offset=offset)

        for i in range(1, len(wall)):
            message = wall[i]
            audios += self._parse_message(message)

        return audios

    def get_all(self):
        """
        Load all audios presented on a wall using
        _get_wall_count() and get_audio() methods
        """

        total = self._get_wall_count()
        all = []

        if total < 1:
            return []

        for i in range(0, total, 100):
            all += self.get_audio(count=100, offset=i)

        return all


def download(info):
    ## todo: get download path as param
    try:
        name = "./dl/%s - %s.mp3" % (info['artist'], info['title'])
        urllib.urlretrieve(info['url'], name)
        # set_tags(name, info)
        return name, info
    except Exception as e:
        print("Some goes wrong ( ._.) %s" % e.message)
        return None, None


def set_tags(path, info):
    ## todo: do smth with crashes
    mp3 = eyed3.load(path)
    mp3.tag.artist = info['artist']
    # mp3.tag.album = info['album']
    mp3.tag.title = info['title']
    mp3.tag.save()
