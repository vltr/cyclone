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

from twisted.trial import unittest
from mock import Mock

from cyclone import escape

class TestEscape(unittest.TestCase):

    def test_xhtml(self):
        self.assertEqual(
            escape.xhtml_escape("abc42"),
            "abc42"
        )
        self.assertEqual(
            escape.xhtml_escape("<>"),
            "&lt;&gt;"
        )
        self.assertEqual(
            escape.xhtml_escape("\"'"),
            "&quot;&#39;"
        )

    def test_to_basestring(self):
        def to_raise():
            return escape.to_basestring({})
        self.assertRaises(AssertionError, to_raise)

    def test_linkify_required_proto(self):
        self.assertEqual(
            "Hello www.example.ltd!",
            escape.linkify("Hello www.example.ltd!", require_protocol=True)
        )

    def test_linkify_no_proto(self):
        self.assertEqual(
            'Hello <a href="http://www.example.ltd">www.example.ltd</a>!',
            escape.linkify("Hello www.example.ltd!")
        )

    def test_linkify_protolen_zero(self):
        link = escape.linkify(
            "Hello www.example.ltd/when/you/have/long/urls/what/to/do!",
            shorten=True)
        self.assertEqual(
            'Hello <a href="http://www.example.ltd/when/you/have/long/urls/what/to/do" title="http://www.example.ltd/when/you/have/long/urls/what/to/do">www.example.ltd/when...</a>!',
            link
        )

    def test_linkify_a_too_long_domain(self):
        link = escape.linkify(
            "Hello my friends! Please visit www.my-super-duper-awesome-domain-example.ltd/when/you/have/long/urls/what/to/do/you/will/be/shocked?you=will&xyz=1&you=will&not=dream&today!",
            shorten=True)
        self.assertEqual(
            'Hello my friends! Please visit <a href="http://www.my-super-duper-awesome-domain-example.ltd/when/you/have/long/urls/what/to/do/you/will/be/shocked?you=will&amp;xyz=1&amp;you=will&amp;not=dream&amp;today" title="http://www.my-super-duper-awesome-domain-example.ltd/when/you/have/long/urls/what/to/do/you/will/be/shocked?you=will&amp;xyz=1&amp;you=will&amp;not=dream&amp;today">www.my-super-duper-awesome-dom...</a>!',
            link
        )

    def test_linkify_a_too_long_domain_with_amp(self):
        link = escape.linkify(
            "Hello my friends! Please visit www.the-big-super-duper-ultra&awesome-domain-example.ltd/when/you/have/long/urls?you=will&freakout!",
            shorten=True)
        self.assertEqual(
            'Hello my friends! Please visit <a href="http://www.the-big-super-duper-ultra&amp;awesome-domain-example.ltd/when/you/have/long/urls?you=will&amp;freakout" title="http://www.the-big-super-duper-ultra&amp;awesome-domain-example.ltd/when/you/have/long/urls?you=will&amp;freakout">www.the-big-super-duper-ultra...</a>!',
            link
        )
