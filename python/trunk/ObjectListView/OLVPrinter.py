# -*- coding: utf-8 -*-
#!/usr/bin/env python
#----------------------------------------------------------------------------
# Name:         OLVPrinter.py
# Author:       Phillip Piper
# Created:      17 July 2008
# SVN-ID:       $Id$
# Copyright:    (c) 2008 by Phillip Piper, 2008
# License:      wxWindows license
#----------------------------------------------------------------------------
# Change log:
# 2008/07/17  JPP   Initial version
#----------------------------------------------------------------------------
# To do:

"""
An OLVPrinter takes an ObjectListView and turns it into a pretty report.

As always, the goal is for this to be as easy to use as possible. A typical
usage should be as simple as::

   printer = OLVPrinter(self.myOlv)
   printer.PrintPreview()

"""

import wx
from ObjectListView import GroupListView

#======================================================================

class OLVPrinter(wx.Printout):
    """
    An OLVPrinter creates a pretty report from an ObjectListView.
    """

    def __init__(self, objectListView=None, title="ObjectListView Printing"):
        """
        """
        wx.Printout.__init__(self, title)
        self.currentPage = 0
        self.totalPages = 0

        self.printData = wx.PrintData()
        self.printData.SetPaperId(wx.PAPER_A4)
        self.printData.SetPrintMode(wx.PRINT_MODE_PRINTER)

        self.isColumnHeadingsOnEachPage = True
        self.alwaysCenterColumnHeader = True
        self.reportHeaderText = "gReport Header Texty"
        self.reportFooterText = "yReport Footer Textg"
        self.pageHeaderText = "gThis is the headery"
        self.pageFooterText = "yThis is the footerg"
        self.isPrintSelectionOnly = False
        self.isShrinkToFit = False

        self.watermarkText = "WATERMARK"
        self.watermarkFont = None
        self.watermarkColor = None

        self.headerFormat = None
        self.footerFormat = None
        self.columnHeadingFormat = None
        self.groupFormat = None
        self.cellFormat = None

        self.blocks = list()
        self.blockInsertionIndex = 0
        self.objectListViews = list()

        self.reportFormat = ReportFormat()

        if objectListView is not None:
            self.AddListCtrl(objectListView, title)

    #----------------------------------------------------------------------------
    # Accessing

    def HasPage(self, page):
        return page <= self.totalPages

    def GetPageInfo(self):
        return (1, self.totalPages, 1, 1)

    def GetNamedFormat(self, name):
        """
        Return the given format
        """
        return self.reportFormat.GetNamedFormat(name)

    #----------------------------------------------------------------------------
    # Setup

    def AddBlock(self, block):
        """
        Add the given block at the current insertion point
        """
        self.blocks.insert(self.blockInsertionIndex, block)
        self.blockInsertionIndex += 1
        block.printer = self


    #----------------------------------------------------------------------------
    # Commands

    def AddListCtrl(self, objectListView, title=None):
        """
        Add the given list to those that will be printed by this report.
        """
        if objectListView.InReportView():
            self.objectListViews.append([objectListView, title])


    def PageSetup(self):
        """
        Show a Page Setup dialog that will change the configuration of this printout
        """
        psdd = wx.PageSetupDialogData(self.printData)
        psdd.CalculatePaperSizeFromId()
        dlg = wx.PageSetupDialog(self, psdd)
        dlg.ShowModal()

        # this makes a copy of the wx.PrintData instead of just saving
        # a reference to the one inside the PrintDialogData that will
        # be destroyed when the dialog is destroyed
        self.printData = wx.PrintData(dlg.GetPageSetupData().GetPrintData())

        dlg.Destroy()


    def PrintPreview(self, parent=None, title="ObjectListView Print Preview", bounds=(20, 20, 400, 500)):
        """
        Show a Print Preview of this report
        """
        data = wx.PrintDialogData(self.printData)
        self.preview = wx.PrintPreview(self, None, data)

        if not self.preview.Ok():
            return False

        pfrm = wx.PreviewFrame(self.preview, parent, title)

        pfrm.Initialize()
        pfrm.SetPosition(bounds[0:2])
        pfrm.SetSize(bounds[2:4])
        pfrm.Show(True)

        return True

    def DoPrint(self, parent=None):
        """
        Send the report to the configured printer
        """
        pdd = wx.PrintDialogData(self.printData)
        printer = wx.Printer(pdd)

        if printer.Print(parent, self, True):
            self.printData = wx.PrintData(printer.GetPrintDialogData().GetPrintData())
        else:
            wx.MessageBox("There was a problem printing.\nPerhaps your current printer is not set correctly?", "Printing", wx.OK)

        printout.Destroy()


    #----------------------------------------------------------------------------
    # Event handlers

    def OnPreparePrinting(self):
        """
        Prepare for printing. This event is sent before any of the others
        """
        self.totalPages = self.CalculateTotalPages()

        self.AddBlock(ReportBlock())

    def OnBeginDocument(self, start, end):
        """
        Begin printing one copy of the document. Return False to cancel the job
        """
        if not super(OLVPrinter, self).OnBeginDocument(start, end):
            return False

        if not self.objectListViews:
            return False

        return True

    def OnEndDocument(self):
        super(OLVPrinter, self).OnEndDocument()

    def OnBeginPrinting(self):
        super(OLVPrinter, self).OnBeginPrinting()

    def OnEndPrinting(self):
        super(OLVPrinter, self).OnEndPrinting()

    def OnPrintPage(self, page):
        self.currentPage = page
        return self.PrintOnePage(self.GetDC())


    #----------------------------------------------------------------------------
    # Printing

    def PrintOnePage(self, dc):
        """
        """
        self.CalculateBounds(dc)
        self.ApplyPageDecorations(dc)

        self.CalculateWorkBounds(dc)

        self.AddBlock(PageHeaderBlock())

        while len(self.blocks) and self.blocks[0].Print(dc):
            self.blocks.pop(0)
            self.blockInsertionIndex = 0

        PageFooterBlock(self).Print(dc)

        return len(self.blocks) > 0


    def ApplyPageDecorations(self, dc):
        """
        """
        pass

    #----------------------------------------------------------------------------
    # Calculating

    def CalculateTotalPages(self):
        return 3


    def CalculateBounds(self, dc):
        """
        Calculate our page bounds
        """
        self.pageBounds = (0, 0) + dc.GetSizeTuple()


    def CalculateWorkBounds(self, dc):
        """
        Calculate our page bounds
        """
        self.workBounds = list(self.pageBounds)

