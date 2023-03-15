# -*- coding: utf-8 -*-

"""PIC-SURE Connection and Authorization Library"""
import ssl

import certifi
import urllib3

import PicSureClient
import httplib2
import json
from urllib.parse import urlparse
import sys


class Client:
    @classmethod
    def version(self):
        print(PicSureClient.__package__ + " Library (version " + PicSureClient.__version__ + ")\n")

    @classmethod
    def help(self):
        print("""
        [HELP] PicSureClient.Client()
            .version()                                                 gives version information for library
            .connect(<url>, <token> [, allowSelfSignedSSL = True])     returns a connection object
            .connect_local(<token>)                                   return a connection object from all-in-one stack
        """)

    @classmethod
    def connect(self, url, token, allowSelfSignedSSL=False):
        """ PicSure.connect returns a configured instance of a PicSureClient.Connection class """
        return PicSureClient.Connection(url, token, allowSelfSignedSSL)

    ####
    ## Use kwargs to override some initializations in Connection class
    ## adding kwargs to the connection class will not break any existing notebooks
    ####
    @classmethod
    def connect_local(self, token, allowSelfSignedSSL=False):
        """ PicSure.connect returns a configured instance of a PicSureClient.Connection class """

        kwargs = {"psama_override": 'http://wildfly:8080/pic-sure-auth-services/auth/'}

        return PicSureClient.Connection('http://wildfly:8080/pic-sure-api-2/PICSURE/', token, allowSelfSignedSSL,
                                        **kwargs)


class Connection:
    def __init__(self, url, token, allowSelfSignedSSL=False, **kwargs):
        url_ret = urlparse(url)
        self.psama_url = url_ret.scheme + "://" + url_ret.netloc + "/psama/"
        self.url = url_ret.scheme + "://" + url_ret.netloc + url_ret.path

        if 'psama_override' in kwargs:
            self.psama_url = kwargs.get('psama_override')

        if 'url_override' in kwargs:
            self.url = kwargs.get('url_overrride')

        self.resource_uuids = []

        if not self.url.endswith("/"):
            self.url = self.url + "/"

        self._token = token

        self.AllowSelfSigned = allowSelfSignedSSL

        self.httpConn = PicSureHttpClient(url=self.url, token=self._token, allowSelfSigned=self.AllowSelfSigned)

        if allowSelfSignedSSL is True:
            # user is allowing self-signed SSL certs, serve them a black box warning
            print("""\033[38;5;91;40m\n
+=========================================================================================+
|        [ WARNING ] you are specifying that you WANT to allow self-signed SSL            |
|        certificates to be acceptable for connections.  This may be useful for           |
|        working in a development environment or on systems that host public              |
|        data.  BEST SECURITY PRACTICES ARE THAT IF YOU ARE WORKING WITH SENSITIVE        |
|        DATA THEN ALL SSL CERTS BY THOSE EVIRONMENTS SHOULD NOT BE SELF-SIGNED.          |
+=========================================================================================+
\033[39;49m""")

        # test server connection and automatically list all the Resource UUIDs
        self.list()

    def help(self):
        print("""
        [HELP] PicSureClient.Client.connect(url, token [, allowSelfSignedSSL = True])
            .list()                         Prints a list of available resources
            .about(resource_uuid)           Prints details about a specific resource

        [Connect to Resource]
            To connect to a resource load its associated resource code library
            and then pass the API connection object (this object) to the
            the library's Client object like this:

            myPicSureConn = PicSureClient.Client.connect(url, token)
            myResourceAdapter = PicSureHpdsLib.Adapter(myPicSureConn)
            myResource = myResourceAdapter.useResource(resource_uuid)
            myResource.help()

            * The above example connects to a HPDS resource.  Each resource has
              a specific type which has its own adapter library.  Libraries will
              follow the naming convention: "PicSureXyzLib" where "Xyz"
              specifies the adapter's storage format.

            ** By default, self-signed SSL certificates are rejected.  To change
              this behavior pass "allowSelfSignedSSL = True" when creating a
              PIC-SURE Connection instance. THE DEFAULT BEHAVIOR OF THIS SETTING IS
              CONSIDERED BEST SECURITY PRACTICES. SELF-SIGNED SSL CERTIFICATES SHOULD
              NEVER BE USED TO PROTECT SYSTEMS HOSTING SENSITIVE DATA.
        """)

    def about(self, resourceId):
        results = self.getInfo(resourceId)
        print(str("---[ Info about " + resourceId + " ]").ljust(94, '-'))
        if type(results) is str:
            info = json.loads(results)
            print(json.dumps(info, indent=2))
        else:
            print("!!!! ERROR !!!!")
            print(json.dumps(results, indent=2))

    def list(self):
        listing = json.loads(self.getResources())
        print("+".ljust(39, '-') + '+'.ljust(55, '-') + "+")
        print("|  Resource UUID".ljust(39, ' ') + '|  Resource Name'.ljust(55, ' ') + "|")
        print("+".ljust(39, '-') + '+'.ljust(55, '-') + "+")
        for rec in listing:
            if type(listing) == list:
                print('| ' + rec.ljust(36, ' ') + " | " + "".ljust(53) + "|")
            else:
                print('| ' + rec.ljust(36, ' ') + " | " + listing[rec].ljust(53) + "|")
        print("+".ljust(39, '-') + '+'.ljust(55, '-') + "+")

    def getInfo(self, uuid):
        return self.httpConn.post("info/" + str(uuid))
        # if resp_headers["status"] != "200":
        #     return {"error": True, "headers": resp_headers, "content": json.loads(content.decode("utf-8"))}
        # else:
        #     return content.decode('utf-8')

    def getResources(self):
        """PicSureClient.resources() function is used to list all resources on the connected endpoint"""
        content = self.httpConn.get("info/resources")
        if hasattr(content, 'error') and content.error is True:
            if hasattr(content, 'status') and content.status == 401:
                return {"error": True, "message": "Invalid token"}

        self.resource_uuids = json.loads(content)
        if type(self.resource_uuids) == dict:
            self.resource_uuids = list(self.resource_uuids.keys())
        return content

    def _api_obj(self):
        """PicSureClient._api_obj() function returns a new, preconfigured PicSureConnectionAPI class instance """
        return PicSureConnectionAPI(self.url, self.psama_url, self._token, allowSelfSignedSSL=self.AllowSelfSigned)


