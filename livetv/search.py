import subprocess
import sys
from setuptools._distutils.util import split_quoted
from flask import Flask, request, Response, send_from_directory, abort
from acestream_search import main as engine, get_options, __version__
import logging
import os
import time
import hashlib

logging.basicConfig(filename='search.log',level=logging.DEBUG)

app = Flask(__name__)
if sys.version_info[0] > 2:
    def u_code(string):
        return string
else:
    def u_code(string):
        return string.encode("utf8")

def get_args():
    opts = {'prog': request.base_url}
    for item in request.args:
        opts[item] = u_code(request.args[item])
    if 'name' in opts:
        opts['name'] = split_quoted(opts['name'])
    if 'query' not in opts:
        opts['query'] = ''
    args = get_options(opts)
    return args

@app.route('/')
def home():
    baseurl = request.base_url
    return '''
    <html>
        <head>
            <title>Live TV Playlist</title>
        </head>
        <body>
            <h1>Welcome to Live TV Playlist</h1>
            <p>IPTV list: <a href="''' + baseurl + '''search.m3u">''' + baseurl + '''search.m3u</a></p>
        </body>
    </html>
    '''

@app.route('/<name>.log')
def get_log(name):
    return Response(open(name + ".log", "r").read(), content_type='text/plain')

@app.route("/w3u")
def livetv():
    return Response(open("livetv.w3u", "r", encoding="utf8").read().replace("http://:",request.base_url), content_type='application/json')

@app.route('/update')
def update():
    result = subprocess.run(['python3', 'livetv.py'], capture_output=True, text=True)
    return f"<pre>{result.stdout}</pre>"

# Definisci la cartella in cui sono memorizzati i file da servire
UPLOAD_FOLDER = 'cust'
@app.route('/m3u/<filename>')
def get_file(filename):
    try:
        # Restituisci il file dalla cartella specificata
        return send_from_directory(UPLOAD_FOLDER, filename + '.m3u')
    except FileNotFoundError:
        # Se il file non esiste, restituisci un errore 404
        abort(404)

# Use two routing rules of Your choice where playlist extension does matter.
@app.route('/m3u')
@app.route('/search.m3u')
@app.route('/search.m3u8')
def main():
    args = get_args()
    # return str(args)
    if args.xml_epg:
        content_type = 'text/xml'
    elif args.json:
        content_type = 'application/json'
    else:
        content_type = 'application/x-mpegURL'

    CACHE_DIR = 'tmp/cache'
    CACHE_EXPIRY = 300
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)

    def generate():               
        cache_key = hashlib.md5(str(args).encode('utf-8')).hexdigest()
        cache_file = os.path.join(CACHE_DIR, cache_key)
        temp_cache_file = cache_file + '.tmp'
        if os.path.exists(cache_file) and (time.time() - os.path.getmtime(cache_file)) < CACHE_EXPIRY:
            with open(cache_file, 'r', encoding='utf-8') as f:
                for line in f:
                    yield line
        else:
            try:
                with open(temp_cache_file, 'w', encoding='utf-8') as f:                              
                    for page in engine(args):
                        f.write(page + '\n')
                os.rename(temp_cache_file, cache_file)
            finally: 
                with open(cache_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        yield line

    if 'version' in args:
        return Response(__version__ + '\n', content_type='text/plain')
    if 'help' in args:
        return Response(args.help, content_type='text/plain')
    if 'usage' in args:
        return Response(args.usage, content_type='text/plain')
    if args.url:
        redirect_url = next(x for x in generate()).strip('\n')
        response = Response('', content_type='')
        response.headers['Location'] = redirect_url
        response.headers['Content-Type'] = ''
        response.status_code = 302
        return response
    return Response(generate(), content_type=content_type)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        port = sys.argv[1]
    else:
        port = 6880
    app.run(host='::', port=port, debug=True)
