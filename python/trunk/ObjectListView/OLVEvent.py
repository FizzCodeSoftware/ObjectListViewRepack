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
# 2008/04/04  JPP   Initial version complete
#----------------------------------------------------------------------------
# To do:

"""
The OLVEvent module ...
"""

__author__ = "Phillip Piper"
__date__ = "3 April 2008"
__version__ = "1.0"

import datetime
import wx

#======================================================================
# Event ids and types

def _EventMaker():
    evt = wx.NewEventType()
    return (evt, wx.PyEventBinder(evt))

(olv_EVT_CELL_EDIT_STARTING, EVT_CELL_EDIT_STARTING) = _EventMaker()
(olv_EVT_CELL_EDIT_FINISHING, EVT_CELL_EDIT_FINISHING) = _EventMaker()

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

        If this is called, the event handler must handle all configuration. In particular,
        it must call ObjectListView.CancelCellEdit() when the user presses Cancel, and it
        must call ObjectListView.CancelCellEdit() when the user presses Enter/Return or
        when the editor loses focus.
        """
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
