from django.core.servers.basehttp import FileWrapper
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from dimagi.utils.couch.database import get_db
from hutch.models import AttachmentImage

def image_proxy(request, doc_id, attachment_key):
    """Simple image proxy to view an image straight from couch.  This does not work with sorl-thumbnail as a viable means to
    dynamically generate image thumbnails.
    """
    db = get_db()
    attach = db.fetch_attachment(doc_id, attachment_key, stream=True)
    wrapper = FileWrapper(attach)
    response = HttpResponse(wrapper, content_type='image/jpeg')
    return response


def show_image(request, attachment_image_id):
    db = get_db()


    size = request.GET.get('size', '')
    if size == '':
        dimensions = '200x200'
    else:
        splitsize = size.split('x')
        if len(splitsize) == 1:
            dimensions = '%sx%s' % (size,size)
        else:
            dimensions = size


    image = AttachmentImage.objects.get(id=attachment_image_id)
    return render_to_response("hutch/show_image.html",
                              {
                                "image": image,
                                'dimensions': dimensions,
                                },
                              context_instance=RequestContext(request))
