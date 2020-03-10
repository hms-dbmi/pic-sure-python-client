#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `PicSureClient` package."""


import PicSureClient
import unittest
from unittest.mock import patch
import io
import sys
import json

class TestClient(unittest.TestCase):

    def test_client_func_version(self):
        with patch('sys.stdout', new=io.StringIO()) as fake_stdout:
            PicSureClient.Client.version()
            sys.stdout = sys.__stdout__  # Reset redirect. Needed for it to work!
            captured = fake_stdout.getvalue()
            print("Captured:\n" + captured)
            self.assertTrue(len(captured.strip()) > 0)


    def test_client_func_help(self):
        with patch('sys.stdout', new=io.StringIO()) as fake_stdout:
            PicSureClient.Client.help()
            sys.stdout = sys.__stdout__  # Reset redirect. Needed for it to work!
            captured = fake_stdout.getvalue()
            print("Captured:\n" + captured)
            self.assertTrue(len(captured.strip()) > 0)


    def test_client_func_connect(self):
        test_url = "http://some.url/PIC-SURE/"
        test_token = "some_security_token"

        test_obj = PicSureClient.Client.connect(test_url, test_token)
        self.assertIsInstance(test_obj, PicSureClient.Connection, "Client.connect() returns the wrong object type")
        self.assertEqual(test_obj.url, test_url)
        self.assertEqual(test_obj._token, test_token)
        self.assertEqual(test_obj.AllowSelfSigned, False, "Accepting self-signed SSL certificates should NOT be the default!")


    def test_client_func_connect_selfsigned_ssl(self):
        test_url = "http://some.url/PIC-SURE/"
        test_token = "some_security_token"

        with patch('sys.stdout', new=io.StringIO()) as fake_stdout:
            test_obj = PicSureClient.Client.connect(test_url, test_token, True)
            sys.stdout = sys.__stdout__  # Reset redirect. Needed for it to work!
            captured = fake_stdout.getvalue()
            print("Captured:\n" + captured)
            self.assertTrue(len(captured.strip()) > 0, "Should print a warning message when allowing self-signed SSL certificates!")
            self.assertEqual(test_obj.AllowSelfSigned, True, "Specified to allow self-signed SSL certificates but it did not propogate")



