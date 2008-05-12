# -*- coding: ISO-8859-1 -*-
#----------------------------------------------------------------------------
# Name:         ObjectListView.py
# Author:       Phillip Piper
# Created:      29 February 2008
# Copyright:    (c) 2008 Phillip Piper
# SVN-ID:       $Id$
# License:      wxWindows license
#----------------------------------------------------------------------------
# Change log:
# 2008/04/18  JPP   Cell editing complete
# 2008/03/31  JPP   Added space filling columns
# 2008/03/29  JPP   Added minimum, maximum and fixed widths for columns
# 2008/03/22  JPP   Added VirtualObjectListView and FastObjectListView
# 2008/02/29  JPP   Version converted from wax
# 2006/11/03  JPP   First version under wax
#----------------------------------------------------------------------------
# To do:
# - checkbox support
# - hidden columns, selectable on right click on header
# - copy selection to clipboard (text and HTML format)
# - secondary sort column
# - optionally preserve selection on RepopulateList
# - find on sort column on keypress

# Performance note: avoid autosized columns when there are a large number of rows.

"""
An `ObjectListView` provides a more convienent and powerful interface to a ListCtrl.

The major features of an `ObjectListView` are:

    * Automatically sorts rows by their data type.
    * Easily edits the values shown in the ListCtrl.
    * Columns can be fixed-width, have a minimum and/or maximum width, or be space-filling.
    * Displays a "list is empty" message when the list is empty (obviously).
    * Supports custom formatting of rows
    * The `FastObjectListView` version can build a list of 10,000 objects in less than 0.1 seconds.
    * The `VirtualObjectListView` version supports millions of rows through ListCtrl's virtual mode.
    * Supports alternate rows background colors.

An `ObjectListView` works in a declarative manner: the programmer configures how it should
work, then gives it the list of objects to display. The primary configuration is in the
definitions of the columns. Columns are configured to know which aspect of their model
they should display, how it should be formatted, and even how new values should be written
back into the model. See `ColumnDefn` for more information.

See the `ObjectListView home page <http://objectlistview.sourceforge.net/>`_ for more information.
This page talks about the C# version of this control, but the ideas are the same. Unforunately,
the wxWindows ListCtrl is not as feature rich as the .NET ListView so some features are not
possible to replicate: owner drawing and grouping spring to mind.

"""

__author__ = "Phillip Piper"
__date__ = "2 May 2008"
__version__ = "1.2"

import wx
import locale
import datetime

import CellEditor
import OLVEvent

