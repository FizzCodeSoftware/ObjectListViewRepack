# -*- coding: ISO-8859-1 -*-
#----------------------------------------------------------------------------
# Name:         OwnerDrawnEditor.py
# Author:       Phillip Piper
# Created:      9 April 2008
# Copyright:    (c) 2008 by Phillip Piper
# RCS-ID:       $Id: timectrl.py 32483 2005-02-28 18:45:13Z RD $
# License:      wxWindows license
#----------------------------------------------------------------------------
# Change log:
# 2008/04/09  JPP   Initial version complete
#----------------------------------------------------------------------------
# To do:

"""
This module holds two owner drawn combo boxes.

FontFaceComboBox allows the user to choose a font face. It displays each font face by
drawing a string in that font.

ColourComboBox allows the user to choose a colour, It displays each colour by drawing
the colour's name on a background of that colour.
"""

import wx
import wx.combo
import wx.lib.colourdb

class Bucket:
    """
    General purpose data container
    """
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

#======================================================================

class FontFaceComboBox(wx.combo.OwnerDrawnComboBox):
    """
    FontFaceComboBox allows the user to choose a font face.

    Interface methods:

        GetValue()
            Returns a string with the name of the font face chosen by the user.

        SetValue(fontOrString)
            Set the font face that is chosen.

    Public attributes:

        fontHeight
            When string is drawn in the popup window, what should be the pixel size of the font?

        maximumPopupWidth
            When the popup window is showen, what is the maximum width that should be allowed?
            The actual width is taken from the width of the widest rendered string.

        evenRowBackground
            In the popup window, what will be the background colour of even rows?

        oddRowBackground
            In the popup window, what will be the background colour of odd rows?
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize a font face combobox.

        In addition to the public attributes describes as public attributes,
        the constructor understands the following parameters:

        extendedText
            This string will be added to the face name to give an indication
            of how the font appears. Typically a panagram.
        """
        self.fontHeight = kwargs.pop("fontHeight", 18)
        self.maximumPopupWidth = kwargs.pop("maximumPopupWidth", 400)
        self.evenRowBackground = kwargs.pop("evenRowBackground", wx.WHITE)
        self.oddRowBackground = kwargs.pop("oddRowBackground", wx.Colour(191, 239, 255))
        extendedText = kwargs.pop("extendedText", " - Big fjords vex quick waltz nymph")

        # Build the data behind the control
        fe = wx.FontEnumerator()
        fe.EnumerateFacenames()
        self.fontInfo = [ Bucket(name=x, display=x+extendedText) for x in sorted(fe.GetFacenames(), key=unicode.lower) ]

        kwargs['style'] = kwargs.get("style", 0) | wx.CB_READONLY
        kwargs["choices"] = [x.name for x in self.fontInfo]
        wx.combo.OwnerDrawnComboBox.__init__(self, *args, **kwargs)

        # Fill in some other information that is better to precalculate.
        # Measuring text has to be done after the control is initialized
        measuringDC = wx.ClientDC(self)
        for x in self.fontInfo:
            x.font = wx.FFont(self.fontHeight, wx.FONTFAMILY_DEFAULT, face=x.name)
            x.extent = measuringDC.GetFullTextExtent(x.display, font=x.font)

    def SetValue(self, value):
        """
        Set the selected value to be the given value, which can be a string or a font
        """
        if isinstance(value, wx.Font):
            value = value.GetFaceName()

        wx.combo.OwnerDrawnComboBox.SetValue(self, value or "")

    def OnDrawItem(self, dc, rect, item, flags):
        if item == wx.NOT_FOUND:
            return

        bucket = self.fontInfo[item]
        if (flags & wx.combo.ODCB_PAINTING_CONTROL) == wx.combo.ODCB_PAINTING_CONTROL:
            fontSize = min(self.fontHeight, max(10, self.GetSize().GetHeight() - 9))
            dc.SetFont(wx.FFont(fontSize, wx.FONTFAMILY_DEFAULT, face=bucket.name))
            display = bucket.name
        else:
            dc.SetFont(bucket.font)
            display = bucket.display
        dc.DrawText(display, rect.x + 3, rect.y + ((rect.height - dc.GetCharHeight()) / 2))

    def OnDrawBackground(self, dc, rect, item, flags):
        # If the item is selected, or we are painting the combo control itself, then use
        # the default rendering.
        if flags & (wx.combo.ODCB_PAINTING_CONTROL | wx.combo.ODCB_PAINTING_SELECTED):
            wx.combo.OwnerDrawnComboBox.OnDrawBackground(self, dc, rect, item, flags)
            return

        # Otherwise, draw every other background with different colour.
        if item & 1:
            backColour = self.oddRowBackground
        else:
            backColour = self.evenRowBackground
        dc.SetBrush(wx.Brush(backColour))
        dc.SetPen(wx.Pen(backColour))
        dc.DrawRectangleRect(rect)

    def OnMeasureItem(self, item):
        (width, height, descent, externalLeading) = self.fontInfo[item].extent
        return min(self.fontHeight * 2, height + descent)

    def OnMeasureItemWidth(self, item):
        (width, height, descent, externalLeading) = self.fontInfo[item].extent
        return min(self.maximumPopupWidth, width)