class TestConnection(unittest.TestCase):
    def test_connection_create(self):
        test_url = "http://some.url/PIC-SURE/"
        test_token = "some_security_token"
        test_conn = PicSureClient.Connection(test_url, test_token)

        self.assertEqual(test_conn.url, test_url)
        self.assertEqual(test_conn._token, test_token)
        self.assertEqual(test_conn.AllowSelfSigned, False, "Accepting self-signed SSL certificates should NOT be the default!")


    def test_connection_func_help(self):
        test_url = "http://some.url/PIC-SURE/"
        test_token = "some_security_token"
        test_conn = PicSureClient.Connection(test_url, test_token)

        with patch('sys.stdout', new=io.StringIO()) as fake_stdout:
            test_conn.help()
            sys.stdout = sys.__stdout__  # Reset redirect. Needed for it to work!
            captured = fake_stdout.getvalue()
            print("Captured:\n" + captured)
            self.assertTrue(len(captured.strip()) > 0, "Should print help message")


    @patch('httplib2.Http.request')
    def test_connection_func_list(self, mock_http):
        test_url = "http://some.url/PIC-SURE/"
        test_token = "some_security_token"

        resp_headers = {"status": "200"}
        json_content = json.dumps(["resource-1-uuid", "resource-2-uuid", "resource-3-uuid"])
        mock_http.return_value = (resp_headers, json_content.encode("utf-8"))

        test_conn = PicSureClient.Connection(test_url, test_token)
        with patch('sys.stdout', new=io.StringIO()) as fake_stdout:
            test_conn.list()
            sys.stdout = sys.__stdout__  # Reset redirect. Needed for it to work!
            captured = fake_stdout.getvalue()
            print("Captured:\n" + captured)
            self.assertTrue(len(captured.strip()) > 0, "Should print list of resource UUIDs")


    @patch('httplib2.Http.request')
    def test_connection_func_about(self, mock_http):
        test_url = "http://some.url/PIC-SURE/"
        test_token = "some_security_token"

        resp_headers = {"status": "200"}
        json_content = json.dumps(["resource-1-uuid", "resource-2-uuid", "resource-3-uuid"])
        mock_http.return_value = (resp_headers, json_content.encode("utf-8"))

        test_conn = PicSureClient.Connection(test_url, test_token)
        with patch('sys.stdout', new=io.StringIO()) as fake_stdout:
            test_conn.list()
            sys.stdout = sys.__stdout__  # Reset redirect. Needed for it to work!
            captured = fake_stdout.getvalue()
            print("Captured:\n" + captured)
            self.assertTrue(len(captured.strip()) > 0, "Should print list of resource UUIDs")


    @patch('httplib2.Http.request')
    def test_connection_func_getResources(self, mock_http):
        test_url = "http://some.url/PIC-SURE/"
        test_token = "some_security_token"

        resp_headers = {"status": "200"}
        resource_list = ["resource-1-uuid", "resource-2-uuid", "resource-3-uuid"]
        json_content = json.dumps(resource_list)
        mock_http.return_value = (resp_headers, json_content.encode("utf-8"))

        test_conn = PicSureClient.Connection(test_url, test_token)
        test_list = test_conn.getResources()
        self.assertEqual(json_content, test_list)
        mock_http.assert_called_with(uri=test_url + "info/resources", headers={'Content-Type': 'application/json', 'Authorization':'Bearer '+test_token}, method="GET")


    @patch('httplib2.Http.request')
    def test_connection_func_getInfo(self, mock_http):
        test_url = "http://some.url/PIC-SURE/"
        test_token = "some_security_token"
        test_uuid = "some_resource_uuid"

        resp_headers = {"status": "200"}
        resource_info = {"uuid":test_uuid, "about":"some information goes here"}
        json_content = json.dumps(resource_info)
        mock_http.return_value = (resp_headers, json_content.encode("utf-8"))
        print(json_content)

        test_conn = PicSureClient.Connection(test_url, test_token)
        test_info = test_conn.getInfo(test_uuid)
        self.assertEqual(json_content, test_info)
        mock_http.assert_called_with(body="{}", uri=test_url + "info/"+test_uuid, headers={'Content-Type': 'application/json', 'Authorization':'Bearer '+test_token}, method="POST")


    def test_connection_func_api_obj(self):
        test_url = "http://some.url/PIC-SURE/"
        test_token = "some_security_token"

        test_conn = PicSureClient.Connection(test_url, test_token)
        test_api_obj = test_conn._api_obj()
        self.assertIsInstance(test_api_obj, PicSureClient.PicSureConnectionAPI, "Connection._api_obj() returns the wrong object type")
        self.assertEqual(test_url, test_api_obj.url_picsure)
        self.assertEqual(test_token, test_api_obj._token)
        self.assertEqual(test_api_obj.AllowSelfSigned, False, "Accepting self-signed SSL certificates should NOT be the default!")



