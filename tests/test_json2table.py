"""
Unit tests to verify proper conversion of JSON to HTML.
"""
from __future__ import division, print_function, absolute_import
from collections import OrderedDict
import unittest
from json2table.json2table import convert, JsonConverter


def _to_ordered_dict(d):
    """
    Recursively converts a dict to OrderedDict. 
    This is needed to preserve `(key, value)` ordering
    with iterating through `dict`'s between Python 2 and Python 3.

    Parameters
    ----------
    d : dict
        Dictionary to order.

    Returns
    -------
    OrderedDict
        Recursively order representation of the input dictionary.
    """
    d_ordered = OrderedDict()
    for key, value in sorted(d.items()):
        if isinstance(value, dict):
            d_ordered[key] = _to_ordered_dict(value)
        elif isinstance(value, list) and (all(isinstance(item, dict) for item in value)):
            list_of_ordered_dicts = []
            for item in value:
                list_of_ordered_dicts.append(_to_ordered_dict(item))
            d_ordered[key] = list_of_ordered_dicts
        else:
            d_ordered[key] = value
    return d_ordered


class TestConvert(unittest.TestCase):
    def setUp(self):
        self.simple_json = {"key" : "value"}
        self.custom_table_attributes = {"border" : 1}
        nested_json = {
        "menu": {
        "id": "file",
        "value": "File",
        "menuitem": [{"value": "New", "onclick": "CreateNewDoc()"},
                     {"value": "Open", "onclick": "OpenDoc()"},
                     {"value": "Close", "onclick": "CloseDoc()"}]
        }}
        self.nested_json = _to_ordered_dict(nested_json)
        self.maxDiff = None

    def test_invalid_build_direction(self):
        with self.assertRaises(ValueError) as context:
            convert(None, build_direction=None)
            self.assertTrue("Invalid build direction" in context.exception)

    def test_invalid_table_attributes(self):
        with self.assertRaises(TypeError) as context:
            convert(None, table_attributes=0)
            self.assertTrue("Table attributes must be either" in context.exception)

    def test_invalid_json(self):
        with self.assertRaises(AttributeError) as context:
            convert(None)

    def test_simple(self):
        result = convert(self.simple_json)
        simple_table = "<table><tr><th>key</th><td>value</td></tr></table>"
        self.assertEqual(result, simple_table)

    def test_custom_table_attributes(self):
        result = convert({}, table_attributes=self.custom_table_attributes)
        self.assertTrue("border=\"1\"" in result)

    def test_build_direction_top_to_bottom(self):
        result = convert(self.simple_json, build_direction="TOP_TO_BOTTOM")
        simple_table = "<table><tr><th>key</th></tr><tr><td>value</td></tr></table>"
        self.assertEqual(result, simple_table)

    def test_clubbed_json(self):
        clubbed_json = _to_ordered_dict({"sample": [ {"a":1, "b":2, "c":3}, {"a":5, "b":6, "c":7} ] })
        result = convert(clubbed_json)
        clubbed_table = "<table><tr><th>sample</th><td><table><tr><th>a</th><th>b</th><th>c</th></tr><"\
                        "tr><td>1</td><td>2</td><td>3</td></tr><tr><td>5</td><td>6</td><td>7</td></tr>"\
                        "</table></td></tr></table>"
        self.assertEqual(result, clubbed_table)

    def test_nested_left_to_right(self):
        result = convert(self.nested_json, build_direction="LEFT_TO_RIGHT")
        nested_table = "<table><tr><th>menu</th><td><table><tr><th>id</th><td>file</td></tr><tr><th>me"\
                       "nuitem</th><td><table><tr><th>onclick</th><th>value</th></tr><tr><td>CreateNew"\
                       "Doc()</td><td>New</td></tr><tr><td>OpenDoc()</td><td>Open</td></tr><tr><td>Clo"\
                       "seDoc()</td><td>Close</td></tr></table></td></tr><tr><th>value</th><td>File</t"\
                       "d></tr></table></td></tr></table>"
        self.assertEqual(result, nested_table)

    def test_nested_top_to_bottom(self):
        result = convert(self.nested_json, build_direction="TOP_TO_BOTTOM")
        nested_table = "<table><tr><th>menu</th></tr><tr><td><table><tr><th>id</th><th>menuitem</th><t"\
                       "h>value</th></tr><tr><td>file</td><td><table><tr><th>onclick</th><th>value</th"\
                       "></tr><tr><td>CreateNewDoc()</td><td>New</td></tr><tr><td>OpenDoc()</td><td>Op"\
                       "en</td></tr><tr><td>CloseDoc()</td><td>Close</td></tr></table></td><td>File</t"\
                       "d></tr></table></td></tr></table>"
        self.assertEqual(result, nested_table)


class TestJsonConverter(unittest.TestCase):
    def setUp(self):
        self.json_converter = JsonConverter()

    def test_empty_list_of_dicts_to_column_headers(self):
        result = self.json_converter._list_of_dicts_to_column_headers([])
        self.assertIs(result, None)

    def test_short_list_of_dicts_to_column_headers(self):
        result = self.json_converter._list_of_dicts_to_column_headers([{"key" : "value"}])
        self.assertIs(result, None)

    def test_noncollapsible_list_of_dicts_to_column_headers(self):
        result = self.json_converter._list_of_dicts_to_column_headers([{"key" : "value"}, {"value" : "key"}])
        self.assertIs(result, None)

    def test_none_markup(self):
        result = self.json_converter._markup(None)
        self.assertEqual(result, "")

    def test_list_markup(self):
        result = self.json_converter._markup([1, 2, 3])
        self.assertEqual(result, "<ul><li>1</li><li>2</li><li>3</li></ul>")

    def test_uncommon_headers_maybe_club(self):
        result = self.json_converter._maybe_club([None])
        self.assertEqual(result, "<td><ul><li></li></ul></td>")

if __name__ == "__main__":
    unittest.main()
