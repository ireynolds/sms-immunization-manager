"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase

import app
import gobbler

from utils.tests import MockRouter, MockApp
from rapidsms.tests.harness.router import CustomRouterMixin

class BlankApp(MockApp):
    return_values = None
    def parse_arguments(*args, **kwargs):
        pass

class OperationParserTest(CustomRouterMixin, TestCase):
    '''Tests for OperationParser.'''

    router_class = "utils.tests.MockRouter"

    def setUp(self):
        MockRouter.register_app("ZZ", BlankApp)
        MockRouter.register_app("QQ", BlankApp)
        MockRouter.register_app("XX", BlankApp)
        MockRouter.register_app("WW", BlankApp)

    def tearDown(self):
        MockRouter.unregister_apps()

    ## Helpers

    def receive(self, text):
        '''
        Treat the given text as the body of an incoming message and route it through
        the phases of RapidSMS as from number '4257886710' and 'mockbackend'.
        '''
        return CustomRouterMixin.receive(self, text, self.lookup_connections('mockbackend', ['4257886710'])[0])

    def parse(self, text):
        '''
        Run the given text through the parser and return the list of 
        (opcode, argument) pairs.
        '''
        message = self.receive(text)
        return message.fields['operations']

    def check(self, text, *expected_ops):
        '''
        Verify the parser identifies the given expected operations
        from the given text. Order is significant.
        '''
        expected_ops = expected_ops
        actual_ops = self.parse(text)
        self.assertEqual(list(expected_ops), actual_ops)

    ## Test OperationParser

    def test_parse_one_opcode_no_args(self):
        self.check("ZZ",
            ("ZZ", ""))

    def test_parse_one_opcode_strip_args(self):
        self.check("ZZ P 100",
            ("ZZ", "P 100"))

    def test_parse_one_opcode_no_delimiters(self):
        self.check("ZZP500", 
            ("ZZ", "P500"))

    def test_parse_two_opcodes_with_args(self):
        self.check("ZZP500QQA",
            ("ZZ", "P500"),
            ("QQ", "A"))

    def test_parse_three_opcodes_with_args(self):
        self.check("xx0ZZP875QQB",
            ("XX", "0"),
            ("ZZ", "P875"),
            ("QQ", "B"))

    def test_parse_two_opcodes_bad_casing(self):
        self.check("xxA50ZZP12QQC",
            ("XX", "A50"),
            ("ZZ", "P12"),
            ("QQ", "C"))

    def test_strips_delims_from_args(self):
        self.check(";;xx;;A;;10;;ZZ;;P;;100;;",
            ("XX", "A;;10"),
            ("ZZ", "P;;100"))

    def test_multiple_of_same_opcode(self):
        self.check("WWAWWDWWP",
            ("WW", "A"),
            ("WW", "D"),
            ("WW", "P"))

    # Test disambiguate_o0

    def test_disambiguate_o0(self):
        self.assertEqual(
            "0ab0q0000",
            app.disambiguate_o0("oab0qoO0O"))

class GobblerTest(TestCase):
    """
    Tests for gobbler.Gobbler.
    """

    ## Helpers        

    def assertGobbles(self, pattern, string, exp_match, exp_remainder, exp_index):
        '''
        Assert that the pattern, applied once to the string by the Gobbler (gobble), returns 
        the expected match from the expected index and leaves the expected remainder.
        '''
        g = gobbler.Gobbler(string)
        act_match = g.gobble(pattern)
        self.assertEqual(exp_match, act_match)
        self.assertEqual(exp_remainder, g.remainder)
        self.assertEqual(exp_index, g.index_of_previous)

    def assertGobblesAll(self, pattern, string, exp_matches, exp_remainder, exp_index):
        '''
        Assert that the pattern, applied as many times as possible to the string by 
        the Gobbler (gobble_all), returns the expected matches (with the last from the 
        expected index) and leaves the expected remainder.
        '''
        g = gobbler.Gobbler(string)
        act_matches = g.gobble_all(pattern)
        self.assertEqual(exp_matches, act_matches)
        self.assertEqual(exp_remainder, g.remainder)
        self.assertEqual(exp_index, g.index_of_previous)

    def assertDoesNotGobble(self, pattern, string, exp_index):
        '''
        Assert that the pattern, applied to the string by the Gobbler (gobble), returns no 
        match and leaves the given index_of_previous.
        '''
        g = gobbler.Gobbler(string)
        act_match = g.gobble(pattern)
        self.assertEqual(None, act_match)
        self.assertEqual(string, g.remainder)
        self.assertEqual(exp_index, g.index_of_previous)

    def assertDoesNotGobbleAny(self, pattern, string, exp_index):
        '''
        Assert that the pattern, applied to the string by the Gobbler as many times
        as possible (gobble_all), returns no matches and leaves the given index_of_previous.
        '''
        g = gobbler.Gobbler(string)
        act_matches = g.gobble_all(pattern)
        self.assertEqual(None, act_matches)
        self.assertEqual(string, g.remainder)
        self.assertEqual(exp_index, g.index_of_previous)

    ## Tests

    # Test gobble

    def test_gobble_no_match(self):
        self.assertDoesNotGobble("a", "bbb",
            None)

    def test_gobble_match_all(self):
        self.assertGobbles("aa", "aa", 
            "aa", "", 0)

    def test_gobble_match_part(self):
        self.assertGobbles("ab", "abcd", 
            "ab", "cd", 0)

    def test_gobble_match_one_of_repeating(self):
        self.assertGobbles("ab", "ababab", 
            "ab", "abab", 0)

    def test_gobble_match_with_preceding_whitespace_mix(self):
        self.assertGobbles("aa", " \taabb", 
            "aa", "bb", 2)

    def test_gobble_match_with_preceding_semicolons(self):
        self.assertGobbles("aa", ";;;aabb", 
            "aa", "bb", 3)

    def test_gobble_match_with_preceding_commas(self):
        self.assertGobbles("aa", ",,,,aabb",
            "aa", "bb", 4)

    def test_gobble_match_with_preceding_delimiter_mix(self):
        self.assertGobbles("aa", ",;\t  ;,,,\taabb",
            "aa", "bb", 10)

    def test_gobble_on_empty_string_zero_length_match(self):
        self.assertGobbles(".*", "", 
            "", "", 0)

    def test_gobble_leaves_leading_delimiters(self):
        self.assertGobbles("a", "a;b",
            "a", ";b", 0)

    # Test gobble_all

    def test_gobble_all_no_matches(self):
        self.assertDoesNotGobbleAny("aa", "bbbbbb",
            None)

    def test_gobble_all_one_matches_part(self):
        self.assertGobblesAll("aa", "aabb",
            ["aa"], "bb", 0)

    def test_gobble_all_one_matches_all(self):
        self.assertGobblesAll("aa", "aa",
            ["aa"], "", 0)

    def test_gobble_all_two_matches_part(self):
        self.assertGobblesAll("aa", "aaaabb",
            ["aa", "aa"], "bb", 2)

    def test_gobble_all_two_matches_all(self):
        self.assertGobblesAll("aa", "aaaaaa", 
            ["aa", "aa", "aa"], "", 4)

    def test_gobble_all_multiple_matches_with_delimiters(self):
        self.assertGobblesAll("aa", ";aa\t\t;,,aa;  ;;b,\tbb",
            ["aa", "aa"], ";  ;;b,\tbb", 8)

    # Test strip_delimiters

    def test_strip_delimiters(self):
        self.assertEqual(
            "Hello there-",
            gobbler.strip_delimiters("; \t,,;Hello there-   ;,;,,\t "))