class TestConnectionAPI(unittest.TestCase):
    def test_connection_api_create(self):
        test_url_psama = "http://some.url/PSAMA/"
        test_url_picsure = "http://some.url/PIC-SURE/"
        test_token = "some_security_token"

        test_api_obj = PicSureClient.PicSureConnectionAPI(test_url_picsure, test_url_psama, test_token)
        self.assertEqual(test_url_psama, test_api_obj.url_psama)
        self.assertEqual(test_url_picsure, test_api_obj.url_picsure)
        self.assertEqual(test_token, test_api_obj._token)
        self.assertEqual(test_api_obj.AllowSelfSigned, False, "Accepting self-signed SSL certificates should NOT be the default!")


    @patch('httplib2.Http.request')
    def test_connectionapi_func_profile(self, mock_http):
        test_url_psama = "http://some.url/PSAMA/"
        test_url_picsure = "http://some.url/PIC-SURE/"
        test_token = "some_security_token"
        test_uuid = "some_resource_uuid"

        resp_headers = {"status": "200"}
        resource_info = {"uuid":test_uuid, "email":"some@email.edu", "privileges":["SUPER_ADMIN","ROLE_SYSTEM","PIC-SURE Unrestricted Query","ADMIN"]}
        json_content = json.dumps(resource_info)
        mock_http.return_value = (resp_headers, json_content.encode("utf-8"))

        test_api_obj = PicSureClient.PicSureConnectionAPI(test_url_picsure, test_url_psama, test_token)
        test_profile = test_api_obj.profile()
        self.assertEqual(json_content, test_profile)
        mock_http.assert_called_with(uri=test_url_psama + "user/me", headers={'Content-Type': 'application/json', 'Authorization':'Bearer '+test_token}, method="GET")


    @patch('httplib2.Http.request')
    def test_connectionapi_func_info(self, mock_http):
        test_url_psama = "http://some.url/PSAMA/"
        test_url_picsure = "http://some.url/PIC-SURE/"
        test_token = "some_security_token"
        test_uuid = "some_resource_uuid"

        resp_headers = {"status": "200"}
        resource_info = {"uuid":test_uuid, "some_info":{}}
        json_content = json.dumps(resource_info)
        mock_http.return_value = (resp_headers, json_content.encode("utf-8"))

        test_api_obj = PicSureClient.PicSureConnectionAPI(test_url_picsure, test_url_psama, test_token)
        test_info = test_api_obj.info(test_uuid)
        self.assertEqual(json_content, test_info)
        mock_http.assert_called_with(uri=test_url_picsure + "info/" + test_uuid, headers={'Content-Type': 'application/json', 'Authorization':'Bearer '+test_token}, method="POST", body="{}")


    @patch('httplib2.Http.request')
    def test_connectionapi_func_search_blank(self, mock_http):
        test_url_psama = "http://some.url/PSAMA/"
        test_url_picsure = "http://some.url/PIC-SURE/"
        test_token = "some_security_token"
        test_uuid = "some_resource_uuid"
        test_query = {"query":""}

        test_query_json = json.dumps(test_query)
        resp_headers = {"status": "200"}
        resource_info = {"results":{"phenotypes":{}, "info":{}},"searchQuery":""}
        json_content = json.dumps(resource_info)
        mock_http.return_value = (resp_headers, json_content.encode("utf-8"))

        test_api_obj = PicSureClient.PicSureConnectionAPI(test_url_picsure, test_url_psama, test_token)
        test_info = test_api_obj.search(test_uuid)
        self.assertEqual(json_content, test_info)
        mock_http.assert_called_with(uri=test_url_picsure + "search/" + test_uuid, headers={'Content-Type': 'application/json', 'Authorization':'Bearer '+test_token}, method="POST", body=test_query_json)


    @patch('httplib2.Http.request')
    def test_connectionapi_func_search_term(self, mock_http):
        test_url_psama = "http://some.url/PSAMA/"
        test_url_picsure = "http://some.url/PIC-SURE/"
        test_token = "some_security_token"
        test_uuid = "some_resource_uuid"
        test_query = {"query":"some-term"}
        test_query_json = json.dumps(test_query)

        resp_headers = {"status": "200"}
        resource_info = {"results":{"phenotypes":{}, "info":{}},"searchQuery":"some-term"}
        json_content = json.dumps(resource_info)
        mock_http.return_value = (resp_headers, json_content.encode("utf-8"))

        test_api_obj = PicSureClient.PicSureConnectionAPI(test_url_picsure, test_url_psama, test_token)
        test_info = test_api_obj.search(test_uuid, test_query_json)
        self.assertEqual(json_content, test_info)
        mock_http.assert_called_with(uri=test_url_picsure + "search/" + test_uuid, headers={'Content-Type': 'application/json', 'Authorization':'Bearer '+test_token}, method="POST", body=test_query_json)


    @patch('httplib2.Http.request')
    def test_connectionapi_func_query_async(self, mock_http):
        test_url_psama = "http://some.url/PSAMA/"
        test_url_picsure = "http://some.url/PIC-SURE/"
        test_token = "some_security_token"
        test_uuid = "some_resource_uuid"
        test_query = {"query":{}}
        test_query_json = json.dumps(test_query)

        resp_headers = {"status": "200"}
        resource_info = {"results":{}}
        json_content = json.dumps(resource_info)
        mock_http.return_value = (resp_headers, json_content.encode("utf-8"))

        test_api_obj = PicSureClient.PicSureConnectionAPI(test_url_picsure, test_url_psama, test_token)
        test_info = test_api_obj.asyncQuery(test_uuid, test_query_json)
        self.assertEqual(json_content, test_info)
        mock_http.assert_called_with(uri=test_url_picsure + "query", headers={'Content-Type': 'application/json', 'Authorization':'Bearer '+test_token}, method="POST", body=test_query_json)


    @patch('httplib2.Http.request')
    def test_connectionapi_func_query_sync(self, mock_http):
        test_url_psama = "http://some.url/PSAMA/"
        test_url_picsure = "http://some.url/PIC-SURE/"
        test_token = "some_security_token"
        test_uuid = "some_resource_uuid"
        test_query = {"query":{}}
        test_query_json = json.dumps(test_query)

        resp_headers = {"status": "200"}
        resource_info = {"results":{}}
        json_content = json.dumps(resource_info)
        mock_http.return_value = (resp_headers, json_content.encode("utf-8"))

        test_api_obj = PicSureClient.PicSureConnectionAPI(test_url_picsure, test_url_psama, test_token)
        test_info = test_api_obj.syncQuery(test_uuid, test_query_json)
        self.assertEqual(json_content, test_info)
        mock_http.assert_called_with(uri=test_url_picsure + "query/sync", headers={'Content-Type': 'application/json', 'Authorization':'Bearer '+test_token}, method="POST", body=test_query_json)


    @patch('httplib2.Http.request')
    def test_connectionapi_func_query_status(self, mock_http):
        test_url_psama = "http://some.url/PSAMA/"
        test_url_picsure = "http://some.url/PIC-SURE/"
        test_token = "some_security_token"
        test_resource_uuid = "some_resource_uuid"
        test_query_uuid = "some_query_uuid"
        test_query = {"resourceUUID": test_resource_uuid, "query": {}, "resourceCredentials":{}}
        test_query_json = json.dumps(test_query)

        resp_headers = {"status": "200"}
        resource_info = {"results":{}}
        json_content = json.dumps(resource_info)
        mock_http.return_value = (resp_headers, json_content.encode("utf-8"))

        test_api_obj = PicSureClient.PicSureConnectionAPI(test_url_picsure, test_url_psama, test_token)
        test_info = test_api_obj.queryStatus(test_resource_uuid, test_query_uuid)
        self.assertEqual(json_content, test_info)
        mock_http.assert_called_with(uri=test_url_picsure + "query/" + test_query_uuid + "/status", headers={'Content-Type': 'application/json', 'Authorization':'Bearer '+test_token}, method="POST", body=test_query_json)


    @patch('httplib2.Http.request')
    def test_connectionapi_func_query_results(self, mock_http):
        # TODO: properly implement this functionality
        test_url_psama = "http://some.url/PSAMA/"
        test_url_picsure = "http://some.url/PIC-SURE/"
        test_token = "some_security_token"
        test_query_uuid = "some_query_uuid"
        test_resource_uuid = "some_resource_uuid"
        test_query_json = "{}"

        resp_headers = {"status": "200"}
        resource_info = {"results":{}}
        json_content = json.dumps(resource_info)
        mock_http.return_value = (resp_headers, json_content.encode("utf-8"))

        test_api_obj = PicSureClient.PicSureConnectionAPI(test_url_picsure, test_url_psama, test_token)
        test_info = test_api_obj.queryResult(test_resource_uuid, test_query_uuid)
        self.assertEqual(json_content, test_info)
        mock_http.assert_called_with(uri=test_url_picsure + "query/" + test_query_uuid + "/result", headers={'Content-Type': 'application/json', 'Authorization':'Bearer '+test_token}, method="POST", body=test_query_json)
