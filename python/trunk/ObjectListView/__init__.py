# -*- coding: ISO-8859-1 -*-
#----------------------------------------------------------------------------
# Name:         ObjectListView module initialization
# Author:       Phillip Piper
# Created:      29 February 2008
# SVN-ID:       $Id$
# Copyright:    (c) 2008 by Phillip Piper
# License:      wxWindows license
#----------------------------------------------------------------------------
# Change log:
# 2008/04/11  JPP   Initial Version

"""
An *ObjectListView* provides a more convienent and powerful interface to a *ListCtrl*.

An *ObjectListView* works in a declarative manner: the programmer configures how it should
work, then gives it the list of objects to display.
"""

__version__ = '1.0'

__copyright__ = "Copyright (c) 2008 Phillip Piper (phillip_piper@bigfoot.com)"

from ObjectListView import ObjectListView, VirtualObjectListView, ColumnDefn, FastObjectListView
from OLVEvent import CellEditFinishingEvent, CellEditStartingEvent
from OLVEvent import EVT_CELL_EDIT_STARTING, EVT_CELL_EDIT_FINISHING
from CellEditor import CellEditorRegistry, MakeAutoCompleteTextBox, MakeAutoCompleteComboBox

__all__ = [
    "CellEditorRegistry",
    "CellEditFinishingEvent",
    "CellEditStartingEvent",
    "ColumnDefn",
    "EVT_CELL_EDIT_FINISHING",
    "EVT_CELL_EDIT_STARTING",
    "MakeAutoCompleteTextBox",
    "MakeAutoCompleteComboBox",
    "FastObjectListView",
    "ObjectListView",
    "VirtualObjectListView",
]
