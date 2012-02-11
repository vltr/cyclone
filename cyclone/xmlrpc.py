# coding: utf-8
#
# Copyright 2010 Alexandre Fiori
# based on the original Tornado by Facebook
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import xmlrpclib

from twisted.internet import defer
from cyclone.web import RequestHandler

class XmlrpcRequestHandler(RequestHandler):
    FAILURE = 8002
    NOT_FOUND = 8001
    separator = "."
    allowNone = False

    def post(self):
        self._auto_finish = False
        self.set_header("Content-Type", "text/xml")
        try:
            args, functionPath = xmlrpclib.loads(self.request.body)
        except Exception, e:
            f = xmlrpclib.Fault(self.FAILURE, "can't deserialize input: %s" % e)
            self._cbRender(f)
        else:
            try:
                function = self._getFunction(functionPath)
            except xmlrpclib.Fault, f:
                self._cbRender(f)
            else:
                d = defer.maybeDeferred(function, *args)
                d.addCallback(self._cbRender)
                d.addErrback(self._ebRender)

    def _getFunction(self, functionPath):
        if functionPath.find(self.separator) != -1:
            prefix, functionPath = functionPath.split(self.separator, 1)
            handler = self.getSubHandler(prefix)
            if handler is None:
                raise xmlrpclib.Fault(self.NOT_FOUND,
                    "no such subHandler %s" % prefix)
            return self._getFunction(functionPath)

        f = getattr(self, "xmlrpc_%s" % functionPath, None)
        if f is None:
            raise xmlrpclib.Fault(self.NOT_FOUND,
                "function %s not found" % functionPath)
        elif not callable(f):
            raise xmlrpclib.Fault(self.NOT_FOUND,
                "function %s not callable" % functionPath)
        else:
            return f

    def _cbRender(self, result):
        if not isinstance(result, xmlrpclib.Fault):
            result = (result,)

        try:
            s = xmlrpclib.dumps(result,
                methodresponse=True, allow_none=self.allowNone)
        except Exception, e:
            f = xmlrpclib.Fault(self.FAILURE, "can't serialize output: %s" % e)
            s = xmlrpclib.dumps(f,
                methodresponse=True, allow_none=self.allowNone)

        self.finish(s)

    def _ebRender(self, failure):
        if isinstance(failure.value, xmlrpclib.Fault):
            s = failure.value
        else:
            s = xmlrpclib.Fault(self.FAILURE, "error")

        self.finish(xmlrpclib.dumps(s, methodresponse=True))

