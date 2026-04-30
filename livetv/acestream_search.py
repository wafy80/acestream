import json
from itertools import count
from datetime import datetime, timedelta
import argparse
import os
import lxml.etree as ET
import time
from requests import get
from unidecode import unidecode
import cust.cust as c

# workaround for python2 vs python3 compatibility
from urllib.request import urlopen, quote

__version__ = 'v1.0.1'

show_epg = 1
group_by_channels = 1

# define default time slot for updated availability
def default_after(delta):
    age = timedelta(hours=delta)
    now = datetime.now()
    return datetime.strftime(now - age, '%Y-%m-%d %H:%M:%S')

def default_zone():
    return time.strftime('%z (%Z)')[0:5]

# transform date time to timestamp
def time_point(point):
    epoch = '1970-01-01 00:00:00'
    isof = '%Y-%m-%d %H:%M:%S'
    epoch = datetime.strptime(epoch, isof)
    try:
        point = datetime.strptime(point, isof)
    except ValueError:
        print("Use 'Y-m-d H:M:S' date time format, for example \'" +
              datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S') +
              '\'')
        exit()
    else:
        return int((point - epoch).total_seconds())


# get command line options with all defaults set
def get_options(args={}):

    parser = argparse.ArgumentParser(
        description='Produce acestream m3u playlist, xml epg or json data.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog=args.get('prog', None)
    )

    parser.add_argument(
        'query',
        nargs='?',
        type=str,
        default='',
        help='Pattern to search tv channels.'
    )
    parser.add_argument(
        '-n', '--name',
        nargs='+',
        type=str,
        help="Exact tv channels to search for, doesn't effect json output."
    )
    parser.add_argument(
        '-c', '--category',
        type=str,
        default='',
        help='filter by category.'
    )
    parser.add_argument(
        '-p', '--proxy',
        type=str,
        default=f"{os.getenv('ACE_ENGINE','127.0.0.1')}:{os.getenv('ACE_PORT','6878')}",
        help='proxy host:port to conntect to engine api.'
    )
    parser.add_argument(
        '-t', '--target',
        type=str,
        default='localhost:6878',
        help='target host:port to conntect to engine hls.'
    )
    parser.add_argument(
        '-s', '--page_size',
        type=int, default=2000,
        help='page size.'
    )
    parser.add_argument(
        '-j', '--json',
        action='store_true',
        help='json output.'
    )
    parser.add_argument(
        '-x', '--xml_epg',
        action='store_true',
        help='make XML EPG.'
    )
    parser.add_argument(
        '-d', '--debug',
        action='store_true',
        help='debug mode.'
    )
    parser.add_argument(
        '-u', '--url',
        action='store_true',
        help='output single bare url of the stream instead of playlist'
    )
    parser.add_argument(
        '-a', '--after',
        type=float,
        default=0,
        help='availability updated at (n. previous hours) '
    )
    parser.add_argument(
        '-V', '--version',
        action='version',
        version='%(prog)s {0}'.format(__version__),
        help='Show version number and exit.'
    )
    parser.add_argument(
        '-z', '--zone',
        type=str,
        default=default_zone(),
        help='timezone shift.'
    )
    parser.add_argument(
        '-m', '--hls',
        action='store_true',
        help='get HLS stream.'
    )
    parser.add_argument(
        '-A', '--api_version',
        type=str, default='1',
        help='api version.'
    )    
    if __name__ == '__main__':
        opts = parser.parse_args()
    else:
        opts = parser.parse_known_args()[0]
    opts.__dict__.update(args)
    if opts.after > 0:
        opts.after = time_point(default_after(float(opts.after) + float(opts.zone[0:3])))
    if 'help' in args:
        opts.help = parser.format_help()
    if 'usage' in args:
        opts.usage = parser.format_usage()
    if not check_proxy('http://' + opts.proxy + '/webui/api/service?method=get_version'):
        opts.proxy='api.acestream.me'
        opts.api_version='4'
    return opts


# api url
def endpoint(args):
    return 'http://' + args.proxy + '/search'


# build request to api with all options set
def build_query(args, page):
    return 'page=' + str(page) + \
           '&query=' + quote(args.query) + \
           '&category=' + quote(args.category) + \
           '&page_size=' + str(args.page_size) + \
           '&group_by_channels=' + str(group_by_channels) + \
           '&show_epg=' + str(show_epg) + \
           '&api_version=' + args.api_version + '&api_key=test_api_key' 


