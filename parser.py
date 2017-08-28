#! python3
# -*- coding: utf-8 -*-

import sys
from bs4 import BeautifulSoup as soup
from urllib.request import urlopen
import re
import codecs
import requests

def get_tags(game_url):

    """Returns full list of tags for the given game's steam page url"""

    tags_soup = soup(urlopen(tags_url).read(), "html.parser")
    tags_html = tags_soup.findAll("a",{"class":"app_tag"})
    tags = []
    for tag in tags_html:
        tags.append(tag.text.strip())
    return tags

def get_profileinfo(profile_url):

    """Returns list of game info in the form of dictionaries:
        {'appid',
        'name',
        'last_played',
        'hours_forever'}"""

    profile_soup = soup(urlopen(profile_url).read(), "html.parser")
    js_text = profile_soup.findAll('script', language="javascript")[0].text

    # basic info:
    basic_regex = re.compile(r'"appid":(\d+),"name":"(.+?)"',re.MULTILINE)
    basic_info = re.findall(basic_regex, js_text)

    # change to dictionary with appid as keys and dictionaries for game info
    basic_info = dict([(a,{'appid':a, 'name':b, 'last_played':'None', 'total_hours':'None'}) for (a,b) in basic_info])

    # searching for optional info:
    totalhours_regex = re.compile(r'"appid":(\d+),.+?,"hours_forever":"(\d+\.\d+)"', re.MULTILINE)
    totalhours_info = re.findall(totalhours_regex, js_text)
    lastplayed_regex = re.compile(r'"appid":(\d+),.+?,"last_played":(\d+)', re.MULTILINE)
    lastplayed_info = re.findall(lastplayed_regex, js_text)
    
    # adding optional info where possible
    for total_hours, last_played in zip(totalhours_info, lastplayed_info):
        if total_hours[0] in basic_info.keys():
            basic_info[total_hours[0]]['total_hours'] = total_hours[1]
        if last_played[0] in basic_info.keys():
            basic_info[last_played[0]]['last_played'] = last_played[1]

    return basic_info.values()

def save_gameurls(game_info, filename):

    """ Saves user's game data from get_gameurls() to .csv """

    if filename[-4:] != '.csv':
        filename = filename+'.csv'

    with codecs.open(filename, 'w+', 'utf-8') as f:
        f.write('appid,name,last_played,total_hours'+'\r\n')
        for entry in game_info:
            f.write(entry['appid']+',"'+entry['name']+'",'+entry['last_played']+','+entry['total_hours']+'\r\n')

def main():
    # Debugging stuff
    games = get_profileinfo(sys.argv[1])
    print(games)
    save_gameurls(games, 'test2.csv')

if __name__ == "__main__":
    main()
