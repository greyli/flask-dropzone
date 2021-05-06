"""
    flask_dropzone.utils
    ~~~~~~~~~~~~~~~~~~~~~

    :author: Grey Li <withlihui@gmail.com>
    :copyright: (c) 2017 by Grey Li.
    :license: MIT, see LICENSE for more details.
"""
import os
import uuid

from flask import url_for


def get_url(endpoint_or_url, **kwargs):
    if endpoint_or_url == '':
        return
    if endpoint_or_url.startswith(('https://', 'http://', '/')):
        return endpoint_or_url
    else:
        return url_for(endpoint_or_url, **kwargs)


# generate a random filename, replacement for werkzeug.secure_filename
def random_filename(old_filename):
    ext = os.path.splitext(old_filename)[1]
    new_filename = uuid.uuid4().hex + ext
    return new_filename
