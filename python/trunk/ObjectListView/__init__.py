# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
# Name:         ObjectListView module initialization
# Author:       Phillip Piper
# Created:      29 February 2008
# SVN-ID:       $Id$
# Copyright:    (c) 2008 by Phillip Piper
# License:      wxWindows license
#----------------------------------------------------------------------------
# Change log:
# 2008/06/19  JPP   Added sort event related material
# 2008/04/11  JPP   Initial Version

"""
An ObjectListView provides a more convienent and powerful interface to a ListCtrl.
"""

__version__ = '1.0.1'
__copyright__ = "Copyright (c) 2008 Phillip Piper (phillip_piper@bigfoot.com)"

from ObjectListView import ObjectListView, VirtualObjectListView, ColumnDefn, FastObjectListView, GroupListView, ListGroup
from OLVEvent import CellEditFinishingEvent, CellEditStartingEvent, SortEvent
from OLVEvent import EVT_CELL_EDIT_STARTING, EVT_CELL_EDIT_FINISHING, EVT_SORT
from CellEditor import CellEditorRegistry, MakeAutoCompleteTextBox, MakeAutoCompleteComboBox

__all__ = [
    "CellEditFinishingEvent",
    "CellEditorRegistry",
    "CellEditStartingEvent",
    "ColumnDefn",
    "EVT_CELL_EDIT_FINISHING",
    "EVT_CELL_EDIT_STARTING",
    "EVT_SORT",
    "FastObjectListView",
    "GroupListView",
    "MakeAutoCompleteTextBox",
    "MakeAutoCompleteComboBox",
    "ListGroup",
    "ObjectListView",
    "SortEvent",
    "VirtualObjectListView",
]
