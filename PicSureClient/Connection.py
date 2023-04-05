# -*- coding: utf-8 -*-

"""PIC-SURE Connection and Authorization Library"""
import urllib3

import PicSureClient
import json
from urllib.parse import urlparse


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
        try:
            print("+".ljust(39, '-') + '+'.ljust(55, '-') + "+")
            print("|  Resource UUID".ljust(39, ' ') + '|  Resource Name'.ljust(55, ' ') + "|")
            print("+".ljust(39, '-') + '+'.ljust(55, '-') + "+")
            for rec in listing:
                if type(listing) == list:
                    print('| ' + rec.ljust(36, ' ') + " | " + "".ljust(53) + "|")
                else:
                    print('| ' + rec.ljust(36, ' ') + " | " + listing[rec].ljust(53) + "|")
            print("+".ljust(39, '-') + '+'.ljust(55, '-') + "+")
        except:
            print("!!!! ERROR !!!!")
            print(json.dumps(listing, indent=2))

    def getInfo(self, uuid):
        content = self.httpConn.post("info/" + str(uuid))
        if hasattr(content, 'error') and content.error is True:
            return {"error": True, "headers": content.headers, "content": json.loads(content)}
        return content

    def getResources(self):
        """PicSureClient.resources() function is used to list all resources on the connected endpoint"""
        content = self.httpConn.get("info/resources")
        if 'error' in content:
            if content['error'] is True:
                if 'status' in content and content['status'] == 401:
                    # If the response is an error, it is likely a 400 error. We need to return the response as part of the error
                    ret = ["ERROR:"]
                    if "message" in content:
                        ret.append("    " + content["message"])
                    else:
                        ret.append("    See message above.")
                    return json.dumps(ret).encode()
                else:
                    return '["ERROR:", "    See message above."]'.encode()
        else:
            self.resource_uuids = json.dumps(content)
            if type(self.resource_uuids) == dict:
                self.resource_uuids = list(self.resource_uuids.keys())

            # We need to return a string, not a dict
            if type(content) == dict:
                return json.dumps(content)

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
        response_str = self.psamaHttpConnect.get("user/me")

        if hasattr(response_str, 'error') and response_str.error:
            print("ERROR: HTTP response was bad requesting PSAMA profile")
            return '{"results":{}, "error":"true"}'

        # Make sure we have a "queryTemplate"
        response_objs = json.loads(response_str)
        if "queryTemplate" not in response_objs:
            # load the query template
            content = self.psamaHttpConnect.get("user/me/queryTemplate/")
            if hasattr(content, 'error') and content.error:
                print("ERROR: HTTP response was bad requesting application queryTemplate")
                return '{"results":{}, "error":"true"}'
            else:
                response_objs["queryTemplate"] = json.loads(content)["queryTemplate"]
        return json.dumps(response_objs)

    def info(self, resource_uuid):
        # https://github.com/hms-dbmi/pic-sure/blob/master/pic-sure-resources/pic-sure-resource-api/src/main/java/edu/harvard/dbmi/avillach/service/ResourceWebClient.java#L43
        content = self.picsureHttpConnect.post("info/" + resource_uuid, data='{}')
        if hasattr(content, 'error') and content.error:
            return json.dumps(content)
        return content

    def search(self, resource_uuid, query=None):
        # make sure a Resource UUID is passed via the body of these commands
        # https://github.com/hms-dbmi/pic-sure/blob/master/pic-sure-resources/pic-sure-resource-api/src/main/java/edu/harvard/dbmi/avillach/service/ResourceWebClient.java#L69
        bodystr = json.dumps({"query": ""}) if query is None else str(query)
        content = self.picsureHttpConnect.post("search/" + resource_uuid, data=bodystr)
        if hasattr(content, 'error') and content.error:
            return json.dumps(content)
        return content

    def asyncQuery(self, resource_uuid, query):
        # make sure a Resource UUID is passed via the body of these commands
        # https://github.com/hms-dbmi/pic-sure/blob/master/pic-sure-resources/pic-sure-resource-api/src/main/java/edu/harvard/dbmi/avillach/service/ResourceWebClient.java#L98
        content = self.picsureHttpConnect.post("query", data=query)
        if hasattr(content, 'error') and content.error:
            raise PicSureClientException('An error has occurred with the server')
        return content

    def syncQuery(self, resource_uuid, query):
        # make sure a Resource UUID is passed via the body of these commands
        # https://github.com/hms-dbmi/pic-sure/blob/master/pic-sure-resources/pic-sure-resource-api/src/main/java/edu/harvard/dbmi/avillach/service/ResourceWebClient.java#L186
        content = self.picsureHttpConnect.post("query/sync", data=query)
        if hasattr(content, 'error') and content.error:
            return json.dumps(content)
        return content

    def queryStatus(self, resource_uuid, query_uuid, query_body="{}"):
        # https://github.com/hms-dbmi/pic-sure/blob/master/pic-sure-resources/pic-sure-resource-api/src/main/java/edu
        # /harvard/dbmi/avillach/service/ResourceWebClient.java#L124 We need to supply a fully formed query body so
        # PSAMA can parse it.  The adapter should pass in an appropriate template.
        query_obj = json.loads(query_body)
        query = {"resourceUUID": resource_uuid, "query": query_obj, "resourceCredentials": {}}
        content = self.picsureHttpConnect.post("query/" + query_uuid + "/status", data=json.dumps(query))
        if hasattr(content, 'error') and content.error:
            return json.dumps(content)
        return content

    # This operation is handled entirely in PIC-SURE, and does not need a resource connection
    def queryMetadata(self, query_uuid):
        content = self.picsureHttpConnect.get("query/" + query_uuid + "/metadata", data=json.dumps({}))
        if hasattr(content, 'error') and content.error:
            return json.dumps(content)
        return content

    def queryResult(self, resource_uuid, query_uuid):
        # https://github.com/hms-dbmi/pic-sure/blob/master/pic-sure-resources/pic-sure-resource-api/src/main/java/edu/harvard/dbmi/avillach/service/ResourceWebClient.java#L155
        content = self.picsureHttpConnect.post("query/" + query_uuid + "/result", data='{}')
        if hasattr(content, 'error') and content.error:
            return json.dumps(content)
        return content


