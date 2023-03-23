#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `PicSureClient` package."""
import io
import json
import unittest
from contextlib import contextmanager
from unittest.mock import patch, MagicMock

import urllib3
import PicSureClient


@contextmanager
def capture_stdout(assert_callback=None):
    fake_stdout = io.StringIO()
    with patch('sys.stdout', new=fake_stdout):
        yield
    captured = fake_stdout.getvalue()
    print("Captured:\n" + captured)
    if assert_callback:
        if isinstance(assert_callback, list):
            for callback in assert_callback:
                callback(captured)
        else:
            assert_callback(captured)


class TestClient(unittest.TestCase):

    def setUp(self):
        self.test_url = "http://some.url/PIC-SURE/"
        self.test_token = "some_security_token"

        self.mock_response = MagicMock(spec=urllib3.response.HTTPResponse)
        self.mock_response.status = 200
        self.mock_response.data = '["SOME-RESOURCE-UUID-HERE"]'.encode()

    def test_client_func_version(self):
        assertion = lambda captured: self.assertTrue(len(captured.strip()) > 0)
        with capture_stdout(assertion):
            PicSureClient.Client.version()

    def test_client_func_help(self):
        with capture_stdout(lambda captured: self.assertTrue(len(captured.strip()) > 0)):
            PicSureClient.Client.help()

    @patch('urllib3.PoolManager.request')
    def test_client_func_connect_success(self, mock_request):
        mock_request.return_value = self.mock_response

        test_obj = PicSureClient.Client.connect(self.test_url, self.test_token)
        self.assertIsInstance(test_obj, PicSureClient.Connection, "Client.connect() returns the wrong object type")
        self.assertEqual(test_obj.url, self.test_url)
        self.assertEqual(test_obj._token, self.test_token)
        self.assertEqual(test_obj.AllowSelfSigned, False,
                         "Accepting self-signed SSL certificates should NOT be the default!")

    @patch('urllib3.PoolManager.request')
    def test_client_func_connect_fail_url(self, mock_request):
        test_url = "http://some.url/PIC-SURE/"
        test_token = "some_security_token"

        self.mock_response.status = 404
        self.mock_response.data = 'Not Found'.encode()
        self.mock_response.headers = {'status': '404'}

        mock_request.return_value = self.mock_response
        assertion = lambda captured: self.assertTrue(captured.strip().index("Invalid URL") > 0,
                                                     "Should print a warning message when the URL is incorrect!")
        with capture_stdout(assertion):
            PicSureClient.Client.connect(test_url, test_token)

    @patch('urllib3.PoolManager.request')
    def test_client_func_connect_fail_token(self, mock_request):
        test_url = "https://copdgene-dev.hms.harvard.edu/picsure/"

        self.mock_response.status = 401
        self.mock_response.data = 'Unauthorized'.encode()
        self.mock_response.__setattr__('headers', "{'status': '401'}")

        mock_request.return_value = self.mock_response

        assertion = lambda captured: self.assertTrue(captured.strip().index("Token invalid") > 0,
                                                     "Should print a warning message when the token is rejected!")
        with capture_stdout(assertion):
            PicSureClient.Client.connect(test_url, self.test_token)

    @patch('urllib3.PoolManager.request')
    def test_client_func_connect_selfsigned_ssl(self, mock_request):
        # Set the return value for the mock request
        mock_request.return_value = self.mock_response

        assertion = lambda captured: self.assertTrue(captured.strip().index("[ WARNING ]") > 0,
                                                     "Should print a warning message when allowing self-signed SSL "
                                                     "certificates!")
        assertion2 = lambda captured: self.assertEqual(test_obj.AllowSelfSigned, True,
                                                       "Specified to allow self-signed SSL certificates but it did "
                                                       "not propagate")

        with capture_stdout([assertion, assertion2]):
            test_obj = PicSureClient.Client.connect(self.test_url, self.test_token, True)


