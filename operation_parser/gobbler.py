import re

DELIMS = re.compile("[\\s;,]+")

LABEL = "[A-Z]"
INTEGER = "\\d+"
OPCODE = "[A-Z]{2}"

def gobble(pattern, string):
    g = Gobbler(string)
    match = g.gobble(pattern)
    return (match, g.remainder)

def gobble_all(pattern, string):
    g = Gobbler(string)
    matches = g.gobble_all(pattern)
    return (matches, g.remainder)

def _gobble(regex, string):
    """
    If zero or more characters at the beginning of string match the regular
    expression pattern, returns (a, b) where a is the corresponding matched string
    and b is the remainder of the string. If there is no match, a is None and
    b is string.
    """
    match = regex.match(string)
    if not match:
        return (None, string)

    match = match.group(0)
    remainder = string[len(match):]
    return (match, remainder)

def strip_delimiters(string):
    """
    Returns a copy of string in which delimiter characters have been 
    stripped from the start and end of the string.
    """
    # Strip off the front
    (_, string) = _gobble(DELIMS, string)

    # Reverse and strip off the front (back, really)
    string = string[::-1]
    (_, string) = _gobble(DELIMS, string)

    # Reverse again to put in correct order and return
    return string[::-1]

class Gobbler():

    def __init__(self, string):
        self.original = string
        self.remainder = strip_delimiters(string)
        self.index_of_previous = None

    def index_of_previous(self):
        return self.index_of_previous

    def gobble(self, pattern):
        """
        If zero or more characters at the beginning of string match the regular
        expression pattern, returns the corresponding matched string. If there 
        is no match, returns None.

        Delimiter characters at the beginning of string are stripped before 
        applying the pattern. The delimiter characters are:
          * any whitespace character
          * semicolon
          * comma
        """
        # Strip off leading delimiters.
        (_, remainder) = _gobble(DELIMS, self.remainder)
        
        # Look for a match on pattern after the delimiters
        regex = re.compile(pattern)
        (match, remainder) = _gobble(regex, remainder)

        if match != None:
            self.remainder = remainder
            self.index_of_previous = len(self.original) - len(self.remainder) - len(match)
            return match
        else:
            return None

    def gobble_all(self, pattern):
        """
        Applies gobble repeatedly on the given string and pattern. Returns the 
        list of all string matches. If there are no matches, then returns None.
        """
        matches = []
        while True:
            match = self.gobble(pattern)
            if not match:
                break
            matches.append(match)
        
        if matches:
            return matches
        else:
            return None 
