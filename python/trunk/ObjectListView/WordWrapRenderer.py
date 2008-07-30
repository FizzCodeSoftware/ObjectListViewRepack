# -*- coding: utf-8 -*-
#!/usr/bin/env python
#----------------------------------------------------------------------------
# Name:         WordWrapRenderer.py
# Author:       Phillip Piper
# Created:      25 July 2008
# SVN-ID:       $Id$
# Copyright:    (c) 2008 by Phillip Piper, 2008
# License:      wxWindows license
#----------------------------------------------------------------------------
# Change log:
# 2008/07/25  JPP   Initial version
#----------------------------------------------------------------------------
# To do:

"""
A WordWrapRenderer encapsulates the ability to draw and measure word wrapped
strings directly to a device context.

It is meant to be good enough for general use.
It is not suitable for typographic layout -- it does not handle kerning or ligatures.

The clever parts of the code belong to Josiah Carlson. All the bugs belong to me.
"""

import textwrap
import wx

class WordWrapRenderer:
    """
    This renderer encapsulates the logic need to draw and measure a word-wrapped
    string within a given rectangle.
    """

    #----------------------------------------------------------------------------
    # Calculating

    @staticmethod
    def CalculateHeight(dc, text, width):
        """
        Calculate the height of the given text when fitted within the given width.

        Remember to set the font on the dc before calling this method.
        """
        wrapper = _VariableTextWrapper(width=width, break_long_words=True)
        wrapper.dc = dc

        # How many lines are needed to draw the string?
        lineCount = 0
        for inputLine in text.split("\n"):
            if inputLine == "":
                lineCount += 1
            else:
                lineCount += len(wrapper.wrap(inputLine))

        return lineCount * WordWrapRenderer._CalculateLineHeight(dc)

    @staticmethod
    def _CalculateLineHeight(dc):
        (width, height, descent, externalLeading) = dc.GetFullTextExtent("Wy")
        return height + externalLeading

    #----------------------------------------------------------------------------
    # Rendering

    @staticmethod
    def DrawString(dc, text, bounds, align=wx.ALIGN_LEFT, allowClipping=True):
        """
        Draw the given text word-wrapped within the given bounds.

        bounds must be a 4-element collection: (left, top, width, height).

        If allowClipping is True, this method changes the clipping region so that no
        text is drawn outside of the given bounds.
        """
        wrapper = _VariableTextWrapper(width=bounds[2], break_long_words=True)
        wrapper.dc = dc

        if allowClipping:
            dc.SetClippingRegion(*bounds)

        height = WordWrapRenderer._CalculateLineHeight(dc)
        x, y = bounds[0:2]
        for inputLine in text.split("\n"):
            if inputLine == "":
                y += height
            else:
                for line in wrapper.wrap(inputLine):
                    WordWrapRenderer._DrawOneLine(dc, line, x, y, bounds[2], align)
                    y += height

        if allowClipping:
            dc.DestroyClippingRegion()

        #dc.SetPen(wx.BLACK_PEN)
        #dc.SetBrush(wx.TRANSPARENT_BRUSH)
        #dc.DrawRectangle(bounds[0], bounds[1], bounds[2], y-bounds[1])

    @staticmethod
    def _DrawOneLine(dc, line, left, top, width, alignment):
        x = left
        if alignment != wx.ALIGN_LEFT:
            lineWidth = dc.GetTextExtent(line)[0]
            if alignment == wx.ALIGN_CENTER:
                x = left + ((width - lineWidth) / 2)
            elif alignment == wx.ALIGN_RIGHT:
                x = left + (width - lineWidth) - 1
        dc.DrawText(line, x, top)