class TestConnection(unittest.TestCase):

    def setUp(self):
        self.test_url = "http://some.url/PIC-SURE/"
        self.test_token = "some_security_token"

        self.mock_response = MagicMock(spec=urllib3.response.HTTPResponse)
        self.mock_response.status = 200
        self.mock_response.data = '["SOME-RESOURCE-UUID-HERE"]'.encode()
        self.mock_response.headers = {'Authorization': 'Bearer ' + self.test_token, 'Content-Type': 'application/json'}

    @patch('urllib3.PoolManager.request')
    def test_connection_create(self, http_request):
        http_request.return_value = self.mock_response
        test_conn = PicSureClient.Connection(self.test_url, self.test_token)

        self.assertEqual(test_conn.url, self.test_url)
        self.assertEqual(test_conn._token, self.test_token)
        self.assertEqual(test_conn.AllowSelfSigned, False,
                         "Accepting self-signed SSL certificates should NOT be the default!")

    @patch('urllib3.PoolManager.request')
    def test_connection_func_help(self, http_request):
        test_conn = PicSureClient.Connection(self.test_url, self.test_token)
        http_request.return_value = self.mock_response

        assertion = lambda captured: self.assertTrue(len(captured.strip()) > 0, "Should print help message")
        with capture_stdout(assertion):
            test_conn.help()

    @patch('urllib3.PoolManager.request')
    def test_connection_func_list(self, mock_request):
        self.mock_response.data = json.dumps(["resource-1-uuid", "resource-2-uuid", "resource-3-uuid"]).encode("utf-8")
        mock_request.return_value = self.mock_response

        test_conn = PicSureClient.Connection(self.test_url, self.test_token)
        assertion = lambda captured: self.assertTrue(len(captured.strip()) > 0, "Should print list of resource UUIDs")
        with capture_stdout(assertion):
            test_conn.list()

    @patch('urllib3.PoolManager.request')
    def test_connection_func_about(self, mock_request):
        self.mock_response.data = json.dumps(["resource-1-uuid", "resource-2-uuid", "resource-3-uuid"]).encode("utf-8")
        mock_request.return_value = self.mock_response
        test_conn = PicSureClient.Connection(self.test_url, self.test_token)

        assertion = lambda captured: self.assertTrue(len(captured.strip()) > 0, "Should print list of resource UUIDs")
        with capture_stdout(assertion):
            test_conn.list()

    @patch('urllib3.PoolManager.request')
    def test_connection_func_getResources(self, mock_request):
        self.mock_response.data = json.dumps(["resource-1-uuid", "resource-2-uuid", "resource-3-uuid"]).encode("utf-8")
        mock_request.return_value = self.mock_response

        test_conn = PicSureClient.Connection(self.test_url, self.test_token)
        test_list = test_conn.getResources()
        self.assertEqual(self.mock_response.data.decode(), test_list)

        # Order of parameters is important here
        mock_request.assert_called_with("GET", self.test_url + "info/resources", fields=None, body=None,
                                        headers=self.mock_response.headers)

    @patch('urllib3.PoolManager.request')
    def test_connection_func_getInfo(self, mock_request):
        test_uuid = "some_resource_uuid"

        resource_info = {"uuid": test_uuid, "about": "some information goes here"}
        json_content = json.dumps(resource_info)

        self.mock_response.data = json_content.encode("utf-8")

        mock_request.return_value = self.mock_response

        test_conn = PicSureClient.Connection(self.test_url, self.test_token)
        test_info = test_conn.getInfo(test_uuid)
        self.assertEqual(json_content, test_info)
        mock_request.assert_called_with("POST", self.test_url + "info/" + test_uuid, fields=None, body=None,
                                        headers=self.mock_response.headers)

    @patch('urllib3.PoolManager.request')
    def test_connection_func_api_obj(self, mock_request):
        self.mock_response.data = json.dumps(["resource-1-uuid", "resource-2-uuid", "resource-3-uuid"]).encode("utf-8")

        # Create a mock request object
        mock_request.return_value = self.mock_response

        test_conn = PicSureClient.Connection(self.test_url, self.test_token)
        test_api_obj = test_conn._api_obj()
        self.assertIsInstance(test_api_obj, PicSureClient.PicSureConnectionAPI,
                              "Connection._api_obj() returns the wrong object type")
        self.assertEqual(self.test_url, test_api_obj.url_picsure)
        self.assertEqual(self.test_token, test_api_obj._token)
        self.assertEqual(test_api_obj.AllowSelfSigned, False,
                         "Accepting self-signed SSL certificates should NOT be the default!")


