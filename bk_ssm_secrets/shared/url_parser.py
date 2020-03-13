from urllib.parse import urlparse


def valid_url(url):
    parsed = urlparse(url)
    if parsed.scheme:
        return True
    return False

def url_to_key(url):
    parsed = urlparse(url)
    key = ''
    if parsed.hostname:
        key += parsed.hostname
    if parsed.port:
        key += ':' + str(parsed.port)
    if parsed.path:
        key += '_' + parsed.path.strip('/').replace('/', '_').replace('~', '_')
    return key

def parse_url(url):
    parsed = urlparse(url)
    print('scheme=', parsed.scheme, sep='')
    print('netloc=', parsed.netloc, sep='')
    print('path=', parsed.path, sep='')
    print('params=', parsed.params, sep='')
    print('query=', parsed.query, sep='')
    print('fragment=', parsed.fragment, sep='')
    print('username=', parsed.username, sep='')
    print('password=', parsed.password, sep='')
    print('hostname=', parsed.hostname, sep='')
    print('port=', parsed.port, sep='')
    return True