# coding: utf-8
#
# Copyright 2014 David Novakovic
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

import cyclone.escape
from mock import Mock
from twisted.trial import unittest
from cyclone.jsonrpc import JsonrpcRequestHandler
from cyclone.web import Application


class TestJsonrpcRequestHandler(unittest.TestCase):

    def setUp(self):
        self.request = Mock()
        self.app = Application()
        self.handler = JsonrpcRequestHandler(self.app, self.request)
        self.handler.finish = Mock()

    def test_post(self):
        self.handler.jsonrpc_foo = lambda: "value"
        self.handler.request.body = '{"id":1, "method":"foo"}'
        self.handler.post()
        # i haven't found any other way to safely test this because json
        # encoders may differ results, specially using pypy -- @vltr
        encoded_object = self.handler.finish.call_args[0][0]
        self.assertTrue(dict(result="value", error=None, id=1) ==
                        cyclone.escape.json_decode(encoded_object))

    def test_default_jsonrpc_headers(self):
        self.handler.jsonrpc_foo = lambda: "value"
        self.handler.request.body = '{"id":1, "method":"foo"}'
        self.handler.post()
        self.assertTrue("Content-Type" in self.handler._headers)
        self.assertTrue("application/json; charset=UTF-8" ==
                        self.handler._headers.get("Content-Type"))
