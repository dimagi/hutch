from django.core.servers.basehttp import FileWrapper
from django.http import HttpResponse
from dimagi.utils.couch.database import get_db

def image_proxy(request, doc_id, attachment_key):
    """Simple image proxy to view an image straight from couch.  This does not work with sorl-thumbnail as a viable means to
    dynamically generate image thumbnails.
    """
    db = get_db()
    attach = db.fetch_attachment(doc_id, attachment_key, stream=True)
    wrapper = FileWrapper(attach)
    response = HttpResponse(wrapper, content_type='image/jpeg')
    return response
