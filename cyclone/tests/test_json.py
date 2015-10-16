# coding: utf-8
#
# Copyright 2015 richard kuesters
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

import datetime
import cyclone.escape

from twisted.trial import unittest


class TestEscapeJson(unittest.TestCase):

    def setUp(self):
        cyclone.escape.reset_json_encoder()
        cyclone.escape.reset_json_decoder()
        """
        JSON example from http://json.org/example.html
        """
        self.example_json = """
            {
                "web-app":{
                    "servlet":[
                        {
                            "servlet-name":"cofaxCDS",
                            "servlet-class":"org.cofax.cds.CDSServlet",
                            "init-param":{
                                "configGlossary:installationAt":"Philadelphia, PA",
                                "configGlossary:adminEmail":"ksm@pobox.com",
                                "configGlossary:poweredBy":"Cofax",
                                "configGlossary:poweredByIcon":"/images/cofax.gif",
                                "configGlossary:staticPath":"/content/static",
                                "templateProcessorClass":"org.cofax.WysiwygTemplate",
                                "templateLoaderClass":"org.cofax.FilesTemplateLoader",
                                "templatePath":"templates",
                                "templateOverridePath":"",
                                "defaultListTemplate":"listTemplate.htm",
                                "defaultFileTemplate":"articleTemplate.htm",
                                "useJSP":false,
                                "jspListTemplate":"listTemplate.jsp",
                                "jspFileTemplate":"articleTemplate.jsp",
                                "cachePackageTagsTrack":200,
                                "cachePackageTagsStore":200,
                                "cachePackageTagsRefresh":60,
                                "cacheTemplatesTrack":100,
                                "cacheTemplatesStore":50,
                                "cacheTemplatesRefresh":15,
                                "cachePagesTrack":200,
                                "cachePagesStore":100,
                                "cachePagesRefresh":10,
                                "cachePagesDirtyRead":10,
                                "searchEngineListTemplate":"forSearchEnginesList.htm",
                                "searchEngineFileTemplate":"forSearchEngines.htm",
                                "searchEngineRobotsDb":"WEB-INF/robots.db",
                                "useDataStore":true,
                                "dataStoreClass":"org.cofax.SqlDataStore",
                                "redirectionClass":"org.cofax.SqlRedirection",
                                "dataStoreName":"cofax",
                                "dataStoreDriver":"com.microsoft.jdbc.sqlserver.SQLServerDriver",
                                "dataStoreUrl":"jdbc:microsoft:sqlserver://LOCALHOST:1433;DatabaseName=goon",
                                "dataStoreUser":"sa",
                                "dataStorePassword":"dataStoreTestQuery",
                                "dataStoreTestQuery":"SET NOCOUNT ON;select test='test';",
                                "dataStoreLogFile":"/usr/local/tomcat/logs/datastore.log",
                                "dataStoreInitConns":10,
                                "dataStoreMaxConns":100,
                                "dataStoreConnUsageLimit":100,
                                "dataStoreLogLevel":"debug",
                                "maxUrlLength":500
                            }
                        },
                        {
                            "servlet-name":"cofaxEmail",
                            "servlet-class":"org.cofax.cds.EmailServlet",
                            "init-param":{
                                "mailHost":"mail1",
                                "mailHostOverride":"mail2"
                            }
                        },
                        {
                            "servlet-name":"cofaxAdmin",
                            "servlet-class":"org.cofax.cds.AdminServlet"
                        },
                        {
                            "servlet-name":"fileServlet",
                            "servlet-class":"org.cofax.cds.FileServlet"
                        },
                        {
                            "servlet-name":"cofaxTools",
                            "servlet-class":"org.cofax.cms.CofaxToolsServlet",
                            "init-param":{
                                "templatePath":"toolstemplates/",
                                "log":1,
                                "logLocation":"/usr/local/tomcat/logs/CofaxTools.log",
                                "logMaxSize":"",
                                "dataLog":1,
                                "dataLogLocation":"/usr/local/tomcat/logs/dataLog.log",
                                "dataLogMaxSize":"",
                                "removePageCache":"/content/admin/remove?cache=pages&id=",
                                "removeTemplateCache":"/content/admin/remove?cache=templates&id=",
                                "fileTransferFolder":"/usr/local/tomcat/webapps/content/fileTransferFolder",
                                "lookInContext":1,
                                "adminGroupID":4,
                                "betaServer":true
                            }
                        }
                    ],
                    "servlet-mapping":{
                        "cofaxCDS":"/",
                        "cofaxEmail":"/cofaxutil/aemail/*",
                        "cofaxAdmin":"/admin/*",
                        "fileServlet":"/static/*",
                        "cofaxTools":"/tools/*"
                    },
                    "taglib":{
                        "taglib-uri":"cofax.tld",
                        "taglib-location":"/WEB-INF/tlds/cofax.tld"
                    }
                }
            }
        """

    def _getkey(self, obj, *keys):  # pragma: no cover
        """
        this is a little helper i use to "safely" navigate through an object,
        specially json parsed objects (public with no warranties whatsoever if
        anyone wants to use it) -- @vltr
        """
        if len(keys) > 0:
            if len(keys) == 1:
                if isinstance(keys[0], int):
                    if len(obj) - 1 >= keys[0]:
                        return obj[keys[0]] or {}
                    else:
                        return {}
                return obj.get(keys[0])
            else:
                if isinstance(obj, (set, list, tuple)):
                    return self._getkey(obj[keys[0]] or {}, *keys[1:])
                return self._getkey(obj.get(keys[0], {}), *keys[1:])
        return None

    def _get_fake_json_encoder(self):
        def fake_encoder(value):
            return "foo"
        return fake_encoder

    def _get_fake_json_decoder(self):
        def fake_decoder(value):
            return 'hello, world!'
        return fake_decoder

    def _get_custom_json_encoder(self):  # pragma: no cover
        try:
            import json
        except:
            import simplejson as json
        """
        totimestamp took from stackexchange:
        http://stackoverflow.com/questions/8777753/converting-datetime-date-to-utc-timestamp-in-python

        it is better to use this approach because `.total_seconds()` was
        only introduced in python 2.7
        """
        def totimestamp(dt, epoch=datetime.datetime(1970, 1, 1)):
            td = dt - epoch
            return (td.microseconds + (td.seconds + td.days * 86400) *
                    10 ** 6) / 10 ** 6

        def simple_hook(obj):
            if isinstance(obj, datetime.datetime):
                return {
                    '__datetime__': True,
                    'raw': totimestamp(obj)
                }
            return obj

        def encoder(obj):
            return json.dumps(obj,
                              default=simple_hook,
                              sort_keys=True,  # so we can expect the output
                              separators=(',', ':'))
        return encoder

    def _get_custom_json_decoder(self):  # pragma: no cover
        try:
            import json
        except:
            import simplejson as json

        def object_hook(obj):
            if b'__datetime__' in obj:
                obj = datetime.datetime.utcfromtimestamp(obj["raw"])
            return obj

        def decoder(obj):
            return json.loads(obj, object_hook=object_hook)
        return decoder

    def test_default_json_encoder(self):
        obj_to_encode = dict(
            foo=dict(
                baz=[0, 1]
            )
        )
        self.assertTrue('{"foo": {"baz": [0, 1]}}' ==
                        cyclone.escape.json_encode(obj_to_encode))

    def test_default_json_decoder(self):
        obj = cyclone.escape.json_decode(self.example_json)
        self.assertIsNot(obj, None)

    def test_default_json_decoder_value(self):
        obj = cyclone.escape.json_decode(self.example_json)
        self.assertTrue("ksm@pobox.com" == self._getkey(obj,
                                                        'web-app',
                                                        'servlet',
                                                        0,
                                                        'init-param',
                                                        'configGlossary:adminEmail'))
        self.assertTrue(self._getkey(obj,
                                     'web-app',
                                     'servlet',
                                     -1,
                                     'init-param',
                                     'betaServer'))

    def test_default_json_encoder_exception(self):
        self.assertRaises(Exception, cyclone.escape.json_encode, lambda ign: 1)

    def test_default_json_decoder_exception(self):
        self.assertRaises(Exception, cyclone.escape.json_decode, '')

    def test_change_default_json_encoder_exception(self):
        self.assertRaises(ValueError, cyclone.escape.change_json_encoder, {})

    def test_change_default_json_decoder_exception(self):
        self.assertRaises(ValueError, cyclone.escape.change_json_decoder, {})

    def test_change_default_json_encoder_for_fake(self):
        self.failUnlessRaises(ValueError, cyclone.escape.change_json_encoder,
                              self._get_fake_json_encoder())

    def test_change_default_json_decoder_for_fake(self):
        self.failUnlessRaises(ValueError, cyclone.escape.change_json_decoder,
                              self._get_fake_json_decoder())

    def test_fake_json_encoder(self):
        self.failUnlessRaises(ValueError, cyclone.escape.change_json_encoder,
                              self._get_fake_json_encoder())
        obj_to_encode = dict(
            foo=dict(
                baz=[0, 1]
            )
        )
        self.assertTrue("foo" == cyclone.escape.json_encode(obj_to_encode))

    def test_fake_json_decoder(self):
        self.failUnlessRaises(ValueError, cyclone.escape.change_json_decoder,
                              self._get_fake_json_decoder())
        json_to_decode = '{"foo": {"baz": [0, 1]}}'
        self.assertTrue("hello, world!" ==
                        cyclone.escape.json_decode(json_to_decode))

    def test_if_current_json_encoder_is_not_default(self):
        self.failUnlessRaises(ValueError, cyclone.escape.change_json_encoder,
                              self._get_fake_json_encoder())
        self.assertFalse(cyclone.escape.json_encoder_is_default())

    def test_if_current_json_decoder_is_not_default(self):
        self.failUnlessRaises(ValueError, cyclone.escape.change_json_decoder,
                              self._get_fake_json_decoder())
        self.assertFalse(cyclone.escape.json_decoder_is_default())

    def test_reset_json_encoder(self):
        self.failUnlessRaises(ValueError, cyclone.escape.change_json_encoder,
                              self._get_fake_json_encoder())
        self.assertTrue(cyclone.escape.reset_json_encoder())
        self.assertFalse(cyclone.escape.reset_json_encoder())

    def test_reset_json_decoder(self):
        self.failUnlessRaises(ValueError, cyclone.escape.change_json_decoder,
                              self._get_fake_json_decoder())
        self.assertTrue(cyclone.escape.reset_json_decoder())
        self.assertFalse(cyclone.escape.reset_json_decoder())

    def test_true_if_current_json_encoder_is_default(self):
        self.assertTrue(cyclone.escape.json_encoder_is_default())

    def test_true_if_current_json_decoder_is_default(self):
        self.assertTrue(cyclone.escape.json_decoder_is_default())

    def test_change_default_json_encoder(self):
        self.failUnlessRaises(ValueError, cyclone.escape.change_json_encoder,
                              self._get_custom_json_encoder())

    def test_change_default_json_decoder(self):
        self.failUnlessRaises(ValueError, cyclone.escape.change_json_decoder,
                              self._get_custom_json_decoder())

    def test_false_if_current_json_encoder_is_default(self):
        self.failUnlessRaises(ValueError, cyclone.escape.change_json_encoder,
                              self._get_fake_json_encoder())
        self.assertFalse(cyclone.escape.json_encoder_is_default())

    def test_false_if_current_json_decoder_is_default(self):
        self.failUnlessRaises(ValueError, cyclone.escape.change_json_decoder,
                              self._get_fake_json_decoder())
        self.assertFalse(cyclone.escape.json_decoder_is_default())

    def test_custom_json_encoder(self):
        self.failUnlessRaises(ValueError, cyclone.escape.change_json_encoder,
                              self._get_custom_json_encoder())
        obj_to_encode = dict(
            foo=dict(
                baz=[0, 1]
            )
        )
        self.assertTrue('{"foo":{"baz":[0,1]}}' ==
                        cyclone.escape.json_encode(obj_to_encode))
        obj_to_encode = dict(
            foo=dict(
                baz=[dict(my_timestamp=datetime.datetime(2000, 1, 1))]
            )
        )
        self.assertTrue('{"foo":{"baz":[{"my_timestamp":{"__datetime__":true,"raw":946684800}}]}}' ==
                        cyclone.escape.json_encode(obj_to_encode))

    def test_custom_json_decoder(self):
        self.failUnlessRaises(ValueError, cyclone.escape.change_json_decoder,
                              self._get_custom_json_decoder())
        json_to_decode = '{"foo":{"baz":[0,1]}}'
        self.assertTrue(dict(foo=dict(baz=[0, 1])) ==
                        cyclone.escape.json_decode(json_to_decode))
        json_to_decode = '{"foo":{"baz":[{"my_timestamp":{"__datetime__":true,"raw":946684800}}]}}'
        decoded_object = cyclone.escape.json_decode(json_to_decode)
        self.assertTrue(datetime.datetime.utcfromtimestamp(946684800) ==
                        self._getkey(decoded_object, 'foo', 'baz', 0,
                                     'my_timestamp'))

    def test_default_json_codecs(self):
        obj_to_encode = dict(
            foo=dict(
                baz=[0, 1]
            )
        )
        encoded_object = cyclone.escape.json_encode(obj_to_encode)
        self.assertTrue('{"foo": {"baz": [0, 1]}}' ==
                        encoded_object)
        self.assertTrue(obj_to_encode ==
                        cyclone.escape.json_decode(encoded_object))

    def test_custom_json_codecs(self):
        self.failUnlessRaises(ValueError, cyclone.escape.change_json_encoder,
                              self._get_custom_json_encoder())
        self.failUnlessRaises(ValueError, cyclone.escape.change_json_decoder,
                              self._get_custom_json_decoder())
        obj_to_encode = dict(
            foo=dict(
                baz=[dict(my_timestamp=datetime.datetime(2000, 1, 1))]
            )
        )
        encoded_object = cyclone.escape.json_encode(obj_to_encode)
        self.assertTrue('{"foo":{"baz":[{"my_timestamp":{"__datetime__":true,"raw":946684800}}]}}' ==
                        encoded_object)
        self.assertTrue(obj_to_encode ==
                        cyclone.escape.json_decode(encoded_object))

    def test_default_json_encoder_with_custom_json_decoder(self):
        self.failUnlessRaises(ValueError, cyclone.escape.change_json_decoder,
                              self._get_custom_json_decoder())
        obj_to_encode = dict(
            foo=dict(
                baz=[dict(my_timestamp=datetime.datetime(2000, 1, 1))]
            )
        )
        # decode will raise TypeError because it can't handle datetime objects
        self.failUnlessRaises(TypeError, cyclone.escape.json_encode,
                              obj_to_encode)
        obj_to_encode = dict(
            foo=dict(
                baz=[0, 1]
            )
        )
        encoded_object = cyclone.escape.json_encode(obj_to_encode)
        self.assertTrue('{"foo": {"baz": [0, 1]}}' ==
                        encoded_object)
        self.assertTrue(obj_to_encode ==
                        cyclone.escape.json_decode(encoded_object))

    def test_custom_json_encoder_with_default_json_decoder(self):
        self.failUnlessRaises(ValueError, cyclone.escape.change_json_encoder,
                              self._get_custom_json_encoder())
        obj_to_encode = dict(
            foo=dict(
                baz=[dict(my_timestamp=datetime.datetime(2000, 1, 1))]
            )
        )
        encoded_object = cyclone.escape.json_encode(obj_to_encode)
        decoded_object = cyclone.escape.json_decode(encoded_object)
        self.assertFalse(obj_to_encode == decoded_object)
        self.assertTrue(946684800 == self._getkey(decoded_object,
                                                  'foo', 'baz', 0,
                                                  'my_timestamp', 'raw'))