class PicSureClientException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return "Error: %s" % self.value


class PicSureConnectionAPI:
    def __init__(self, url_picsure, url_psama, token, allowSelfSignedSSL=False):

        # save values
        self.url_picsure = url_picsure
        self.url_psama = url_psama
        self._token = token
        self.AllowSelfSigned = allowSelfSignedSSL
        self.psamaHttpConnect = PicSureHttpClient(self.url_psama, self._token, self.AllowSelfSigned)
        self.picsureHttpConnect = PicSureHttpClient(self.url_picsure, self._token, self.AllowSelfSigned)

    def profile(self):
        from urllib.parse import urlparse
        response_str = self.psamaHttpConnect.get("user/me")

        # Make sure we have a "queryTemplate"
        response_objs = json.loads(response_str)
        if "queryTemplate" not in response_objs:
            # load the query template
            content = self.psamaHttpConnect.get("user/me/queryTemplate/");
            # TODO: Convert printout to user match on '{error: true, }'
            if content == '{"error":true}':
                print("ERROR: HTTP response was bad requesting application queryTemplate")
                return '{"results":{}, "error":"true"}'
            else:
                response_objs["queryTemplate"] = json.loads(content)["queryTemplate"]

        return json.dumps(response_objs)

    def info(self, resource_uuid):
        # https://github.com/hms-dbmi/pic-sure/blob/master/pic-sure-resources/pic-sure-resource-api/src/main/java/edu/harvard/dbmi/avillach/service/ResourceWebClient.java#L43
        httpConn = httplib2.Http(disable_ssl_certificate_validation=self.AllowSelfSigned)
        httpHeaders = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + self._token}
        url = self.url_picsure + "info/" + resource_uuid
        (resp_headers, content) = httpConn.request(uri=url, method="POST", headers=httpHeaders, body="{}")

    def search(self, resource_uuid, query=None):
        # make sure a Resource UUID is passed via the body of these commands
        # https://github.com/hms-dbmi/pic-sure/blob/master/pic-sure-resources/pic-sure-resource-api/src/main/java/edu/harvard/dbmi/avillach/service/ResourceWebClient.java#L69
        httpConn = httplib2.Http(disable_ssl_certificate_validation=self.AllowSelfSigned, )
        httpHeaders = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + self._token}
        if query == None:
            bodystr = json.dumps({"query": ""})
        else:
            bodystr = str(query)
        url = self.url_picsure + "search/" + resource_uuid
        (resp_headers, content) = httpConn.request(uri=url, method="POST", headers=httpHeaders, body=bodystr)
        if resp_headers["status"] != "200":
            print("ERROR: HTTP response was bad")
            print(url)
            print(resp_headers)
            print(content.decode("utf-8"))
            return '{"results":{}, "error":"true"}'
        else:
            return content.decode("utf-8")

    def asyncQuery(self, resource_uuid, query):
        # make sure a Resource UUID is passed via the body of these commands
        # https://github.com/hms-dbmi/pic-sure/blob/master/pic-sure-resources/pic-sure-resource-api/src/main/java/edu/harvard/dbmi/avillach/service/ResourceWebClient.java#L98
        httpConn = httplib2.Http(disable_ssl_certificate_validation=self.AllowSelfSigned)
        httpHeaders = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + self._token}
        url = self.url_picsure + "query"
        (resp_headers, content) = httpConn.request(uri=url, method="POST", headers=httpHeaders, body=query)
        if resp_headers["status"] != "200":
            print("ERROR: HTTP response was bad")
            print(url)
            print(resp_headers)
            print(content.decode('utf-8'))
            raise PicSureClientException('An error has occurred with the server')
        else:
            return content.decode("utf-8")

    def syncQuery(self, resource_uuid, query):
        # make sure a Resource UUID is passed via the body of these commands
        # https://github.com/hms-dbmi/pic-sure/blob/master/pic-sure-resources/pic-sure-resource-api/src/main/java/edu/harvard/dbmi/avillach/service/ResourceWebClient.java#L186
        httpConn = httplib2.Http(disable_ssl_certificate_validation=self.AllowSelfSigned)
        httpHeaders = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + self._token}
        url = self.url_picsure + "query/sync"
        (resp_headers, content) = httpConn.request(uri=url, method="POST", headers=httpHeaders, body=query)
        self.picsureHttpConnect.post("query/sync", data=query)

    def queryStatus(self, resource_uuid, query_uuid, query_body="{}"):
        # https://github.com/hms-dbmi/pic-sure/blob/master/pic-sure-resources/pic-sure-resource-api/src/main/java/edu
        # /harvard/dbmi/avillach/service/ResourceWebClient.java#L124 We need to supply a fully formed query body so
        # PSAMA can parse it.  The adapter should pass in an appropriate template.
        query_obj = json.loads(query_body)
        query = {"resourceUUID": resource_uuid, "query": query_obj, "resourceCredentials": {}}
        return self.picsureHttpConnect.post("query/" + query_uuid + "/status", data=json.dumps(query))

    # This operation is handled entirely in PIC-SURE, and does not need a resource connection
    def queryMetadata(self, query_uuid):
        return self.psamaHttpConnect.get("query/" + query_uuid + "/metadata")

    def queryResult(self, resource_uuid, query_uuid):
        # https://github.com/hms-dbmi/pic-sure/blob/master/pic-sure-resources/pic-sure-resource-api/src/main/java/edu/harvard/dbmi/avillach/service/ResourceWebClient.java#L155
        query = '{}'
        content = self.picsureHttpConnect.post("query/" + query_uuid + "/result", data=query)
        if hasattr(content, 'error') and content.error:
            return json.dumps(content)