# fetch one page with json data
def fetch_page(args, query):
    url = endpoint(args) + '?' + query
    return json.loads(urlopen(url).read().decode('utf8'))

def check_proxy(url):
    try:
        result = json.loads(urlopen(url).read().decode('utf8'))
        if 'error' in result:
            if result['error'] == None:
                return True
    except:
        return False

# compose m3u playlist from json data and options
def make_playlist(args, counter, group):
    if len(group['items']) > 0:
        if group['items'][0]['availability_updated_at'] >= args.after \
                and (not args.name or group['name'].strip() in args.name): 
            categories = ''
            if 'categories' in group['items'][0]:            
                for kind in group['items'][0]['categories']:
                    if kind == '': kind = 'Other'
                    categories += kind + ';'                           
                categories = unidecode(categories[:-1]).title()
            if categories == '': categories = 'Other'
            title = '#EXTINF:-1'        
            chid = group['items'][0]['infohash'][:10]            
            if show_epg:
                if args.api_version == '4': 
                    if 'channel_id' in group:
                        chid = str(group['channel_id']) 
                else:        
                    if 'channel_id' in group['items'][0]:
                        chid = str(group['items'][0]['channel_id'])
            tmpcat = c.get_cat(unidecode(str(group['name'])))
            if tmpcat != "":
                categories = tmpcat
            order = counter
            iscust = False        
            tmpchid = c.trascochid(unidecode(str(group['name'])))
            if tmpchid:
                channel_id, order = tmpchid
                chid = channel_id
                iscust = True
            title += ' tvg-id="' + chid + '"'               
            title += ' tvg-chno="' + str(order) + '"'    
            title += ' group-title="' + categories + '"'
            if not iscust:
                if 'icons' in group:
                    title += ' tvg-logo="' + group['icons'][0]['url'] + '"'
                else:
                    title += ' tvg-logo="https://placehold.co/100/lightgray/black.png?font=source-sans-pro&text=' + unidecode(str(group['name'])).replace(" ","\\n") + '"'        
            title += ',"' 
            if iscust:
                title += '.' + str(order) + '. ' 
            title += unidecode(str(group['name'])) + '"'
            if args.debug:
                title += ' [' + categories + ' ]'            
                dt = datetime.fromtimestamp(group['items'][0]['availability_updated_at'])
                title += ' ' + dt.isoformat(sep=' ')
                title += ' a=' + str(group['items'][0]['availability']) 
                if 'bitrate' in group['items'][0]:
                    title += " b=" + str(group['items'][0]['bitrate'])
            if args.hls:
                stream_type = 'manifest.m3u8'
            else:
                stream_type = 'getstream'
            if args.url:
                return ('http://' + args.target + '/ace/' + stream_type + '?id=' +
                        get_content_id(args,group['items'][0]['infohash']))
            else:
                return (title + '\n' +
                        'http://' + args.target + '/ace/' + stream_type + '?id=' + group['items'][0]['infohash']) + '\n'
                        #get_content_id(args,group['items'][0]['infohash']) + '\n')