class TestConnectionAPI(unittest.TestCase):

    def setUp(self):
        self.test_token = "some_security_token"
        self.test_url_picsure = "http://some.url/PIC-SURE/"
        self.test_url_psama = "http://some.url/PSAMA/"
        self.test_uuid = "some_resource_uuid"

        self.mock_response = MagicMock(spec=urllib3.response.HTTPResponse)
        self.mock_response.status = 200
        self.mock_response.data = '["SOME-RESOURCE-UUID-HERE"]'.encode()
        self.mock_response.headers = {'Authorization': 'Bearer ' + self.test_token, 'Content-Type': 'application/json'}

    def test_connection_api_create(self):
        test_api_obj = PicSureClient.PicSureConnectionAPI(self.test_url_picsure, self.test_url_psama, self.test_token)
        self.assertEqual(self.test_url_psama, test_api_obj.url_psama)
        self.assertEqual(self.test_url_picsure, test_api_obj.url_picsure)
        self.assertEqual(self.test_token, test_api_obj._token)
        self.assertEqual(test_api_obj.AllowSelfSigned, False,
                         "Accepting self-signed SSL certificates should NOT be the default!")

    @patch('urllib3.PoolManager.request')
    def test_connectionapi_func_profile(self, mock_request):
        resource_info = {"uuid": self.test_uuid, "email": "some@email.edu",
                         "privileges": ["SUPER_ADMIN", "ROLE_SYSTEM", "PIC-SURE Unrestricted Query", "ADMIN"],
                         "queryTemplate": ""}
        json_content = json.dumps(resource_info)

        self.mock_response.data = json_content.encode("utf-8")
        mock_request.return_value = self.mock_response

        test_api_obj = PicSureClient.PicSureConnectionAPI(self.test_url_picsure, self.test_url_psama, self.test_token)
        test_profile = test_api_obj.profile()
        self.assertEqual(json_content, test_profile)
        mock_request.assert_called_with("GET", self.test_url_psama + "user/me", fields=None, body=None,
                                        headers=self.mock_response.headers)

    @patch('urllib3.PoolManager.request')
    def test_connectionapi_func_info(self, mock_request):
        resource_info = {"uuid": self.test_uuid, "some_info": {}}
        json_content = json.dumps(resource_info)
        self.mock_response.data = json_content.encode("utf-8")
        mock_request.return_value = self.mock_response

        test_api_obj = PicSureClient.PicSureConnectionAPI(self.test_url_picsure, self.test_url_psama, self.test_token)
        test_info = test_api_obj.info(self.test_uuid)
        self.assertEqual(json_content, test_info)
        mock_request.assert_called_with("POST", self.test_url_picsure + "info/" + self.test_uuid,
                                        fields=None, body="{}", headers=self.mock_response.headers)

    @patch('urllib3.PoolManager.request')
    def test_connectionapi_func_search_blank(self, mock_http):
        test_query = {"query": ""}

        test_query_json = json.dumps(test_query)
        resource_info = {"results": {"phenotypes": {}, "info": {}}, "searchQuery": ""}
        self.mock_response.data = json.dumps(resource_info).encode("utf-8")
        mock_http.return_value = self.mock_response

        test_api_obj = PicSureClient.PicSureConnectionAPI(self.test_url_picsure, self.test_url_psama, self.test_token)
        test_info = test_api_obj.search(self.test_uuid)
        self.assertEqual(self.mock_response.data.decode(), test_info)
        mock_http.assert_called_with("POST", self.test_url_picsure + "search/" + self.test_uuid, fields=None,
                                     body=test_query_json, headers=self.mock_response.headers)

    @patch('urllib3.PoolManager.request')
    def test_connectionapi_func_search_term(self, mock_http):
        test_query = {"query": "some-term"}
        test_query_json = json.dumps(test_query)

        resource_info = {"results": {"phenotypes": {}, "info": {}}, "searchQuery": "some-term"}
        json_content = json.dumps(resource_info).encode("utf-8")
        self.mock_response.data = json_content
        mock_http.return_value = self.mock_response

        test_api_obj = PicSureClient.PicSureConnectionAPI(self.test_url_picsure, self.test_url_psama, self.test_token)
        test_info = test_api_obj.search(self.test_uuid, test_query_json)
        self.assertEqual(json_content.decode(), test_info)
        mock_http.assert_called_with("POST", self.test_url_picsure + "search/" + self.test_uuid,
                                     fields=None, body=test_query_json, headers=self.mock_response.headers)

    @patch('urllib3.PoolManager.request')
    def test_connectionapi_func_query_async(self, mock_http):
        test_query = {"query": {}}
        test_query_json = json.dumps(test_query)

        resource_info = {"results": {}}
        json_content = json.dumps(resource_info)
        self.mock_response.data = json_content.encode("utf-8")
        mock_http.return_value = self.mock_response

        test_api_obj = PicSureClient.PicSureConnectionAPI(self.test_url_picsure, self.test_url_psama, self.test_token)
        test_info = test_api_obj.asyncQuery(self.test_uuid, test_query_json)
        self.assertEqual(json_content, test_info)
        mock_http.assert_called_with("POST", self.test_url_picsure + "query", fields=None,
                                     body=test_query_json, headers=self.mock_response.headers)

    @patch('urllib3.PoolManager.request')
    def test_connectionapi_func_query_sync(self, mock_http):
        test_query = {"query": {}}
        test_query_json = json.dumps(test_query)

        resource_info = {"results": {}}
        json_content = json.dumps(resource_info)
        self.mock_response.data = json_content.encode("utf-8")
        mock_http.return_value = self.mock_response

        test_api_obj = PicSureClient.PicSureConnectionAPI(self.test_url_picsure, self.test_url_psama, self.test_token)
        test_info = test_api_obj.syncQuery(self.test_uuid, test_query_json)
        self.assertEqual(json_content, test_info)
        mock_http.assert_called_with("POST", self.test_url_picsure + "query/sync", fields=None, body=test_query_json,
                                     headers=self.mock_response.headers)

    @patch('urllib3.PoolManager.request')
    def test_connectionapi_func_query_status(self, mock_http):
        test_resource_uuid = "some_resource_uuid"

        test_query = {"resourceUUID": test_resource_uuid, "query": {}, "resourceCredentials": {}}
        test_query_json = json.dumps(test_query)

        resource_info = {"results": {}}
        json_content = json.dumps(resource_info)
        self.mock_response.data = json_content.encode("utf-8")
        mock_http.return_value = self.mock_response

        test_api_obj = PicSureClient.PicSureConnectionAPI(self.test_url_picsure, self.test_url_psama, self.test_token)
        test_info = test_api_obj.queryStatus(test_resource_uuid, self.test_uuid)
        self.assertEqual(json_content, test_info)
        mock_http.assert_called_with("POST", self.test_url_picsure + "query/" + self.test_uuid + "/status",
                                     fields=None, body=test_query_json, headers=self.mock_response.headers)

    @patch('urllib3.PoolManager.request')
    def test_connectionapi_func_query_results(self, mock_http):
        test_query_uuid = self.test_uuid
        test_resource_uuid = "some_resource_uuid"
        test_query_json = "{}"

        resource_info = {"results": {}}
        json_content = json.dumps(resource_info)
        self.mock_response.data = json_content.encode("utf-8")
        mock_http.return_value = self.mock_response

        test_api_obj = PicSureClient.PicSureConnectionAPI(self.test_url_picsure, self.test_url_psama, self.test_token)
        test_info = test_api_obj.queryResult(test_resource_uuid, test_query_uuid)
        self.assertEqual(json_content, test_info)
        mock_http.assert_called_with("POST", self.test_url_picsure + "query/" + test_query_uuid + "/result",
                                     fields=None, body=test_query_json, headers=self.mock_response.headers)
