# -*- coding: utf-8 -*-

"""PIC-SURE Connection and Authorization Library"""

import PicSureClient
import httplib2
import json

class Client:
    @classmethod
    def version(self):
        print(PicSureClient.__package__ + " Library (version " + PicSureClient.__version__ + ")\n")
    @classmethod
    def help(self):
        print("""
        This is the help information for PIC-SURE Client Library
            client = PicSureClient.Client
            client.version()
            client.help()
            connection = client.connect(<url>, <token>)
        """)
        pass
    @classmethod
    def connect(self, url, token):
        """ PicSure.connect returns a configured instance of a PicSureClient.Connection class """
        return PicSureClient.Connection(url,token)

class Connection:
    def __init__(self, url, token):
        self.url = url
        self._token = token

    def help(self):
        print("This is the help string for the PicSureClient.help() function.")
        pass

    def about(self):
        # print out info from /info about the endpoint
        h = httplib2.Http()
        (resp_headers, content) = h.request(self.url, "POST")
        pass

    def list(self):
        listing = self.resources()
        print("|__uuid".ljust(39, '_') + '|_name'.ljust(50, '_'))
        for rec in listing:
            print('| ' + rec['uuid'].ljust(35,' ') + ' | ' + rec['name'])
            print('| Description: '+rec['description'])
            print('+'.ljust(89,'-'))

    def resources(self):
        """PicSureClient.resources() function is used to list all resources on the connected endpoint"""
        httpConn = httplib2.Http()
        httpHeaders = {'content-type':'application/json', 'Authorization':'Bearer '+self._token}
        (resp_headers, content) = httpConn.request(self.url+"/info/resources", "GET", headers=httpHeaders)
        return json.loads(content)



    def _api_obj(self):
        """PicSureClient._api_obj() function returns a new, preconfigured PicSureConnectionAPI class instance """
        return PicSureConnectionAPI(self.url, self._token)


class PicSureConnectionAPI:
    def __init__(self, url, token):
        self.url = url
        self._token = token

    def info(self):
        # https://github.com/hms-dbmi/pic-sure/blob/master/pic-sure-resources/pic-sure-resource-api/src/main/java/edu/harvard/dbmi/avillach/service/ResourceWebClient.java#L43
        pass

    def search(self):
        # make sure a Resource UUID is passed via the body of these commands
        # https://github.com/hms-dbmi/pic-sure/blob/master/pic-sure-resources/pic-sure-resource-api/src/main/java/edu/harvard/dbmi/avillach/service/ResourceWebClient.java#L69
        pass

    def asyncQuery(self, query):
        # make sure a Resource UUID is passed via the body of these commands
        # https://github.com/hms-dbmi/pic-sure/blob/master/pic-sure-resources/pic-sure-resource-api/src/main/java/edu/harvard/dbmi/avillach/service/ResourceWebClient.java#L98
        pass

    def syncQuery(self, query):
        # make sure a Resource UUID is passed via the body of these commands
        # https://github.com/hms-dbmi/pic-sure/blob/master/pic-sure-resources/pic-sure-resource-api/src/main/java/edu/harvard/dbmi/avillach/service/ResourceWebClient.java#L186
        pass

    def queryStatus(self, resource_uuid, query_uuid):
        # https://github.com/hms-dbmi/pic-sure/blob/master/pic-sure-resources/pic-sure-resource-api/src/main/java/edu/harvard/dbmi/avillach/service/ResourceWebClient.java#L124
        pass

    def queryResult(self, resource_uuid, query_uuid):
        # https://github.com/hms-dbmi/pic-sure/blob/master/pic-sure-resources/pic-sure-resource-api/src/main/java/edu/harvard/dbmi/avillach/service/ResourceWebClient.java#L155
        pass
