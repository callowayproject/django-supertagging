""" Django snippet - http://www.djangosnippets.org/snippets/588/"""

import unicodedata, sys


# Translation dictionary.  Translation entries are added to this
# dictionary as needed.

CHAR_REPLACEMENT = {
    # latin-1 characters that don't have a unicode decomposition
    0xc6: u"AE", # LATIN CAPITAL LETTER AE
    0xd0: u"D",  # LATIN CAPITAL LETTER ETH
    0xd8: u"OE", # LATIN CAPITAL LETTER O WITH STROKE
    0xde: u"Th", # LATIN CAPITAL LETTER THORN
    0xdf: u"ss", # LATIN SMALL LETTER SHARP S
    0xe6: u"ae", # LATIN SMALL LETTER AE
    0xf0: u"d",  # LATIN SMALL LETTER ETH
    0xf8: u"oe", # LATIN SMALL LETTER O WITH STROKE
    0xfe: u"th", # LATIN SMALL LETTER THORN
    0x2018: u"'", # LEFT SINGLE QUOTATION MARK
    0x2019: u"'", # RIGHT SINGLE QUOTATION MARK
    0x201c: u'"', # LEFT DOUBLE QUOTATION MARK
    0x201d: u'"', # RIGHT DOUBLE QUOTATION MARK
    0x215D: u"5/8", # VULGAR FRACTION FIVE EIGHTHS
    0x215A: u"5/6", # VULGAR FRACTION FIVE SIXTHS
    0x2158: u"4/5", # VULGAR FRACTION FOUR FIFTHS
    0x215B: u"1/8", # VULGAR FRACTION ONE EIGHTH
    0x2155: u"1/5", # VULGAR FRACTION ONE FIFTH
    0x00BD: u"1/2", # VULGAR FRACTION ONE HALF
    0x00BC: u"1/4", # VULGAR FRACTION ONE QUARTER
    0x2159: u"1/6", # VULGAR FRACTION ONE SIXTH
    0x2153: u"1/3", # VULGAR FRACTION ONE THIRD
    0x215E: u"7/8", # VULGAR FRACTION SEVEN EIGHTHS
    0x215C: u"3/8", # VULGAR FRACTION THREE EIGHTHS
    0x2157: u"3/5", # VULGAR FRACTION THREE FIFTHS
    0x00BE: u"3/4", # VULGAR FRACTION THREE QUARTERS
    0x2156: u"2/5", # VULGAR FRACTION TWO FIFTHS
    0x2154: u"2/3", # VULGAR FRACTION TWO THIRDS
}


class unaccented_map(dict):
    """
    Maps a unicode character code (the key) to a replacement code
    (either a character code or a unicode string).
    """

    def mapchar(self, key):
        ch = self.get(key)
        if ch is not None:
            return ch
        
        de = unicodedata.decomposition(unichr(key))
        if key not in CHAR_REPLACEMENT and de:
            try:
                ch = int(de.split(None, 1)[0], 16)
            except (IndexError, ValueError):
                ch = key
        else:
            ch = CHAR_REPLACEMENT.get(key, key)
        self[key] = ch
        return ch

    if sys.version >= "2.5":
        # use __missing__ where available
        __missing__ = mapchar
    else:
        # otherwise, use standard __getitem__ hook (this is slower,
        # since it's called for each character)
        __getitem__ = mapchar


def unicode_to_ascii(unicodestring):
    """
    Convert a unicode string into an ASCII representation, converting non-ascii
    characters into close approximations where possible.
    
    Special thanks to http://effbot.org/zone/unicode-convert.htm
    
    @param Unicode String unicodestring  The string to translate
    @result String
    """
    charmap = unaccented_map()
    return unicodestring.translate(charmap).encode("ascii", "ignore")