#======================================================================

class ReportFormat(object):
    """
    A ReportFormat defines completely how a report is formatted.

    It holds a collection of BlockFormat objects which control the
    formatting of individual blocks of the report

    """

    def __init__(self):
        """
        """
        self.formats = [
            "ReportHeader",
            "PageHeader",
            "ListTitle",
            "GroupTitle",
            "List",
            "ColumnHeader",
            "ListRows",
            "ListRowCells",
            "PageFooter",
            "ReportFooter"
        ]
        for x in self.formats:
            setattr(self, x, BlockFormat())

    def GetNamedFormat(self, name):
        """
        Return the format used in to format a block with the given name.
        """
        return getattr(self, name)


#======================================================================

class BlockFormat(object):
    """
    A block format defines how a Block is formatted.

    """

    def __init__(self):
        """
        """
        self.padding = None
        self.decorations = list()
        self.font = wx.FFont(10, wx.FONTFAMILY_SWISS, face="Gill Sans")
        self.textColor = None
        self.textAlignment = wx.ALIGN_LEFT

    #----------------------------------------------------------------------------
    # Accessing

    def GetFont(self):
        """
        Return the font used by this format
        """
        return self.font

    def SetFont(self, font):
        """
        Set the font used by this format
        """
        self.font = font

    def GetTextColor(self):
        """
        Return the color of text in this format
        """
        return self.textColor

    def SetTextColor(self, color):
        """
        Set the color of text in this format
        """
        self.textColor = color

    def GetPadding(self):
        """
        Get the padding around this given format
        """
        return self.padding

    def SetPadding(self, padding):
        """
        Set the padding around this given format

        Padding is either a single numeric (indicating the values on all sides)
        or a collection of paddings [left, top, right, bottom]
        """
        try:
            if len(padding) < 4:
                padding = (tuple(padding) + (0, 0, 0, 0))[:4]
        except TypeError:
            padding = (padding) * 4
        self.padding = padding


    Font = property(GetFont, SetFont)
    Padding = property(GetPadding, SetPadding)
    TextColor = property(GetTextColor, SetTextColor)

    #----------------------------------------------------------------------------
    # Decorations

    def Add(self, decoration):
        """
        Add the given decoration to those adorning blocks with this format
        """
        self.decorations.append(decoration)

    #----------------------------------------------------------------------------
    # Commands

    def SubtractPadding(self, bounds):
        """
        Subtract any padding used by this format from the given bounds
        """
        if self.padding is None:
            return bounds
        else:
            return RectUtils.InsetRect(bounds, self.padding)


    def SubtractDecorations(self, bounds):
        """
        Subtract any space used by decoration in this format from the given bounds
        """
        for x in self.decorations:
            bounds = x.SubtractFrom(bounds)
        return bounds



