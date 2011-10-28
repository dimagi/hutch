Dimagi Hutch
=============

Hutch is a media storage framework for django-couchdbkit projects.

The goal of Hutch is to allow for different ways to handle media in a django project using couchdbkit.

1. Retrieve and use media from existing attachments to couchdbkit documents
2. Handle any media type to any document type for couchdbkit models
3. Do easy thumbnail/media display of said attachments in couch

Requirements
=============
* couchdbkit
* sorl-thumbnail


Setup
=====

Your django project's MEDIA_ROOT should be accessible and writeable.  The ImageField for sorl-thumbnail requires this to
create the intermediary sizes of your thumbnails.


In Use
======

Existing documents with attachments::

    image_dict = AttachmentImage.objects.get_doc_attachments(couchdocument)

This yields a dictionary keyed by the document's _attachments keys and values are ImageAttachment and are a subset of popular image types found here (http://en.wikipedia.org/wiki/Internet_media_type#Type_image)


Using the AuxMedia schema

The AuxMedia document schema is an added on feature for making form interactions easier to manage with attachments.  You can also arbitrarily add
attachments to your documents.  The AuxMedia class lets you provide more metadata for a given attachment.

You can add the AuxMedia as a SchemaListProperty - by default the manager assumes you will set it as aux_media for your document class you want to add it to.
But you can also define multiple list for it and call the manager repeatedly and set the kwarg to the property you want to check off of.

In usage::

    aux_image_dict = AttachmentImage.objects.get_doc_auxmedia(couchdocument, auxmedia_prop='aux_media') #that's the default property it checks

This returns a dictionary keyed by the aux_media subdocument as the key, and the value is the AttachmentImage

These manager methods create an AttachmentImage where one doesn't exist.

Rendering Images In Templates
=============================

To do this, use the sorl-thumbnail API for using in your templates. This assumes you've setup sorl-thumbnails up corrrectly.

In this current release, the method for using in requires a few steps.

* In your view, for your couchdoc, call the appropriate manager to get your AttachmentImage dictionary and set them to your context:

context['image_dict'] = AttachmentImage.objects.get_doc_attachments(couchdoc)

* Next, your template should look like this:

    {% load thumbnail %} {#sorl thumbnail template tags #}
    {% for k, v in image_dict.items %} {#where v is the AttachmentImage instance #}
        {% thumbnail v.image "200x200" as im %} {#this is sorl-thumbnail template convention #}
        <p>
            <img src="{{ im.url }}" width="{{ im.width }}" height="{{ im.height }}">
            {{ k }} {# _attachments key #}
        </p>
        {% endthumbnail %}
    {%endfor %}


Notes
=====

The AttachmentImage model is NOT to be relied upon for managing your media.  This is what your couch document stores them for.

As such, the AttachmentImage can and will be blown away from time to time to save space.

As of this writing the creation of the AttachmentImage still seems a bit hokey.  An ideal development of this system would negate the need to create an intermediary ImageField utilizing model, which creates in the filesystem
a copy of the original attachment.  Long term this is not a tractable solution.
However, accessing the couchdoc's attachment stream does not seem to work correctly with sorl-thumbnails templating system just yet.


* About the name:  Traditionally on an office desk some of them offer a media storage unit shelf to go over the shelf, called a hutch, hence the use of the furniture pun.
