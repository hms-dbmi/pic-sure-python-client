#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `PicSureClient` package."""


import PicSureClient
import unittest
from unittest.mock import patch, MagicMock
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
            PicSureClient.Client.version()
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
    def test_connection_func_list(self, MockHttp):
        test_url = "http://some.url/PIC-SURE/"
        test_token = "some_security_token"

        resp_headers = {"status": "200"}
        json_content = json.dumps(["resource-1-uuid", "resource-2-uuid", "resource-3-uuid"])
        MockHttp.return_value = (resp_headers, json_content.encode("utf-8"))

        test_conn = PicSureClient.Connection(test_url, test_token)
        with patch('sys.stdout', new=io.StringIO()) as fake_stdout:
            test_conn.list()
            sys.stdout = sys.__stdout__  # Reset redirect. Needed for it to work!
            captured = fake_stdout.getvalue()
            print("Captured:\n" + captured)
            self.assertTrue(len(captured.strip()) > 0, "Should print list of resource UUIDs")


    @patch('httplib2.Http.request')
    def test_connection_func_about(self, MockHttp):
        test_url = "http://some.url/PIC-SURE/"
        test_token = "some_security_token"

        resp_headers = {"status": "200"}
        json_content = json.dumps(["resource-1-uuid", "resource-2-uuid", "resource-3-uuid"])
        MockHttp.return_value = (resp_headers, json_content.encode("utf-8"))

        test_conn = PicSureClient.Connection(test_url, test_token)
        with patch('sys.stdout', new=io.StringIO()) as fake_stdout:
            test_conn.list()
            sys.stdout = sys.__stdout__  # Reset redirect. Needed for it to work!
            captured = fake_stdout.getvalue()
            print("Captured:\n" + captured)
            self.assertTrue(len(captured.strip()) > 0, "Should print list of resource UUIDs")


    @patch('httplib2.Http.request')
    def test_connection_func_getResources(self, MockHttp):
        test_url = "http://some.url/PIC-SURE/"
        test_token = "some_security_token"

        resp_headers = {"status": "200"}
        resource_list = ["resource-1-uuid", "resource-2-uuid", "resource-3-uuid"]
        json_content = json.dumps(resource_list)
        MockHttp.return_value = (resp_headers, json_content.encode("utf-8"))

        test_conn = PicSureClient.Connection(test_url, test_token)
        test_list = test_conn.getResources()
        self.assertEqual(json_content, test_list)
        MockHttp.assert_called_with(uri=test_url + "info/resources", headers={'Content-Type': 'application/json', 'Authorization':'Bearer '+test_token}, method="GET")


    @patch('httplib2.Http.request')
    def test_connection_func_getInfo(self, MockHttp):
        test_url = "http://some.url/PIC-SURE/"
        test_token = "some_security_token"
        test_uuid = "some_resource_uuid"

        resp_headers = {"status": "200"}
        resource_info = {"uuid":test_uuid, "about":"some information goes here"}
        json_content = json.dumps(resource_info)
        MockHttp.return_value = (resp_headers, json_content.encode("utf-8"))
        print(json_content)

        test_conn = PicSureClient.Connection(test_url, test_token)
        test_info = test_conn.getInfo(test_uuid)
        self.assertEqual(json_content, test_info)
        MockHttp.assert_called_with(body="{}", uri=test_url + "info/"+test_uuid, headers={'Content-Type': 'application/json', 'Authorization':'Bearer '+test_token}, method="POST")


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


