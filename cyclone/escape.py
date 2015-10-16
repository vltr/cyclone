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

"""Escaping/unescaping methods for HTML, JSON, URLs, and others.

Also includes a few other miscellaneous string manipulation functions that
have crept in over time.
"""

from __future__ import absolute_import, division, with_statement

import htmlentitydefs
import re
import urllib

from cyclone.util import basestring_type
from cyclone.util import bytes_type
from cyclone.util import unicode_type

try:
    from urlparse import parse_qs  # Python 2.6+
except ImportError:  # pragma: nocover
    from cgi import parse_qs

# json module is in the standard library as of python 2.6; fall back to
# simplejson if present for older versions.
try:
    import json
    assert hasattr(json, "loads") and hasattr(json, "dumps")
    _default_json_decode = json.loads
    _default_json_encode = json.dumps
except Exception:  # pragma: nocover
    try:
        import simplejson
        _default_json_decode = lambda s: simplejson.loads(_unicode(s))
        _default_json_encode = lambda v: simplejson.dumps(v)
    except ImportError:
        try:
            # For Google AppEngine
            from django.utils import simplejson
            _default_json_decode = lambda s: simplejson.loads(_unicode(s))
            _default_json_encode = lambda v: simplejson.dumps(v)
        except ImportError:
            def _default_json_decode(s):
                raise NotImplementedError(
                    "A JSON parser is required, e.g., simplejson at "
                    "http://pypi.python.org/pypi/simplejson/")
            _default_json_encode = _default_json_decode


_JSON_CODECS = dict()

_JSON_CODECS['active_json_encoder'] = _default_json_encode
_JSON_CODECS['active_json_decoder'] = _default_json_decode