class ObjectListView(wx.ListCtrl):
    """
    An object list displays various aspects of a list of objects in a multi-column list control.

    To use an ObjectListView, the programmer defines what columns are in the control and which
    bits of information each column should display. The programmer then calls `SetObjects` with
    the list of objects that the ObjectListView should display. The ObjectListView then builds
    the control.

    Columns hold much of the intelligence of this control. Columns define both the format
    (width, alignment), the aspect to be shown in the column, and the columns behaviour.
    See `ColumnDefn` for full details.

    These are public instance variables. (All other variables should be considered private.)

    * cellEditMode
        This control whether and how the cells of the control are editable. It can be
        set to one of the following values:

        CELLEDIT_NONE
           Cell editing is not allowed on the control This is the default.

        CELLEDIT_SINGLECLICK
           Single clicking on any subitem cell begins an edit operation on that cell.
           Single clicking on the primaru cell does *not* start an edit operation.
           It simply selects the row. Pressing F2 edits the primary cell.

        CELLEDIT_DOUBLECLICK
           Double clicking any cell starts an edit operation on that cell, including
           the primary cell. Pressing F2 edits the primary cell.

        CELLEDIT_F2ONLY
           Pressing F2 edits the primary cell. Tab/Shift-Tab can be used to edit other
           cells. Clicking does not start any editing.

    * evenRowsBackColor
        When `useAlternateBackColors` is true, even numbered rows will have this
        background color.

    * oddRowsBackColor
        When `useAlternateBackColors` is true, odd numbered rows will have this
        background color.

    * rowFormatter
        To further control the formatting of individual rows, this property
        can be set to a callable that expects three parameters: the
        listitem whose characteristics are to be set, the index of the row being
        formatted, and the model object being displayed on that row. The row formatter
        is called after the alternate back colours (if any) have been set.

        Remember: the background and text colours are overridden by system defaults
        while a row is selected.

    * useAlternateBackColors
        If this property is true, even and odd rows will be given different
        background. The background colors are controlled by the properties
        `evenRowsBackColor` and `oddRowsBackColor`. This is true by default.
    """

    CELLEDIT_NONE = 0
    CELLEDIT_SINGLECLICK = 1
    CELLEDIT_DOUBLECLICK = 2
    CELLEDIT_F2ONLY = 3

    def __init__(self, *args, **kwargs):
        """
        Create an ObjectListView.

        Apart from the normal ListCtrl parameters, this constructor looks for any of the following optional parameters:

            * `cellEditMode`
            * `rowFormatter`
            * `useAlternateBackColors`

        The behaviour of these properties are described in the class documentation.

        """
        self.objects = []
        self.columns = []
        self.sortColumn = None
        self.sortAscending = True
        self.smallImageList = None
        self.normalImageList = None
        self.downArrowIndex = -1
        self.upArrowIndex = -1
        self.cellEditor = None
        self.cellBeingEdited = None
        self.selectionBeforeCellEdit = []
        self.rowFormatter = kwargs.pop("rowFormatter", None)
        self.useAlternateBackColors = kwargs.pop("useAlternateBackColors", True)
        self.cellEditMode = kwargs.pop("cellEditMode", self.CELLEDIT_NONE)

        wx.ListCtrl.__init__(self, *args, **kwargs)

        self.SetImageLists()
        self.EnableSorting()

        self.evenRowsBackColor = wx.Colour(240, 248, 255) # ALICE BLUE
        self.oddRowsBackColor = wx.Colour(255, 250, 205) # LEMON CHIFFON

        self.Bind(wx.EVT_CHAR, self.HandleChar)
        self.Bind(wx.EVT_LEFT_UP, self.HandleLeftClickOrDoubleClick)
        self.Bind(wx.EVT_LEFT_DCLICK, self.HandleLeftClickOrDoubleClick)
        self.Bind(wx.EVT_LIST_COL_BEGIN_DRAG, self.HandleColumnBeginDrag)
        #self.Bind(wx.EVT_LIST_COL_DRAGGING, self.HandleColumnDragging) # When is this event triggered?
        self.Bind(wx.EVT_LIST_COL_END_DRAG, self.HandleColumnEndDrag)
        self.Bind(wx.EVT_MOUSEWHEEL, self.HandleMouseWheel)
        self.Bind(wx.EVT_SCROLLWIN, self.HandleScroll)
        self.Bind(wx.EVT_SIZE, self.HandleSize)

        self.stEmptyListMsg = wx.StaticText(self, -1, "This list is empty", wx.Point(0,0), wx.Size(0,0), wx.ALIGN_CENTER | wx.ST_NO_AUTORESIZE)
        self.stEmptyListMsg.Hide()
        self.stEmptyListMsg.SetForegroundColour(wx.LIGHT_GREY)
        self.stEmptyListMsg.SetBackgroundColour(self.GetBackgroundColour())
        self.stEmptyListMsg.SetFont(wx.Font(24, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))


    #--------------------------------------------------------------#000000#FFFFFF
    # Setup

    def SetColumns(self, columns):
        """
        Set the list of columns that will be displayed.

        The elements of the list can be either ColumnDefn objects or a tuple holding the values
        to be given to the ColumnDefn constructor.
        The first column is the principle value, that will be shown in the the non-report views.
        """
        self.ClearAll()
        self.columns = []
        for x in columns:
            if isinstance(x, ColumnDefn):
                self._AppendColumnDefn(x)
            else:
                self._AppendColumnDefn(ColumnDefn(*x))
        self.RepopulateList()


    def _AppendColumnDefn(self, defn):
        """
        Append the given ColumnDefn object to our list of active columns
        """
        self.InsertColumn(len(self.columns), defn.title, defn.GetAlignment(), defn.width)
        self.columns.append(defn)


    def RegisterSortIndicators(self, sortUp, sortDown):
        """
        Register the bitmaps that should be used to indicated which column is being sorted
        These bitmaps must be the same dimensions as the small image list (not sure
        why that should be so, but it is)
        """
        self.downArrowIndex = self.AddImages(sortDown)
        self.upArrowIndex = self.AddImages(sortUp)


    def SetImageLists(self, smallImageList=None, normalImageList=None):
        """
        Remember the image lists to be used for this control.

        Use this to change the size of images shown by the list control.
        If the small image list is 16x16 in size, the default sort indicators
        will be registered in the image lists. Otherwise, the user will have
        to call RegisterSortIndicators() with images of the correct size
        """
        self.smallImageList = smallImageList or wx.ImageList(16, 16)
        self.SetImageList(self.smallImageList, wx.IMAGE_LIST_SMALL)

        self.normalImageList = normalImageList or wx.ImageList(32, 32)
        self.SetImageList(self.normalImageList, wx.IMAGE_LIST_NORMAL)

        #LINUX: this returns 0 if the list is empty
        # Install the default sort indicators
        #if self.smallImageList.GetSize(0) == (16,16):

        self.RegisterSortIndicators(_getSmallUpArrowBitmap(), _getSmallDownArrowBitmap())

    #--------------------------------------------------------------#000000#FFFFFF
    # Commands

    def AddImages(self, smallImage=None, normalImage=None):
        """
        Add the given images to the list of available images. Return the index of the image.
        """
        if isinstance(smallImage, (str, unicode)):
            smallImage = wx.Bitmap(smallImage)
        if isinstance(normalImage, (str, unicode)):
            normalImage = wx.Bitmap(normalImage)

        # There must always be the same number of small and normal bitmaps,
        # so if we aren't given one, we have to make an empty one of the right size
        smallImage = smallImage or wx.EmptyBitmap(*self.smallImageList.GetSize(0))
        normalImage = normalImage or wx.EmptyBitmap(*self.normalImageList.GetSize(0))

        self.smallImageList.Add(smallImage)
        return self.normalImageList.Add(normalImage)


    def AutoSizeColumns(self):
        """
        Resize our auto sizing columns to match the data
        """
        for (iCol, col) in enumerate(self.columns):
            if col.width == wx.LIST_AUTOSIZE:
                self.SetColumnWidth(iCol, wx.LIST_AUTOSIZE)

                # The new width must be within our minimum and maximum
                colWidth = self.GetColumnWidth(iCol)
                boundedWidth = col.CalcBoundedWidth(colWidth)
                if colWidth != boundedWidth:
                    self.SetColumnWidth(iCol, boundedWidth)


    def ClearAll(self):
        """
        Remove all items and columns
        """
        wx.ListCtrl.ClearAll(self)
        self.SetObjects(list())


    def DeleteAllItems(self):
        """
        Remove all items
        """
        wx.ListCtrl.DeleteAllItems(self)
        self.SetObjects(list())


    def EnsureCellVisible(self, rowIndex, subItemIndex):
        """
        Make sure the user can see all of the given cell, scrolling if necessary.
        Return the bounds to the cell calculated after the cell has been made visible.
        Return None if the cell cannot be made visible (non-Windows platforms can't scroll
        the listview horizontally)

        If the cell is bigger than the ListView, the top left of the cell will be visible.
        """
        self.EnsureVisible(rowIndex)
        bounds = self.GetSubItemRect(rowIndex, subItemIndex, wx.LIST_RECT_BOUNDS)
        boundsRight = bounds[0]+bounds[2]
        if bounds[0] < 0 or boundsRight > self.GetSize()[0]:
            if bounds[0] < 0:
                horizDelta = bounds[0] - (self.GetSize()[0] / 4)
            else:
                horizDelta = boundsRight - self.GetSize()[0] + (self.GetSize()[0] / 4)
            if wx.Platform == "__WXMSW__":
                self.ScrollList(horizDelta, 0)
            else:
                return None

        return self.GetSubItemRect(rowIndex, subItemIndex, wx.LIST_RECT_LABEL)


    def FormatAllRows(self):
        """
        Set up the required formatting on all rows
        """
        for i in range(self.GetItemCount()):
            item = self.GetItem(i)
            self.FormatOneItem(item, i, self.GetObjectAt(i))
            self.SetItem(item)


    def FormatOneItem(self, item, index, model):
        """
        Give the given row it's correct background color
        """
        if self.useAlternateBackColors:
            if index & 1:
                item.SetBackgroundColour(self.oddRowsBackColor)
            else:
                item.SetBackgroundColour(self.evenRowsBackColor)

        if self.rowFormatter is not None:
            self.rowFormatter(item, model)


    def RepopulateList(self):
        """
        Completely rebuild the contents of the list control
        """
        self.Freeze()
        try:
            wx.ListCtrl.DeleteAllItems(self)
            if len(self.objects) == 0 or len(self.columns) == 0:
                self.Refresh()
                self.stEmptyListMsg.Show()
                return

            self.stEmptyListMsg.Hide()

            # Sort the objects so they are in the order they will be displayed.
            # Sorting like this is 5-10x faster than relying on the ListCtrl::SortItems()
            # (under Windows, at least)
            if self.sortColumn is not None:
                self.SortObjects()

            # Insert all the rows
            item = wx.ListItem()
            item.SetColumn(0)
            colZero = self.columns[0]
            for (i, x) in enumerate(self.objects):
                # Insert the new row
                item.Clear()
                item.SetId(i)
                item.SetData(i)
                item.SetText(colZero.GetStringValue(x))
                item.SetImage(colZero.GetImage(x))
                self.FormatOneItem(item, i, x)
                self.InsertItem(item)

                # Insert all the subitems
                for iCol in range(1, len(self.columns)):
                    self.SetStringItem(i, iCol, self.GetStringValueAt(x, iCol), self.GetImageAt(x, iCol))

            # Auto-resize once all the data has been added
            self.AutoSizeColumns()
        finally:
            self.Thaw()


    def RefreshIndex(self, index, object):
        """
        Refresh the item at the given index with data associated with the given object
        """
        item = self.GetItem(index)
        item.SetText(self.GetStringValueAt(object, 0))
        item.SetImage(self.GetImageAt(object, 0))
        self.FormatOneItem(item, index, object)
        self.SetItem(item)

        for iCol in range(1, len(self.columns)):
            self.SetStringItem(index, iCol, self.GetStringValueAt(object, iCol), self.GetImageAt(object, iCol))


    def RefreshObject(self, object):
        """
        Refresh the display of the given object
        """
        try:
            i = self.objects.index(object)
        except ValueError:
            return

        self.RefreshIndex(self.FindItemData(-1, i), object)


    def RefreshObjects(self, aList):
        """
        Refresh all the objects in the given list
        """
        try:
            self.Freeze()
            for x in aList:
                self.RefreshObject(x)
        finally:
            self.Thaw()


    def ResizeSpaceFillingColumns(self):
        """
        Change the width of space filling columns so that they fill the
        unoccupied width of the listview
        """
        # If the list isn't in report view or there are no space filling columns, just return
        if not self.HasFlag(wx.LC_REPORT):
            return

        if True not in set(x.isSpaceFilling for x in self.columns):
            return

        # Calculate how much free space is available in the control
        totalFixedWidth = sum(self.GetColumnWidth(i) for (i,x) in enumerate(self.columns) if not x.isSpaceFilling)
        freeSpace = max(0, self.GetClientSizeTuple()[0] - totalFixedWidth)

        # Calculate the total number of slices the free space will be divided into
        totalProportion = sum(x.freeSpaceProportion for x in self.columns if x.isSpaceFilling)

        # Space filling columns that would escape their boundary conditions
        # are treated as fixed size columns
        columnsToResize = []
        for (i, col) in enumerate(self.columns):
            if col.isSpaceFilling:
                newWidth = freeSpace * col.freeSpaceProportion / totalProportion
                boundedWidth = col.CalcBoundedWidth(newWidth)
                if newWidth == boundedWidth:
                    columnsToResize.append((i,col))
                else:
                    freeSpace -= boundedWidth
                    totalProportion -= col.freeSpaceProportion
                    if self.GetColumnWidth(i) != boundedWidth:
                        self.SetColumnWidth(i, boundedWidth)

        # Finally, give each remaining space filling column a proportion of the free space
        for (i, col) in columnsToResize:
            newWidth = freeSpace * col.freeSpaceProportion / totalProportion
            boundedWidth = col.CalcBoundedWidth(newWidth)
            if self.GetColumnWidth(i) != boundedWidth:
                self.SetColumnWidth(i, boundedWidth)


    def SetColumnFixedWidth(self, colIndex, width):
        """
        Make the given column to be fixed width
        """
        self.SetColumnWidth(colIndex, width)
        self.columns[colIndex].SetFixedWidth(width)


    def SetEmptyListMsg(self, msg):
        """
        When there are no objects in the list, show this message in the control
        """
        self.stEmptyListMsg.SetLabel(msg)


    def SetEmptyListMsgFont(self, font):
        """
        In what font should the empty list msg be rendered?
        """
        self.stEmptyListMsg.SetFont(font)


    def SetObjects(self, objects, preserveSelection=False):
        """
        Set the list of objects to be displayed by the control.
        """

        if preserveSelection:
            selection = self.GetSelectedObjects()

        if objects is None:
            self.objects = list()
        else:
            self.objects = objects[:]
        self.RepopulateList()

        if preserveSelection:
            self.SelectObjects(selection)

    # Synonym as per many wxWindows widgets
    SetValue = SetObjects


    #--------------------------------------------------------------#000000#FFFFFF
    # Accessing

    def GetFocusedRow(self):
        """
        Return the index of the row that has the focus. -1 means no focus
        """
        return self.GetNextItem(-1, wx.LIST_NEXT_ALL, wx.LIST_STATE_FOCUSED)


    def GetImageAt(self, object, columnIndex):
        """
        Return the index of the image that should be display at the given column of the given object
        """
        column = self.columns[columnIndex]
        return column.GetImage(object)


    def GetObjectAt(self, index):
        """
        Return the model object at the given row of the list.
        """
        # Because of sorting, index can't be used directly, which is
        # why we set the item data to be the real index
        return self.objects[self.GetItemData(index)]


    def __getitem__(self, index):
        """
        Synactic sugar over GetObjectAt()
        """
        return self.GetObjectAt(index)


    def GetSelectedObject(self):
        """
        Return the selected object or None if nothing is selected or if more than one is selected.
        """
        objs = self.GetSelectedObjects()
        if len(objs) == 1:
            return objs[0]
        else:
            return None


    def GetSelectedObjects(self):
        """
        Return a list of the selected objects
        """
        #TODO: Implement another method that uses yield, and use that method here
        objs = list()
        i = self.GetNextItem(-1, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
        while i != -1:
            objs.append(self.GetObjectAt(i))
            i = self.GetNextItem(i, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)

        return objs


    def GetSubItemRect(self, rowIndex, subItemIndex, flag):
        """
        Poor mans replacement for missing wxWindows method.

        The rect returned takes scroll position into account, so negative x and y are
        possible.
        """
        #print "GetSubItemRect(self, %d, %d, %d):" % (rowIndex, subItemIndex, flag)

        # Linux doesn't handle wx.LIST_RECT_LABEL flag. So we always get
        # the whole bounds then par it down to the cell we want
        rect = self.GetItemRect(rowIndex, wx.LIST_RECT_BOUNDS)

        if self.HasFlag(wx.LC_REPORT):
            rect = [0-self.GetScrollPos(wx.HORIZONTAL), rect.Y, 0, rect.Height]
            for i in range(subItemIndex+1):
                rect[0] += rect[2]
                rect[2] = self.GetColumnWidth(i)

        # If we want only the label rect for sub items, we have to manually
        # adjust for any image the subitem might have
        if flag == wx.LIST_RECT_LABEL:
            lvi = self.GetItem(rowIndex, subItemIndex)
            if lvi.GetImage() != -1:
                imageWidth = self.smallImageList.GetSize(0)[0] + 1
                rect[0] += imageWidth
                rect[2] -= imageWidth

        #print "rect=%s" % rect
        return rect


    def GetStringValueAt(self, object, columnIndex):
        """
        Return a string representation of the value that should be display at the given column of the given object
        """
        column = self.columns[columnIndex]
        return column.GetStringValue(object)


    def GetValueAt(self, object, columnIndex):
        """
        Return the value that should be display at the given column of the given object
        """
        column = self.columns[columnIndex]
        return column.GetValue(object)


    def HitSubItem(self, pt):
        """
        Return a tuple indicating which (item, subItem) the given pt (client coordinates) is over.
        """
        (rowIndex, flags) = self.HitTest(pt)

        # Did the point hit any item?
        if (flags & wx.LIST_HITTEST_ONITEM) == 0:
            return (-1, -1)

        # If it did hit an item and we are not in report mode, it must be the primary cell
        if not self.HasFlag(wx.LC_REPORT):
            return (rowIndex, 0)

        # Find which subitem is hit
        right = 0
        scrolledX = self.GetScrollPos(wx.HORIZONTAL) + pt.x
        for i in range(self.GetColumnCount()):
            right += self.GetColumnWidth(i)
            if scrolledX < right:
                return (rowIndex, i)

        return (rowIndex, -1)


    def IsCellEditing(self):
        """
        Is some cell currently being edited?
        """
        return self.cellEditor and self.cellEditor.IsShown()


    def IsObjectSelected(self, obj):
        """
        Is the given object selected?
        """
        return obj in self.GetSelectedObjects()


    #----------------------------------------------------------------------------
    # Event handling

    def HandleChar(self, evt):
        if evt.GetKeyCode() == wx.WXK_F2 and not self.IsCellEditing():
            return self.PossibleStartCellEdit(self.GetFocusedRow(), 0)

        # We have to catch Return/Enter/Escape here since some types of controls
        # (e.g. ComboBox, UserControl) don't trigger key events that we can listen for.
        # Treat Return or Enter as committing the current edit operation
        if evt.GetKeyCode() in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER) and self.IsCellEditing():
            return self.FinishCellEdit()

        # Treat Escape as cancel the current edit operation
        if evt.GetKeyCode() in (wx.WXK_ESCAPE, wx.WXK_CANCEL) and self.IsCellEditing():
            return self.CancelCellEdit()

        # Tab to the next editable column
        if evt.GetKeyCode() == wx.WXK_TAB and self.IsCellEditing():
            return self.HandleTabKey(evt.ShiftDown())

        evt.Skip()


    def HandleColumnBeginDrag(self, evt):
        """
        Handle when the user begins to resize a column
        """
        colIndex = evt.GetColumn()
        if 0 > colIndex >= len(self.columns):
            evt.Skip()
        else:
            col = self.columns[colIndex]
            if col.IsFixedWidth() or col.isSpaceFilling:
                evt.Veto()
            else:
                evt.Skip()


    def HandleColumnClick(self, evt):
        """
        The user has clicked on a column title
        """
        evt.Skip()

        # Toggle the sort column on the second click
        if evt.GetColumn() == self.sortColumn:
            self.sortAscending = not self.sortAscending
        else:
            self.sortAscending = True

        # TODO: Trigger vetoable SortEvent here

        self.SortBy(evt.GetColumn(), self.sortAscending)
        self.FormatAllRows()


    def HandleColumnDragging(self, evt):
        """
        A column is being dragged
        """
        # When is this triggered?

        # The processing should be the same processing as Dragged
        evt.Skip()


    def HandleColumnEndDrag(self, evt):
        """
        The user has finished resizing a column
        """
        colIndex = evt.GetColumn()
        if 0 > colIndex >= len(self.columns):
            evt.Skip()
        else:
            currentWidth = self.GetColumnWidth(colIndex)
            col = self.columns[colIndex]
            newWidth = col.CalcBoundedWidth(currentWidth)
            if currentWidth != newWidth:
                wx.CallAfter(self._SetColumnWidthAndResize, colIndex, newWidth)
            else:
                evt.Skip()
                wx.CallAfter(self.ResizeSpaceFillingColumns)

    def _SetColumnWidthAndResize(self, colIndex, newWidth):
        self.SetColumnWidth(colIndex, newWidth)
        self.ResizeSpaceFillingColumns()


    def HandleLeftClickOrDoubleClick(self, evt):
        """
        Handle a left click or left double click on the ListView
        """
        evt.Skip()

        # IF any modifiers are down, OR
        #    the listview isn't editable, OR
        #    we should edit on double click and this is a single click, OR
        #    we should edit on single click and this is a double click,
        # THEN we don't try to start a cell edit operation
        if evt.m_altDown or evt.m_controlDown or evt.m_shiftDown:
            return
        if self.cellEditMode == self.CELLEDIT_NONE:
            return
        if evt.LeftUp() and self.cellEditMode == self.CELLEDIT_DOUBLECLICK:
            return
        if evt.LeftDClick() and self.cellEditMode == self.CELLEDIT_SINGLECLICK:
            return

        # Which item did the user click?
        (rowIndex, subItemIndex) = self.HitSubItem(evt.GetPosition())
        if subItemIndex == -1:
            return

        # A single click on column 0 doesn't start an edit
        if subItemIndex == 0 and self.cellEditMode == self.CELLEDIT_SINGLECLICK:
            return

        self.StartCellEdit(rowIndex, subItemIndex)


    def HandleMouseWheel(self, evt):
        """
        The user spun the mouse wheel
        """
        self.PossibleFinishCellEdit()
        evt.Skip()


    def HandleScroll(self, evt):
        """
        The ListView is being scrolled
        """
        self.PossibleFinishCellEdit()
        evt.Skip()


    def HandleSize(self, evt):
        """
        The ListView is being resized
        """
        evt.Skip()
        self.ResizeSpaceFillingColumns()
        # Make sure our empty msg is reasonably positioned
        sz = self.GetClientSize()
        self.stEmptyListMsg.SetDimensions(0, sz.GetHeight()/3, sz.GetWidth(), sz.GetHeight())


    def HandleTabKey(self, isShiftDown):
        """
        Handle a Tab key during a cell edit operation
        """
        (rowBeingEdited, subItem) = self.cellBeingEdited

        # Prevent a nasty flicker when tabbing between fields where the selected rows
        # are restored at the end of one cell edit, and removed at the start of the next
        shadowSelection = self.selectionBeforeCellEdit
        self.selectionBeforeCellEdit = []
        self.FinishCellEdit()

        # If we are in report view, move to the next (or previous) editable subitem,
        # wrapping at the edges
        if self.HasFlag(wx.LC_REPORT):
            columnCount = self.GetColumnCount()
            for i in range(columnCount-1):
                if isShiftDown:
                    subItem = (columnCount + subItem - 1) % columnCount
                else:
                    subItem = (subItem + 1) % columnCount
                if self.columns[subItem].isEditable and self.GetColumnWidth(subItem) > 0:
                    self.StartCellEdit(rowBeingEdited, subItem)
                    break

        self.selectionBeforeCellEdit = shadowSelection


    #--------------------------------------------------------------#000000#FFFFFF
    # Sorting

    def EnableSorting(self):
        """
        Enable automatic sorting when the user clicks on a column title
        """
        self.Bind(wx.EVT_LIST_COL_CLICK, self.HandleColumnClick)


    def SortBy(self, newColumn, ascending=True):
        """
        Sort the items by the given column
        """
        oldSortColumn = self.sortColumn
        self.sortColumn = newColumn
        self.sortAscending = ascending

        self.SortItems(self.SorterCallback)
        self.UpdateColumnSortIndicators(self.sortColumn, oldSortColumn)


    def SortObjects(self):
        """
        Sort our model objects in place
        """
        col = self.columns[self.sortColumn]

        def getLowerCaseSortValue(x):
            value = col.GetValue(x)
            if isinstance(value, (str, unicode)):
                return value.lower()
            else:
                return value

        self.objects.sort(key=getLowerCaseSortValue, reverse=(not self.sortAscending))


    def SorterCallback(self, key1, key2):
        """
        Sort callback used by SortItems().
        For some reason, key1 and key2 are the item data for each item.
        """
        col = self.sortColumn
        item1 = self.GetValueAt(self.objects[key1], col)
        item2 = self.GetValueAt(self.objects[key2], col)

        if isinstance(item1, (str, unicode)):
            cmpVal = locale.strcoll(item1.lower(), item2.lower())

            # Uncomment this line if you want captialized strings to come before lowercase strings
            #cmpVal = locale.strcoll(item1, item2)
        else:
            cmpVal = cmp(item1, item2)

        if self.sortAscending:
            return cmpVal
        else:
            return -cmpVal


    def UpdateColumnSortIndicators(self, sortColumn, oldSortColumn):
        """
        Change the column that is showing a sort indicator
        """
        if oldSortColumn is not None:
            self.ClearColumnImage(oldSortColumn)

        if sortColumn is not None:
            if self.sortAscending:
                self.SetColumnImage(sortColumn, self.upArrowIndex)
            else:
                self.SetColumnImage(sortColumn, self.downArrowIndex)


    #--------------------------------------------------------------#000000#FFFFFF
    # Selecting

    def SelectAll(self):
        """
        Selected all objects
        """
                    # On Windows, -1 indicates 'all items'. Not sure about other platforms
        self.SetItemState(-1, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)

                    # Elsewhere, use this code. But it's much slower especially for virtual lists
