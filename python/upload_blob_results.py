"""Example of uploading a blob and then uploading a result linking to it"""
import base64
import hashlib
import json
import os

import requests

# Read API_KEY from envvar
api_key = os.environ['API_KEY']
# If you have a private deploy, this may be YOURCOMPANY.benchling.com
api_host = 'benchling.com'


def api_get(endpoint):
    rv = requests.get('https://%s%s' % (api_host, endpoint), auth=(api_key, ''))
    return rv.json()


def api_post(endpoint, params):
    rv = requests.post('https://%s%s' % (api_host, endpoint), auth=(api_key, ''), json=params)
    return rv.json()


def upload_blob(name, file_path):
    blob_id = api_post(api_host, api_key, '/v2/blobs', {
        'name': name,
        'type': 'RAW_FILE',
    })['id']

    with open(file_path, 'rb') as f:
        blob_data = f.read()
        etag = api_post(api_host, api_key, u'/v2/blobs/{}/parts'.format(blob_id), {
            'partNumber': 1,
            'data64': base64.b64encode(blob_data),
            'md5': hashlib.md5(blob_data).hexdigest(),
        })['eTag']
    
    api_post(api_host, api_key, u'/v2/blobs/{}:complete-upload'.format(blob_id), {
        'parts': [{'eTag': etag, 'partNumber': 1}],
    })
    return blob_id


def main():
    # Grab the first schema
    assay_schemas = api_get('/api/v2/assay-schemas')['assaySchemas']
    result_schemas = [schema for schema in assay_schemas if schema['type'] == 'assay_result']
    schema_id = result_schemas[0]['id']

    # Upload a blob
    blob_id = upload_blob('my_file_name.jpg', './path/to/my_file_name.jpg')
    
    # Upload a result linked to the blob
    response = api_post('/api/v2/assay-results', [
        {
            'schemaId': schema_id,
            'fields': {
                'blob': blob_id,
                # Fill in other fields here
            },
        },
    ])
    print 'Response:'
    print json.dumps(response, indent=2)


if __name__ == '__main__':
    main()
