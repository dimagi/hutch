"""
This is a Custom Storage System for Django with CouchDB backend.
Created by Christian Klein.

Modified for storage WITHIN a document by dan myung and using couchdbkit
(c) Copyright 2009 HUDORA GmbH. All Rights Reserved.
"""
from django.core.files.base import ContentFile
from django.core.urlresolvers import reverse
from cStringIO import StringIO

from django.conf import settings
from django.core.files import File
from django.core.files.storage import Storage
from django.core.exceptions import ImproperlyConfigured
import os
from dimagi.utils.couch.database import PerseverentDatabase

DEFAULT_SERVER= getattr(settings, 'COUCHDB_SERVER_ROOT', 'localhost:5984')

def _split_file(name):
    splits = os.path.split(name)
    filename = splits[-1]
    return tuple(filename.split('_-_-_'))

class CouchDBDocStorage(Storage):
    """
    CouchDBDocStorage - a Django Storage class for CouchDB.

    Uses the couchdb url for the database you want to connect to
    """


    def __init__(self, **kwargs):
        self.couchdb_url = kwargs.get('db_url', settings.COUCH_DATABASE)
        self.db = PerseverentDatabase(self.couchdb_url)

    def _put_file(self, name, content):
        doc_id, attachment_key=_split_file(name)
        self.db.put_attachment(doc_id, content, name=attachment_key)
        return doc_id

    def get_document(self, doc_id):
        return self.db.get(doc_id)

    def _open(self, name, mode='rb'):
        doc_id, attachment_key=_split_file(name)
        couchdb_file = CouchDBAttachmentFile(doc_id, attachment_key, self, mode=mode)
        return couchdb_file

    def _save(self, name, content):
        doc_id, attachment_key=_split_file(name)
        content.open()
        if hasattr(content, 'chunks'):
            content_str = ''.join(chunk for chunk in content.chunks())
        else:
            content_str = content.read()
        #name = name.replace('/', '-')
        return self._put_file(name, content_str)

    def exists(self, name):
        doc_id, attachment_key=_split_file(name)
        if self.db.doc_exist(doc_id):
            return self.db.open_doc(doc_id)['_attachments'].has_key(attachment_key)
        else:
            return False

    def size(self, name):
        doc_id, attachment_key=_split_file(name)
        doc = self.get_document(doc_id)
        if doc:
            return doc['_attachments'][attachment_key]['length']
        return 0

    def url(self, name):
        doc_id, attachment_key=_split_file(name)
#        return urljoin(self.base_url,
#                       os.path.join(quote_plus(self.db.name),
#                       quote_plus(name),
#                       'content'))
        return reverse('hutch.views.image_proxy', kwargs={'doc_id': doc_id, 'attachment_key': attachment_key})

    def delete(self, name):
        doc_id, attachment_key=_split_file(name)
        try:
            doc = self.get_document(doc_id)
            del doc['_attachments'][attachment_key]
        except Exception, ex:
            print "Ex: %s" % ex
            raise IOError("File not found: %s" % name)

    #def listdir(self, name):
    # _all_docs?
    #    pass


class CouchDBAttachmentFile(File):
    """
    An adaptation of CouchDBFile - a Django File-like class for CouchDB documents.


    Only treats a known attachment to a document
    """

    def __init__(self, doc_id, attachment_key, storage, mode):
        self._doc_id = doc_id
        self._attachment_filename = attachment_key
        self._storage = storage
        self._mode = mode
        self._is_dirty = False

#        try:
        print doc_id
        self._doc = self._storage.get_document(doc_id)
        print attachment_key
        attachment = ContentFile(self._storage.db.fetch_attachment(self._doc, attachment_key, stream=True).read())
        print "getting attachment"
        self.file = attachment
        print "finished getting attachment"
#        except Exception, ex:
#        #except couchdb.client.ResourceNotFound:
#            print "Error init couchdb attachment file: %s " % (ex)
#            if 'r' in self._mode:
#                raise ValueError("The file cannot be reopened.")
#            else:
#                self.file = StringIO()
#                self._is_dirty = True

    @property
    def size(self):
        return self._doc['_attachments'][self._attachment_filename]['length']

    def write(self, content):
        if 'w' not in self._mode:
            raise AttributeError("File was opened for read-only access.")
        self.file = StringIO(content)
        self._is_dirty = True

    def close(self):
        if self._is_dirty:
            self._storage._put_file('%s/%s' % (self._doc['_id'], self._attachment_filename), self.file.read())
        self.file.close()