#        for i in range(self.GetItemCount()):
#            self.SetItemState(i, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)


    def DeselectAll(self):
        """
        De-selected all objects
        """
                    # On Windows, -1 indicates 'all items'. Not sure about other platforms
        self.SetItemState(-1, 0, wx.LIST_STATE_SELECTED)

                    # Elsewhere, use this code. But it's much slower especially for virtual lists
#        i = self.GetNextItem(-1, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
#        while i != -1:
#            self.SetItemState(i, 0, wx.LIST_STATE_SELECTED)
#            i = self.GetNextItem(i, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)


    def SelectObject(self, obj, deselectOthers=True):
        """
        Select the given object. If deselectOthers is True, all other objects will be deselected
        """
        try:
            i = self.objects.index(obj)
        except ValueError:
            return

        if deselectOthers:
            self.DeselectAll()

        self.SetItemState(self.FindItemData(-1, i), wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)


    def SelectObjects(self, objects, deselectOthers=True):
        """
        Select all of the given objects. If deselectOthers is True, all other objects will be deselected
        """
        if deselectOthers:
            self.DeselectAll()

        # Select each object that is in 'objects'
        objectSet = frozenset(objects)
        for (i, x) in enumerate(self.objects):
            if x in objectSet:
                self.SetItemState(self.FindItemData(-1, i), wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)

        # If you wanted to punish future maintainers, you could collapse the above loop into one list comprehension:
        # [self.SetItemState(self.FindItemData(-1, i), wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED) for (i, x) in enumerate(self.objects) if x in objectSet]
        # but that would just be being mean :-)
        # The list comprehension does run marginally faster (1.15 secs instead of 1.18 seconds when selecting 1000 objects out of a list of 2000),
        # but that speed saving is not worth the loss of understandability.


    #----------------------------------------------------------------------------
    # Cell editing

    def PossibleStartCellEdit(self, rowIndex, subItemIndex):
        """
        Start an edit operation on the given cell after performing some sanity checks
        """
        if 0 > rowIndex >= self.GetItemCount():
            return

        if 0 > subItemIndex >= self.GetColumnCount():
            return

        if self.cellEditMode == self.CELLEDIT_NONE:
            return

        if not self.columns[subItemIndex].isEditable:
            return

        self.StartCellEdit(rowIndex, subItemIndex)


    def PossibleFinishCellEdit(self):
        """
        If a cell is being edited, finish and commit an edit operation on the given cell.
        """
        if self.IsCellEditing():
            self.FinishCellEdit()


    def PossibleCancelCellEdit(self):
        """
        If a cell is being edited, cancel the edit operation.
        """
        if self.IsCellEditing():
            self.CancelCellEdit()


    def StartCellEdit(self, rowIndex, subItemIndex):
        """
        Begin an edit operation on the given cell.
        """

        # Collect the information we need for the StartingEditEvent
        modelObject = self.GetObjectAt(rowIndex)
        cellValue = self.GetValueAt(modelObject, subItemIndex)

        # Make sure the user can see where the editor is going to be. If the bounds are
        # null, this means we needed to scroll horizontally but were unable (this can only
        # happen on non-Windows platforms). In that case we can't let the edit happen
        # since the user won't be able to see the cell
        cellBounds = self.EnsureCellVisible(rowIndex, subItemIndex)
        if cellBounds is None:
            wx.Bell()
            return

        # Give the world the chance to veto the edit, or to change its characteristics
        defaultEditor = self.MakeDefaultCellEditor(rowIndex, subItemIndex, cellValue)
        evt = OLVEvent.CellEditStartingEvent(self, rowIndex, subItemIndex, modelObject, cellValue, cellBounds, defaultEditor)
        self.GetEventHandler().ProcessEvent(evt)
        if evt.IsVetoed():
            defaultEditor.Destroy()
            return

        # Remember that we are editing something (and make sure we can see it)
        self.selectionBeforeCellEdit = self.GetSelectedObjects()
        self.DeselectAll()
        self.cellEditor = evt.newEditor or evt.editor
        self.cellBeingEdited = (rowIndex, subItemIndex)

        # If we aren't using the default editor, destroy it
        if self.cellEditor != defaultEditor:
            defaultEditor.Destroy()

        # If the event handler hasn't already configured the editor, do it now.
        if evt.shouldConfigureEditor:
            print evt.cellValue
            self.cellEditor.SetValue(evt.cellValue)
            self.ConfigureCellEditor(self.cellEditor, evt.cellBounds, rowIndex, subItemIndex)

        self.cellEditor.SetFocus()
        self.cellEditor.Show()
        self.cellEditor.Raise()


    def ConfigureCellEditor(self, editor, bounds, rowIndex, subItemIndex):
        """
        Perform the normal configuration on the cell editor.
        """
        editor.SetDimensions(*bounds)

        colour = self.GetItemBackgroundColour(rowIndex)
        if colour.IsOk():
            editor.SetBackgroundColour(colour)
        else:
            editor.SetBackgroundColour(self.GetBackgroundColour())

        colour = self.GetItemTextColour(rowIndex)
        if colour.IsOk():
            editor.SetForegroundColour(colour)
        else:
            editor.SetForegroundColour(self.GetTextColour())

        font = self.GetItemFont(rowIndex)
        if font.IsOk():
            editor.SetFont(font)
        else:
            editor.SetFont(self.GetFont())

        if hasattr(self.cellEditor, "SelectAll"):
            self.cellEditor.SelectAll()

        editor.Bind(wx.EVT_CHAR, self.Editor_OnChar)
        editor.Bind(wx.EVT_COMMAND_ENTER, self.Editor_OnChar)
        editor.Bind(wx.EVT_KILL_FOCUS, self.Editor_KillFocus)

    def MakeDefaultCellEditor(self, rowIndex, subItemIndex, value):
        """
        Return an editor that can edit the value of the given cell.
        """

        # The column could have editor creation function registered.
        # Otherwise, we have to guess the editor from the type of the value.
        # If the given cell actually holds None, we can't decide what editor to use.
        # So we try to find any non-null value in the same column.
        # If all else fails, we use a string editor.
        creatorFunction = self.columns[subItemIndex].cellEditorCreator
        if creatorFunction is None:
            value = value or self._CalcNonNullValue(subItemIndex)
            creatorFunction = CellEditor.CellEditorRegistry().GetCreatorFunction(value)
            if creatorFunction is None:
                creatorFunction = CellEditor.CellEditorRegistry().GetCreatorFunction("")
        return creatorFunction(self, rowIndex, subItemIndex)

    def _CalcNonNullValue(self, colIndex, maxRows=1000):
        """
        Return the first non-null value in the given column, processing
        at most maxRows rows
        """
        column = self.columns[colIndex]
        for i in range(min(self.GetItemCount(), maxRows)):
            value = column.GetValue(self.GetObjectAt(i))
            if value is not None:
                return value
        return None

    def Editor_OnChar(self, evt):
        self.HandleChar(evt)

    def Editor_KillFocus(self, evt):
        evt.Skip()

        # Some control trigger FocusLost events even when they still have focus
        focusWindow = wx.Window.FindFocus()
        if focusWindow is not None and self.cellEditor != focusWindow:
            self.PossibleFinishCellEdit()

    def FinishCellEdit(self):
        """
        Finish and commit an edit operation on the given cell.
        """
        (rowIndex, subItemIndex) = self.cellBeingEdited

        # Give the world the chance to veto the edit, or to change its characteristics
        rowModel = self.GetObjectAt(rowIndex)
        evt = OLVEvent.CellEditFinishingEvent(self, rowIndex, subItemIndex, rowModel, self.cellEditor.GetValue(), self.cellEditor, False)
        self.GetEventHandler().ProcessEvent(evt)
        if not evt.IsVetoed() and evt.cellValue is not None:
            self.columns[subItemIndex].SetValue(rowModel, evt.cellValue)
            self.RefreshIndex(rowIndex, rowModel)

        self.CleanupCellEdit()

    def CancelCellEdit(self):
        """
        Cancel an edit operation on the given cell.
        """
        # Tell the world that the user cancelled the edit
        (rowIndex, subItemIndex) = self.cellBeingEdited
        evt = OLVEvent.CellEditFinishingEvent(self, rowIndex, subItemIndex, self.GetObjectAt(rowIndex), self.cellEditor.GetValue(), self.cellEditor, True)
        self.GetEventHandler().ProcessEvent(evt)
        self.CleanupCellEdit()

    def CleanupCellEdit(self):
        """
        Cleanup after finishing a cell edit operation
        """
        self.SelectObjects(self.selectionBeforeCellEdit)
        self.cellEditor.Hide()
        self.cellEditor = None
        self.cellBeingEdited = None
        self.SetFocus()


