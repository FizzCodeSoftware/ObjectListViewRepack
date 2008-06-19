# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
# Name:         ObjectListView.py
# Author:       Phillip Piper
# Created:      29 February 2008
# Copyright:    (c) 2008 Phillip Piper
# SVN-ID:       $Id$
# License:      wxWindows license
#----------------------------------------------------------------------------
# Change log:
# 2008/06/16  JPP   - Search by sorted column works, even on virtual lists
# 2008/06/12  JPP   - Added sortable parameter
#                   - Renamed sortColumn to be sortColumnIndex to make it clear
#                   - Allow returns in multiline cell editors
# v1.0
# 2008/05/29  JPP   Used named images internally
# 2008/05/26  JPP   Fixed pyLint annoyances
# 2008/05/24  JPP   Images can be referenced by name
# 2008/05/17  JPP   Checkboxes supported
# 2008/04/18  JPP   Cell editing complete
# 2008/03/31  JPP   Added space filling columns
# 2008/03/29  JPP   Added minimum, maximum and fixed widths for columns
# 2008/03/22  JPP   Added VirtualObjectListView and FastObjectListView
# 2008/02/29  JPP   Version converted from wax
# 2006/11/03  JPP   First version under wax
#----------------------------------------------------------------------------
# To do:
# - cancellable Sort event
# - images in the column headers
# - selectable columns, triggered on right click on header
# - copy selection to clipboard (text and HTML format)
# - secondary sort column
# - optionally preserve selection on RepopulateList
# - get rid of scrollbar when editing label in icon view
# - need a ChangeView() method to help when switching between views

"""
An `ObjectListView` provides a more convienent and powerful interface to a ListCtrl.

The major features of an `ObjectListView` are:

    * Automatically transforms a collection of model objects into a ListCtrl.
    * Automatically sorts rows by their data type.
    * Easily edits the values shown in the ListCtrl.
    * Supports all ListCtrl views (report, list, large and small icons).
    * Columns can be fixed-width, have a minimum and/or maximum width, or be space-filling.
    * Displays a "list is empty" message when the list is empty (obviously).
    * Supports custom formatting of rows
    * Supports alternate rows background colors.
    * Supports checkbox columns
    * Supports searching (by typing) on the sorted column -- even on virtual lists.
    * The `FastObjectListView` version can build a list of 10,000 objects in less than 0.1 seconds.
    * The `VirtualObjectListView` version supports millions of rows through ListCtrl's virtual mode.

An `ObjectListView` works in a declarative manner: the programmer configures how it should
work, then gives it the list of objects to display. The primary configuration is in the
definitions of the columns. Columns are configured to know which aspect of their model
they should display, how it should be formatted, and even how new values should be written
back into the model. See `ColumnDefn` for more information.

"""

__author__ = "Phillip Piper"
__date__ = "18 June 2008"
__version__ = "1.0.1"