class _VariableTextWrapper(textwrap.TextWrapper):
    """
    This code is adapted from a wxPython-user mailing list posting by
    Josiah Carlson on Nov 06, 2005
    """

    def GetTextWidth(self, text):
        return self.dc.GetTextExtent(text)[0]

    def _handle_long_word(self, chunks, cur_line, cur_len, width):
        """_handle_long_word(chunks : [string],
                             cur_line : [string],
                             cur_len : int, width : int)

        Handle a chunk of text (most likely a word, not whitespace) that
        is too long to fit in any line.
        """
        space_left = max(width - cur_len, 1)

        # If we're allowed to break long words, then do so: put as much
        # of the next chunk onto the current line as will fit.
        if self.break_long_words:
            use = 0
            x = self.GetTextWidth(chunks[0][use])
            while x < space_left and use < len(chunks[0])-1:
                space_left -= x
                use += 1
                x = self.GetTextWidth(chunks[0][use])
            if use > 0:
                use -= 1
            cur_line.append(chunks[0][:use])
            chunks[0] = chunks[0][use:]

        # Otherwise, we have to preserve the long word intact.  Only add
        # it to the current line if there's nothing already there --
        # that minimizes how much we violate the width constraint.
        elif not cur_line:
            cur_line.append(chunks.pop(0))

        # If we're not allowed to break long words, and there's already
        # text on the current line, do nothing.  Next time through the
        # main loop of _wrap_chunks(), we'll wind up here again, but
        # cur_len will be zero, so the next line will be entirely
        # devoted to the long word that we can't handle right now.

    def _wrap_chunks(self, chunks):
        """_wrap_chunks(chunks : [string]) -> [string]

        Wrap a sequence of text chunks and return a list of lines of
        length 'self.width' or less.  (If 'break_long_words' is false,
        some lines may be longer than this.)  Chunks correspond roughly
        to words and the whitespace between them: each chunk is
        indivisible (modulo 'break_long_words'), but a line break can
        come between any two chunks.  Chunks should not have internal
        whitespace; ie. a chunk is either all whitespace or a "word".
        Whitespace chunks will be removed from the beginning and end of
        lines, but apart from that whitespace is preserved.
        """
        lines = []
        if self.width <= 0:
            raise ValueError("invalid width %r (must be > 0)" % self.width)

        while chunks:

            # Start the list of chunks that will make up the current line.
            # cur_len is just the length of all the chunks in cur_line.
            cur_line = []
            cur_len = 0

            # Figure out which static string will prefix this line.
            if lines:
                indent = self.subsequent_indent
            else:
                indent = self.initial_indent

            # Maximum width for this line.
            width = self.width - self.GetTextWidth(indent)

            # First chunk on line is whitespace -- drop it, unless this
            # is the very beginning of the text (ie. no lines started yet).
            if chunks[0].strip() == '' and lines:
                del chunks[0]

            while chunks:
                l = self.GetTextWidth(chunks[0])

                # Can at least squeeze this chunk onto the current line.
                if cur_len + l <= width:
                    cur_line.append(chunks.pop(0))
                    cur_len += l

                # Nope, this line is full.
                else:
                    break

            # The current line is full, and the next chunk is too big to
            # fit on *any* line (not just this one).
            if chunks and self.GetTextWidth(chunks[0]) > width:
                self._handle_long_word(chunks, cur_line, cur_len, width)

            # If the last chunk on this line is all whitespace, drop it.
            if cur_line and cur_line[-1].strip() == '':
                del cur_line[-1]

            # Convert current line back to a string and store it in list
            # of all lines (return value).
            if cur_line:
                lines.append(indent + ''.join(cur_line))

        return lines


#======================================================================
# TESTING ONLY
#======================================================================

if __name__ == '__main__':

    class TestPanel(wx.Panel):
        def __init__(self, parent):
            wx.Panel.__init__(self, parent, -1, style=wx.FULL_REPAINT_ON_RESIZE)
            self.Bind(wx.EVT_PAINT, self.OnPaint)

            self.text = """This is the text to be drawn. It needs to be long to see if wrapping works. Thisisareallylongwordtoseewhathappens to long words.
This is on new line by itself.

This should have a blank line in front of it but still wrap when we reach the edge.

The bottom of the red rectangle should be immediately below this."""
            self.font = wx.FFont(12, wx.FONTFAMILY_MODERN, 0, "Arial")
            if wx.Platform == "__WXMSW__":
                #self.font = wx.FFont(36, wx.FONTFAMILY_DEFAULT, 0, "Gill Sans")
                self.font = wx.FFont(24, wx.FONTFAMILY_DEFAULT, 0, "Chiller")
            if wx.Platform == "__WXGTK__":
                self.font = wx.FFont(18, wx.FONTFAMILY_DEFAULT, 0, "FreeSerif")

        def OnPaint(self, evt):
            dc = wx.PaintDC(self)

            inset = (20, 20, 20, 20)
            bounds = list(self.GetRect())
            rect = [bounds[0]+inset[0], bounds[1]+inset[1], bounds[2]-(inset[0]+inset[2]), bounds[3]-(inset[1]+inset[3])]

            # Calculate exactly how high the wrapped is going to be and put a frame around it.
            dc.SetFont(self.font)
            dc.SetPen(wx.RED_PEN)
            rect[3] = WordWrapRenderer.CalculateHeight(dc, self.text, rect[2])
            dc.DrawRectangle(*rect)
            WordWrapRenderer.DrawString(dc, self.text, rect, wx.ALIGN_CENTER)

    class MyFrame(wx.Frame):
        def __init__(self, *args, **kwds):
            kwds["style"] = wx.DEFAULT_FRAME_STYLE
            wx.Frame.__init__(self, *args, **kwds)

            self.panel = wx.Panel(self, -1)
            self.testPanel = TestPanel(self.panel)

            sizer_2 = wx.BoxSizer(wx.VERTICAL)
            sizer_2.Add(self.testPanel, 1, wx.ALL|wx.EXPAND, 4)
            self.panel.SetSizer(sizer_2)
            self.panel.Layout()

            sizer_1 = wx.BoxSizer(wx.VERTICAL)
            sizer_1.Add(self.panel, 1, wx.EXPAND)
            self.SetSizer(sizer_1)
            self.Layout()


    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