class PicSureHttpClient:
    def __init__(self, url, token, allowSelfSigned, **kwargs):
        self.url = url
        self.token = token
        self.allow_self_signed = allowSelfSigned
        if self.allow_self_signed:
            urllib3.disable_warnings()
            self.http = urllib3.PoolManager(
                cert_reqs='CERT_REQUIRED',
                ca_certs=certifi.where(),
                assert_hostname=False
            )
        else:
            self.http = urllib3.PoolManager()

    def get(self, path, params=None):
        return self._request('GET', path, params)

    def post(self, path, params=None, data=None):
        return self._request('POST', path, params, data)

    def put(self, path, params=None, data=None):
        return self._request('PUT', path, params, data)

    def delete(self, path, params=None):
        return self._request('DELETE', path, params)

    def _request(self, method, path, params=None, data=None):
        url = self.url + path
        headers = {'Authorization': 'Bearer ' + self.token}
        if data is not None:
            headers['Content-Type'] = 'application/json'
        if self.allow_self_signed:
            headers['verify'] = False
        try:
            response = self.http.request(method, url, fields=params, body=data, headers=headers)
            result = {"result": response.data.decode('utf-8'), "error": False}
        except urllib3.exceptions.SSLError as e:
            print("ERROR: SSL error")
            print(url)
            print(e)
            raise PicSureClientException('An error has occurred with the server')
        else:
            if response.status != 200:
                print("ERROR: HTTP response was bad")
                print(url)
                print(response.status)
                print(response.headers)
                result["error"] = True
                if response.status == 401:
                    result["message"] = "Invalid token. Unable to authenticate."
                return result
            else:
                return response.data.decode('utf-8')
