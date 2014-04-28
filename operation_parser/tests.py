"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase

import app
import gobbler

class MockMessage: 
    """
    A useful class that satisfies the interface of a RapidSMS
    Message on which OperationParser depends.
    """
    def __init__(self, text):
        # Satisfy the interface upon which OperationParser.parse depends
        self.text = text
        self.fields = {}

class OperationParserTest(TestCase):
    """
    Tests for app.OperationParser.
    """
    
    ## Helpers

    def parse(self, text):
        # No connection -- leave it as None
        op = app.OperationParser(None)
        msg = MockMessage(text)
        op.parse(msg)
        return msg.fields['operations']

    def check(self, text, *expected_ops):
        expected_ops = dict(expected_ops)
        actual_ops = self.parse(text)
        self.assertEqual(expected_ops, actual_ops)

    ## Tests

    def test_recognize_opcode(self):
        self.check("SL",
            ("SL", ""))

    def test_not_split_args(self):
        self.check("SL P 100",
            ("SL", "P 100"))

class GobblerTest(TestCase):
    """
    Tests for gobbler.
    """

    ## Helpers        

    def assertGobbles(self, pattern, string, exp_match, exp_remainder):
        act_match, act_remainder = gobbler.gobble(pattern, string)
        self.assertEqual(exp_match, act_match)
        self.assertEqual(exp_remainder, act_remainder)

    def assertGobblesAll(self, pattern, string, exp_matches, exp_remainder):
        act_matches, act_remainder = gobbler.gobble_all(pattern, string)
        self.assertEqual(exp_matches, act_matches)
        self.assertEqual(exp_remainder, act_remainder)

    def assertDoesNotGobble(self, pattern, string):
        act_match, act_remainder = gobbler.gobble(pattern, string)
        self.assertEqual(None, act_match)
        self.assertEqual(string, act_remainder)        

    def assertDoesNotGobbleAny(self, pattern, string):
        act_matches, act_remainder = gobbler.gobble_all(pattern, string)
        self.assertEqual(None, act_matches)
        self.assertEqual(string, act_remainder)

    ## Tests

    # Test gobble

    def test_gobble_no_match(self):
        self.assertDoesNotGobble("a", "bbb")

    def test_gobble_match_all(self):
        self.assertGobbles("aa", "aa", 
            "aa", "")

    def test_gobble_match_part(self):
        self.assertGobbles("ab", "abcd", 
            "ab", "cd")

    def test_gobble_match_one_of_repeating(self):
        self.assertGobbles("ab", "ababab", 
            "ab", "abab")

    def test_gobble_match_with_preceding_whitespace_mix(self):
        self.assertGobbles("aa", " \taabb", 
            "aa", "bb")

    def test_gobble_match_with_preceding_semicolons(self):
        self.assertGobbles("aa", ";;;aabb", 
            "aa", "bb")

    def test_gobble_match_with_preceding_commas(self):
        self.assertGobbles("aa", ",,,,aabb",
            "aa", "bb")

    def test_gobble_match_with_preceding_delimiter_mix(self):
        self.assertGobbles("aa", ",;\t  ;,,,\taabb",
            "aa", "bb")

    def test_gobble_on_empty_string_zero_length_match(self):
        self.assertGobbles(".*", "", 
            "", "")

    def test_gobble_leaves_leading_delimiters(self):
        self.assertGobbles("a", "a;b",
            "a", ";b")

    # Test gobble_all

    def test_gobble_all_no_matches(self):
        self.assertDoesNotGobbleAny("aa", "bbbbbb")

    def test_gobble_all_one_matches_part(self):
        self.assertGobblesAll("aa", "aabb",
            ["aa"], "bb")

    def test_gobble_all_one_matches_all(self):
        self.assertGobblesAll("aa", "aa",
            ["aa"], "")

    def test_gobble_all_two_matches_part(self):
        self.assertGobblesAll("aa", "aaaabb",
            ["aa", "aa"], "bb")

    def test_gobble_all_two_matches_all(self):
        self.assertGobblesAll("aa", "aaaaaa", 
            ["aa", "aa", "aa"], "")

    def test_gobble_all_multiple_matches_with_delimiters(self):
        self.assertGobblesAll("aa", ";aa\t\t;,,aa;  ;;b,\tbb",
            ["aa", "aa"], ";  ;;b,\tbb")

    # Test disambiguate_o0

    def test_disambiguate_o0(self):
        self.assertEqual(
            "0ab0q0000",
            gobbler.disambiguate_o0("oab0qoO0O"))

    # Test strip_delimiters

    def test_strip_delimiters(self):
        self.assertEqual(
            "Hello there-",
            gobbler.strip_delimiters("; \t,,;Hello there-   ;,;,,\t "))