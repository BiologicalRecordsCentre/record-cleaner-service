import base64
import hmac
import requests
from typing import Annotated
import urllib.parse

from fastapi import Depends

import app.config as config
import app.auth as auth


def get_auth_header(url):
    settings = config.get_settings()
    key = settings.indicia_rest_password.encode('utf-8')
    msg = urllib.parse.quote(url).encode('utf-8')
    hash = hmac.digest(key, msg, 'sha1')
    b64hash = base64.b64encode(hash)
    auth = f'USER:{settings.indicia_rest_user}:HMAC:{b64hash}'
    return auth


def get_taxon_by_tvk(auth: Annotated[bool, Depends(auth.authenticate)],
                     tvk=None):
    settings = config.get_settings()
    url = settings.indicia_url + "taxa/search"
    headers = {"Authorization": get_auth_header(url)}
    params = {
        'taxon_list_id': settings.indicia_taxon_list_id,
        'external_key': tvk
    }

    r = requests.get(url, headers=headers, params=params)
    if r.status_code == requests.codes.ok:
        return r.json()
    else:
        return


def get_taxon_by_name(name):
    return 1
