from chainlit.data.storage_clients.s3 import S3StorageClient
import dotenv
import os
import json
from urllib.request import urlopen

dotenv.load_dotenv()

kwargs = {
        'aws_access_key_id':os.environ['APP_AWS_ACCESS_KEY'],
        'aws_secret_access_key':os.environ['APP_AWS_SECRET_KEY']
    }

storage = S3StorageClient('52713ed5-d0d2-4eaf-8701-dcb26067a9f3',**kwargs)

def upload_source(key, object):
    storage.sync_upload_file(key, object, mime='application/json')

def load_source(key):
    try:
        url = storage.sync_get_read_url(key)
        return json.loads(urlopen(url).read().decode('utf-8'))
    except:
        return None