#======================================================================

class Block(object):
    """
    A Block is a portion of a report that will stack vertically with other
    Block. A report consists of several Blocks.
    """

    def __init__(self):
        self.printer = None # This is set when the block is added to a print job

    #----------------------------------------------------------------------------
    # Accessing

    def GetFont(self):
        """
        Return Font that should be used to draw text in this block
        """
        return self.GetFormat().GetFont()


    def GetFormat(self):
        """
        Return the BlockFormat object that controls the formatting of this block
        """
        return self.printer.GetNamedFormat(self.__class__.__name__[:-5])


    def GetReducedBlockBounds(self, bounds=None):
        """
        Return the bounds of this block once padding and decoration have taken their toll.
        """
        bounds = bounds or list(self.GetWorkBounds())
        fmt = self.GetFormat()
        if fmt:
            bounds = fmt.SubtractPadding(bounds)
            bounds = fmt.SubtractDecorations(bounds)
        return bounds


    def GetWorkBounds(self):
        """
        Return the boundaries of the work area for this block
        """
        return self.printer.workBounds


    def ChangeWorkBoundsTopBy(self, amt):
        """
        Move the top of our work bounds down by the given amount
        """
        RectUtils.MoveTopBy(self.printer.workBounds, amt)

    #----------------------------------------------------------------------------
    # Calculating

    def CalculateExtrasHeight(self, dc):
        """
        Return the height of the padding and decorations themselves
        """
        return 0 - RectUtils.Height(self.GetReducedBlockBounds([0, 0, 0, 0]))


    def CalculateHeight(self, dc):
        """
        Return the heights of this block in pixels
        """
        return -1


    def CalculateTextHeight(self, dc, txt, bounds=None, font=None):
        """
        Return the height of the given txt in pixels
        """
        bounds = bounds or self.GetReducedBlockBounds()
        font = font or self.GetFormat().GetFont()
        (width, height, descent, externalLeading) = dc.GetFullTextExtent(txt, font)
        return height


    def CanFit(self, height):
        """
        Can this block fit into the remaining work area on the page?
        """
        return height <= RectUtils.Height(self.GetWorkBounds())

    #----------------------------------------------------------------------------
    # Commands

    def Print(self, dc):
        """
        Print this Block.

        Return True if the Block has finished printing
        """
        # If this block does not have a format, it is simply skipped
        if not self.GetFormat():
            return True

        height = self.CalculateHeight(dc)
        if not self.CanFit(height):
            return False

        bounds = self.GetWorkBounds()
        bounds = RectUtils.SetHeight(list(bounds), height)
        self.Draw(dc, bounds)
        self.ChangeWorkBoundsTopBy(height)
        return True


    def Draw(self, dc, bounds):
        """
        Draw this block and its decorations allowing for any padding
        """
        bounds = self.GetFormat().SubtractPadding(bounds)
        self.DrawDecorations(dc, bounds)
        bounds = self.GetFormat().SubtractDecorations(bounds)
        self.DrawSelf(dc, bounds)


    def DrawSelf(self, dc, bounds):
        """
        Do the actual work of rendering this block.
        """
        pass


    def DrawDecorations(self, dc, bounds):
        """
        Draw the decorations that are attached to this block
        """
        for x in self.GetFormat().decorations:
            x.Draw(dc, bounds, self)


    def DrawText(self, dc, txt, bounds, font=None, alignment=wx.ALIGN_LEFT, image=None):
        """
        """
        dc.SetFont(font or self.GetFont())
        dc.DrawText(txt, bounds[0], bounds[1])


#======================================================================