import wx
import datetime
import itertools
import locale
import operator
import string

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
        can be set to a callable that expects two parameters: the listitem whose
        characteristics are to be set, and the model object being displayed on that row.

        The row formatter is called after the alternate back colours (if any) have been
        set.

        Remember: the background and text colours are overridden by system defaults
        while a row is selected.

    * typingSearchesSortColumn
        If this boolean is True (the default), when the user types into the list, the
        control will try to find a prefix match on the values in the sort column. If this
        is False, or the list is unsorted or if the sorted column is marked as not
        searchable (via `isSearchable` attribute), the primary column will be matched.

    * useAlternateBackColors
        If this property is true, even and odd rows will be given different
        background. The background colors are controlled by the properties
        `evenRowsBackColor` and `oddRowsBackColor`. This is true by default.
    """

    CELLEDIT_NONE = 0
    CELLEDIT_SINGLECLICK = 1
    CELLEDIT_DOUBLECLICK = 2
    CELLEDIT_F2ONLY = 3

    """Names of standard images used within the ObjectListView. If you want to use your
    own image in place of a standard one, simple register it with AddNamedImages() using
    one of the following names."""
    NAME_DOWN_IMAGE = "objectListView.downImage"
    NAME_UP_IMAGE = "objectListView.upImage"
    NAME_CHECKED_IMAGE = "objectListView.checkedImage"
    NAME_UNCHECKED_IMAGE = "objectListView.uncheckedImage"
    NAME_UNDETERMINED_IMAGE = "objectListView.undeterminedImage"

    """When typing into the list, a delay between keystrokes greater than this (in ms)
    will be interpretted as a new search and any previous search text will be cleared"""
    SEARCH_KEYSTROKE_DELAY = 750

    """When typing into a list and searching on an unsorted column, we don't even try to search
    if there are more than this many rows."""
    MAX_ROWS_FOR_UNSORTED_SEARCH = 100000

    def __init__(self, *args, **kwargs):
        """
        Create an ObjectListView.

        Apart from the normal ListCtrl parameters, this constructor looks for any of the following optional parameters:

            * `cellEditMode`
            * `rowFormatter`
            * `sortable`
            * `useAlternateBackColors`

        The behaviour of these properties are described in the class documentation, except for `sortable.`

        `sortable` controls whether the rows of the control will be sorted when the user clicks on the header.
        This is true by default. If it is False, clicking the header will be nothing, and no images will be
        registered in the image lists. This parameter only has effect at creation time -- it has no impact
        after creation.

        """
        self.modelObjects = []
        self.columns = []
        self.sortColumnIndex = None
        self.sortAscending = True
        self.smallImageList = None
        self.normalImageList = None
        self.cellEditor = None
        self.cellBeingEdited = None
        self.selectionBeforeCellEdit = []
        self.checkStateColumn = None

        self.rowFormatter = kwargs.pop("rowFormatter", None)
        self.useAlternateBackColors = kwargs.pop("useAlternateBackColors", True)
        self.sortable = kwargs.pop("sortable", True)
        self.cellEditMode = kwargs.pop("cellEditMode", self.CELLEDIT_NONE)
        self.typingSearchesSortColumn = kwargs.pop("typingSearchesSortColumn", True)

        self.evenRowsBackColor = wx.Colour(240, 248, 255) # ALICE BLUE
        self.oddRowsBackColor = wx.Colour(255, 250, 205) # LEMON CHIFFON

        wx.ListCtrl.__init__(self, *args, **kwargs)

        if self.sortable:
            self.EnableSorting()

        # NOTE: On Windows, ListCtrl's don't trigger EVT_LEFT_UP :(

        self.Bind(wx.EVT_CHAR, self._HandleChar)
        self.Bind(wx.EVT_LEFT_DOWN, self._HandleLeftDown)
        self.Bind(wx.EVT_LEFT_UP, self._HandleLeftClickOrDoubleClick)
        self.Bind(wx.EVT_LEFT_DCLICK, self._HandleLeftClickOrDoubleClick)
        self.Bind(wx.EVT_LIST_COL_BEGIN_DRAG, self._HandleColumnBeginDrag)
        self.Bind(wx.EVT_LIST_COL_END_DRAG, self._HandleColumnEndDrag)
        self.Bind(wx.EVT_MOUSEWHEEL, self._HandleMouseWheel)
        self.Bind(wx.EVT_SCROLLWIN, self._HandleScroll)
        self.Bind(wx.EVT_SIZE, self._HandleSize)

        # When is this event triggered?
        #self.Bind(wx.EVT_LIST_COL_DRAGGING, self._HandleColumnDragging)

        self.stEmptyListMsg = wx.StaticText(self, -1, "This list is empty",
            wx.Point(0, 0), wx.Size(0, 0), wx.ALIGN_CENTER | wx.ST_NO_AUTORESIZE)
        self.stEmptyListMsg.Hide()
        self.stEmptyListMsg.SetForegroundColour(wx.LIGHT_GREY)
        self.stEmptyListMsg.SetBackgroundColour(self.GetBackgroundColour())
        self.stEmptyListMsg.SetFont(wx.Font(24, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))

        self.searchPrefix = u""
        self.whenLastTypingEvent = 0

    #--------------------------------------------------------------#000000#FFFFFF
    # Setup

    def SetColumns(self, columns):
        """
        Set the list of columns that will be displayed.

        The elements of the list can be either ColumnDefn objects or a tuple holding the values
        to be given to the ColumnDefn constructor.

        The first column is the primary column -- this will be shown in the the non-report views.

        This clears any preexisting CheckStateColumn. The first column that is a check state
        column will be installed as the CheckStateColumn for this listview.
        """
        self.ClearAll()
        self.checkStateColumn = None
        self.columns = []
        for x in columns:
            if isinstance(x, ColumnDefn):
                self.AddColumnDefn(x)
            else:
                self.AddColumnDefn(ColumnDefn(*x))
        self.RepopulateList()


    def AddColumnDefn(self, defn):
        """
        Append the given ColumnDefn object to our list of active columns.

        If this method is called directly, you must also call RepopulateList()
        to populate the new column with data.
        """
        self.InsertColumn(len(self.columns), defn.title, defn.GetAlignment(), defn.width)
        self.columns.append(defn)

        # The first checkbox column becomes the check state column for the control
        if defn.HasCheckState() and self.checkStateColumn is None:
            self.InstallCheckStateColumn(defn)


    def _InitializeCheckBoxImages(self):
        """
        Initialize some checkbox images for use by this control.
        """
        def _makeBitmap(state, size):
            bitmap = wx.EmptyBitmap(size, size)
            dc = wx.MemoryDC(bitmap)
            dc.Clear()
            wx.RendererNative.Get().DrawCheckBox(self, dc, (0, 0, size, size), state)
            dc.SelectObject(wx.NullBitmap)
            return bitmap

        def _makeBitmaps(name, state):
            self.AddNamedImages(name, _makeBitmap(state, 16), _makeBitmap(state, 32))

        # If there isn't a small image list, make one
        if self.smallImageList is None:
            self.SetImageLists()

        _makeBitmaps(ObjectListView.NAME_CHECKED_IMAGE, wx.CONTROL_CHECKED)
        _makeBitmaps(ObjectListView.NAME_UNCHECKED_IMAGE, wx.CONTROL_CURRENT)
        _makeBitmaps(ObjectListView.NAME_UNDETERMINED_IMAGE, wx.CONTROL_UNDETERMINED)


    def CreateCheckStateColumn(self, columnIndex=0):
        """
        Create a fixed width column at the given index to show the checkedness
        of objects in this list.

        If this is installed at column 0 (which is the default), the listview
        should only be used in Report view.

        This should be called after SetColumns() has been called, since
        SetColumns() removed any previous check state column.

        RepopulateList() or SetObjects() must be called after this.
        """
        col = ColumnDefn("", fixedWidth=24, isEditable=False)
        col.valueGetter = col.GetCheckState # Install a value getter so sorting works
        col.stringConverter = lambda x: "" # We don't want any string for the value
        self.columns.insert(columnIndex, col)
        self.SetColumns(self.columns)
        self.InstallCheckStateColumn(col)


    def InstallCheckStateColumn(self, column):
        """
        Configure the given column so that it shows the check state of each row in this
        control.

        This column's checkbox will be toggled when the user pressed space when a row is
        selected.

        `RepopulateList()` or `SetObjects()` must be called after a new check state column is
        installed for the check state column to be visible.

        Set to None to remove the check state column.
        """
        self.checkStateColumn = column
        if column is None:
            return

        if self.smallImageList == None or \
           not self.smallImageList.HasName(ObjectListView.NAME_CHECKED_IMAGE):
            self._InitializeCheckBoxImages()

        # Is the column already configured to handle check state?
        if column.HasCheckState():
            return

        # The column isn't managing it's own check state, so install handlers
        # that will manage the state. This is useful when the checkedness is
        # related to the view and is not an attribute of the model.
        checkState = dict()
        def _handleGetCheckState(modelObject):
            return checkState.get(modelObject, False) # objects are not checked by default

        def _handleSetCheckState(modelObject, newValue):
            checkState[modelObject] = newValue
            return newValue

        column.checkStateGetter = _handleGetCheckState
        column.checkStateSetter = _handleSetCheckState


    def RegisterSortIndicators(self, sortUp=None, sortDown=None):
        """
        Register the bitmaps that should be used to indicated which column is being sorted
        These bitmaps must be the same dimensions as the small image list (not sure
        why that should be so, but it is)

        If no parameters are given, 16x16 default images will be registered
        """
        self.AddNamedImages(ObjectListView.NAME_DOWN_IMAGE, sortDown or _getSmallDownArrowBitmap())
        self.AddNamedImages(ObjectListView.NAME_UP_IMAGE, sortUp or _getSmallUpArrowBitmap())


    def SetImageLists(self, smallImageList=None, normalImageList=None):
        """
        Remember the image lists to be used for this control.

        Call this without parameters to create reasonable default image lists.

        Use this to change the size of images shown by the list control.
        """
        if isinstance(smallImageList, NamedImageList):
            self.smallImageList = smallImageList
        else:
            self.smallImageList = NamedImageList(smallImageList, 16)
        self.SetImageList(self.smallImageList.imageList, wx.IMAGE_LIST_SMALL)

        if isinstance(normalImageList, NamedImageList):
            self.normalImageList = normalImageList
        else:
            self.normalImageList = NamedImageList(normalImageList, 32)
        self.SetImageList(self.normalImageList.imageList, wx.IMAGE_LIST_NORMAL)


    #--------------------------------------------------------------#000000#FFFFFF
    # Commands

    def AddImages(self, smallImage=None, normalImage=None):
        """
        Add the given images to the list of available images. Return the index of the image.
        """
        return self.AddNamedImages(None, smallImage, normalImage)


    def AddNamedImages(self, name, smallImage=None, normalImage=None):
        """
        Add the given images to the list of available images. Return the index of the image.

        If a name is given, that name can later be used to refer to the images rather
        than having to use the returned index.
        """
        if isinstance(smallImage, basestring):
            smallImage = wx.Bitmap(smallImage)
        if isinstance(normalImage, basestring):
            normalImage = wx.Bitmap(normalImage)

        # We must have image lists for images to be added to them
        if self.smallImageList is None or self.normalImageList is None:
            self.SetImageLists()

        # There must always be the same number of small and normal bitmaps,
        # so if we aren't given one, we have to make an empty one of the right size
        smallImage = smallImage or wx.EmptyBitmap(*self.smallImageList.GetSize(0))
        normalImage = normalImage or wx.EmptyBitmap(*self.normalImageList.GetSize(0))

        self.smallImageList.AddNamedImage(name, smallImage)
        return self.normalImageList.AddNamedImage(name, normalImage)


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


    def Check(self, modelObject):
        """
        Mark the given model object as checked.
        """
        self.SetCheckState(modelObject, True)


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


    def _FormatAllRows(self):
        """
        Set up the required formatting on all rows
        """
        for i in range(self.GetItemCount()):
            item = self.GetItem(i)
            self._FormatOneItem(item, i, self.GetObjectAt(i))
            self.SetItem(item)


    def _FormatOneItem(self, item, index, model):
        """
        Give the given row it's correct background color
        """
        if self.useAlternateBackColors and self.InReportView():
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
            if len(self.modelObjects) == 0 or len(self.columns) == 0:
                self.Refresh()
                self.stEmptyListMsg.Show()
                return

            self.stEmptyListMsg.Hide()

            # Sort the objects so they are in the order they will be displayed.
            # Sorting like this is 5-10x faster than relying on the ListCtrl::SortItems()
            # (under Windows, at least)
            if self.sortColumnIndex is not None:
                self._SortObjects()

            # Insert all the rows
            item = wx.ListItem()
            item.SetColumn(0)
            colZero = self.columns[0]
            for (i, x) in enumerate(self.modelObjects):
                # Insert the new row
                item.Clear()
                item.SetId(i)
                item.SetData(i)
                item.SetText(colZero.GetStringValue(x))
                item.SetImage(self.GetImageAt(x, 0))
                self._FormatOneItem(item, i, x)
                self.InsertItem(item)

                # Insert all the subitems
                for iCol in range(1, len(self.columns)):
                    self.SetStringItem(i, iCol, self.GetStringValueAt(x, iCol),
                                       self.GetImageAt(x, iCol))

            # Auto-resize once all the data has been added
            self.AutoSizeColumns()
        finally:
            self.Thaw()


    def RefreshIndex(self, index, modelObject):
        """
        Refresh the item at the given index with data associated with the given object
        """
        item = self.GetItem(index)
        item.SetText(self.GetStringValueAt(modelObject, 0))
        item.SetImage(self.GetImageAt(modelObject, 0))
        self._FormatOneItem(item, index, modelObject)
        self.SetItem(item)

        for iCol in range(1, len(self.columns)):
            self.SetStringItem(index, iCol, self.GetStringValueAt(modelObject, iCol),
                               self.GetImageAt(modelObject, iCol))


    def RefreshObject(self, modelObject):
        """
        Refresh the display of the given model
        """
        try:
            i = self.modelObjects.index(modelObject)
        except ValueError:
            return

        self.RefreshIndex(self.FindItemData(-1, i), modelObject)


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


    def _ResizeSpaceFillingColumns(self):
        """
        Change the width of space filling columns so that they fill the
        unoccupied width of the listview
        """
        # If the list isn't in report view or there are no space filling columns, just return
        if not self.HasFlag(wx.LC_REPORT):
            return

        # Don't do anything if there are no space filling columns
        if True not in set(x.isSpaceFilling for x in self.columns):
            return

        # Calculate how much free space is available in the control
        totalFixedWidth = sum(self.GetColumnWidth(i) for (i, x) in enumerate(self.columns)
                              if not x.isSpaceFilling)
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
                    columnsToResize.append((i, col))
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


    def SetCheckState(self, modelObject, state):
        """
        Set the check state of the given model object.

        'state' can be True, False or None (which means undetermined)
        """
        if self.checkStateColumn is None:
            return None
        else:
            return self.checkStateColumn.SetCheckState(modelObject, state)


    def SetColumnFixedWidth(self, colIndex, width):
        """
        Make the given column to be fixed width
        """
        if 0 <= colIndex < self.GetColumnCount():
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


    def SetObjects(self, modelObjects, preserveSelection=False):
        """
        Set the list of modelObjects to be displayed by the control.
        """

        if preserveSelection:
            selection = self.GetSelectedObjects()

        if modelObjects is None:
            self.modelObjects = list()
        else:
            self.modelObjects = modelObjects[:]
        self.RepopulateList()

        if preserveSelection:
            self.SelectObjects(selection)

    # Synonym as per many wxWindows widgets
    SetValue = SetObjects


    def ToggleCheck(self, modelObject):
        """
        Toggle the "checkedness" of the given model.

        Checked becomes unchecked; unchecked or undetermined becomes checked.
        """
        self.SetCheckState(modelObject, not self.IsChecked(modelObject))


    def Uncheck(self, modelObject):
        """
        Mark the given model object as unchecked.
        """
        self.SetCheckState(modelObject, False)

    #--------------------------------------------------------------#000000#FFFFFF
    # Accessing

    def GetCheckedObjects(self):
        """
        Return a collection of the modelObjects that are checked in this control.
        """
        if self.checkStateColumn is None:
            return list()
        else:
            return [x for x in self.modelObjects if self.IsChecked(x)]


    def GetCheckState(self, modelObject):
        """
        Return the check state of the given model object.

        Returns a boolean or None (which means undetermined)
        """
        if self.checkStateColumn is None:
            return None
        else:
            return self.checkStateColumn.GetCheckState(modelObject)


    def GetFocusedRow(self):
        """
        Return the index of the row that has the focus. -1 means no focus
        """
        return self.GetNextItem(-1, wx.LIST_NEXT_ALL, wx.LIST_STATE_FOCUSED)


    def GetImageAt(self, modelObject, columnIndex):
        """
        Return the index of the image that should be display at the given column of the given modelObject
        """
        column = self.columns[columnIndex]

        # If the column is a checkbox column, return the image appropriate to the check
        # state
        if column.HasCheckState():
            name = {
                True: ObjectListView.NAME_CHECKED_IMAGE,
                False: ObjectListView.NAME_UNCHECKED_IMAGE,
                None: ObjectListView.NAME_UNDETERMINED_IMAGE
            }.get(column.GetCheckState(modelObject))
            return self.smallImageList.GetImageIndex(name)

        # Not a checkbox column, so just return the image
        imageIndex = column.GetImage(modelObject)
        if isinstance(imageIndex, basestring):
            return self.smallImageList.GetImageIndex(imageIndex)
        else:
            return imageIndex


    def GetObjectAt(self, index):
        """
        Return the model object at the given row of the list.
        """
        # Because of sorting, index can't be used directly, which is
        # why we set the item data to be the real index
        return self.modelObjects[self.GetItemData(index)]


    def __getitem__(self, index):
        """
        Synactic sugar over GetObjectAt()
        """
        return self.GetObjectAt(index)


    def GetSelectedObject(self):
        """
        Return the selected modelObject or None if nothing is selected or if more than one is selected.
        """
        if self.GetSelectedItemCount() == 1:
            return self.GetSelectedObjects()[0]
        else:
            return None


    def GetSelectedObjects(self):
        """
        Return a list of the selected modelObjects
        """
        return list(self.YieldSelectedObjects())


    def GetStringValueAt(self, modelObject, columnIndex):
        """
        Return a string representation of the value that should be display at the given column of the given modelObject
        """
        column = self.columns[columnIndex]
        return column.GetStringValue(modelObject)


    def GetValueAt(self, modelObject, columnIndex):
        """
        Return the value that should be display at the given column of the given modelObject
        """
        column = self.columns[columnIndex]
        return column.GetValue(modelObject)


    def IsCellEditing(self):
        """
        Is some cell currently being edited?
        """
        return self.cellEditor and self.cellEditor.IsShown()


    def IsChecked(self, modelObject):
        """
        Return a boolean indicating if the given modelObject is checked.
        """
        return self.GetCheckState(modelObject) == True


    def IsObjectSelected(self, modelObject):
        """
        Is the given modelObject selected?
        """
        return modelObject in self.GetSelectedObjects()


    def YieldSelectedObjects(self):
        """
        Progressively yield the selected modelObjects
        """
        i = self.GetNextItem(-1, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
        while i != -1:
            yield self.GetObjectAt(i)
            i = self.GetNextItem(i, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)


    #----------------------------------------------------------------------------
    # Calculating

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

        if self.InReportView():
            rect = [0-self.GetScrollPos(wx.HORIZONTAL), rect.Y, 0, rect.Height]
            for i in range(subItemIndex+1):
                rect[0] += rect[2]
                rect[2] = self.GetColumnWidth(i)

        # If we want only the label rect for sub items, we have to manually
        # adjust for any image the subitem might have
        if flag == wx.LIST_RECT_LABEL:
            lvi = self.GetItem(rowIndex, subItemIndex)
            if lvi.GetImage() != -1:
                if self.HasFlag(wx.LC_ICON):
                    imageWidth = self.normalImageList.GetSize(0)[0]
                    rect[1] += imageWidth
                    rect[3] -= imageWidth
                else:
                    imageWidth = self.smallImageList.GetSize(0)[0] + 1
                    rect[0] += imageWidth
                    rect[2] -= imageWidth

        #print "rect=%s" % rect
        return rect


    def HitTestSubItem(self, pt):
        """
        Return a tuple indicating which (item, subItem) the given pt (client coordinates) is over.

        This uses the buildin version on Windows, and poor mans replacement on other platforms.
        """
        # The buildin version works on Windows
        if wx.Platform == "__WXMSW__":
            return wx.ListCtrl.HitTestSubItem(self, pt)

        (rowIndex, flags) = self.HitTest(pt)

        # Did the point hit any item?
        if (flags & wx.LIST_HITTEST_ONITEM) == 0:
            return (-1, 0, -1)

        # If it did hit an item and we are not in report mode, it must be the primary cell
        if not self.InReportView():
            return (rowIndex, wx.LIST_HITTEST_ONITEM, 0)

        # Find which subitem is hit
        right = 0
        scrolledX = self.GetScrollPos(wx.HORIZONTAL) + pt.x
        for i in range(self.GetColumnCount()):
            left = right
            right += self.GetColumnWidth(i)
            if scrolledX < right:
                if (scrolledX - left) < self.smallImageList.GetSize(0)[0]:
                    flag = wx.LIST_HITTEST_ONITEMICON
                else:
                    flag = wx.LIST_HITTEST_ONITEMLABEL
                return (rowIndex, flag, i)

        return (rowIndex, 0, -1)


    #----------------------------------------------------------------------------
    # Event handling

    def _HandleChar(self, evt):
        if evt.GetKeyCode() == wx.WXK_F2 and not self.IsCellEditing():
            return self._PossibleStartCellEdit(self.GetFocusedRow(), 0)

        # We have to catch Return/Enter/Escape here since some types of controls
        # (e.g. ComboBox, UserControl) don't trigger key events that we can listen for.
        # Treat Return or Enter as committing the current edit operation unless the control
        # is a multiline text control, in which case we treat it as data
        if evt.GetKeyCode() in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER) and self.IsCellEditing():
            if self.cellEditor and self.cellEditor.HasFlag(wx.TE_MULTILINE):
                return evt.Skip()
            else:
                return self.FinishCellEdit()

        # Treat Escape as cancel the current edit operation
        if evt.GetKeyCode() in (wx.WXK_ESCAPE, wx.WXK_CANCEL) and self.IsCellEditing():
            return self.CancelCellEdit()

        # Tab to the next editable column
        if evt.GetKeyCode() == wx.WXK_TAB and self.IsCellEditing():
            return self._HandleTabKey(evt.ShiftDown())

        # Space bar with a selection on a listview with checkboxes toggles the checkboxes
        if (evt.GetKeyCode() == wx.WXK_SPACE and
            not self.IsCellEditing() and
            self.checkStateColumn is not None and
            self.GetSelectedItemCount() > 0):
            return self._ToggleCheckBoxForSelection()

        if not self.IsCellEditing():
            if self._HandleTypingEvent(evt):
                return

        evt.Skip()

    def _HandleTypingEvent(self, evt):
        """
        """
        if self.GetItemCount() == 0 or self.GetColumnCount() == 0:
            return False

        if evt.GetModifiers() != 0 and evt.GetModifiers() != wx.MOD_SHIFT:
            return False

        if evt.GetKeyCode() > wx.WXK_START:
            return False

        if evt.GetKeyCode() in (wx.WXK_BACK, wx.WXK_DELETE):
            self.searchPrefix = u""
            return True

        # On which column are we going to compare values? If we should search on the
        # sorted column, and there is a sorted column and it is searchable, we use that
        # one, otherwise we fallback to the primary column
        if self.typingSearchesSortColumn and self.sortColumnIndex is not None:
            searchColumn = self.columns[self.sortColumnIndex]
            if not searchColumn.isSearchable:
                searchColumn = self.columns[0]
        else:
            searchColumn = self.columns[0]

        uniChar = unichr(evt.GetUnicodeKey())
        if uniChar not in string.printable:
            return False

        if (evt.GetTimestamp() - self.whenLastTypingEvent) > self.SEARCH_KEYSTROKE_DELAY:
            self.searchPrefix = uniChar
        else:
            self.searchPrefix += uniChar
        self.whenLastTypingEvent = evt.GetTimestamp()

        #import time
        #start = time.clock()
        self.__rows = 0
        self._FindByTyping(searchColumn, self.searchPrefix)
        #print "Considered %d rows in %2f secs" % (self.__rows, time.clock() - start)

        return True

    def _FindByTyping(self, searchColumn, prefix):
        """
        Select the first row passed the currently focused row that has a string representation
        that begins with 'prefix' in the given column
        """
        start = max(self.GetFocusedRow(), 0)

        # If the user is starting a new search, we don't want to consider the current row
        if len(prefix) == 1:
            start = (start + 1) % self.GetItemCount()

        # If we are searching on a sorted column, use a binary search
        if self._CanUseBisect(searchColumn):
            if self._FindByBisect(searchColumn, prefix, start, self.GetItemCount()):
                return
            if self._FindByBisect(searchColumn, prefix, 0, start):
                return
        else:
            # A binary search on a sorted column can handle any number of rows. A linear
            # search cannot. So we impose an arbitrary limit on the number of rows to
            # consider. Above that, we don't even try
            if self.GetItemCount() > self.MAX_ROWS_FOR_UNSORTED_SEARCH:
                self._SelectAndFocus(0)
                return

            # Do a linear, wrapping search to find the next match. To wrap, we consider
            # the rows in two partitions: start to the end of the collection, and then
            # from the beginning to the start position. Expressing this in other languages
            # is a pain, but it's elegant in Python. I just love Python :)
            for i in itertools.chain(range(start, self.GetItemCount()), range(0, start)):
                self.__rows += 1
                strValue = searchColumn.GetStringValue(self.GetObjectAt(i))
                if strValue.lower().startswith(prefix):
                    self._SelectAndFocus(i)
                    return
        wx.Bell()

    def _CanUseBisect(self, searchColumn):
        """
        Return True if we can use binary search on the given column
        """
        # If the list isn't sorted, we can't
        if self.sortColumnIndex is None:
            return False

        # If the list is sorted by some other column, we can't
        if self.columns[self.sortColumnIndex] != searchColumn:
            return False

        # If the column doesn't knows whether it should or not, make a guess based on the
        # type of data in the column (strings and booleans are probably safe). We already
        # know that the list isn't empty.
        if searchColumn.useBinarySearch is None:
            aspect = searchColumn.GetValue(self.GetObjectAt(0))
            searchColumn.useBinarySearch = isinstance(aspect, (basestring, bool))

        return searchColumn.useBinarySearch

    def _FindByBisect(self, searchColumn, prefix, start, end):
        """
        Use a binary search to look for rows that match the given prefix between the rows given.

        If a match was found, select/focus/reveal that row and return True.
        """

        # If the sorting is ascending, we use less than to find the first match
        # If the sort is descending, we have to use greater-equal, and suffix the
        # search string to make sure we find the first match (without the suffix
        # we always find the last match)
        if self.sortAscending:
            cmpFunc = operator.lt
            searchFor = prefix
        else:
            cmpFunc = operator.ge
            searchFor = prefix + "z"

        # Adapted from bisect std module
        lo = start
        hi = end
        while lo < hi:
            self.__rows += 1
            mid = (lo + hi) // 2
            strValue = searchColumn.GetStringValue(self.GetObjectAt(mid))
            if cmpFunc(searchFor, strValue.lower()):
                hi = mid
            else:
                lo = mid+1

        if lo < start or lo >= end:
            return False

        strValue = searchColumn.GetStringValue(self.GetObjectAt(lo))
        if strValue.lower().startswith(prefix):
            self._SelectAndFocus(lo)
            return True

        return False

    def _SelectAndFocus(self, rowIndex):
        """
        Select and focus on the given row.
        """
        self.DeselectAll()
        self.Select(rowIndex)
        self.Focus(rowIndex)

    def _ToggleCheckBoxForSelection(self):
        """
        Toggles the checkedness of the selected modelObjects.
        """
        selection = self.GetSelectedObjects()
        newValue = not self.IsChecked(selection[0])
        for x in selection:
            self.SetCheckState(x, newValue)
        self.RefreshObjects(selection)

    def _HandleColumnBeginDrag(self, evt):
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


    def _HandleColumnClick(self, evt):
        """
        The user has clicked on a column title
        """
        evt.Skip()

        # Toggle the sort column on the second click
        if evt.GetColumn() == self.sortColumnIndex:
            self.sortAscending = not self.sortAscending
        else:
            self.sortAscending = True

        self.SortBy(evt.GetColumn(), self.sortAscending)
        self._FormatAllRows()


    def _HandleColumnDragging(self, evt):
        """
        A column is being dragged
        """
        # When is this triggered?

        # The processing should be the same processing as Dragged
        evt.Skip()


    def _HandleColumnEndDrag(self, evt):
        """
        The user has finished resizing a column. Make sure that it is not
        bigger than it should be, then resize any space filling columns.
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
                wx.CallAfter(self._ResizeSpaceFillingColumns)

    def _SetColumnWidthAndResize(self, colIndex, newWidth):
        self.SetColumnWidth(colIndex, newWidth)
        self._ResizeSpaceFillingColumns()


    def _HandleLeftDown(self, evt):
        """
        Handle a left down on the ListView
        """
        evt.Skip()

        # Test for a mouse down on the image of the check box column
        if self.InReportView():
            (row, flags, subitem) = self.HitTestSubItem(evt.GetPosition())
        else:
            (row, flags) = self.HitTest(evt.GetPosition())
            subitem = 0
        column = self.columns[subitem]
        if column.HasCheckState():
            if flags == wx.LIST_HITTEST_ONITEMICON:
                self._PossibleFinishCellEdit()
                modelObject = self.GetObjectAt(row)
                column.SetCheckState(modelObject, not column.GetCheckState(modelObject))
                self.RefreshIndex(row, modelObject)
                return
        evt.Skip()


    def _HandleLeftClickOrDoubleClick(self, evt):
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
        (rowIndex, ignored, subItemIndex) = self.HitTestSubItem(evt.GetPosition())
        if subItemIndex == -1:
            return

        # A single click on column 0 doesn't start an edit
        if subItemIndex == 0 and self.cellEditMode == self.CELLEDIT_SINGLECLICK:
            return

        self.StartCellEdit(rowIndex, subItemIndex)


    def _HandleMouseWheel(self, evt):
        """
        The user spun the mouse wheel
        """
        self._PossibleFinishCellEdit()
        evt.Skip()


    def _HandleScroll(self, evt):
        """
        The ListView is being scrolled
        """
        self._PossibleFinishCellEdit()
        evt.Skip()


    def _HandleSize(self, evt):
        """
        The ListView is being resized
        """
        evt.Skip()
        self._ResizeSpaceFillingColumns()
        # Make sure our empty msg is reasonably positioned
        sz = self.GetClientSize()
        self.stEmptyListMsg.SetDimensions(0, sz.GetHeight()/3, sz.GetWidth(), sz.GetHeight())


    def _HandleTabKey(self, isShiftDown):
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
            for ignored in range(columnCount-1):
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
        self.Bind(wx.EVT_LIST_COL_CLICK, self._HandleColumnClick)

        # Install sort indicators if they don't already exist
        if self.smallImageList is None:
            self.SetImageLists()
        if (not self.smallImageList.HasName(ObjectListView.NAME_DOWN_IMAGE) and
            self.smallImageList.GetSize(0) == (16,16)):
            self.RegisterSortIndicators()


    def SortBy(self, newColumn, ascending=True):
        """
        Sort the items by the given column
        """
        oldSortColumnIndex = self.sortColumnIndex
        self.sortColumnIndex = newColumn
        self.sortAscending = ascending

        # Let the world have a change to sort the items
        evt = OLVEvent.SortEvent(self, self.sortColumnIndex, self.sortAscending, self.IsVirtual())
        self.GetEventHandler().ProcessEvent(evt)
        if evt.IsVetoed():
            return

        if not evt.wasHandled:
            self._SortItemsNow()

        self._UpdateColumnSortIndicators(self.sortColumnIndex, oldSortColumnIndex)


    def _SortItemsNow(self):
        """
        Sort the actual items in the list now, according to the current column and order
        """
        col = self.columns[self.sortColumnIndex]
        def itemComparer(object1, object2):
            value1 = col.GetValue(object1)
            value2 = col.GetValue(object2)

            if isinstance(value1, basestring):
                return locale.strcoll(value1.lower(), value2.lower())
            else:
                return cmp(value1, value2)

        self.SortListItemsBy(itemComparer)


    def SortListItemsBy(self, cmpFunc, ascending=None):
        """
        Sort the existing list items using the given comparison function.

        The comparison function must accept two model objects as parameters.
        """
        if ascending is None:
            ascending = self.sortAscending

        def sorter(key1, key2):
            cmpVal = cmpFunc(self.modelObjects[key1], self.modelObjects[key2])
            if ascending:
                return cmpVal
            else:
                return -cmpVal

        self.SortItems(sorter)


    def _SortObjects(self):
        """
        Sort our model modelObjects in place.

        This does not change the information shown in the control itself.
        """

        # Let the world have a change to sort the model objects
        evt = OLVEvent.SortEvent(self, self.sortColumnIndex, self.sortAscending, True)
        self.GetEventHandler().ProcessEvent(evt)
        if evt.IsVetoed() or evt.wasHandled:
            return

        col = self.columns[self.sortColumnIndex]

        def _getLowerCaseSortValue(x):
            value = col.GetValue(x)
            if isinstance(value, basestring):
                return value.lower()
            else:
                return value

        self.modelObjects.sort(key=_getLowerCaseSortValue, reverse=(not self.sortAscending))


    def _UpdateColumnSortIndicators(self, sortColumnIndex, oldSortColumnIndex):
        """
        Change the column that is showing a sort indicator
        """
        if oldSortColumnIndex is not None:
            self.ClearColumnImage(oldSortColumnIndex)

        if sortColumnIndex is not None and self.smallImageList is not None:
            if self.sortAscending:
                imageIndex = self.smallImageList.GetImageIndex(ObjectListView.NAME_UP_IMAGE)
            else:
                imageIndex = self.smallImageList.GetImageIndex(ObjectListView.NAME_DOWN_IMAGE)

            if imageIndex != -1:
                self.SetColumnImage(sortColumnIndex, imageIndex)


    #--------------------------------------------------------------#000000#FFFFFF
    # Selecting

    def SelectAll(self):
        """
        Selected all rows in the control
        """
        # On Windows, -1 indicates 'all items'. Not sure about other platforms
        self.SetItemState(-1, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)

                    # Elsewhere, use this code. But it's much slower especially for virtual lists
        #if wx.Platform != "__WXMSW__":
        #    for i in range(self.GetItemCount()):
        #        self.SetItemState(i, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)


    def DeselectAll(self):
        """
        De-selected all rows in the control
        """
        # On Windows, -1 indicates 'all items'. Not sure about other platforms
        self.SetItemState(-1, 0, wx.LIST_STATE_SELECTED)

                    # Elsewhere, use this code. But it's much slower especially for virtual lists
        #if wx.Platform != "__WXMSW__":
        #    i = self.GetNextItem(-1, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
        #    while i != -1:
        #        self.SetItemState(i, 0, wx.LIST_STATE_SELECTED)
        #        i = self.GetNextItem(i, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)


    def SelectObject(self, modelObject, deselectOthers=True):
        """
        Select the given modelObject. If deselectOthers is True, all other rows will be deselected
        """
        try:
            i = self.modelObjects.index(modelObject)
        except ValueError:
            return

        if deselectOthers:
            self.DeselectAll()

        self.SetItemState(self.FindItemData(-1, i), wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)


    def SelectObjects(self, modelObjects, deselectOthers=True):
        """
        Select all of the given modelObjects. If deselectOthers is True, all other rows will be deselected
        """
        if deselectOthers:
            self.DeselectAll()

        # Select each modelObject that is in 'modelObjects'
        objectSet = frozenset(modelObjects)
        for (i, x) in enumerate(self.modelObjects):
            if x in objectSet:
                self.SetItemState(self.FindItemData(-1, i),
                                  wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)
        """
        If you wanted to punish future maintainers, you could collapse the above loop into
        one list comprehension:
            [self.SetItemState(self.FindItemData(-1, i),
                               wx.LIST_STATE_SELECTED,
                               wx.LIST_STATE_SELECTED)
             for (i, x) in enumerate(self.modelObjects) if x in objectSet]
        but that would just be being mean :-)
        The list comprehension does run marginally faster (1.15 secs instead of 1.18
        seconds when selecting 1000 modelObjects out of a list of 2000),
        but that speed saving is not worth the loss of understandability.
        """

    #----------------------------------------------------------------------------
    # Cell editing

    def _PossibleStartCellEdit(self, rowIndex, subItemIndex):
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


    def _PossibleFinishCellEdit(self):
        """
        If a cell is being edited, finish and commit an edit operation on the given cell.
        """
        if self.IsCellEditing():
            self.FinishCellEdit()


    def _PossibleCancelCellEdit(self):
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
        defaultEditor = self._MakeDefaultCellEditor(rowIndex, subItemIndex, cellValue)
        evt = OLVEvent.CellEditStartingEvent(self, rowIndex, subItemIndex, modelObject,
                                             cellValue, cellBounds, defaultEditor)
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
            self.cellEditor.SetValue(evt.cellValue)
            self._ConfigureCellEditor(self.cellEditor, evt.cellBounds, rowIndex, subItemIndex)

        self.cellEditor.SetFocus()
        self.cellEditor.Show()
        self.cellEditor.Raise()


    def _ConfigureCellEditor(self, editor, bounds, rowIndex, subItemIndex):
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

        editor.Bind(wx.EVT_CHAR, self._Editor_OnChar)
        editor.Bind(wx.EVT_COMMAND_ENTER, self._Editor_OnChar)
        editor.Bind(wx.EVT_KILL_FOCUS, self._Editor_KillFocus)


    def _MakeDefaultCellEditor(self, rowIndex, subItemIndex, value):
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


    def _Editor_OnChar(self, evt):
        """
        A character has been pressed in a cell editor
        """
        self._HandleChar(evt)


    def _Editor_KillFocus(self, evt):
        evt.Skip()

        # Some control trigger FocusLost events even when they still have focus
        focusWindow = wx.Window.FindFocus()
        if focusWindow is not None and self.cellEditor != focusWindow:
            self._PossibleFinishCellEdit()

    def FinishCellEdit(self):
        """
        Finish and commit an edit operation on the given cell.
        """
        (rowIndex, subItemIndex) = self.cellBeingEdited

        # Give the world the chance to veto the edit, or to change its characteristics
        rowModel = self.GetObjectAt(rowIndex)
        evt = OLVEvent.CellEditFinishingEvent(self, rowIndex, subItemIndex, rowModel,
                                              self.cellEditor.GetValue(), self.cellEditor, False)
        self.GetEventHandler().ProcessEvent(evt)
        if not evt.IsVetoed() and evt.cellValue is not None:
            self.columns[subItemIndex].SetValue(rowModel, evt.cellValue)
            self.RefreshIndex(rowIndex, rowModel)

        self._CleanupCellEdit()

    def CancelCellEdit(self):
        """
        Cancel an edit operation on the given cell.
        """
        # Tell the world that the user cancelled the edit
        (rowIndex, subItemIndex) = self.cellBeingEdited
        evt = OLVEvent.CellEditFinishingEvent(self, rowIndex, subItemIndex,
                                              self.GetObjectAt(rowIndex),
                                              self.cellEditor.GetValue(),
                                              self.cellEditor,
                                              True)
        self.GetEventHandler().ProcessEvent(evt)
        self._CleanupCellEdit()


    def _CleanupCellEdit(self):
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

    By default, a VirtualObjectListView cannot sort its rows when the user click on a header.
    If you have a back store that can sort the data represented in the virtual list, you
    can listen for the EVT_SORT events, and then order your model objects accordingly.

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
        self.objectGetter = None
        self.listItemAttr = None
        #self.cacheHit = 0
        #self.cacheMiss = 0

        self.SetObjectGetter(kwargs.pop("getter", None))

        # We have to set the item count after the list has been created
        if "count" in kwargs:
            wx.CallAfter(self.SetItemCount, kwargs.pop("count"))

        # By default, virtual lists aren't sortable
        if "sortable" not in kwargs:
            kwargs["sortable"] = False

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
        self.stEmptyListMsg.Show(count == 0)
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


    def RefreshObject(self, modelObject):
        """
        Refresh the display of the given modelObject
        """
        # We only have a hammer so everything looks like a nail
        self.RefreshObjects()


    def RefreshIndex(self, index, modelObject):
        """
        Refresh the item at the given index with data associated with the given modelObject
        """
        self.lastGetObjectIndex = -1
        self.RefreshItem(index)


    def SelectObject(self, modelObject, deselectOthers=True):
        """
        Select the given modelObject. If deselectOthers is True, all other objects will be deselected
        """
        # This doesn't work for virtual lists, since the virtual list has no way
        # of knowing where 'modelObject' is within the list.
        pass


    def SelectObjects(self, modelObjects, deselectOthers=True):
        """
        Select all of the given modelObjects. If deselectOthers is True, all other modelObjects will be deselected
        """
        # This doesn't work for virtual lists, since the virtual list has no way
        # of knowing where any of the modelObjects are within the list.
        pass


    def _FormatAllRows(self):
        """
        Set up the required formatting on all rows
        """
        # This can't work for virtual lists since a virtual list can't iterate all its items
        pass


    #----------------------------------------------------------------------------
    # Virtual list callbacks.
    # These are called a lot! Keep them efficient

    def OnGetItemText(self, itemIdx, colIdx):
        """
        Return the text that should be shown at the given cell
        """
        return self.GetStringValueAt(self.GetObjectAt(itemIdx), colIdx)


    def OnGetItemImage(self, itemIdx):
        """
        Return the image index that should be shown on the primary column of the given item
        """
        return self.GetImageAt(self.GetObjectAt(itemIdx), 0)


    def OnGetItemColumnImage(self, itemIdx, colIdx):
        """
        Return the image index at should be shown at the given cell
        """
        return self.GetImageAt(self.GetObjectAt(itemIdx), colIdx)


    def OnGetItemAttr(self, itemIdx):
        """
        Return the display attributes that should be used for the given row
        """
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
        self._FormatOneItem(self.listItemAttr, itemIdx, model)

        return self.listItemAttr


    #----------------------------------------------------------------------------
    # Accessing

    def GetObjectAt(self, index):
        """
        Return the model modelObject at the given row of the list.

        This method is called a lot! Keep it as efficient as possible.
        """

        # For reasons of performance, it may even be worthwhile removing this test and
        # ensure/assume that objectGetter is never None
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

    #---Sorting-------------------------------------------------------#000000#FFFFFF

    def _SortItemsNow(self):
        """
        Sort the items by our current settings.

        VirtualObjectListView can't sort anything by themselves, so this is a no-op.
        """
        pass