_XHTML_ESCAPE_RE = re.compile('[&<>"\']')
_XHTML_ESCAPE_DICT = {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": "&#39;"}


def xhtml_escape(value):
    """Escapes a string so it is valid within XML or XHTML."""
    return _XHTML_ESCAPE_RE.sub(lambda match:
                    _XHTML_ESCAPE_DICT[match.group(0)], to_basestring(value))


def xhtml_unescape(value):
    """Un-escapes an XML-escaped string."""
    return re.sub(r"&(#?)(\w+?);", _convert_entity, _unicode(value))


def json_encode(value):
    """JSON-encodes the given Python object."""
    # JSON permits but does not require forward slashes to be escaped.
    # This is useful when json data is emitted in a <script> tag
    # in HTML, as it prevents </script> tags from prematurely terminating
    # the javscript.  Some json libraries do this escaping by default,
    # although python's standard library does not, so we do it here.
    # http://stackoverflow.com/questions/1580647/\
    #       json-why-are-forward-slashes-escaped
    return _JSON_CODECS['active_json_encoder'].__call__(
        recursive_unicode(value)).replace("</", "<\\/")


def change_json_encoder(encoder_fn):
    """Changes the default JSON encoder used by cyclone"""
    if callable(encoder_fn):
        _JSON_CODECS['active_json_encoder'] = encoder_fn
    raise ValueError("the given JSON encoder is not a function")


def json_encoder_is_default():
    """Returns True if the current JSON encoder is cyclone's default,
    else False.
    """
    return _JSON_CODECS['active_json_encoder'] == _default_json_encode


def reset_json_encoder():
    """Returns True if cyclone's default JSON encoder is put back in place as
    default, else False
    """
    if json_encoder_is_default():
        return False
    _JSON_CODECS['active_json_encoder'] = _default_json_encode
    return json_encoder_is_default()


def json_decode(value):
    """Returns Python objects for the given JSON string."""
    return _JSON_CODECS['active_json_decoder'].__call__(to_basestring(value))


def change_json_decoder(decoder_fn):
    """Changes the default JSON decoder used by cyclone"""
    if callable(decoder_fn):
        _JSON_CODECS['active_json_decoder'] = decoder_fn
    raise ValueError("the given JSON decoder is not a function")


def json_decoder_is_default():
    """Returns True if the current JSON decoder is cyclone's default,
    else False.
    """
    return _JSON_CODECS['active_json_decoder'] == _default_json_decode


def reset_json_decoder():
    """Returns True if cyclone's default JSON decoder is put back in place as
    default, else False
    """
    if json_decoder_is_default():
        return False
    _JSON_CODECS['active_json_decoder'] = _default_json_decode
    return json_decoder_is_default()


def squeeze(value):
    """Replace all sequences of whitespace chars with a single space."""
    return re.sub(r"[\x00-\x20]+", " ", value).strip()


def url_escape(value):
    """Returns a valid URL-encoded version of the given value."""
    return urllib.quote_plus(utf8(value))


def url_unescape(value, encoding='utf-8'):
    """Decodes the given value from a URL.

    The argument may be either a byte or unicode string.

    If encoding is None, the result will be a byte string.  Otherwise,
    the result is a unicode string in the specified encoding.
    """
    if encoding is None:
        return urllib.unquote_plus(utf8(value))
    else:
        return unicode(urllib.unquote_plus(utf8(value)), encoding)

parse_qs_bytes = parse_qs

_UTF8_TYPES = (bytes, type(None))


def utf8(value):
    """Converts a string argument to a byte string.

    If the argument is already a byte string or None, it is returned unchanged.
    Otherwise it must be a unicode string and is encoded as utf8.
    """
    if isinstance(value, _UTF8_TYPES):
        return value
    assert isinstance(value, unicode_type)
    return value.encode("utf-8")

_TO_UNICODE_TYPES = (unicode_type, type(None))


def to_unicode(value):
    """Converts a string argument to a unicode string.

    If the argument is already a unicode string or None, it is returned
    unchanged.  Otherwise it must be a byte string and is decoded as utf8.
    """
    if isinstance(value, _TO_UNICODE_TYPES):
        return value
    assert isinstance(value, bytes_type)
    return value.decode("utf-8")

# to_unicode was previously named _unicode not because it was private,
# but to avoid conflicts with the built-in unicode() function/type
_unicode = to_unicode

# When dealing with the standard library across python 2 and 3 it is
# sometimes useful to have a direct conversion to the native string type
if str is unicode_type:  # pragma: nocover
    native_str = to_unicode
else:
    native_str = utf8

_BASESTRING_TYPES = (basestring_type, type(None))


def to_basestring(value):
    """Converts a string argument to a subclass of basestring.

    In python2, byte and unicode strings are mostly interchangeable,
    so functions that deal with a user-supplied argument in combination
    with ascii string constants can use either and should return the type
    the user supplied.  In python3, the two types are not interchangeable,
    so this method is needed to convert byte strings to unicode.
    """
    if isinstance(value, _BASESTRING_TYPES):
        return value
    assert isinstance(value, bytes_type)
    return value.decode("utf-8") # pragma: no cover
    # NOTE: in python 2.6+ (except 3.x), we'll never get here


def recursive_unicode(obj):
    """Walks a simple data structure, converting byte strings to unicode.

    Supports lists, tuples, and dictionaries.
    """
    if isinstance(obj, dict):
        return dict((recursive_unicode(k), recursive_unicode(v))
                     for (k, v) in obj.iteritems())
    elif isinstance(obj, list):
        return list(recursive_unicode(i) for i in obj)
    elif isinstance(obj, tuple):
        return tuple(recursive_unicode(i) for i in obj)
    elif isinstance(obj, bytes_type):
        return to_unicode(obj)
    else:
        return obj

# I originally used the regex from
# http://daringfireball.net/2010/07/improved_regex_for_matching_urls
# but it gets all exponential on certain patterns (such as too many trailing
# dots), causing the regex matcher to never return.
# This regex should avoid those problems.
# Use to_unicode instead of tornado.util.u - we don't want backslashes getting
# processed as escapes.
_URL_RE = re.compile(to_unicode(r"""\b((?:([\w-]+):(/{1,3})|www[.])"""
                                r"""(?:(?:(?:[^\s&()]|&amp;|&quot;)*"""
                                r"""(?:[^!"#$%&'()*+,.:;<=>?@\[\]^`{|}~\s]))"""
                                r"""|(?:\((?:[^\s&()]|&amp;|&quot;)*\)))+)"""))


def linkify(text, shorten=False, extra_params="",
            require_protocol=False, permitted_protocols=["http", "https"]):
    """Converts plain text into HTML with links.

    For example: ``linkify("Hello http://cyclone.io!")`` would return
    ``Hello <a href="http://cyclone.io">http://cyclone.io</a>!``

    Parameters:

    shorten: Long urls will be shortened for display.

    extra_params: Extra text to include in the link tag, or a callable
        taking the link as an argument and returning the extra text
        e.g. ``linkify(text, extra_params='rel="nofollow" class="external"')``,
        or::

            def extra_params_cb(url):
                if url.startswith("http://example.com"):
                    return 'class="internal"'
                else:
                    return 'class="external" rel="nofollow"'
            linkify(text, extra_params=extra_params_cb)

    require_protocol: Only linkify urls which include a protocol. If this is
        False, urls such as www.facebook.com will also be linkified.

    permitted_protocols: List (or set) of protocols which should be linkified,
        e.g. linkify(text, permitted_protocols=["http", "ftp", "mailto"]).
        It is very unsafe to include protocols such as "javascript".
    """
    if extra_params and not callable(extra_params):
        extra_params = " " + extra_params.strip()

    def make_link(m):
        url = m.group(1)
        proto = m.group(2)
        if require_protocol and not proto:
            return url  # not protocol, no linkify

        if proto and proto not in permitted_protocols:
            return url  # bad protocol, no linkify

        href = m.group(1)
        if not proto:
            href = "http://" + href   # no proto specified, use http

        if callable(extra_params):
            params = " " + extra_params(href).strip()
        else:
            params = extra_params

        # clip long urls. max_len is just an approximation
        max_len = 30
        if shorten and len(url) > max_len:
            before_clip = url
            if proto:
                proto_len = len(proto) + 1 + len(m.group(3) or "")  # +1 for :
            else:
                proto_len = 0

            parts = url[proto_len:].split("/")
            if len(parts) > 1:
                # Grab the whole host part plus the first bit of the path
                # The path is usually not that interesting once shortened
                # (no more slug, etc), so it really just provides a little
                # extra indication of shortening.
                url = url[:proto_len] + parts[0] + "/" + \
                        parts[1][:8].split('?')[0].split('.')[0]

            if len(url) > max_len * 1.5:  # still too long
                url = url[:max_len]

            if url != before_clip:
                amp = url.rfind('&')
                # avoid splitting html char entities
                if amp > max_len - 5:
                    url = url[:amp]
                url += "..."

                if len(url) >= len(before_clip):
                    url = before_clip  # TODO probably the code will not reach
                                       # here
                else:
                    # full url is visible on mouse-over (for those who don't
                    # have a status bar, such as Safari by default)
                    params += ' title="%s"' % href

        return ('<a href="%s"%s>%s</a>'.decode("unicode_escape") %
                (href, params, url))

    # First HTML-escape so that our strings are all safe.
    # The regex is modified to avoid character entites other than &amp; so
    # that we won't pick up &quot;, etc.
    text = _unicode(xhtml_escape(text))
    return _URL_RE.sub(make_link, text)


def _convert_entity(m):
    if m.group(1) == "#":
        try:
            return unichr(int(m.group(2)))
        except ValueError:
            return "&#%s;" % m.group(2)
    try:
        return _HTML_UNICODE_MAP[m.group(2)]
    except KeyError:
        return "&%s;" % m.group(2)


def _build_unicode_map():
    unicode_map = {}
    for name, value in htmlentitydefs.name2codepoint.items():
        unicode_map[name] = unichr(value)
    return unicode_map

_HTML_UNICODE_MAP = _build_unicode_map()