class TextBlock(Block):
    """
    A TextBlock prints a string objects.
    """

    def GetText(self):
        return "Missing GetText() in class %s" % self.__class__.__name__

    def CalculateHeight(self, dc):
        """
        Return the heights of this block in pixels
        """
        textHeight = self.CalculateTextHeight(dc, self.GetText())
        extras = self.CalculateExtrasHeight(dc)
        return textHeight + extras

    def DrawSelf(self, dc, bounds):
        """
        Do the actual work of rendering this block.
        """
        self.DrawText(dc, self.GetText(), bounds)


#======================================================================

class CellBlock(Block):
    """
    A CellBlock is a Block whose data is presented in a cell format.
    """

    #----------------------------------------------------------------------------
    # Accessing - Subclasses should override

    def GetCellWidths(self):
        """
        Return a list of the widths of the cells in this block
        """
        return list()

    def GetTexts(self):
        """
        Return a list of the texts that should be drawn with the cells
        """
        return list()

    def GetAlignments(self):
        """
        Return a list indicating how the text within each cell is aligned.
        """
        return list()

    def GetImages(self):
        """
        Return a list of the images that should be drawn in each cell
        """
        return list()

    #----------------------------------------------------------------------------
    # Accessing

    def CanCellsWrap(self):
        """
        Return True if the text values can wrap within a cell, producing muliline cells
        """
        return self.printer.canCellsWrap

    def GetCombinedLists(self):
        """
        Return a collection of dictionaries that hold all the values of the
        subclass-overriddable collections above
        """
        dicts = [{"cellWidth":x, "txt":"", "align":None, "image":None} for x in self.GetCellWidths()]
        for (i, x) in enumerate(self.GetTexts()):
            dicts[i]["txt"] = x
        for (i, x) in enumerate(self.GetImages()):
            dicts[i]["image"] = x
        for (i, x) in enumerate(self.GetAlignments()):
            dicts[i]["align"] = x

        return dicts

    #----------------------------------------------------------------------------
    # Calculating

    def CalculateHeight(self, dc):
        """
        Return the heights of this block in pixels
        """
        if not self.CanCellsWrap():
            return self.CalculateTextHeight(dc, "Wy")

        font = self.GetFont()
        cellFmt = self.GetFormat().GetCellFormat()
        height = 0
        for x in self.GetCombinedLists():
            bounds = [0, 0, cellWidth, 99999]
            if cellFmt:
                bounds = cellFmt.SubtractPadding(bounds)
                bounds = cellFmt.SubtractDecorations(bounds)
            height = max(height, self.CalculateTextHeight(dc, x["txt"], bounds, font))
        return height

    #----------------------------------------------------------------------------
    # Commands

    def DrawSelf(self, dc, bounds):
        """
        Do the actual work of rendering this block.
        """
        cellOuterBounds = list(bounds)
        cellOuterBounds[2] = 0
        cellFmt = self.GetFormat().GetCellFormat()
        for x in self.GetCombinedLists():
            RectUtils.SetLeft(cellOuterBounds, RectUtils.Right(cellOuterBounds))
            RectUtils.SetWidth(cellOuterBounds, x["cellWidth"])
            cellBounds = list(cellOuterBounds)
            if cellFmt:
                cellBounds = cellFmt.SubtractPadding(cellBounds)
                cellBounds = cellFmt.SubtractDecorations(cellBounds)
            self.DrawText(dc, x["txt"], cellBounds, self.GetFont(), x["align"], x["image"])


#======================================================================

class ReportBlock(Block):
    """
    A ReportBlock is boot strap Block that represents an entire report.
    """

    #----------------------------------------------------------------------------
    # Commands

    def Print(self, dc):
        """
        Print this Block.

        Return True if the Block has finished printing
        """
        self.printer.AddBlock(ReportHeaderBlock())
        for (olv, title) in self.printer.objectListViews:
            self.printer.AddBlock(ListBlock(olv, title))
        self.printer.AddBlock(ReportFooterBlock())
        return True

#======================================================================

class ReportHeaderBlock(TextBlock):
    """
    A ReportHeader is a text message that appears at the very beginning
    of a report.
    """

    def GetText(self):
        return self.printer.reportHeaderText

#======================================================================

