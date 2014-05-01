import re

DELIMS = re.compile("[\\s;,]+")

def _gobble(regex, string):
    """
    If zero or more characters at the beginning of string match the regular
    expression pattern, returns (a, b) where a is the corresponding matched 
    string and b is the remainder of the string. If there is no match, a is 
    None.
    """
    match = regex.match(string)
    if match:
        match = match.group(0)
        remainder = string[len(match):]
        return (match, remainder)
    else:
        return (None, string)

def gobble(pattern, string):
    """
    If zero or more characters at the beginning of string match the regular
    expression pattern, returns (a, b) where a is the corresponding matched 
    string and b is the remainder of the string. If there is no match, a is 
    None.

    Delimiter characters at the beginning of string are stripped before 
    applying the pattern. The delimiter characters are:
      * any whitespace character
      * semicolon
      * comma
    """
    # Strip off leading delimiters.
    (delim_match, delim_remainder) = _gobble(DELIMS, string)
    if delim_match:
        string = delim_remainder

    # Look for a match on pattern after the delimiters
    regex = re.compile(pattern)
    return _gobble(regex, string)

def gobble_all(pattern, string):
    """
    Applies gobble repeatedly on the given string and pattern. Returns the 
    pair (z, b), where z is the list of all string matches and b is the 
    remainder of the string. If there are no matches, then z is None.
    """
    matches = []
    while True:
        # Look for a match on pattern
        (match, remainder) = gobble(pattern, string)
        if not match:
            break

        # Update the current string
        string = remainder
        matches.append(match)

    return (matches, string) if matches else (None, string)

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