########################################################################

class FastObjectListView(VirtualObjectListView):
    """
    A fast object list view is a nice compromise between the functionality of an ObjectListView
    and the speed of a VirtualObjectListView.

    This class codes around the limitations of a virtual list. Specifically, it allows
    sorting and selection by object.
    """

    def __init__(self, *args, **kwargs):

        # By default, fast lists are sortable
        if "sortable" not in kwargs:
            kwargs["sortable"] = True

        VirtualObjectListView.__init__(self, *args, **kwargs)

        self.SetObjectGetter(lambda index: self.modelObjects[index])


    def RepopulateList(self):
        """
        Completely rebuild the contents of the list control
        """
        self.lastGetObjectIndex = -1
        if self.sortColumnIndex is not None:
            self._SortObjects()

        self.SetItemCount(len(self.modelObjects))
        self.Refresh()

        # Auto-resize once all the data has been added
        self.AutoSizeColumns()


    def SelectObject(self, modelObject, deselectOthers=True):
        """
        Select the given modelObject. If deselectOthers is True, all other modelObjects will be deselected
        """
        try:
            i = self.modelObjects.index(modelObject)
        except ValueError:
            return

        if deselectOthers:
            self.DeselectAll()

        self.SetItemState(i, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)


    def SelectObjects(self, modelObjects, deselectOthers=True):
        """
        Select all of the given modelObjects. If deselectOthers is True, all other modelObjects will be deselected
        """
        if deselectOthers:
            self.DeselectAll()

        # Select each modelObject that is in 'modelObjects'
        objectSet = frozenset(modelObjects)
        for (i, x) in enumerate(self.modelObjects):
            if x in objectSet:
                self.SetItemState(i, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)


    def RefreshObject(self, modelObject):
        """
        Refresh the display of the given modelObject
        """
        VirtualObjectListView.RefreshObject(self, modelObject)

        # We could be more precise and only refresh one row. But if
        # self.modelObjects is a large collection (>10,000) finding the object
        # in the collection could be slower than simply redrawing everything
        # (which is what the base method does)

        #try:
        #    self.RefreshIndex(self.modelObjects.index(modelObject))
        #except ValueError:
        #    pass


    #---Sorting-------------------------------------------------------#000000#FFFFFF

    def _SortItemsNow(self):
        """
        Sort the items by our current settings.

        FastObjectListView don't sort the items, they sort the model objects themselves.
        """
        selection = self.GetSelectedObjects()
        self._SortObjects()
        self.SelectObjects(selection)
        self.RefreshObjects()


