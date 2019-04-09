# -*- coding: utf-8 -*-

"""PIC-SURE Connection and Authorization Library"""

import PicSureClient

class PicSure:

    def version(self):
        print(PicSureHpdsClient.__package__ + " Library (version " + PicSureHpdsClient.__version__ + ")\n")

    def help(self):
        pass

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
        pass

    def resources(self):
        """PicSureClient.help() function is used to list all resources on the connected endpoint"""
        pass

    def _api_obj(self):
        """PicSureClient._api_obj() function returns a new, preconfigured PicSureConnectionAPI class instance """
        return PicSureConnectionAPI(self.url, self._token)


class PicSureConnectionAPI:
    def __init__(self, url, token):
        self.url = url
        self._token = token

# make sure a GUID is passed via the body of these commands


    def info(self):
        # https://github.com/hms-dbmi/pic-sure/blob/master/pic-sure-resources/pic-sure-resource-api/src/main/java/edu/harvard/dbmi/avillach/service/ResourceWebClient.java#L43
        pass

    def search(self):
        # https://github.com/hms-dbmi/pic-sure/blob/master/pic-sure-resources/pic-sure-resource-api/src/main/java/edu/harvard/dbmi/avillach/service/ResourceWebClient.java#L69
        pass

    def asyncQuery(self):
        # https://github.com/hms-dbmi/pic-sure/blob/master/pic-sure-resources/pic-sure-resource-api/src/main/java/edu/harvard/dbmi/avillach/service/ResourceWebClient.java#L98
        pass

    def syncQuery(self):
        # https://github.com/hms-dbmi/pic-sure/blob/master/pic-sure-resources/pic-sure-resource-api/src/main/java/edu/harvard/dbmi/avillach/service/ResourceWebClient.java#L186
        pass

    def queryStatus(self):
        # https://github.com/hms-dbmi/pic-sure/blob/master/pic-sure-resources/pic-sure-resource-api/src/main/java/edu/harvard/dbmi/avillach/service/ResourceWebClient.java#L124
        pass

    def queryResult(self, queryID):
        # https://github.com/hms-dbmi/pic-sure/blob/master/pic-sure-resources/pic-sure-resource-api/src/main/java/edu/harvard/dbmi/avillach/service/ResourceWebClient.java#L155
        pass
