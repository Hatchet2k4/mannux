#!/usr/bin/env python

import ika


class Font(object):
    """A proportional bitmap font."""

    def __init__(self, filename):
        super(Font, self).__init__()
        self.name = filename
        self.position = 0, 0
        self.alignment = 'left'
        self._font = ika.Font('%s/%s' % ("fonts", filename))

    def write(self, text, position=None, alignment=None):
        """Prints a string of text on screen at position."""
        if position is not None:
            x, y = position
        else:
            x, y = self.position
        if alignment is None:
            alignment = self.alignment
        else:
            self.alignment = alignment
        {'left': self._font.Print,
         'center': self._font.CenterPrint,
         'right': self._font.RightPrint
        }[alignment](x, y, text)
        increment = self.height * text.count('\n')
        if increment:
            y += increment
        else:
            x += self.string_width(text)
        self.position = x, y
        return self

    def center(self, x=None, y=None):
        if x is None:
            x = ika.Video.xres / 2
        if y is None:
            y = (ika.Video.yres - self.height) / 2
        self.position = x, y
        self.alignment = 'center'
        return self

    def string_width(self, text):
        """Returns how many pixels in width the passed string would be,
        if printed in this font.
        """
        return self._font.StringWidth(text)

    def __call__(self, x, y, align=None):
        self.position = x, y
        if align is not None:
            self.alignment = align
        else:
            self.alignment = "left"
        return self

    height = property(lambda self: self._font.width)
    width = property(lambda self: self._font.height,
                     doc="""Gets the width of the widest glyph in the
                         font.
                         """)
    ex = property(lambda self: self.string_width('x'))
    em = property(lambda self: self.string_width('m'))
    en = property(lambda self: self.string_width('n'))
    tabsize = property(lambda self: self._font.tabsize,
                       lambda self, value: setattr(self._font, 'tabsize',
                                                   value),
                       doc="""Gets or sets the tab size of the font.""")