class ReportFooterBlock(TextBlock):
    """
    A ReportFooter is a text message that appears at the very end of a report.
    """

    def GetText(self):
        return self.printer.reportFooterText


#======================================================================

class PageHeaderBlock(TextBlock):
    """
    A PageHeaderBlock appears at the top of every page.
    """

    def GetText(self):
        return self.printer.pageHeaderText

#======================================================================

class PageFooterBlock(TextBlock):
    """
    A PageFooterBlock appears at the bottom of every page
    """

    def __init__(self, printer):
        self.printer = printer

    def GetText(self):
        return self.printer.pageFooterText

    def Print(self, dc):
        """
        Print this Block.

        Return True if the Block has finished printing
        """
        # Make the footer print at the bottom of the page area
        height = self.CalculateHeight(dc)
        pageBounds = self.printer.pageBounds
        bounds = [RectUtils.Left(pageBounds), RectUtils.Bottom(pageBounds) - height,
                  RectUtils.Width(pageBounds), height]
        self.Draw(dc, bounds)

        return True


#======================================================================

class ListBlock(Block):
    """
    A ListBlock handles the printing of an entire ObjectListView.
    """

    def __init__(self, olv, title):
        self.olv = olv
        self.title = title

    #----------------------------------------------------------------------------
    # Commands

    def Print(self, dc):
        """
        Print this Block.

        Return True if the Block has finished printing
        """
        for (left, right) in self.CalculateListSlices():
            self.printer.AddBlock(ListTitleBlock(self.olv, self.title))
            self.printer.AddBlock(ListSliceBlock(self.olv, left, right))
        return True

    def CalculateListSlices(self):
        """
        Return a list of integer pairs, where each pair represents
        the left and right columns that can fit into the width of one page
        """
        if self.printer.isShrinkToFit:
            return [ (0, self.olv.GetColumnCount()-1) ]

        boundsWidth = RectUtils.Width(self.GetWorkBounds())
        pairs = list()
        left = 0
        width = 0
        for i in range(self.olv.GetColumnCount()):
            width += self.olv.GetColumnWidth(i)
            if width > boundsWidth:
                pairs.append([left, max(left, i-1)])
                width = 0
                left = i + 1

        if width > 0:
            pairs.append([left, i])
        return pairs


#======================================================================

class ListTitleBlock(TextBlock):
    """
    A ListHeaderBlock is the title that comes before an ObjectListView.
    """

    def __init__(self, olv, title):
        self.olv = olv
        self.title = title

    def GetText(self):
        return self.title


#======================================================================

class ListSliceBlock(Block):
    """
    A ListSliceBlock prints a vertical slice of an ObjectListView.
    """

    def __init__(self, olv, left, right):
        self.olv = olv
        self.left = left
        self.right = right


    #----------------------------------------------------------------------------
    # Commands

    def Print(self, dc):
        """
        Print this Block.

        Return True if the Block has finished printing
        """
        self.printer.AddBlock(ColumnHeaderBlock(self.olv, self.left, self.right))
        if isinstance(self.olv, GroupListView) and self.olv.showGroup:
            for g in self.olv.groups:
                self.printer.AddBlock(ListGroupBlock(self.olv, g, self.left, self.right))
        else:
            self.printer.AddBlock(ListRowsBlock(self.olv, None, self.left, self.right))


#======================================================================

class ColumnHeaderBlock(Block):
    """
    A ColumnHeaderBlock prints a portion of the columns header in
    an ObjectListView.
    """

    def __init__(self, olv, left, right):
        self.olv = olv
        self.left = left
        self.right = right

    #----------------------------------------------------------------------------
    # Accessing - Subclasses should override

    def GetCellWidths(self):
        """
        Return a list of the widths of the cells in this block
        """
        return list()

    def GetTexts(self):
        """
        Return a list of the texts that should be drawn with the cells
        """
        return list()

    def GetAlignments(self):
        """
        Return a list indicating how the text within each cell is aligned.
        """
        return list()

    def GetImages(self):
        """
        Return a list of the images that should be drawn in each cell
        """
        return list()

#======================================================================

class ListGroupBlock(Block):
    """
    A ListGroupBlock prints a vertical slice of an single ListGroup.
    """

    def __init__(self, olv, group, left, right):
        self.olv = olv
        self.group = group
        self.left = left
        self.right = right


#======================================================================

