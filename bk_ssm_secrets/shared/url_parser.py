import sys, getopt
from urllib.parse import urlparse
# from url_parse import url_parse
# from rfc3987 import parse
# https://code-examples.net/en/q/bfba6a
# def valid_url(url):
#     parse(url, rule='IRI')
# username = os.environ['USER']

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
        key += '_' + parsed.path.strip('/').replace('/', '_')
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

# def main(argv):
#    ret = True
#    url = ''
#    try:
#       opts, args = getopt.getopt(argv,"hvpu:k",["url=", "key"])
#    except getopt.GetoptError:
#       print('url_parse.py -h -v -k -p --key -u <url>')
#       sys.exit(2)
#    for opt, arg in opts:
#       if opt == '-h':
#          print('url_parse.py -h -v -p -k --key -u <url>')
#          sys.exit()
#       elif opt in ("-u", "--url"):
#          url=arg
#       elif opt in ("-p"):
#          ret = parse_url(url)
#       elif opt in ("-k", "--key"):
#          ret = url_to_key(url)
#       elif opt in ("-v"):
#          ret = valid_url(url)
#    if ret:
#       sys.exit(0)
#    else:
#       sys.exit(1)

# if __name__ == "__main__":
#    main(sys.argv[1:])