# -*- coding: utf-8 -*-

import struct

import pytest
import httmock
import mock

import pushjack
from pushjack import (
    APNSClient,
    GCMClient,
    create_apns_config,
    create_gcm_config
)
from pushjack.apns import APNS_ERROR_RESPONSE_COMMAND
from pushjack.utils import json_dumps, json_loads


# pytest.mark is a generator so create alias for convenience
parametrize = pytest.mark.parametrize


def apns_socket_factory(return_status):
    class MagicSocket(mock.MagicMock):
        def write(self, frame):
            self.frame = frame

    sock = mock.MagicMock()
    sock.recv = lambda n: struct.pack('!BBI',
                                      APNS_ERROR_RESPONSE_COMMAND,
                                      return_status,
                                      0)

    return sock


@pytest.fixture
def apns_client():
    """Return APNS client."""
    return APNSClient(create_apns_config())


@pytest.fixture
def apns_sock():
    """Return mock for APNS socket client."""
    sock = mock.MagicMock()
    sock.recv = lambda n: ''
    return sock


def gcm_server_response_factory(content):
    @httmock.all_requests
    def response(url, request):
        headers = {'content-type': 'application/json'}
        return httmock.response(200, content, headers, None, 1, request)
    return response


@httmock.all_requests
def gcm_server_response(url, request):
    payload = json_loads(request.body)
    headers = {'content-type': 'application/json'}
    content = {
        'multicast_id': 1,
        'success': len(payload['registration_ids']),
        'failure': 0,
        'canonical_ids': 0,
        'results': []
    }

    content['results'] = [{'message_id': registration_id}
                          for registration_id in payload['registration_ids']]

    return httmock.response(200, content, headers, None, 1, request)


@pytest.fixture
def gcm_client():
    """Return GCM client."""
    return GCMClient(create_gcm_config({'GCM_API_KEY': '1234'}))
