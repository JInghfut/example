#coding=utf-8
import time

from mongoengine.connection import disconnect

from models import Artist, Song, Comment, User, Process
from app import create_app

from spider.utils import get_user_agent, get_tree, post

DISCOVER_URL = 'http://music.163.com/discover/artist/cat?id={}&initial={}'
ARTIST_URL = 'http://music.163.com/artist?id={}'
SONG_URL = 'http://music.163.com/song?id={}'
COMMENTS_URL = 'http://music.163.com/weapi/v1/resource/comments/R_SO_4_{}'  # noqa


def parser_artist_list(cat_id, initial_id):
    tree = get_tree(DISCOVER_URL.format(cat_id, initial_id))
    artist_items = tree.xpath('//a[contains(@class, "nm-icn")]/@href')

    return [item.split('=')[1] for item in artist_items]

#get aritist list

def unprocess_artist_list():
    create_app()
    unprocess = Process.objects.filter(status=Process.PENDING)
    unprocess_list=[p.id for p in unprocess]
    return unprocess_list


def parser_artist(artist_id):
    create_app()
    process = Process.get_or_create(id=artist_id)
    if process.is_success:
        print "find process artist finished ,return"
        return

    print 'Starting fetch artist: {}'.format(artist_id)
    start = time.time()
    process = Process.get_or_create(id=artist_id)

    tree = get_tree(ARTIST_URL.format(artist_id)) #get artist url
    if tree==None:
        print "fetch artist url get none,return !"
        return

    artist = Artist.objects.filter(id=artist_id)
    if not artist:
        print "create artist "+str(artist_id)
        artist_name = tree.xpath('//h2[@id="artist-name"]/text()')[0]
        picture = tree.xpath(
            '//div[contains(@class, "n-artist")]//img/@src')[0]
        artist = Artist(id=artist_id, name=artist_name, picture=picture)

        artist.save()

    else:
        artist = artist[0]
        print "artist exist " + str(artist_id)
    print "fetching all song comments"
    song_items = tree.xpath('//div[@id="artist-top50"]//ul/li/a/@href')
    #song_items2=tree.xpath('//ul[@class="f-hide"]/li/a/@href') the same
    songs = []
    print song_items
    if song_items==[]:
        print "Artist  get no songs ,return fetch artist {}".format(artist_id)
        return
    for item in song_items:
        song_id = item.split('=')[1]
        song = parser_song(song_id, artist)
        if song is  None:
            print "parse song failed,return "
            return
        else:
            songs.append(song)
    artist.songs = songs
    artist.save()
    process.make_succeed()
    print 'Finished fetch artist: {} Cost: {}'.format(
        artist_id, time.time() - start)


def parser_song(song_id, artist):
    tree = get_tree(SONG_URL.format(song_id))
    if tree==None:
        print "fetch song url get none,return !"
        return
    song = Song.objects.filter(id=song_id)
    r= post(COMMENTS_URL.format(song_id),song_id)
    data=r.json()
    print 'get comment ok '+str(song_id)
    print str(data['code']) + str(song_id)
    if data['code'] != 200:
        print "fetch comment get cheating " + str(data['code']) + " program stop"
        return
    if not song:  #如果是新歌
        for404 = tree.xpath('//div[@class="n-for404"]')
        if for404:
            print "404 found"
            return

        try:
            song_name = tree.xpath('//em[@class="f-ff2"]/text()')[0].strip()
        except IndexError:
            try:
                song_name = tree.xpath(
                    '//meta[@name="keywords"]/@content')[0].strip()
            except IndexError:
                print 'Fetch limit!'
                time.sleep(10)
                return parser_song(song_id, artist)
        song = Song(id=song_id, name=song_name, artist=artist,
                    comment_count=data['total'])
        song.save()
    else:
        song = song[0]  #如果歌曲已存在
    comments = []

    for comment_ in data['hotComments']:
        comment_id = comment_['commentId']
        content = comment_['content']
        like_count = comment_['likedCount']
        user = comment_['user']
        if not user:
            continue
        user = User.get_or_create(id=user['userId'], name=user['nickname'],
                                  picture=user['avatarUrl'])
        comment = Comment.get_or_create(id=comment_id, content=content,
                                        like_count=like_count, user=user,
                                        song=song)
        comment.save()
        comments.append(comment)
    song.comments = comments
    song.save()
    print "song comments finish"
    time.sleep(0.5)
    return song