########################################################################

class VirtualObjectListView(ObjectListView):
    """
    A virtual object list displays various aspects of an unlimited numbers of objects in a
    multi-column list control.

    A virtual list must be given an "object getter", which is a callable that accepts the
    index of the model object required and returns the model. This can be set via the
    SetObjectGetter() method, or passed into the constructor as the "getter" parameter.

    Due to the vagarities of virtual lists, rowFormatters must operate in a slightly
    different manner for virtual lists. Instead of being passed a ListItem, rowFormatters
    are passed a ListItemAttr instance. This supports the same formatting methods as a
    ListItem -- SetBackgroundColour(), SetTextColour(), SetFont() -- but no other ListItem
    methods. Obviously, being a virtual list, the rowFormatter cannot call any SetItem*
    method on the ListView itself.

    """

    def __init__(self, *args, **kwargs):
        self.lastGetObjectIndex = -1
        self.lastGetObject = None
        #self.cacheHit = 0
        #self.cacheMiss = 0

        self.SetObjectGetter(kwargs.pop("getter", None))
        if kwargs.has_key("count"):
            wx.CallAfter(self.SetItemCount, kwargs.pop("count"))

        # Virtual lists have to be in report format
        kwargs["style"] = kwargs.get("style", 0) | wx.LC_REPORT | wx.LC_VIRTUAL

        ObjectListView.__init__(self, *args, **kwargs)


    #----------------------------------------------------------------------------
    # Commands

    def SetObjectGetter(self, aCallable):
        """
        Remember the callback that will be used to fetch the objects being displayed in
        this list
        """
        self.objectGetter = aCallable


    def SetItemCount(self, count):
        """
        Change the number of items visible in the list
        """
        wx.ListCtrl.SetItemCount(self, count)
        self.Refresh()
        self.lastGetObjectIndex = -1


    def ClearAll(self):
        """
        Remove all items and columns
        """
        ObjectListView.ClearAll(self)
        self.lastGetObjectIndex = -1


    def DeleteAllItems(self):
        """
        Remove all items
        """
        ObjectListView.DeleteAllItems(self)
        self.lastGetObjectIndex = -1


    def RepopulateList(self):
        """
        Completely rebuild the contents of the list control
        """
        # Virtual lists never need to rebuild -- they simply redraw
        self.RefreshObjects()


    def RefreshObjects(self, aList=None):
        """
        Refresh all the objects in the given list
        """
        # We can only refresh everything
        self.lastGetObjectIndex = -1
        self.RefreshItems(0, self.GetItemCount()-1)
        self.Refresh()


    def RefreshObject(self, object):
        """
        Refresh the display of the given object
        """
        # We only have a hammer so everything looks like a nail
        self.RefreshObjects()


    def RefreshIndex(self, index, object):
        """
        Refresh the item at the given index with data associated with the given object
        """
        self.lastGetObjectIndex = -1
        self.RefreshItem(index)


    def SelectObject(self, obj, deselectOthers=True):
        """
        Select the given object. If deselectOthers is True, all other objects will be deselected
        """
        # This doesn't work for virtual lists, since the virtual list has no way
        # of knowing where 'obj' is within the list.
        pass


    def SelectObjects(self, objects, deselectOthers=True):
        """
        Select all of the given objects. If deselectOthers is True, all other objects will be deselected
        """
        # This doesn't work for virtual lists, since the virtual list has no way
        # of knowing where any of the objects are within the list.
        pass


    def FormatAllRows(self):
        """
        Set up the required formatting on all rows
        """
        # This can't work for virtual lists since a virtual list can't iterate all its items
        pass


    #----------------------------------------------------------------------------
    # Virtual list callbacks.
    # These are called a lot! Keep them efficient

    def OnGetItemText(self, itemIdx, colIdx):
        return self.GetStringValueAt(self.GetObjectAt(itemIdx), colIdx)


    def OnGetItemImage(self, itemIdx):
        return self.GetImageAt(self.GetObjectAt(itemIdx), 0)


    def OnGetItemColumnImage(self, itemIdx, colIdx):
        return self.GetImageAt(self.GetObjectAt(itemIdx), colIdx)


    def OnGetItemAttr(self, itemIdx):
        if not self.useAlternateBackColors and self.rowFormatter is None:
            return None

        # We only get the model if we have a row formatter. This is a virtual list and
        # getting the model may be expensive, so we avoid it where possible
        if self.rowFormatter is None:
            model = None
        else:
            model = self.GetObjectAt(itemIdx)

        # We have to keep a reference to the ListItemAttr or the garbage collector
        # will clear it up immeditately, before the ListCtrl has time to process it.
        self.listItemAttr = wx.ListItemAttr()
        self.FormatOneItem(self.listItemAttr, itemIdx, model)

        return self.listItemAttr


    #----------------------------------------------------------------------------
    # Accessing

    def GetObjectAt(self, index):
        """
        Return the model object at the given row of the list.

        This method is called a lot! Keep it as efficient as possible.
        """

        # It may even be worthwhile removing this test by ensuring that objectGetter
        # is never None
        if self.objectGetter is None:
            return None

        #if index == self.lastGetObjectIndex:
        #    self.cacheHit += 1
        #else:
        #    self.cacheMiss += 1
        #print "hit: %d / miss: %d" % (self.cacheHit, self.cacheMiss)

        # Cache the last result (the hit rate is normally good: 5-10 hits to 1 miss)
        if index != self.lastGetObjectIndex:
            self.lastGetObjectIndex = index
            self.lastGetObject = self.objectGetter(index)

        return self.lastGetObject


