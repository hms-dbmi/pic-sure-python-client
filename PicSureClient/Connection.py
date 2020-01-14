# -*- coding: utf-8 -*-

"""PIC-SURE Connection and Authorization Library"""

import PicSureClient
import httplib2
import json
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
        tempurl = url.strip()
        if tempurl.endswith("/"):
            tempurl = url
        else:
            tempurl = tempurl + "/"
        self.url = tempurl
        self._token = token
        self.AllowSelfSigned = allowSelfSignedSSL
        if allowSelfSignedSSL is True:
            # user is allowing self-signed SSL certs, serve them a black box warning
            print("""\033[38;5;196;40m\n
+=========================================================================================+
|        [ WARNING ] you are specifying that you WANT to allow self-signed SSL            |
|        certificates to be acceptable for connections.  This may be useful for           |
|        working in a development environment or on systems that host public              |
|        data.  BEST SECURITY PRACTICES ARE THAT IF YOU ARE WORKING WITH SENSITIVE        |
|        DATA THEN ALL SSL CERTS BY THOSE EVIRONMENTS SHOULD NOT BE SELF-SIGNED.          |
+=========================================================================================+
            \033[39;49m""")

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

    def about(self, resourceId = None):
        # print out info from /info about the endpoint
        # TODO: finish this
        url = self.url + "info/"
        if resourceId == None:
            url = url + "resources"
        else:
            url = url + str(resourceId)

        httpConn = httplib2.Http(disable_ssl_certificate_validation=self.AllowSelfSigned)
        httpHeaders = {'Content-Type':'application/json', 'Authorization':'Bearer '+self._token}
        (resp_headers, content) = httpConn.request(url, "GET", headers=httpHeaders)
        if resp_headers["status"] != "200":
            print("ERROR: HTTP response was bad")
            print(resp_headers)
            print(content.decode("utf-8"))
            return {"error":True, "headers":resp_headers, "content":json.loads(content.decode("utf-8"))}
        else:
            return {"error":False, "headers":resp_headers, "content":json.loads(content.decode('utf-8'))}

    def list(self):
        listing = json.loads(self.getResources())
        print("+".ljust(39, '-') + '+'.ljust(55, '-'))
        print("|  Resource UUID".ljust(39, ' ') + '|  Resource Name'.ljust(50, ' '))
        print("+".ljust(39, '-') + '+'.ljust(55, '-'))
        for rec in listing:
            print('| ' + rec.ljust(35,' '))
        print("+".ljust(39, '-') + '+'.ljust(55, '-'))

    def getInfo(self, uuid):
        pass

    def getResources(self):
        """PicSureClient.resources() function is used to list all resources on the connected endpoint"""
        httpConn = httplib2.Http(disable_ssl_certificate_validation=self.AllowSelfSigned)
        httpHeaders = {'Content-Type':'application/json', 'Authorization':'Bearer '+self._token}
        url = self.url + "info/resources"
        (resp_headers, content) = httpConn.request(url, "GET", headers=httpHeaders)
        if resp_headers["status"] != "200":
            print("ERROR: HTTP response was bad")
            print(resp_headers)
            print(content.decode("utf-8"))
            return "[]"
        else:
            return content.decode("utf-8")

    def _api_obj(self):
        """PicSureClient._api_obj() function returns a new, preconfigured PicSureConnectionAPI class instance """
        return PicSureConnectionAPI(self.url, self._token, allowSelfSignedSSL = self.AllowSelfSigned)


class PicSureConnectionAPI:
    def __init__(self, url, token, allowSelfSignedSSL = False):
        # make sure passed URL ends in slash
        url = url.strip()
        if not url.endswith("/"):
            url = url + "/"
        # save values
        self.url = url
        self._token = token
        self.AllowSelfSigned = allowSelfSignedSSL

    def info(self, resource_uuid):
        # https://github.com/hms-dbmi/pic-sure/blob/master/pic-sure-resources/pic-sure-resource-api/src/main/java/edu/harvard/dbmi/avillach/service/ResourceWebClient.java#L43
        httpConn = httplib2.Http(disable_ssl_certificate_validation=self.AllowSelfSigned)
        httpHeaders = {'Content-Type':'application/json', 'Authorization':'Bearer '+self._token}
        url = self.url + "info/" + resource_uuid
        (resp_headers, content) = httpConn.request(url, "POST", headers=httpHeaders, body="{}")
        if resp_headers["status"] != "200":
            print("ERROR: HTTP response was bad")
            print(url)
            print(resp_headers)
            print(content.decode("utf-8"))
            return '{"results":{}, "error":"true"}'
        else:
            return content.decode("utf-8")

    def search(self, resource_uuid, query):
        # make sure a Resource UUID is passed via the body of these commands
        # https://github.com/hms-dbmi/pic-sure/blob/master/pic-sure-resources/pic-sure-resource-api/src/main/java/edu/harvard/dbmi/avillach/service/ResourceWebClient.java#L69
        httpConn = httplib2.Http(disable_ssl_certificate_validation=self.AllowSelfSigned)
        httpHeaders = {'Content-Type':'application/json', 'Authorization':'Bearer '+self._token}
        if query == None:
            bodystr = json.dumps({"query":""})
        else:
            bodystr = str(query)
        url = self.url + "search/" + resource_uuid
        (resp_headers, content) = httpConn.request(url, "POST", headers=httpHeaders, body=bodystr)
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
        httpHeaders = {'Content-Type':'application/json', 'Authorization':'Bearer '+self._token}
        pass

    def syncQuery(self, resource_uuid, query):
        # make sure a Resource UUID is passed via the body of these commands
        # https://github.com/hms-dbmi/pic-sure/blob/master/pic-sure-resources/pic-sure-resource-api/src/main/java/edu/harvard/dbmi/avillach/service/ResourceWebClient.java#L186
        httpConn = httplib2.Http(disable_ssl_certificate_validation=self.AllowSelfSigned)
        httpHeaders = {'Content-Type':'application/json', 'Authorization':'Bearer '+self._token}
        url = self.url + "query/sync"
        (resp_headers, content) = httpConn.request(url, "POST", headers=httpHeaders, body=query)
        if resp_headers["status"] != "200":
            print("ERROR: HTTP response was bad")
            print(url)
            print(resp_headers)
            print(content.decode('utf-8'))
            return '{"results":{}, "error":"true"}'
        else:
            return content.decode("utf-8")

    def queryStatus(self, resource_uuid, query_uuid):
        # https://github.com/hms-dbmi/pic-sure/blob/master/pic-sure-resources/pic-sure-resource-api/src/main/java/edu/harvard/dbmi/avillach/service/ResourceWebClient.java#L124
        httpHeaders = {'Content-Type':'application/json', 'Authorization':'Bearer '+self._token}
        pass

    def queryResult(self, resource_uuid, query_uuid):
        # https://github.com/hms-dbmi/pic-sure/blob/master/pic-sure-resources/pic-sure-resource-api/src/main/java/edu/harvard/dbmi/avillach/service/ResourceWebClient.java#L155
        httpHeaders = {'Content-Type':'application/json', 'Authorization':'Bearer '+self._token}
        pass
