# -*- coding: utf-8 -*-

"""PIC-SURE Connection and Authorization Library"""

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
        """)

    @classmethod
    def connect(self, url, token, allowSelfSignedSSL = False):
        """ PicSure.connect returns a configured instance of a PicSureClient.Connection class """
        return PicSureClient.Connection(url, token, allowSelfSignedSSL)

class Connection:
    def __init__(self, url, token, allowSelfSignedSSL = False):
        url_ret = urlparse(url)
        self.psama_url = url_ret.scheme + "://" + url_ret.netloc + "/psama/"
        self.url = url_ret.scheme + "://" + url_ret.netloc + url_ret.path
        self.resource_uuids = []
        if not self.url.endswith("/"):
            self.url = self.url + "/"
        self._token = token

        self.AllowSelfSigned = allowSelfSignedSSL
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
        # print out info from /info about the endpoint
        # TODO: finish this
        results = self.getInfo(resourceId)
        print(str("---[ Info about "+resourceId+" ]").ljust(94, '-'))
        if type(results) is str:
            info = json.loads(results)
            print(json.dumps(info, indent=2))
        else:
            print("!!!! ERROR !!!!")
            print(json.dumps(results, indent=2))


    def list(self):
        listing = json.loads(self.getResources())
        print("+".ljust(39, '-') + '+'.ljust(55, '-'))
        print("|  Resource UUID".ljust(39, ' ') + '|  Resource Name'.ljust(50, ' '))
        print("+".ljust(39, '-') + '+'.ljust(55, '-'))
        for rec in listing:
            print('| ' + rec.ljust(35,' '))
        print("+".ljust(39, '-') + '+'.ljust(55, '-'))

    def getInfo(self, uuid):
        url = self.url + "info/" + str(uuid)

        httpConn = httplib2.Http(disable_ssl_certificate_validation=self.AllowSelfSigned)
        httpHeaders = {'Content-Type':'application/json', 'Authorization':'Bearer '+self._token}
        (resp_headers, content) = httpConn.request(uri=url, method="POST", headers=httpHeaders, body="{}")
        if resp_headers["status"] != "200":
            print("ERROR: HTTP response was bad")
            print(resp_headers)
            print(content.decode("utf-8"))
            return {"error":True, "headers":resp_headers, "content":json.loads(content.decode("utf-8"))}
        else:
            return content.decode('utf-8')

    def getResources(self):
        import socket, httplib2
        """PicSureClient.resources() function is used to list all resources on the connected endpoint"""
        httpConn = httplib2.Http(disable_ssl_certificate_validation=self.AllowSelfSigned)
        httpHeaders = {'Content-Type':'application/json', 'Authorization':'Bearer '+self._token}
        url = self.url + "info/resources"
        try:
            (resp_headers, content) = httpConn.request(uri=url, method="GET", headers=httpHeaders)
        except (socket.gaierror, httplib2.ServerNotFoundError):
            print('ERROR: The address "'+url+'" is invalid')
            return '["ERROR:", "   Invalid URL!"]'.encode()
        else:
            if resp_headers["status"] != "200":
                if resp_headers["status"] == "401":
                    ret = ["ERROR:"]
                    json_resp = json.loads(content.decode("utf-8"))
                    if "message" in json_resp:
                        ret.append("    "+json_resp["message"])
                    else:
                        ret.append("    See message above.")
                    return json.dumps(ret).encode()
                else:
                    print("ERROR: HTTP response was bad")
                    print(resp_headers)
                    print(content.decode("utf-8"))
                    return '["ERROR:", "    See message above."]'.encode()
            else:
                ret = content.decode("utf-8")
                self.resource_uuids = json.loads(ret)
                return content.decode("utf-8")

    def _api_obj(self):
        """PicSureClient._api_obj() function returns a new, preconfigured PicSureConnectionAPI class instance """
        return PicSureConnectionAPI(self.url, self.psama_url, self._token, allowSelfSignedSSL = self.AllowSelfSigned)


class PicSureConnectionAPI:
    def __init__(self, url_picsure, url_psama, token, allowSelfSignedSSL = False):
        # save values
        self.url_picsure = url_picsure
        self.url_psama = url_psama
        self._token = token
        self.AllowSelfSigned = allowSelfSignedSSL

    def profile(self):
        from urllib.parse import urlparse
        httpConn = httplib2.Http(disable_ssl_certificate_validation=self.AllowSelfSigned)
        httpHeaders = {'Content-Type':'application/json', 'Authorization':'Bearer '+self._token}
        (resp_headers, content) = httpConn.request(uri=self.url_psama + "user/me", method="GET", headers=httpHeaders)
        if resp_headers["status"] != "200":
            print("ERROR: HTTP response was bad requesting PSAMA profile")
            print(self.url_psama + "user/me")
            print(resp_headers)
            print(content.decode("utf-8"))
            return '{"results":{}, "error":"true"}'
        else:
            response_str = content.decode("utf-8")

            # Make sure we have a "queryTemplate"
            response_objs = json.loads(response_str)
            if "queryTemplate" not in response_objs:
                    #load the query template
                    temp_url = self.url_psama + "user/me/queryTemplate/"
                    (resp_headers, content) = httpConn.request(uri=temp_url, method="GET", headers=httpHeaders)
                    if resp_headers["status"] != "200":
                        print("ERROR: HTTP response was bad requesting application queryTemplate")
                        print(temp_url)
                        print(resp_headers)
                        print(content.decode("utf-8"))
                        return '{"results":{}, "error":"true"}'
                    else:
                        response_objs["queryTemplate"] = json.loads(content.decode("utf-8"))["queryTemplate"]

            return json.dumps(response_objs)

    def info(self, resource_uuid):
        # https://github.com/hms-dbmi/pic-sure/blob/master/pic-sure-resources/pic-sure-resource-api/src/main/java/edu/harvard/dbmi/avillach/service/ResourceWebClient.java#L43
        httpConn = httplib2.Http(disable_ssl_certificate_validation=self.AllowSelfSigned)
        httpHeaders = {'Content-Type':'application/json', 'Authorization':'Bearer '+self._token}
        url = self.url_picsure + "info/" + resource_uuid
        (resp_headers, content) = httpConn.request(uri=url, method="POST", headers=httpHeaders, body="{}")
        if resp_headers["status"] != "200":
            print("ERROR: HTTP response was bad")
            print(url)
            print(resp_headers)
            print(content.decode("utf-8"))
            return '{"results":{}, "error":"true"}'
        else:
            return content.decode("utf-8")


    def search(self, resource_uuid, query=None):
        # make sure a Resource UUID is passed via the body of these commands
        # https://github.com/hms-dbmi/pic-sure/blob/master/pic-sure-resources/pic-sure-resource-api/src/main/java/edu/harvard/dbmi/avillach/service/ResourceWebClient.java#L69
        httpConn = httplib2.Http(disable_ssl_certificate_validation=self.AllowSelfSigned)
        httpHeaders = {'Content-Type':'application/json', 'Authorization':'Bearer '+self._token}
        if query == None:
            bodystr = json.dumps({"query":""})
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
            return '{"results":{}, "error":"true"}'
        else:
            return content.decode("utf-8")

    def syncQuery(self, resource_uuid, query):
        # make sure a Resource UUID is passed via the body of these commands
        # https://github.com/hms-dbmi/pic-sure/blob/master/pic-sure-resources/pic-sure-resource-api/src/main/java/edu/harvard/dbmi/avillach/service/ResourceWebClient.java#L186
        httpConn = httplib2.Http(disable_ssl_certificate_validation=self.AllowSelfSigned)
        httpHeaders = {'Content-Type':'application/json', 'Authorization':'Bearer '+self._token}
        url = self.url_picsure + "query/sync"
        (resp_headers, content) = httpConn.request(uri=url, method="POST", headers=httpHeaders, body=query)
        if resp_headers["status"] != "200":
            print("ERROR: HTTP response was bad")
            print(url)
            print(resp_headers)
            print(content.decode('utf-8'))
            return '{"results":{}, "error":"true"}'
        else:
            return content.decode("utf-8")

    def queryStatus(self, resource_uuid, query_uuid, query_body):
        # https://github.com/hms-dbmi/pic-sure/blob/master/pic-sure-resources/pic-sure-resource-api/src/main/java/edu/harvard/dbmi/avillach/service/ResourceWebClient.java#L124
        httpConn = httplib2.Http(disable_ssl_certificate_validation=self.AllowSelfSigned)
        httpHeaders = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + self._token}
        url = self.url_picsure + "query/" + query_uuid + "/status"
        query_obj = json.loads(query_body)
        query = {"resourceUUID": resource_uuid, "query": query_obj, "resourceCredentials": {}}
        (resp_headers, content) = httpConn.request(uri=url, method="POST", headers=httpHeaders, body=json.dumps(query))
        if resp_headers["status"] != "200":
            print("ERROR: HTTP response was bad")
            print(url)
            print(resp_headers)
            print(content.decode('utf-8'))
            return '{"results":{}, "error":"true"}'
        else:
            return content.decode("utf-8")

    def queryResult(self, resource_uuid, query_uuid):
        # https://github.com/hms-dbmi/pic-sure/blob/master/pic-sure-resources/pic-sure-resource-api/src/main/java/edu/harvard/dbmi/avillach/service/ResourceWebClient.java#L155
        httpConn = httplib2.Http(disable_ssl_certificate_validation=self.AllowSelfSigned)
        httpHeaders = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + self._token}
        httpHeaders = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + self._token}
        url = self.url_picsure + "query/" + query_uuid + "/result"
        pass
        query = '{}'
        (resp_headers, content) = httpConn.request(uri=url, method="POST", headers=httpHeaders, body=query)
        if resp_headers["status"] != "200":
            print("ERROR: HTTP response was bad")
            print(url)
            print(resp_headers)
            print(content.decode('utf-8'))
            return '{"results":{}, "error":"true"}'
        else:
            return content.decode("utf-8")
