#!/usr/bin/env python3
"""A light standalone script that uploads 10 blobs and records how long the various calls took"""
import base64
import hashlib
import json
import os
import random
import string
import sys
import time
import urllib.request, urllib.error, urllib.parse


ONE_KILOBYTE = 1024
BLOB_SIZE = ONE_KILOBYTE
NUM_ATTEMPTS = 10


def random_str(length):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(length))


def api_post(api_host, api_key, path, body):
    url = '{}{}'.format(api_host, path)

    password_manager = urllib.request.HTTPPasswordMgrWithDefaultRealm()
    password_manager.add_password(None, url, api_key, 'pass')
    auth_manager = urllib.request.HTTPBasicAuthHandler(password_manager)
    opener = urllib.request.build_opener(auth_manager)

    urllib.request.install_opener(opener)
    response = urllib.request.urlopen(url=url, data=json.dumps(body).encode('utf-8'))
    data = response.read().decode('utf-8')

    if response.getcode() >= 400:
        raise Exception('Server returned status {}. Response:\n{}'.format(response.getcode(), data))
    return json.loads(data)


def upload_blob(api_host, api_key):
    print('Starting upload...')
    t0 = time.time()
    blob_id = api_post(api_host, api_key, '/v2/blobs', {
        'name': random_str(40),
        'type': 'RAW_FILE',
    })['id']

    t1 = time.time()
    part_number = 1
    contents = os.urandom(BLOB_SIZE)
    etag = api_post(api_host, api_key, '/v2/blobs/{}/parts'.format(blob_id), {
        'partNumber': part_number,
        'data64': base64.b64encode(contents).decode('utf-8'),
        'md5': hashlib.md5(contents).hexdigest(),
    })['eTag']

    t2 = time.time()
    api_post(api_host, api_key, '/v2/blobs/{}:complete-upload'.format(blob_id), {
        'parts': [{'eTag': etag, 'partNumber': part_number}],
    })
    print('Uploaded blob {}'.format(blob_id))

    return t1 - t0, t2 - t1, time.time() - t2


def benchmark(api_host, api_key):
    times_start = []
    times_upload = []
    times_finish = []
    times_total = []
    for attempt in range(NUM_ATTEMPTS):
        print('Attempt {}/{}'.format(attempt + 1, NUM_ATTEMPTS))
        time_start, time_upload, time_finish = upload_blob(api_host, api_key)
        times_start.append(time_start)
        times_upload.append(time_upload)
        times_finish.append(time_finish)
        times_total.append(time_start + time_upload + time_finish)
    times_start = sorted(times_start)
    times_upload = sorted(times_upload)
    times_finish = sorted(times_finish)
    times_total = sorted(times_total)

    print('')
    print('Total: median={} max={}'.format(times_total[NUM_ATTEMPTS / 2 + 1], times_total[-1]))
    print('Start: median={} max={}'.format(times_start[NUM_ATTEMPTS / 2 + 1], times_start[-1]))
    print('Upload: median={} max={}'.format(times_upload[NUM_ATTEMPTS / 2 + 1], times_upload[-1]))
    print('Finish: median={} max={}'.format(times_finish[NUM_ATTEMPTS / 2 + 1], times_finish[-1]))


if __name__ == '__main__':
    benchmark(sys.argv[1], sys.argv[2])