class ListRowsBlock(Block):
    """
    A ListRowsBlock prints rows of an ObjectListView.
    """

    def __init__(self, olv, modelObjects, left, right):
        """
        If modelObjects is None, all rows in the ObjectListView will be printed.
        """
        self.olv = olv
        self.modelObjects = modelObjects
        self.left = left
        self.right = right

#======================================================================

class Decoration(object):
    """
    A Decoration add some visual effect to a Block (e.g. borders,
    background image, watermark). They can also reserve a chunk of their Blocks
    space for their own use.

    Decorations are added to a BlockFormat which is then applied to a ReportBlock
    """

    LEFT = 0
    RIGHT = 1
    TOP = 2
    BOTTOM = 3

    def __init__(self, *args):
        pass

    #----------------------------------------------------------------------------
    # Accessing

    #----------------------------------------------------------------------------
    # Calculating

    #----------------------------------------------------------------------------
    # Commands

    def SubtractFrom(self, bounds):
        """
        Subtract the space used by this decoration from the given bounds
        """
        return bounds

    def Draw(self, dc, bounds, block):
        """
        Draw this decoration
        """
        pass

class BackgroundDecoration(Decoration):
    """
    """

    def __init__(self, color=None):
        self.color = color

    def Draw(self, dc, bounds, block):
        """
        Draw this decoration
        """
        if self.color is None:
            return
        dc.SetPen(wx.NullPen)
        dc.SetBrush(wx.Brush(self.color))
        dc.DrawRectangle(*bounds)

class LineDecoration(Decoration):
    """
    """

    def __init__(self, side=Decoration.BOTTOM, pen=None, space=0):
        self.side = side
        self.pen = pen
        self.space = space

    #----------------------------------------------------------------------------
    # Commands

    def SubtractFrom(self, bounds):
        """
        Subtract the space used by this decoration from the given bounds
        """
        inset = self.space
        if self.pen is not None:
            inset += self.pen.GetWidth()

        if self.side == Decoration.LEFT:
            return RectUtils.MoveLeftBy(bounds, inset)
        if self.side == Decoration.RIGHT:
            return RectUtils.MoveRightBy(bounds, inset)
        if self.side == Decoration.TOP:
            return RectUtils.MoveTopBy(bounds, inset)
        if self.side == Decoration.BOTTOM:
            return RectUtils.MoveBottomBy(bounds, inset)
        return bounds


    def Draw(self, dc, bounds, block):
        """
        Draw this decoration
        """
        if self.pen == None:
            return

        if self.side == Decoration.LEFT:
            pt1 = RectUtils.TopLeft(bounds)
            pt2 = RectUtils.BottomLeft(bounds)
        elif self.side == Decoration.RIGHT:
            pt1 = RectUtils.TopRight(bounds)
            pt2 = RectUtils.BottomRight(bounds)
        elif self.side == Decoration.TOP:
            pt1 = RectUtils.TopLeft(bounds)
            pt2 = RectUtils.TopRight(bounds)
        elif self.side == Decoration.BOTTOM:
            pt1 = RectUtils.BottomLeft(bounds)
            pt2 = RectUtils.BottomRight(bounds)
        else:
            return

        dc.SetPen(self.pen)
        dc.DrawLine(pt1[0], pt1[1], pt2[0], pt2[1])

#======================================================================

class RectUtils:
    """
    Static rectangle utilities
    """

    #----------------------------------------------------------------------------
    # Accessing

    @staticmethod
    def Left(r): return r[0]

    @staticmethod
    def Top(r): return r[1]

    @staticmethod
    def Width(r): return r[2]

    @staticmethod
    def Height(r): return r[3]

    @staticmethod
    def Right(r): return r[0] + r[2]

    @staticmethod
    def Bottom(r): return r[1] + r[3]

    @staticmethod
    def TopLeft(r): return [r[0], r[1]]

    @staticmethod
    def TopRight(r): return [r[0] + r[2], r[1]]

    @staticmethod
    def BottomLeft(r): return [r[0], r[1] + r[3]]

    @staticmethod
    def BottomRight(r): return [r[0] + r[2], r[1] + r[3]]

    #----------------------------------------------------------------------------
    # Modifying

    @staticmethod
    def SetLeft(r, l):
        r[0] = l
        return r

    @staticmethod
    def SetTop(r, t):
        r[1] = t
        return r

    @staticmethod
    def SetWidth(r, w):
        r[2] = w
        return r

    @staticmethod
    def SetHeight(r, h):
        r[3] = h
        return r

    @staticmethod
    def MoveLeftBy(r, delta):
        r[0] += delta
        r[2] -= delta
        return r

    @staticmethod
    def MoveTopBy(r, delta):
        r[1] += delta
        r[3] -= delta
        return r

    @staticmethod
    def MoveRightBy(r, delta):
        r[2] -= delta
        return r

    @staticmethod
    def MoveBottomBy(r, delta):
        r[3] -= delta
        return r

    #----------------------------------------------------------------------------
    # Calculations

    @staticmethod
    def InsetRect(r, r2):
        return [r[0] + r2[0], r[1] + r2[1], r[2] - (r2[0] + r2[2]), r[3] - (r2[1] + r2[3])]


