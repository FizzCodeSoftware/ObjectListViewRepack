# -*- coding: utf-8 -*-
#!/usr/bin/env python
#----------------------------------------------------------------------------
# Name:         SqlExample.py
# Author:       Phillip Piper
# Created:      17 August 2008
# SVN-ID:       $Id$
# Copyright:    (c) 2008 by Phillip Piper, 2008
# License:      wxWindows license
#----------------------------------------------------------------------------
# Change log:
# 2008/08/17  JPP   Initial version
#----------------------------------------------------------------------------
# To do:

"""
This example shows a simply SQL SELECT dataset browser/editor.

The example is pointed at sqlite database, and the user can then enter SELECT
statements against that database. The example dynamically generates an
ObjectListView that will browse/edit the results of the SELECT statement.

For the ObjectListView to be editable, the SELECT must include the primary key for the
table (which obviously requires that the table have a primary key).

It is NOT a Toad-replacement! The browsing portion should handle any SQL SELECT statement,
but the updating is simple-minded and will be confused by anything complicated.

"""

import datetime
import os
import os.path
import re
import time
import wx
import sqlite3 as sqlite

# Where can we find the ObjectListView module?
import sys
sys.path.append("..")

from ObjectListView import ObjectListView, FastObjectListView, ColumnDefn, EVT_CELL_EDIT_FINISHED, EVT_CELL_EDIT_STARTING

import ExampleModel

class MyFrame(wx.Frame):

    DB_PATH = "" # Give this a full path if you want to look at an existing database

    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        self.tableName = ""
        self.primaryKey = ""

        self.InitWidgets()
        self.InitDb()
        self.UpdateListEditability()


    def InitDb(self):
        path = self.DB_PATH or os.path.join(wx.StandardPaths.Get().GetTempDir(), "SqlExample.sqlite")
        if os.path.exists(path):
            self.connection = sqlite.connect(path)
        else:
            self.connection = self.CreateDb(path)


    def CreateDb(self, path):
        CREATE_STMT = "CREATE TABLE tracks (trackId int, title text, artist text, album text, sizeInBytes int, rating int, PRIMARY KEY (trackId))"
        INSERT_STMT = "INSERT INTO tracks VALUES(?, ?, ?, ?, ?, ?)"
        NUMBER_OF_ROWS = 10000

        connection = sqlite.connect(path)
        connection.execute(CREATE_STMT)
        connection.commit()

        start = time.clock()
        i = 0
        while i < NUMBER_OF_ROWS:
            for x in ExampleModel.GetTracks():
                connection.execute(INSERT_STMT, [i, x.title + str(i), x.artist, x.album, x.sizeInBytes, x.rating])
                i += 1
        connection.commit()
        #print "Building database of %d rows took %2f seconds." % (NUMBER_OF_ROWS, time.clock() - start)

        return connection


    def InitWidgets(self):
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)

        self.tcSql = wx.TextCtrl(panel, -1, "select trackId, title, artist, album, sizeInBytes, rating from tracks;", style=wx.TE_MULTILINE|wx.TE_PROCESS_ENTER)
        self.myOlv = FastObjectListView(panel, -1, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        self.stMsg = wx.StaticText(panel, -1, "Default value")
        sizer_2 = wx.FlexGridSizer(3, 1, 0, 0)
        sizer_2.Add(self.tcSql, 1, wx.ALL|wx.EXPAND, 4)
        sizer_2.Add(self.myOlv, 1, wx.ALL|wx.EXPAND, 4)
        sizer_2.Add(self.stMsg, 1, wx.ALL|wx.EXPAND, 4)
        sizer_2.AddGrowableCol(0)
        sizer_2.AddGrowableRow(1)

        panel.SetSizer(sizer_2)

        self.Bind(wx.EVT_TEXT_ENTER, self.HandleTextEnter, self.tcSql)
        self.myOlv.Bind(EVT_CELL_EDIT_STARTING, self.HandleCellEditStarting)
        self.myOlv.Bind(EVT_CELL_EDIT_FINISHED, self.HandleCellEditFinished)

        self.Layout()

    #----------------------------------------------------------------------------
    # Event handling

    def HandleTextEnter(self, evt):
        self.tableName = ""
        self.primaryKey = ""
        try:
            self.myOlv.SetEmptyListMsg("Executing statement...")
            self.DoSelect(self.tcSql.GetValue())
            self.CalculatePrimaryKey(self.tcSql.GetValue())
        except sqlite.Error, e:
            self.myOlv.SetEmptyListMsg("Error: %s" % e.args[0])
        self.UpdateListEditability()

    def HandleCellEditStarting(self, evt):
        if evt.subItemIndex == self.primaryKeyIndex:
            evt.Veto()
            wx.Bell()
            self.stMsg.SetLabel("Cannot edit the primary key")


    def HandleCellEditFinished(self, evt):
        ""
        if evt.userCancelled:
            return

        stmt = "UPDATE %s SET %s=? WHERE %s = ?" % (self.tableName, self.myOlv.columns[evt.subItemIndex].title, self.primaryKey)
        try:
            self.connection.execute(stmt, (evt.rowModel[evt.subItemIndex], evt.rowModel[self.primaryKeyIndex]))
            self.connection.commit()
        except sqlite.Error, e:
            wx.MessageBox("Error when updating: %s.\nStatement: %s" % (e.args[0], stmt))

    #----------------------------------------------------------------------------
    # Commands

    def DoSelect(self, stmt):
        # Clear the existing query results
        self.myOlv.SetObjects(list())

        # Run the query
        cur = self.connection.cursor()
        cur.execute(stmt)

        # Create a columnDefn for each column in the query.
        # The value to be shown in a cell is the i'th value in the list
        self.myOlv.SetColumns(ColumnDefn(x[0], valueGetter=i, minimumWidth=40) for (i,x) in enumerate(cur.description))

        # fetchall() returns tuples which can't be modified in place, so we convert them to lists
        self.myOlv.SetObjects([list(x) for x in cur.fetchall()])


    def UpdateListEditability(self):
        self.myOlv.cellEditMode = ObjectListView.CELLEDIT_NONE

        if self.primaryKey:
            if self.primaryKey in [x.title for x in self.myOlv.columns]:
                self.stMsg.SetLabel("Editable: True.  Primary key: %s." % self.primaryKey)
                self.myOlv.cellEditMode = ObjectListView.CELLEDIT_DOUBLECLICK
            else:
                self.stMsg.SetLabel("Editable: False.  Primary key ('%s') not in columns." % self.primaryKey)
        else:
            self.stMsg.SetLabel("Editable: False.  Could not calculate primary key.")


    def CalculatePrimaryKey(self, stmt):
        """
        Figure out the primary key of the table involved in the given statement.
        """
        # Can we find the name of the table involved?
        match = re.search(r"from\s+(\b[a-z0-9$@_]+\b)", stmt, flags=re.IGNORECASE)
        if not match:
            return

        # There is no definitive way to find the primary key of the table, so we assume
        # the first unique index on the table is the primary key

        self.tableName = match.group(1)
        cur = self.connection.cursor()
        cur.execute("pragma index_list(%s)" % self.tableName)
        # Collect the index names of unique indicies
        uniqueIndexNames = [x[1] for x in cur.fetchall() if x[2]]
        if not uniqueIndexNames:
            return

        cur.execute("pragma index_info(%s)" % uniqueIndexNames[0])
        self.primaryKey = cur.fetchone()[2]
        self.primaryKeyIndex = [x.title for x in self.myOlv.columns].index(self.primaryKey)



if __name__ == '__main__':
    app = wx.App(0)
    wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "SQL Example")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
