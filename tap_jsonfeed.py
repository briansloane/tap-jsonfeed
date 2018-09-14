import argparse
import requests
import singer
import json
import os
import sys
import singer.stats

session = requests.Session()
logger = singer.get_logger()


def authed_get(source, url, headers={}):
    with singer.stats.Timer(source=source) as stats:
        session.headers.update(headers)
        resp = session.request(method='get', url=url)
        stats.http_status_code = resp.status_code
        return resp

def authed_get_all_pages(source, url, headers={}):
    while True:
        r = authed_get(source, url, headers)
        yield r
        if 'next' in r.links:
            url = r.links['next']['url']
        else:
            break

def get_abs_path(path):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), path)

def load_schemas():
    schemas = {}

    with open(get_abs_path('tap_jsonfeed/feed.json')) as file:
        schemas['feed'] = json.load(file)

    return schemas

def get_feed(feed_url, state):
    with singer.stats.Counter(source='commits') as stats:
        for response in authed_get_all_pages('feed', feed_url):
            feed = response.json()

            for post in feed['items']:
                stats.add(record_count=1)

            singer.write_records('feed', feed['items'])

    return 0

def do_sync(config, state):
    feed_url = config['feed_url']
    schemas = load_schemas()

    if state:
        logger.info('Replicating commits since %s from %s', state, feed_url)
    else:
        logger.info('Replicating all commits from %s', feed_url)


    singer.write_schema('feed', schemas['feed'], 'id')
    state = get_feed(feed_url, state)
    singer.write_state(state)

def do_discover():
    logger.info("Starting discover")
    streams = []
    streams.append({'stream': 'feed', 'tap_stream_id': 'feed', 'schema': load_schemas()})
    json.dump({'streams': streams}, sys.stdout, indent=2)
    logger.info("Finished discover")


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-c', '--config', help='Config file', required=True)
    parser.add_argument(
        '-s', '--state', help='State file')
    parser.add_argument(
        '-d', '--discover', action='store_true', help='Discover schemas')

    args = parser.parse_args()

    with open(args.config) as config_file:
        config = json.load(config_file)

    missing_keys = []
    for key in ['feed_url']:
        if key not in config:
            missing_keys += [key]

    if len(missing_keys) > 0:
        logger.fatal("Missing required configuration keys: {}".format(missing_keys))
        exit(1)

    if args.discover:
        do_discover()
    else:
        state = {}
        if args.state:
            with open(args.state, 'r') as file:
                for line in file:
                    state = json.loads(line.strip())

        do_sync(config, state)

if __name__ == '__main__':
    main()
