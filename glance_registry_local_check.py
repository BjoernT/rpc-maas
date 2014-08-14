#!/usr/bin/env python

from maas_common import (status_ok, status_err, metric, get_keystone_client,
                         get_auth_ref, metric_bool)
from requests import Session
from requests import exceptions as exc


def check(auth_ref):
    # We call get_keystone_client here as there is some logic within to get a
    # new token if previous one is bad.
    keystone = get_keystone_client(auth_ref)
    auth_token = keystone.auth_token
    registry_endpoint = 'http://127.0.0.1:9191'

    api_is_up = True
    milliseconds = 0

    s = Session()

    s.headers.update(
        {'Content-type': 'application/json',
         'x-auth-token': auth_token})

    try:
        # /images returns a list of public, non-deleted images
        r = s.get('%s/images' % registry_endpoint, verify=False, timeout=10)
    except (exc.ConnectionError, exc.HTTPError, exc.Timeout):
        api_is_up = False
        milliseconds = -1
    except Exception as e:
        status_err(str(e))
    else:
        milliseconds = r.elapsed.total_seconds() * 1000

        api_is_up = r.ok

    status_ok()
    metric_bool('glance_registry_local_status', api_is_up)
    if api_is_up:
        metric('glance_registry_local_response_time', 'int32', milliseconds)


def main():
    auth_ref = get_auth_ref()
    check(auth_ref)


if __name__ == "__main__":
    main()