class PicSureHttpClient:
    def __init__(self, url, token, allowSelfSigned=False, **kwargs):
        self.url = url
        self.token = token
        self.allowSelfSigned = allowSelfSigned
        if self.allowSelfSigned is True:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            self.http = urllib3.PoolManager(cert_reqs='CERT_NONE')
        else:
            self.http = urllib3.PoolManager()

    def get(self, path, params=None, data=None):
        return self._request('GET', path, params, data)

    def post(self, path, params=None, data=None):
        return self._request('POST', path, params, data)

    def put(self, path, params=None, data=None):
        return self._request('PUT', path, params, data)

    def delete(self, path, params=None):
        return self._request('DELETE', path, params)

    def _request(self, method, path, params=None, data=None):
        url = self.url + path
        headers = self.setHeaders()
        try:
            response = self.http.request(method, url, fields=params, body=data, headers=headers)
        except (urllib3.exceptions.NewConnectionError, urllib3.exceptions.SSLError,
                urllib3.exceptions.MaxRetryError) as e:
            print('ERROR: The address "' + url + '" is invalid')
            return '["ERROR:", "   Invalid URL!"]'
        else:
            return self.handleResponse(response, url)

    def setHeaders(self):
        return {'Authorization': 'Bearer ' + self.token, 'Content-Type': 'application/json'}

    def handleResponse(self, response, url):
        if response.status != 200:
            result = {"result": {}, "error": True}
            if response.status == 401:
                result["message"] = "Token invalid"
            elif response.status == 403:
                result["message"] = "Forbidden"
            elif response.status == 404:
                result["message"] = "Invalid URL"

            result["status"] = response.status

            # These error messages are used in unit tests, so don't change them without updating the tests.
            print("ERROR: " + (result["message"] if "message" in result else ""))
            print(url)
            print(response.status)
            print(response.headers)

            return result
        else:
            return response.data.decode('utf-8')