########################################################################

class FastObjectListView(VirtualObjectListView):
    """
    A fast object list view is a nice compromise between the functionality of an ObjectListView
    and the speed of a VirtualObjectListView.

    This class codes around the limitations of a virtual list.
    """

    def __init__(self, *args, **kwargs):

        VirtualObjectListView.__init__(self, *args, **kwargs)

        self.SetObjectGetter(lambda index: self.objects[index])


    def RepopulateList(self):
        """
        Completely rebuild the contents of the list control
        """
        self.lastGetObjectIndex = -1

        if self.sortColumn is not None:
            self.SortObjects()

        self.SetItemCount(len(self.objects))
        self.Refresh()
        self.stEmptyListMsg.Show(len(self.objects) == 0)

        # Auto-resize once all the data has been added
        self.AutoSizeColumns()


    def SelectObject(self, obj, deselectOthers=True):
        """
        Select the given object. If deselectOthers is True, all other objects will be deselected
        """
        try:
            i = self.objects.index(obj)
        except ValueError:
            return

        if deselectOthers:
            self.DeselectAll()

        self.SetItemState(i, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)


    def SelectObjects(self, objects, deselectOthers=True):
        """
        Select all of the given objects. If deselectOthers is True, all other objects will be deselected
        """
        if deselectOthers:
            self.DeselectAll()

        # Select each object that is in 'objects'
        objectSet = frozenset(objects)
        for (i, x) in enumerate(self.objects):
            if x in objectSet:
                self.SetItemState(i, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)


    def RefreshObject(self, object):
        """
        Refresh the display of the given object
        """
        VirtualObjectListView.RefreshObject(self, object)

        # We could be more precise and only refresh one row. But if
        # self.objects is a large collection (>10,000) finding the object
        # in the collection could be slower than simply redrawing everything
        # (which is what the base method does)

        #try:
        #    self.RefreshIndex(self.objects.index(object))
        #except ValueError:
        #    pass


    #---Sorting-------------------------------------------------------#000000#FFFFFF

    def SortBy(self, newColumn, ascending=True):
        """
        Sort the items by the given column
        """
        oldSortColumn = self.sortColumn
        self.sortColumn = newColumn
        self.sortAscending = ascending

        selection = self.GetSelectedObjects()
        self.SortObjects()
        self.SelectObjects(selection)
        self.UpdateColumnSortIndicators(self.sortColumn, oldSortColumn)
        self.RefreshObjects()


