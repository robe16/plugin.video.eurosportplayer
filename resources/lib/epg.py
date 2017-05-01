from resources.lib.items import Items
import datetime
import ast
from resources.lib.common import *
import resources.lib.simple_requests as requests
from resources.lib.bs4 import BeautifulSoup

items = Items()

ESLISTINGS_URL = "http://uk.eurosportplayer.com/tvschedule.xml"

def listings():
    #
    try:
        #
        listings = getListing()
        #
        if listings:
            soup = BeautifulSoup(listings, 'html.parser')
            #
            li_all = soup.findAll("li", {"class": "tvschedule-main__right-program"})
            #
            proglist = {}
            #
            for li in li_all:
                #
                dateformat = '%Y-%m-%dT%H:%M:%S'
                dt_start = datetime.datetime.strptime(li.attrs['data-startdate'], dateformat)
                dt_end = datetime.datetime.strptime(li.attrs['data-enddate'], dateformat)
                #
                if dt_start >= datetime.datetime.now() or dt_end >= datetime.datetime.now():
                    #
                    if not 'no-prog' in li.attrs['class']:
                        #
                        data_prog = li.attrs['data-prg']
                        data_prog = ast.literal_eval(data_prog)
                        #
                        channel_id = data_prog['channelid']
                        title_full = data_prog['sporteventname']
                        title_short = data_prog['shortname']
                        desc = data_prog['description']
                        img = data_prog['data-channelimg']
                        #

                        if data_prog['transmissiontype'] == '1':
                            live = ' [COLOR red]LIVE[/COLOR]'
                        else:
                            live = ''
                        #
                        dict_key = '{start_time}_{channel_id}'.format(start_time=dt_start.strftime('%Y-%m-%d_%H:%M'),
                                                                      channel_id=channel_id)
                        #
                        proglist[dict_key] = {'channel_id': channel_id,
                                              'title_full': title_full,
                                              'title_short': title_short,
                                              'desc': desc,
                                              'live': live,
                                              'img': img,
                                              'dt_start': dt_start,
                                              'dt_end': dt_end}
                        #
            for key in sorted(proglist.iterkeys()):
                #
                if proglist[key]['dt_start'] <= datetime.datetime.now() and proglist[key]['dt_end'] >= datetime.datetime.now():
                    datetime_lbl = 'NOW'
                else:
                    if proglist[key]['dt_start'].date() == datetime.datetime.now().date():
                        start_date = 'Today'
                    elif  proglist[key]['dt_start'].date() == (datetime.datetime.now() + datetime.timedelta(days=1)).date():
                        start_date = 'Tomorrow'
                    else:
                        start_date = proglist[key]['dt_start'].strftime("%d-%m"),
                    #
                    datetime_lbl = '{start_date} {start_time}'.format(start_date=start_date,
                                                                      start_time=proglist[key]['dt_start'].strftime("%H:%M"))
                #
                duration = (proglist[key]['dt_end'] - proglist[key]['dt_start']) // datetime.timedelta(minutes=1)
                #
                item_label = '{datetime_lbl}{live} {title} [{duration} mins]'.format(datetime_lbl=datetime_lbl,
                                                                                live=proglist[key]['live'],
                                                                                title=proglist[key]['title_full'],
                                                                                duration=duration)
                #
                items.add({'mode': '#', 'title': item_label, 'thumb': proglist[key]['img']})
        #
        items.list()
        #
    except Exception as e:
        log('Eurosportplayer: ERROR attempting to retrieve and present tv schedule - {error}'.format(error=e))

def getListing():
    #
    r = requests.get(ESLISTINGS_URL)
    #
    if r.status_code == 200:
        return r.text
    else:
        log('Eurosportplayer: ERROR attempting to retrieve - status code {code} returned'.format(code=r.status_code))
        return False