#======================================================================
# TESTING ONLY
#======================================================================

if __name__ == '__main__':
    import wx
    from ObjectListView import ObjectListView, ColumnDefn

    # Where can we find the Example module?
    import sys
    sys.path.append("../Examples")

    import ExampleModel
    import ExampleImages

    class MyFrame(wx.Frame):
        def __init__(self, *args, **kwds):
            kwds["style"] = wx.DEFAULT_FRAME_STYLE
            wx.Frame.__init__(self, *args, **kwds)

            self.panel = wx.Panel(self, -1)
            self.olv = ObjectListView(self.panel, -1, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
            #theFastObjectListView = FastObjectListView(self.panel, -1, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
            #theVirtualObjectListView = VirtualObjectListView(self.panel, -1, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
            #theGroupObjectListView = GroupListView(self.panel, -1, style=wx.LC_REPORT|wx.SUNKEN_BORDER)

            sizer_2 = wx.BoxSizer(wx.VERTICAL)
            sizer_2.Add(self.olv, 1, wx.ALL|wx.EXPAND, 4)
            self.panel.SetSizer(sizer_2)
            self.panel.Layout()

            sizer_1 = wx.BoxSizer(wx.VERTICAL)
            sizer_1.Add(self.panel, 1, wx.EXPAND)
            self.SetSizer(sizer_1)
            self.Layout()

            groupImage = self.olv.AddImages(ExampleImages.getGroup16Bitmap(), ExampleImages.getGroup32Bitmap())
            userImage = self.olv.AddImages(ExampleImages.getUser16Bitmap(), ExampleImages.getUser32Bitmap())
            musicImage = self.olv.AddImages(ExampleImages.getMusic16Bitmap(), ExampleImages.getMusic32Bitmap())

            self.olv.SetColumns([
                ColumnDefn("Title", "left", 120, "title", imageGetter=musicImage),
                ColumnDefn("Artist", "left", 120, "artist", imageGetter=groupImage),
                ColumnDefn("Size", "center", 100, "sizeInBytes"),
                ColumnDefn("Last Played", "left", 100, "lastPlayed"),
                ColumnDefn("Rating", "center", 100, "rating")
            ])
            #self.olv.CreateCheckStateColumn()
            self.olv.SetObjects(ExampleModel.GetTracks())

            wx.CallLater(50, self.run)

        def run(self):
            printer = OLVPrinter(self.olv, "First ObjectListView Report")
            fmt = printer.reportFormat
            fmt.PageHeader.Font = wx.FFont(36, wx.FONTFAMILY_SWISS, face="Gill Sans")
            fmt.PageHeader.Add(BackgroundDecoration(wx.BLUE))
            fmt.PageHeader.Add(LineDecoration(side=Decoration.TOP, pen=wx.Pen(wx.RED, 5), space=0))
            fmt.PageHeader.Add(LineDecoration(pen=wx.BLACK_PEN, space=0))

            fmt.PageFooter.Font = wx.FFont(12, wx.FONTFAMILY_SWISS, face="Gill Sans")
            fmt.PageFooter.Add(BackgroundDecoration(wx.GREEN))
            fmt.PageFooter.Add(LineDecoration(pen=wx.Pen(wx.BLUE, 5), space=0))
            fmt.PageFooter.Add(LineDecoration(side=Decoration.TOP, pen=wx.RED_PEN, space=0))
            printer.PrintPreview(self)


    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
