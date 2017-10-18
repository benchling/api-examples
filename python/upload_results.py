"""Example of uploading results"""
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


def main():
    # Grab the first schema
    assay_schemas = api_get('/api/v2/assay-schemas')['assaySchemas']
    result_schemas = [schema for schema in assay_schemas if schema['type'] == 'assay_result']
    schema_id = result_schemas[0]['id']
    
    response = api_post('/api/v2/assay-results', [
        {
            'schemaId': schema_id,
            'fields': {
                'string_field': 'abc',
                'int_field': 123,
            },
        },
    ])
    print 'Response:'
    print repr(response)


if __name__ == '__main__':
    main()
