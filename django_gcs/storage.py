import io
import re
import sys
import os
import tempfile
from pprint import pprint

import oauth2client.client
from django.core.files.storage import Storage
from django.conf import settings
from google.cloud import storage as gc_storage
from google.cloud import exceptions


DJANGO_GCS_PRIVATE_KEY_PATH = getattr(settings, 'DJANGO_GCS_PRIVATE_KEY_PATH', None)
DJANGO_GCS_BLOB_MAKE_PUBLIC = getattr(settings, 'DJANGO_GCS_BLOB_MAKE_PUBLIC', False)

if not DJANGO_GCS_PRIVATE_KEY_PATH or \
    not os.path.exists(DJANGO_GCS_PRIVATE_KEY_PATH):
    raise Exception("Can't find DJANGO_GCS_PRIVATE_KEY_PATH(with full path to existing JSON key for authentication) variable in django.conf.settings")




class GoogleCloudStorage(Storage):
    def __init__(self, bucket_name=None, **kwargs):
        self.bucket_name = bucket_name or getattr(settings, 'DJANGO_GCS_BUCKET', None)
        self.client = gc_storage.Client()

        ext = os.path.splitext(DJANGO_GCS_PRIVATE_KEY_PATH)[-1].lower()
        if ext == '.json':
            self.client.from_service_account_json(DJANGO_GCS_PRIVATE_KEY_PATH)
        elif ext == '.p12':
            self.client.from_service_account_p12(DJANGO_GCS_PRIVATE_KEY_PATH)
        if kwargs.has_key('public'):
            self.public = kwargs['public']
        else:
            self.public = DJANGO_GCS_BLOB_MAKE_PUBLIC

        try:
            self.gc_bucket = self.client.get_bucket(self.bucket_name)
        except exceptions.NotFound:
            # if the bucket hasn't been created, create one
            # TODO: creating buckets here is not functional,
            # buckets won't be created.
            self.gc_bucket = self.client.create_bucket(self.bucket_name)
        except oauth2client.client.AccessTokenRefreshError:
            # Temporarily ignore this exception
            # It causes 502 Bad Gateway on GCE,
            # but it seems OK to ignore this exception.
            pprint(sys.exc_info())
            pass

    # Helpers
    def __get_key(self, name):
        return self.gc_bucket.get_blob(name)

    # required methods
    def path(self, name):
        return name

    def _open(self, name, mode='rb'):
        gc_file = self.__get_key(self.path(name))

        temp_file = tempfile.TemporaryFile()

        gc_file.download_to_file(temp_file)

        temp_file.seek(0)

        return temp_file

    def _save(self, name, content):
        # content := django.db.models.fields.files.FieldFile
        gc_file = self.gc_bucket.blob(self.path(name))

        try:
            content.seek(0)
            gc_file.upload_from_file(content.file)
        except (io.UnsupportedOperation, ValueError):
            # some text file such as ContentFile will fail here
            # cus it's not a real file and doesn't support fileno() operation,
            # use string uplaoding approach

            content.seek(0)     # make sure file reading goes from head
            gc_file.upload_from_string(content.read())

        if self.public:
            gc_file.make_public()

        return gc_file.name

    def delete(self, name):
        gc_file = self.__get_key(self.path(name))

        gc_file.delete()

    def exists(self, name):
        gc_file = self.__get_key(self.path(name))

        return gc_file.exists() if gc_file else False

    def url(self, name):
        gc_file = self.__get_key(self.path(name))
        return gc_file.public_url

    def size(self, name):
        gc_file = self.__get_key(self.path(name))
        return gc_file.size

    def listdir(self, path):
        def extract_foldername(name):
            return re.search(r'^[^/]+', name).group(0)

        def extract_filename(name):
            return re.search(r'[^/]+$', name).group(0)

        def extract_path(keys, path):
            rtn = []
            for name in keys:
                new_name = re.search(r'^%s/(.*)$' % path, name).group(1)
                rtn.append(new_name)

            return rtn

        # convert to string for speeding up
        all_keys = [k.name for k in self.gc_bucket.list_blobs()]
        keys_under_path = extract_path(
            filter(lambda k: k.startswith(path), all_keys), path
        )

        # '/' in the name means the key is under a folder structure,
        # we extract the folder name. otherwise, extract the file name
        keys_files = filter(lambda k: '/' not in k, keys_under_path)
        keys_contains_dir = filter(lambda k: '/' in k, keys_under_path)

        # extract name
        dirs = map(extract_foldername, keys_contains_dir)

        # dirs has duplicated names, remove them.
        reduced_dirs = list(set(dirs))

        files = map(extract_filename, keys_files)

        return reduced_dirs, files
