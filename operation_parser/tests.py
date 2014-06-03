"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.conf import settings

import app
import gobbler

from utils.tests import MockRouter, MockApp, SIMTestCase, CustomRouterMixin
from user_registration.models import Facility

class BlankApp(MockApp):
    return_values = None
    def parse_arguments(*args, **kwargs):
        pass

class OperationParserTest(CustomRouterMixin, SIMTestCase):
    '''Tests for OperationParser.'''

    router_class = "utils.tests.MockRouter"

    def setUp(self):
        MockRouter.register_app("ZZ", BlankApp, settings.PERIODIC)
        MockRouter.register_app("QQ", BlankApp, settings.PERIODIC, limit_one=True)
        MockRouter.register_app("XX", BlankApp, settings.SPONTANEOUS)
        MockRouter.register_app("WW", BlankApp, settings.CONTEXTUAL)

    def tearDown(self):
        MockRouter.unregister_apps()

    ## Helpers

    def check_ok(self, text, *expected_ops):
        '''
        Verify the parser identifies the given expected operations
        from the given text. Order is significant.
        '''
        message = self.receive(text)
        actual_ops = message.fields['operations']
        self.assertEqual(list(expected_ops), actual_ops)
        return message

    def check_error(self, text):
        '''
        Verify that the parser attaches an error effect as a result
        of parsing the given text.
        '''
        message = self.receive(text)
        actual_effects = message.fields['operation_effects']
        self.assertErrorIn(actual_effects)
        return message

    ## Test OperationParser

    def test_parse_one_opcode_no_args(self):
        self.check_ok("ZZ",
            ("ZZ", ""))

    def test_parse_one_opcode_strip_args(self):
        self.check_ok("ZZ P 100",
            ("ZZ", "P 100"))

    def test_parse_one_opcode_no_delimiters(self):
        self.check_ok("ZZP500", 
            ("ZZ", "P500"))

    def test_parse_two_opcodes_with_args(self):
        self.check_ok("ZZP500QQA",
            ("ZZ", "P500"),
            ("QQ", "A"))

    def test_parse_three_opcodes_with_args(self):
        self.check_ok("zz0ZZP875QQB",
            ("ZZ", "0"),
            ("ZZ", "P875"),
            ("QQ", "B"))

    def test_parse_two_opcodes_bad_casing(self):
        self.check_ok("zZA50ZZP12QQC",
            ("ZZ", "A50"),
            ("ZZ", "P12"),
            ("QQ", "C"))

    def test_strips_delims_from_args(self):
        self.check_ok(";;ZZ;;A;;10;;ZZ;;P;;100;;",
            ("ZZ", "A;;10"),
            ("ZZ", "P;;100"))

    def test_multiple_of_same_opcode(self):
        self.check_ok("XXAXXDXXP",
            ("XX", "A"),
            ("XX", "D"),
            ("XX", "P"))

    def test_disallow_duplicates(self):
        self.check_error("QQ A QQ B")

    def test_disallow_from_multiple_groups(self):
        self.check_error("QQ A XX B")

    def test_disallow_from_multiple_groups_except_contextual(self):
        self.check_ok("ZZ A QQ B WW C",
            ("ZZ", "A"),
            ("QQ", "B"),
            ("WW", "C"))

    def test_adds_group_to_fields_not_contextual(self):
        message = self.check_ok("WW A ZZ A",
            ("WW", "A"),
            ("ZZ", "A"))
        self.assertEqual(settings.PERIODIC, message.fields['group'])

    def test_error_if_only_contextual(self):
        self.check_error("WW A")

    def test_parses_he(self):
        msg = self.receive("SL A 10 HE SL ")
        self.assertEqual(
            [("SL", "A 10"), ("HE", "SL")],
            msg.fields['operations']
        )

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
            "Hello there",
            gobbler.strip_delimiters("; \t,,;Hello there-   ;,;,,\t "))