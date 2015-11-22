from vk import *
import eventlet
import sys


def main():
    ## todo: use argparse, Luke!
    if len(sys.argv) < 4:
        print("usage ./%s group offset count" % sys.argv[0])
        sys.exit(1)

    group = sys.argv[1]
    offset = int(sys.argv[2])
    count = int(sys.argv[3])

    print('init...')
    vk = Parser(app_id='', client_key='')
    vk.set_group_name(group)

    print('parse audios...')
    audios = vk.get_audio(count=count, offset=offset)

    print('start downloading...')
    pool = eventlet.GreenPool(25)
    for name, info in pool.imap(download, audios):
        print('%s OK.' % name)


main()