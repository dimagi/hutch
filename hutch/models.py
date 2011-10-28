from couchdbkit.ext.django.schema import   Document
from couchdbkit.schema.properties import StringProperty, DateTimeProperty, DictProperty
from django.core.files.base import ContentFile
import os
from django.conf import settings
from django.db import models
from dimagi.utils import make_uuid
from sorl.thumbnail import ImageField
from hutch.couchdb_doc_storage import CouchDBDocStorage


storage = CouchDBDocStorage(db_url=settings.COUCH_DATABASE)


class AuxMedia(Document):
    """
    Additional metadata companion for couchmodels you want to supply add arbitrary attachments to
    """
    uploaded_date = DateTimeProperty()
    uploaded_by = StringProperty()
    uploaded_filename = StringProperty() #the uploaded filename info
    checksum = StringProperty()
    attachment_id = StringProperty() #the actual attachment id in _attachments
    media_meta = DictProperty()
    notes = StringProperty()



class MediaAttachmentManager(models.Manager):

    def get_doc_auxmedia(self, couchdoc, auxmedia_prop='aux_media'):
        """
        If your Document has a SchemaListProperty of additional aux_media, or another property of your choosing, then you can extract the richer metadata from them here


        Returns a dictionary keyed by the aux_media items
        """

        aux_list = couchdoc[auxmedia_prop]
        ret = dict()

        for aux in aux_list:
            attach_dict = couchdoc['_attachments'].get(aux['attachment_id'],None)
            if attach_dict['content_type'].lower() not in ['image/jpeg', 'image/png', 'image/gif', 'image/tiff']:
                #skip non media attachments
                continue
            imgs = super(MediaAttachmentManager, self).get_query_set().filter(doc_id=couchdoc['_id'], attachment_key=aux['attachment_id'])

            if imgs.count() == 0:
                img = self.model()

                img = self.model()
                img.doc_id = couchdoc['_id']
                img.doc_type = couchdoc['doc_type']
                img.attachment_key = aux['attachment_id']
                img.content_length = attach_dict['length']
                img.content_type = attach_dict['content_type']
                imgfile = ContentFile(couchdoc.fetch_attachment(aux['attachment_id'], stream=True).read())

                img.image.save(aux['attachment_id'], imgfile)
                img.save()
            else:
                img = imgs[0]
            ret[aux]=img
        return ret


    def get_doc_attachments(self, couchdoc):
        """
        Returns AttachmentImage objects for a given couchdbkit document that has received attachments traditionally

        Returns a dictionary keyed by the attachment key
        """
        #check if an AttachmentImage exists for it.
        ret = dict()
        for attachment_key in couchdoc['_attachments'].keys():
            attach_dict = couchdoc['_attachments'].get(attachment_key,None)

            if attach_dict['content_type'].lower() not in ['image/jpeg', 'image/png', 'image/gif', 'image/tiff']:
                continue
            imgs = super(MediaAttachmentManager, self).get_query_set().filter(doc_id=couchdoc['_id'], attachment_key=attachment_key)
            if imgs.count() == 0:
                #make new AttachmentImage
                attach_dict = couchdoc['_attachments'].get(attachment_key,None)
                img = self.model()
                img.doc_id = couchdoc['_id']
                img.doc_type = couchdoc['doc_type']
                img.attachment_key = attachment_key
                img.content_length = attach_dict['length']
                img.content_type = attach_dict['content_type']

                imgfile = ContentFile(couchdoc.fetch_attachment(attachment_key, stream=True).read())
                img.image.save(attachment_key, imgfile)
                img.save()
            else:
                img = imgs[0]
            ret[attachment_key]=img
        return ret

class AttachmentImage(models.Model):
    """
    Django model for metadata handling of attachments in couchdbkit models
    This is specifically an ephemeral model for managing thumbnails for attachment media that are images.
    """
    id = models.CharField(max_length=32, unique=True, default=make_uuid, primary_key=True, editable=False)
    doc_id = models.CharField(max_length=32, null=True, blank=True, db_index=True)
    doc_type = models.CharField(max_length=64)
    attachment_key = models.CharField(max_length=255, db_index=True, help_text="the key in the _attachments dict of the doc to retrieve the file")
    content_type = models.CharField(max_length=160)
    content_length=models.IntegerField()
    checksum = models.CharField(max_length=32, help_text='MD5 of the Image submitted')

    image = ImageField(max_length=255,upload_to=os.path.join(settings.MEDIA_ROOT, 'attachments'))
    #image = ImageField(max_length=255, storage=couchdb_storage, upload_to=os.path.join(settings.MEDIA_ROOT, 'attachments'))

    objects = MediaAttachmentManager()


    class Meta:
        unique_together=('doc_id','attachment_key')

    def clean(self):
        from django.core.exceptions import ValidationError
        #Don't allow both patient_guid AND xform_id to be None
        if self.patient_guid is None and xform_id is None:
            raise ValidationError('You must either set a patient_guid or xform_id, both cannot be None')


    def __unicode__(self):
        return "%s (Filename: %s, Content-Type: %s, Size: %d)" % (self.doc_id, self.attachment_key, self.content_type, self.content_length)