# build xml epg
def make_epg(args, group):
    xmlstr=""
    try:
        tmpchid = c.trascochid(unidecode(str(group['name'])))
        if tmpchid:
            channel_id, order = tmpchid
        else:
            raise Exception('No channel id')   
        channel = ET.Element('channel')
        channel.set('id', channel_id)
        display = ET.SubElement(channel, 'display-name')
        display.text = str(group['name'])

        localfile="cust/epg/" + channel_id + ".xml"
        if not os.path.exists(localfile):
            localfile="tmp/" + channel_id + ".xml"
            if ((os.path.exists(localfile) and ((time.time() - os.path.getctime(localfile)) / 60) > 360) or not os.path.exists(localfile)):
                req = get('https://epg.pw/api/epg.xml?channel_id=' + channel_id).text
                with open(localfile, "w", encoding='utf-8') as filew:
                    filew.write(req)

        req = ""
        f = open(localfile, "r", encoding="utf8")
        for fl in f:
            fl = c.fixepg(str(group['name']),fl)
            req += fl
        if xmlstr == "":
            inizioepg = req.find('<channel') 
        else:    
            inizioepg = req.find('</channel>') + 10
        fineepg = req.find('</tv>')
        progch = req[inizioepg:fineepg].replace('+0000',c.get_shift(channel_id))        
        xmlstr += progch
        
    except:            
        if 'epg' in group and (not args.name or group['name'] in args.name):
            start = datetime.fromtimestamp(
                int(group['epg'][0]['start'])).strftime('%Y%m%d%H%M%S')
            stop = datetime.fromtimestamp(
                int(group['epg'][0]['stop'])).strftime('%Y%m%d%H%M%S')
            if args.api_version == '4':
                channel_id = str(group['channel_id'])
            else:    
                channel_id = str(group['items'][0]['channel_id'])
            channel = ET.Element('channel')
            channel.set('id', channel_id)
            display = ET.SubElement(channel, 'display-name')
            display.text = unidecode(str(group['name']))
            if 'icon' in group:
                icon = ET.SubElement(channel, 'icon')
                icon.set('src', group['icon'])
            programme = ET.Element('programme')
            programme.set('start', start + ' ' + args.zone)
            programme.set('stop', stop + ' ' + args.zone)
            programme.set('channel', channel_id)
            title = ET.SubElement(programme, 'title')
            title.text = unidecode(group['epg'][0]['name'])
            if 'description' in group['epg']:
                desc = ET.SubElement(programme, 'desc')
                desc.text = group['epg'][0]['description']
            xmlstr = ET.tostring(channel, encoding="unicode", pretty_print=True)
            xmlstr += ET.tostring(programme, encoding="unicode", pretty_print=True)

    if xmlstr.strip() == "":
        return ''
    else:
        return '  ' + xmlstr.replace('\n', '\n  ')

def get_content_id(args, infohash: str) -> str:
    """Fetch content_id for a given infohash from the acestream engine API."""
    import requests
    try:
        url = f"http://{args.proxy}/server/api"
        params = {
            "api_version": 3,
            "method": "get_content_id",
            "infohash": infohash
        }
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get("result", {}).get("content_id")
    except Exception as e:       
        return str(e)

    
# channels stream generator
def get_channels(args):
    page = count()
    while True:
        query = build_query(args, next(page))
        if args.api_version == '4':
            chunk = fetch_page(args, query)['results']
        else:    
            chunk = fetch_page(args, query)['result']['results']
        if len(chunk) == 0 or not group_by_channels and (
                'infohash' in chunk[0].keys() and chunk[0][
                'availability_updated_at'] < args.after):
            break
        yield chunk


# iterate the channels generator
def convert_json(args):
    counter = count(2000)
    for channels in get_channels(args):
        # Ordina i canali per nome (case insensitive)
        channels_sorted = sorted(channels, key=lambda group: unidecode(str(group.get('name', ''))).lower())
        # output raw json data
        if args.json:
            yield json.dumps(channels_sorted, ensure_ascii=False, indent=4)
        # output xml epg
        elif args.xml_epg:
            for group in channels_sorted:
                yield make_epg(args, group)
        # e infine playlist m3u ordinata
        else:
            m3u = ''
            for group in channels_sorted:
                if 'items' in group:
                    match = make_playlist(args, next(counter), group)
                    if match:
                        if args.url:
                            yield match
                            break
                        m3u += match
                    if match and args.url:
                        break
            if m3u:
                yield m3u.strip('\n')


def iter_data(args):
    '''Iterate all data types according to options.'''
    if args.name:
        channels = args.name
        # set "query" to "name" to speed up handling
        for station in channels:
            args.query = station
            args.name = [station]
            yield convert_json(args)
    else:
        yield convert_json(args)


def pager(args):
    '''chunked output'''
    for page in iter_data(args):
        if page:
            for item in page:
                if item:
                    yield item


def main(args):
    '''Wrap all output with header and footer.'''
    if args.xml_epg:
        yield '<?xml version="1.0" encoding="utf-8" ?>\n<tv>'
    elif args.json:
        yield '['
    elif not args.url:
        yield '#EXTM3U url-tvg="' + args.prog + '?xml_epg=1&proxy=' + args.proxy + \
                                                          '&api_version=' + args.api_version + '"'
    # make a correct json list of pages
    for page in pager(args):
        if args.json:
            page = page.strip('[]\n') + ','
        yield page
    if args.xml_epg:
        yield '</tv>'
    elif args.json:
        yield '    {\n    }\n]'


# command line function
def cli():
    args = get_options()
    for chunk in main(args):
        print(chunk)


# run command line script
if __name__ == '__main__':
    cli()