#######################################################################

class ColumnDefn(object):
    """
    A ColumnDefn controls how one column of information is sourced and formatted.

    Much of the intelligence and ease of use of an ObjectListView comes from the column
    definitions. It is worthwhile gaining an understanding of the capabilities of this class.

    Public Attributes (alphabetically):

    * align
        How will the title and the cells of the this column be aligned. Possible
        values: 'left', 'centre', 'right'

    * cellEditorCreator
        This is a callable that will be invoked to create an editor for value in this
        column. The callable should accept three parameters: the objectListView starting
        the edit, the rowIndex and the subItemIndex. It should create and return a Control
        that is capable of editing the value.

        If this is None, a cell editor will be chosen based on the type of objects in this
        column (See CellEditor.EditorRegistry).

    * freeSpaceProportion
        If the column is space filling, this attribute controls what proportion of the
        space should be given to this column. By default, all spacing filling column share
        the free space equally. By changing this attribute, a column can be given a larger
        proportion of the space.

    * imageGetter
        A string, callable or integer that is used to get a index of the image to be
        shown in a cell.

        Strings and callable are used as for the `valueGetter` attribute.

        Integers are treated as constants (that is, all rows will have the same
        image).

    * isEditable
        Can the user edit cell values in this column? Default is True

    * isSearchable
        If this column is the sort column, when the user types into the ObjectListView,
        will a match be looked for using values from this column? If this is False,
        values from column 0 will be used.
        Default is True.

    * isSpaceFilling
        Is this column a space filler? Space filling columns resize to occupy free
        space within the listview. As the listview is expanded, space filling columns
        expand as well. Conversely, as the control shrinks these columns shrink too.

        Space filling columns can disappear (i.e. have a width of 0) if the control
        becomes too small. You can set `minimumWidth` to prevent them from
        disappearing.

    * maximumWidth
        An integer indicate the number of pixels above which this column will not resize.
        Default is -1, which means there is no limit.

    * minimumWidth
        An integer indicate the number of pixels below which this column will not resize.
        Default is -1, which means there is no limit.

    * useBinarySearch
        If isSearchable and useBinarySearch are both True, the ObjectListView will use a
        binary search algorithm to locate a match. If useBinarySearch is False, a simple
        linear search will be done.

        The binary search can quickly search large numbers of row (10,000,000 in about 25
        comparisons), which makes them ideal for virtual lists. However, there are two
        constraints:

            - the ObjectListView must be sorted by this column

            - sorting by string representation must give the same ordering as sorting
              by the aspect itself.

        The second constraint is necessary because the user types characters, expecting
        them to match the string representation of the data. The binary search will make
        its decisions using the string representation, but the rows ordered
        by aspect value. This will only work if sorting by string representation
        would give the same ordering as sorting by the aspect value.

        In general, binary searches work with strings, YYYY-MM-DD dates, and booleans.
        They do not work with numerics or other date formats.

        If either of these constrains are not true, you must set
        useBinarySearch to False and be content with linear searches. Otherwise, the
        searching will not work correctly.

    * stringConverter
        A string or a callable that will used to convert a cells value into a presentation
        string.

        If it is a callble, it will be called with the value for the cell and must return
        a string.

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

    * valueSetter
        A string, callable or integer that is used to write an edited value back into the
        model object.

        A callable is called with the model object and the new value. Example::

            myCol.valueSetter(modelObject, newValue)

        An integer can only be used if the model object is a mutable sequence. The integer
        is used as an index into the list. Example::

            modelObject[myCol.valueSetter] = newValue

        The string can be:

        * the name of a method to be invoked, in which case the method should accept the
          new value as its parameter. Example::

            method = getattr(modelObject, myCol.valueSetter)
            method(newValue)

        * the name of an attribute to be updated. This attribute will not be created: it
          must already exist. Example::

            setattr(modelObject, myCol.valueSetter, newValue)

        * for dictionary like model objects, an index into the dictionary. Example::

            modelObject[myCol.valueSetter] = newValue

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
                 cellEditorCreator=None, autoCompleteCellEditor=False, autoCompleteComboBoxCellEditor=False,
                 checkStateGetter=None, checkStateSetter=None,
                 isSearchable=True, useBinarySearch=None):
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
        self.isSearchable = isSearchable
        self.useBinarySearch = useBinarySearch

        self.minimumWidth = minimumWidth
        self.maximumWidth = maximumWidth
        self.width = self.CalcBoundedWidth(width)

        if fixedWidth is not None:
            self.SetFixedWidth(fixedWidth)

        if autoCompleteCellEditor:
            self.cellEditorCreator = lambda olv, row, col: CellEditor.MakeAutoCompleteTextBox(olv, col)

        if autoCompleteComboBoxCellEditor:
            self.cellEditorCreator = lambda olv, row, col: CellEditor.MakeAutoCompleteComboBox(olv, col)

        self.checkStateGetter = checkStateGetter
        self.checkStateSetter = checkStateSetter

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

    def GetValue(self, modelObject):
        """
        Return the value for this column from the given modelObject
        """
        return self._Munge(modelObject, self.valueGetter)


    def GetStringValue(self, modelObject):
        """
        Return a string representation of the value for this column from the given modelObject
        """
        value = self.GetValue(modelObject)
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


    def GetImage(self, modelObject):
        """
        Return the image index for this column from the given modelObject. -1 means no image.
        """
        if self.imageGetter is None:
            return -1
        elif isinstance(self.imageGetter, int):
            return self.imageGetter
        else:
            return self._Munge(modelObject, self.imageGetter) or -1


    def SetValue(self, modelObject, value):
        """
        Set this columns aspect of the given modelObject to have the given value.
        """
        if self.valueSetter is None:
            return self._SetValueUsingMunger(modelObject, value, self.valueGetter, False)
        else:
            return self._SetValueUsingMunger(modelObject, value, self.valueSetter, True)


    def _SetValueUsingMunger(self, modelObject, value, munger, shouldInvokeCallable):
        """
        Look for ways to update modelObject with value using munger. If munger finds a
        callable, it will be called if shouldInvokeCallable == True.
        """
        # If there isn't a munger, we can't do anything
        if munger is None:
            return

        # Is munger a function?
        if callable(munger):
            if shouldInvokeCallable:
                munger(modelObject, value)
            return

        # Try indexed access for dictionary or list like objects
        try:
            modelObject[munger] = value
            return
        except:
            pass

        # Is munger the name of some slot in the modelObject?
        try:
            attr = getattr(modelObject, munger)
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
        # property on modelObject. Try to set, realising that many things could still go wrong.
        try:
            setattr(modelObject, munger, value)
        except:
            pass


    def _Munge(self, modelObject, munger):
        """
        Wrest some value from the given modelObject using the munger.
        With a description like that, you know this method is going to be obscure :-)

        'munger' can be:

        1) a callable.
           This method will return the result of executing 'munger' with 'modelObject' as its parameter.

        2) the name of an attribute of the modelObject.
           If that attribute is callable, this method will return the result of executing that attribute.
           Otherwise, this method will return the value of that attribute.

        3) an index (string or integer) onto the modelObject.
           This allows dictionary-like objects and list-like objects to be used directly.
        """
        if munger is None:
            return None

        # Use the callable directly, if possible
        if callable(munger):
            return munger(modelObject)

        # THINK: The following code treats an instance variable with the value of None
        # as if it doesn't exist. Is that best?

        # Try attribute access
        try:
            attr = getattr(modelObject, munger, None)
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
            return modelObject[munger]
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
        return self.minimumWidth != -1 and \
               self.maximumWidth != -1 and \
               (self.minimumWidth >= self.maximumWidth)


    def SetFixedWidth(self, width):
        """
        Make this column fixed width
        """
        self.width = self.minimumWidth = self.maximumWidth = width

    #----------------------------------------------------------------------------
    # Check state

    def HasCheckState(self):
        """
        Return if this column is showing a check box?
        """
        return self.checkStateGetter is not None


    def GetCheckState(self, modelObject):
        """
        Return the check state of the given model object
        """
        if self.checkStateGetter is None:
            return None
        else:
            return self._Munge(modelObject, self.checkStateGetter)


    def SetCheckState(self, modelObject, state):
        """
        Set the check state of the given model object
        """
        if self.checkStateSetter is None:
            return self._SetValueUsingMunger(modelObject, state, self.checkStateGetter, False)
        else:
            return self._SetValueUsingMunger(modelObject, state, self.checkStateSetter, True)

#======================================================================

class NamedImageList(object):
    """
    A named image list is an Adaptor that gives a normal image list
    the ability to reference images by name, rather than just index
    """

    def __init__(self, imageList=None, imageSize=16):
        """
        """
        self.imageList = imageList or wx.ImageList(imageSize, imageSize)
        self.imageSize = imageSize
        self.nameToImageIndexMap = {}


    def GetSize(self, ignored=None):
        """
        Return a pair that represents the size of the image in this list
        """
        # Mac and Linux have trouble getting the size of empty image lists
        if self.imageList.GetImageCount() == 0:
            return (self.imageSize, self.imageSize)
        else:
            return self.imageList.GetSize(0)


    def AddNamedImage(self, name, image):
        """
        Add the given image to our list, and remember its name.
        Returns the images index.
        """
        imageIndex = self.imageList.Add(image)
        if name is not None:
            self.nameToImageIndexMap[name] = imageIndex
        return imageIndex


    def HasName(self, name):
        """
        Does this list have an image with the given name?"
        """
        return name in self.nameToImageIndexMap


    def GetImageIndex(self, name):
        """
        Return the image with the given name, or -1 if it doesn't exist
        """
        return self.nameToImageIndexMap.get(name, -1)

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