#######################################################################

class ColumnDefn(object):
    """
    A ColumnDefn controls how one column of information is sourced and formatted.

    Much of the intelligence and ease of use of an ObjectListView comes from the column
    definitions. It is worthwhile gaining an understanding of capabilities of this class.

    Public Attributes (alphabetically):

    * align
        How will the title and the cells of the this column be aligned. Possible
        values: 'left', 'centre', 'right'

    * cellEditorCreator
        This is a callable that will be invoked when a value in this column needs to
        be edited. The callable should accept three parameters: the objectListView
        starting the edit, the rowIndex and the subItemIndex. If this is None, a cell
        editor will be chosen based on the type of objects in this column (See
        CellEditor.EditorRegistry).

    * freeSpaceProportion
        If the column is space filling, what proportion of the space should be given
        to this column. By default, all spacing filling column share the free space
        equally. By changing this attribute, a column can be given a larger proportion
        of the space.

    * isSpaceFilling
        Is this column a space filler? Space filling columns resize to occupy free
        space within the listview. As the listview is expanded, space filling columns
        expand as well. Conversely, as the control shrinks these columns shrink too.
        Space filling columns can disappear (i.e. have a width of 0) if the control
        becomes too small. You can set `minimumWidth` to prevent them from
        disappearing.

    * imageGetter
        A string, callable or integer that is used to get a index of the image to be
        shown in a cell.

        Strings and callable are used as for the `valueGetter` attribute.

        Integers are treated as constants (that is, all rows will have the same
        image).

    * isEditable
        Can the user edit cell values in this column? Default is True

    * maximumWidth
        An integer indicate the number of pixels above which this column will not resize.
        Default is -1, which means there is no limit.

    * minimumWidth
        An integer indicate the number of pixels below which this column will not resize.
        Default is -1, which means there is no limit.

    * stringConverter
        A string or a callable that will used to convert a cells value into a presentation string.

        If it is a callble, it will be called with the value for the cell and must return a string.

        If it is a string, it will be used as a format string with the % operator, e.g.
        "self.stringConverter % value." For dates and times, the stringConverter will be
        passed as the first parameter to the strftime() method on the date/time.

    * title
        A string that will be used as the title of the column in the listview

    * valueGetter
        A string, callable or integer that is used to get the value to be displayed in
        a cell. See _Munge() for details on how this attribute is used.

        A callable is simply called and the result is the value for the cell.

        The string can be the name of a method to be invoked, the name of an attribute
        to be fetched, or (for dictionary like objects) an index into the dictionary.

        An integer can only be used for list-like objects and is used as an index into
        the list.

    * width
        How many pixels wide will the column be? -1 means auto size to contents. For a list with
        thousands of items, autosize can be noticably slower than specifically setting the size.


    The `title`, `align` and `width` attributes are only references when the column definition is given to the
    ObjectListView via the `SetColumns()` or `AddColumnDefn()` methods. The other attributes are referenced
    intermittently -- changing them will change the behaviour of the `ObjectListView`.

    Without a string converter, None will be converted to an empty string. Install a string converter ('%s'
    will suffice) if you want to see the 'None' instead.

    BUG: Double-clicking on a divider (under Windows) can resize a column beyond its minimum and maximum widths.
    """

    def __init__(self, title="title", align="left", width=-1,
                 valueGetter=None, imageGetter=None, stringConverter=None, valueSetter=None, isEditable=True,
                 fixedWidth=None, minimumWidth=-1, maximumWidth=-1, isSpaceFilling=False,
                 cellEditorCreator=None, autoCompleteCellEditor=False, autoCompleteComboBoxCellEditor=False):
        """
        Create a new ColumnDefn using the given attributes.

        The attributes behave as described in the class documentation, except for:

        * fixedWidth
            An integer which indicates that this column has the given width and is not resizable.
            Useful for column that always display fixed with data (e.g. a single icon). Setting this
            parameter overrides the width, minimumWidth and maximumWidth parameters.

        * autoCompleteCellEditor
            If this is True, the column will use an autocomplete TextCtrl when
            values of this column are edited. This overrules the cellEditorCreator parameter.

        * autoCompleteComboBoxCellEditor
            If this is True, the column will use an autocomplete ComboBox when
            values of this column are edited. This overrules the cellEditorCreator parameter.
        """
        self.title = title
        self.align = align
        self.valueGetter = valueGetter
        self.imageGetter = imageGetter
        self.stringConverter = stringConverter
        self.valueSetter = valueSetter
        self.isSpaceFilling = isSpaceFilling
        self.cellEditorCreator = cellEditorCreator
        self.freeSpaceProportion = 1
        self.isEditable = isEditable

        self.minimumWidth = minimumWidth
        self.maximumWidth = maximumWidth
        self.width = self.CalcBoundedWidth(width)

        if fixedWidth is not None:
            self.SetFixedWidth(fixedWidth)

        if autoCompleteCellEditor:
            self.cellEditorCreator = lambda olv, row, col: CellEditor.MakeAutoCompleteTextBox(olv, col)

        if autoCompleteComboBoxCellEditor:
            self.cellEditorCreator = lambda olv, row, col: CellEditor.MakeAutoCompleteComboBox(olv, col)

    #-------------------------------------------------------------------------------
    # Column properties

    def GetAlignment(self):
        """
        Return the alignment that this column uses
        """
        alignment = {
            "l": wx.LIST_FORMAT_LEFT,
            "c": wx.LIST_FORMAT_CENTRE,
            "r": wx.LIST_FORMAT_RIGHT
        }.get(self.align[:1], wx.LIST_FORMAT_LEFT)

        return alignment

    def GetAlignmentForText(self):
        """
        Return the alignment of this column in a form that can be used as
        a style flag on a text control
        """
        return {
            "l": wx.TE_LEFT,
            "c": wx.TE_CENTRE,
            "r": wx.TE_RIGHT,
        }.get(self.align[:1], wx.TE_LEFT)

    #-------------------------------------------------------------------------------
    # Value accessing

    def GetValue(self, object):
        """
        Return the value for this column from the given object
        """
        return self._Munge(object, self.valueGetter)


    def GetStringValue(self, object):
        """
        Return a string representation of the value for this column from the given object
        """
        value = self.GetValue(object)
        if callable(self.stringConverter):
            return self.stringConverter(value)

        if self.stringConverter and isinstance(value, (datetime.datetime, datetime.date, datetime.time)):
            return value.strftime(self.stringConverter)

        # By default, None is changed to an empty string.
        if not self.stringConverter and not value:
            return ""

        fmt = self.stringConverter or "%s"
        try:
            return fmt % value
        except UnicodeError:
            return unicode(fmt) % value


    def GetImage(self, object):
        """
        Return the image index for this column from the given object. -1 means no image.
        """
        if self.imageGetter is None:
            return -1
        elif isinstance(self.imageGetter, int):
            return self.imageGetter
        else:
            return self._Munge(object, self.imageGetter) or -1


    def SetValue(self, object, value):
        """
        Set this columns aspect of the given object to have the given value.
        """
        if self.valueSetter is None:
            return self._SetValueUsingMunger(object, value, self.valueGetter, False)
        else:
            return self._SetValueUsingMunger(object, value, self.valueSetter, True)


    def _SetValueUsingMunger(self, object, value, munger, shouldInvokeCallable):
        """
        Look for ways to update object with value using munger. If munger finds a
        callable, it will be called if shouldInvokeCallable == True.
        """
        # If there isn't a munger, we can't do anything
        if munger is None:
            return

        # Is munger a function?
        if callable(munger):
            if shouldInvokeCallable:
                munger(object, value)
            return

        # Try indexed access for dictionary or list like objects
        try:
            object[munger] = value
            return
        except:
            pass

        # Is munger the name of some slot in the object?
        try:
            attr = getattr(object, munger)
        except TypeError:
            return
        except AttributeError:
            return

        # Is munger the name of a method?
        if callable(attr):
            if shouldInvokeCallable:
                attr(value)
            return

        # If we get to here, it seems that munger is the name of an attribute or
        # property on object. Try to set, realising that many things could still go wrong.
        try:
            setattr(object, munger, value)
        except:
            pass


    def _Munge(self, object, munger):
        """
        Wrest some value from the given object using the munger.
        With a description like that, you know this method is going to be obscure :-)

        'munger' can be:

        1) a callable.
           This method will return the result of executing 'munger' with 'object' as its parameter.

        2) the name of an attribute of the object.
           If that attribute is callable, this method will return the result of executing that attribute.
           Otherwise, this method will return the value of that attribute.

        3) an index (string or integer) onto the object.
           This allows dictionary-like objects and list-like objects to be used directly.
        """
        if munger is None:
            return None

        # Use the callable directly, if possible
        if callable(munger):
            return munger(object)

        # THINK: The following code treats an instance variable with the value of None
        # as if it doesn't exist. Is that best?

        # Try attribute access
        try:
            attr = getattr(object, munger, None)
            if attr is not None:
                if callable(attr):
                    return attr()
                else:
                    return attr
        except TypeError:
            # Happens when munger is a number
            pass

        # Try dictionary-like indexing
        try:
            return object[munger]
        except:
            return None

    #-------------------------------------------------------------------------------
    # Width management

    def CalcBoundedWidth(self, width):
        """
        Calculate the given width bounded by the (optional) minimum and maximum column widths
        """

        # Values of < 0 have special meanings, so just return them
        if width < 0:
            return width

        if self.maximumWidth >= 0:
            width = min(self.maximumWidth, width)
        return max(self.minimumWidth, width)


    def IsFixedWidth(self):
        """
        Is this column fixed width?
        """
        return self.minimumWidth != -1 and self.maximumWidth != -1 and (self.minimumWidth >= self.maximumWidth)


    def SetFixedWidth(self, width):
        """
        Make this column fixed width
        """
        self.width = self.minimumWidth = self.maximumWidth = width

