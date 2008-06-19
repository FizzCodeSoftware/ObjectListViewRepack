# -*- coding: ISO-8859-1 -*-
#----------------------------------------------------------------------------
# Name:         OLVEvent.py
# Author:       Phillip Piper
# Created:      3 April 2008
# SVN-ID:       $Id$
# Copyright:    (c) 2008 by Phillip Piper, 2008
# License:      wxWindows license
#----------------------------------------------------------------------------
# Change log:
# 2008/06/19  JPP   Added EVT_SORT
# 2008/05/26  JPP   Fixed pyLint annoyances
# 2008/04/04  JPP   Initial version complete
#----------------------------------------------------------------------------
# To do:

"""
The OLVEvent module holds all the events used by the ObjectListView module.
"""

__author__ = "Phillip Piper"
__date__ = "3 May 2008"
__version__ = "1.0.1"

import wx

#======================================================================
# Event ids and types

def _EventMaker():
    evt = wx.NewEventType()
    return (evt, wx.PyEventBinder(evt))

(olv_EVT_CELL_EDIT_STARTING, EVT_CELL_EDIT_STARTING) = _EventMaker()
(olv_EVT_CELL_EDIT_FINISHING, EVT_CELL_EDIT_FINISHING) = _EventMaker()
(olv_EVT_SORT, EVT_SORT) = _EventMaker()

#======================================================================
# Event parameter blocks

class VetoableEvent(wx.PyCommandEvent):
    """
    Base class for all cancellable actions
    """

    def __init__(self, evtType):
        wx.PyCommandEvent.__init__(self, evtType, -1)
        self.veto = False

    def Veto(self, isVetoed=True):
        """
        Veto (or un-veto) this event
        """
        self.veto = isVetoed

    def IsVetoed(self):
        """
        Has this event been vetod?
        """
        return self.veto


class CellEditEvent(VetoableEvent):
    """
    Base class for all cell editing events
    """

    def SetParameters(self, objectListView, rowIndex, subItemIndex, rowModel, cellValue, editor):
        self.objectListView = objectListView
        self.rowIndex = rowIndex
        self.subItemIndex = subItemIndex
        self.rowModel = rowModel
        self.cellValue = cellValue
        self.editor = editor


class CellEditStartingEvent(CellEditEvent):
    """
    A cell is about to be edited.

    All attributes are public and should be considered read-only. Methods are provided for
    information that can be changed.
    """

    def __init__(self, objectListView, rowIndex, subItemIndex, rowModel, cellValue, cellBounds, editor):
        CellEditEvent.__init__(self, olv_EVT_CELL_EDIT_STARTING)
        self.SetParameters(objectListView, rowIndex, subItemIndex, rowModel, cellValue, editor)
        self.cellBounds = cellBounds
        self.newEditor = None
        self.shouldConfigureEditor = True

    def SetCellBounds(self, rect):
        """
        Change where the editor will be placed.
        rect is a list: [left, top, width, height]
        """
        self.cellBounds = rect

    def SetNewEditor(self, control):
        """
        Use the given control instead of the editor.
        """
        self.newEditor = control

    def DontConfigureEditor(self):
        """
        The editor will not be automatically configured.

        If this is called, the event handler must handle all configuration. In
        particular, it must configure its own event handlers to that
        ObjectListView.CancelCellEdit() is called when the user presses Escape,
        and ObjectListView.CommitCellEdit() is called when the user presses
        Enter/Return or when the editor loses focus. """
        self.shouldConfigureEditor = False


class CellEditFinishingEvent(CellEditEvent):
    """
    The user has finished editing a cell.

    If this event is vetoed, the edit will be cancelled silently. This is useful if the
    event handler completely handles the model updating.
    """
    def __init__(self, objectListView, rowIndex, subItemIndex, rowModel, cellValue, editor, userCancelled):
        CellEditEvent.__init__(self, olv_EVT_CELL_EDIT_FINISHING)
        self.SetParameters(objectListView, rowIndex, subItemIndex, rowModel, cellValue, editor)
        self.userCancelled = userCancelled

    def SetCellValue(self, value):
        """
        If the event handler sets the cell value here, this value will be used to update the model
        object, rather than the value that was actually in the cell editor
        """
        self.cellValue = value


class SortEvent(VetoableEvent):
    """
    The user wants to sort the ObjectListView.

    When sortModelObjects is True, the event handler should sort the model objects used by
    the given ObjectListView. For a plain OLV and a FastObjectListView, this is the
    "modelObjects" collection. For a VirtualObjectListView, this is whatever backing store
    is being used.

    When sortModelObjects is False, the event handler must sort the actual ListItems in
    the OLV. It does this by calling SortListItemsBy(), passing a callable that accepts
    two model objects as parameters. sortModelObjects cannot only be False for a
    VirtualObjectListView or a FastObjectListView.

    If the handler calls Veto(), no further default processing will be done.
    If the handler calls Handled(), default processing concerned with UI will be done. This
    includes updating sort indicators.
    If the handler calls neither of these, all default processing will be done.
    """
    def __init__(self, objectListView, sortColumnIndex, sortAscending, sortModelObjects):
        VetoableEvent.__init__(self, olv_EVT_SORT)
        self.objectListView = objectListView
        self.sortColumnIndex = sortColumnIndex
        self.sortAscending = sortAscending
        self.sortModelObjects = sortModelObjects
        self.wasHandled = False

    def Handled(self, wasHandled=True):
        """
        Indicate that the event handler has sorted the ObjectListView.
        The OLV will handle other tasks like updating sort indicators
        """
        self.wasHandled = wasHandled
