__author__ = 'weirded'

import json
import urllib2

# set your params here
app_id = ""
keyword = ""
group_name = ""

api_url = 'https://api.vk.com/method/'

def get_access_token(app_id, keyword):
    auth_url = 'https://oauth.vk.com/access_token?' + \
               'client_id=' + app_id + \
               '&client_secret=' + keyword + \
               '&grant_type=client_credentials'
    return json.loads(urllib2.urlopen(auth_url).read())['access_token']


def group_get_by_id(group_name):
    url = api_url + 'groups.getById?' + \
          'gid=' + group_name
    response = urllib2.urlopen(url)
    return json.loads(response.read())['response'][0]['gid']


def wall_get(group_id):
    owner_id = str(-group_id)
    #TODO:  count 100 while count etc
    count = '100'
    filter = 'owner'
    url = api_url + 'wall.get?' + \
          '&owner_id=' + owner_id + \
          '&count=' + count + \
          '&filter=' + filter
    response = urllib2.urlopen(url).read()
    json_resp = json.loads(response)
    return json_resp['response']


def print_audio_attachment(attachment):
    performer = attachment['performer']
    title = attachment['title']

    # url = attachment['url']
    url = attachment['url'].split('?', 1)[0]
    print performer + ' - ' + title + ' | ' + url


def archive_name(artists, text):
    if len(artists) > 1:
        print text.replace('#[a-z]*', '') + '.tar.gz'
    else:
        print artists[0].replace(' ', '_') + '.tar.gz'


def print_message(message):
    if 'attachments' in message:
        have_audio = 0
        attachments = message['attachments']

        for i in range(0, len(attachments)):
            if 'audio' in attachments[i]:
                have_audio = 1
                break

        if have_audio != 1:
            return

        artists = []
        print '# ' + str(message['id']) + ": " + message['text']
        for i in range(0, len(attachments)):
            if 'audio' in attachments[i]:
                print_audio_attachment(attachments[i]['audio'])
                performer = attachments[i]['audio']['performer'].lower()
                if performer not in artists:
                    artists.append(performer)
        archive_name(artists, message['text'])
        print


def print_wall(wall):
    for i in range(1, 100):
        message = wall[i]
        print_message(message)


def main():
    access_token = get_access_token(app_id, keyword)
    group_id = group_get_by_id(group_name)
    wall = wall_get(group_id)
    print_wall(wall)


main()