#-------------------------------------------------------------------------------
# Built in images so clients don't have to do the same

import cStringIO, zlib

def _getSmallUpArrowData():
    return zlib.decompress(
'x\xda\xeb\x0c\xf0s\xe7\xe5\x92\xe2b``\xe0\xf5\xf4p\t\x02\xd2\x02 \xcc\xc1\
\x06$\xe5?\xffO\x04R,\xc5N\x9e!\x1c@P\xc3\x91\xd2\x01\xe4[z\xba8\x86X\xf4&\
\xa7\xa4$\xa5-`1\x08\\R\xcd"\x11\x10\x1f\xfe{~\x0es\xc2,N\xc9\xa6\xab\x0c%\
\xbe?x\x0e\x1a0LO\x8ay\xe4sD\xe3\x90\xfay\x8bYB\xec\x8d\x8c\x0c\xc1\x01b9\
\xe1\xbc\x8fw\x01\ra\xf0t\xf5sY\xe7\x94\xd0\x04\x00\xb7\x89#\xbb' )

def _getSmallUpArrowBitmap():
    stream = cStringIO.StringIO(_getSmallUpArrowData())
    return wx.BitmapFromImage(wx.ImageFromStream(stream))

#----------------------------------------------------------------------

def _getSmallDownArrowData():
    return zlib.decompress(
'x\xda\xeb\x0c\xf0s\xe7\xe5\x92\xe2b``\xe0\xf5\xf4p\t\x02\xd2\x02 \xcc\xc1\
\x06$\xe5?\xffO\x04R,\xc5N\x9e!\x1c@P\xc3\x91\xd2\x01\xe4\x07x\xba8\x86X\xf4\
&\xa7\xa4$\xa5-`1\x08\\R}\x85\x81\r\x04\xc4R\xfcjc\xdf\xd6;II\xcd\x9e%Y\xb8\
\x8b!v\xd2\x844\x1e\xe6\x0f\x92M\xde2\xd9\x12\x0b\xb4\x8f\xbd6rSK\x9b\xb3c\
\xe1\xc2\x87\xf6v\x95@&\xdb\xb1\x8bK|v22,W\x12\xd0\xdb-\xc4\xe4\x044\x9b\xc1\
\xd3\xd5\xcfe\x9dSB\x13\x00$1+:' )


def _getSmallDownArrowBitmap():
    stream = cStringIO.StringIO(_getSmallDownArrowData())
    return wx.BitmapFromImage(wx.ImageFromStream(stream))

#
#######################################################################
# TESTING ONLY

if __name__ == '__main__':
    pass