#======================================================================

class ColourComboBox(wx.combo.OwnerDrawnComboBox):
    """
    ColourComboBox allows the user to choose a colour.

    Interface methods:

        GetValue()
            Returns a wx.Colour chosen by the user.

        SetValue(colour)
            Set the colour that is chosen.

    Public attributes:

        popupRowHeight
            When the popup window is showen, what is the height of each row?
    """

    def __init__(self, *args, **kwargs):
        self.popupRowHeight = kwargs.pop("popupRowHeight", 24)

        # Collect the colours with different values
        self.colourList = []
        lastColour = None
        for x in wx.lib.colourdb.getColourInfoList():
            colour = x[1:]
            if colour != lastColour:
                self.colourList.append(Bucket(name=x[0], colour=wx.Colour(*colour), intensity=sum(colour)))
                lastColour = colour

        kwargs['style'] = kwargs.get('style', 0) | wx.CB_READONLY
        kwargs['choices'] = [x.name for x in self.colourList]
        wx.combo.OwnerDrawnComboBox.__init__(self, *args, **kwargs)

    GetStringValue = wx.combo.OwnerDrawnComboBox.GetValue

    def GetValue(self):
        """
        Return a wx.Colour that is selected
        """
        strValue = self.GetStringValue()
        for x in self.colourList:
            if x.name == strValue:
                return x.colour
        return None

    def SetValue(self, value):
        """
        Set the selected value to be the given value, which can be a string or a colour
        """
        if isinstance(value, wx.Colour):
            for x in self.colourList:
                if x.colour == value:
                    value = x.name
                    break

        wx.combo.OwnerDrawnComboBox.SetValue(self, value or "")

    def OnDrawItem(self, dc, rect, item, flags):
        if item == wx.NOT_FOUND:
            return

        bucket = self.colourList[item]

        if flags & wx.combo.ODCB_PAINTING_SELECTED:
            dc.DrawRectangleRect(rect)
        else:
            if bucket.intensity > (255+255+255)*2/3:
                dc.SetTextForeground(wx.BLACK)
            else:
                dc.SetTextForeground(wx.WHITE)

        dc.DrawText(bucket.name, rect.x + 3, rect.y + ((rect.height - dc.GetCharHeight()) / 2))

    def OnDrawBackground(self, dc, rect, item, flags):
        # If the item is selected, then use the default rendering.
        # Otherwise, draw each row with its own colour as the background
        if flags & wx.combo.ODCB_PAINTING_SELECTED:
            wx.combo.OwnerDrawnComboBox.OnDrawBackground(self, dc, rect, item, flags)
        else:
            backColour = self.colourList[item].colour
            dc.SetBrush(wx.Brush(backColour))
            dc.SetPen(wx.Pen(backColour))
            dc.DrawRectangleRect(rect)

    def OnMeasureItem(self, item):
        return self.popupRowHeight

#======================================================================
# Testing only

if __name__ == '__main__':

    class MyFrame(wx.Frame):
        def __init__(self, *args, **kwds):
            kwds["style"] = wx.DEFAULT_FRAME_STYLE
            wx.Frame.__init__(self, *args, **kwds)

            self.panel = wx.Panel(self, -1)
            self.cbFont = FontFaceComboBox(self.panel, -1)
            self.cbFont2 = FontFaceComboBox(self.panel, -1, fontHeight=12, extendedText="Junk MTV quiz graced by fox whelps",
                                        maximumPopupWidth=250, evenRowBackground=wx.Colour(191, 229, 245), oddRowBackground=wx.Colour(255, 248, 220))
            self.cbColour = ColourComboBox(self.panel, -1)
            self.cbColour2 = ColourComboBox(self.panel, -1, popupRowHeight=14)

            sizer_2 = wx.BoxSizer(wx.VERTICAL)
            sizer_2.Add(self.cbFont, 1, wx.ALL, 4)
            sizer_2.Add(self.cbFont2, 1, wx.ALL, 4)
            sizer_2.Add(self.cbColour, 1, wx.ALL, 4)
            sizer_2.Add(self.cbColour2, 1, wx.ALL, 4)
            self.panel.SetSizer(sizer_2)

            sizer_1 = wx.BoxSizer(wx.VERTICAL)
            sizer_1.Add(self.panel, 1, wx.ALL, 4)
            self.SetSizer(sizer_1)
            self.Layout()

            self.cbFont.Bind(wx.EVT_COMBOBOX, self.HandleFontComboBox)
            self.cbFont2.Bind(wx.EVT_COMBOBOX, self.HandleFontComboBox2)
            self.cbColour.Bind(wx.EVT_COMBOBOX, self.HandleColourComboBox)
            self.cbColour2.Bind(wx.EVT_COMBOBOX, self.HandleColourComboBox2)

            wx.CallAfter(self.run)

        def HandleFontComboBox(self, evt):
            print self.cbFont.GetValue()

        def HandleFontComboBox2(self, evt):
            print self.cbFont2.GetValue()

        def HandleColourComboBox(self, evt):
            print self.cbColour.GetValue()

        def HandleColourComboBox2(self, evt):
            print self.cbColour2.GetValue()

        def run(self):
            self.cbColour.SetValue("CORNSILK")

    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
