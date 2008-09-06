# -*- coding: utf-8 -*-
#!/usr/bin/env python
#----------------------------------------------------------------------------
# Name:         UsingVirtualListExample.py
# Author:       Phillip Piper
# Created:      20 July 2008
# SVN-ID:       $Id$
# Copyright:    (c) 2008 by Phillip Piper, 2008
# License:      wxWindows license
#----------------------------------------------------------------------------
# Change log:
# 2008/08/30  JPP   Simplified initial insertions (removed executemany)
# 2008/06/20  JPP   Initial version
#----------------------------------------------------------------------------
# To do:

"""
This example shows how to use a VirtualObjectListView.

We create a large (100,000 rows) temporary database, and then
use a VirtualList to browse that database.

The slowest parts of this example are building the database
and then sorting it when the user clicks a column heading.

You can change the size of the temporary database by
changing NUMBER_OF_ROWS.
"""

import datetime
import os
import os.path
import time
import wx
import sqlite3 as sqlite

# Where can we find the ObjectListView module?
import sys
sys.path.append("..")

from ObjectListView import VirtualObjectListView, ColumnDefn, EVT_SORT

# We store our images as python code
import ExampleImages

class MyFrame(wx.Frame):

    CREATE_STMT = "CREATE TABLE tracks (trackId int, title text, artist text, album text, PRIMARY KEY (trackId))"
    INSERT_STMT = "INSERT INTO tracks VALUES(?, ?, ?, ?)"

    SELECT_ONE_STMT = "SELECT trackId, title, artist , album FROM tracks WHERE trackId=?"
    SELECT_IDS_STMT = "SELECT trackId FROM tracks ORDER BY %s %s"
    COUNT_ROWS_STMT = "SELECT count(*) FROM tracks"

    NUMBER_OF_ROWS = 100000

    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        self.Init()

    def Init(self):
        self.InitWidgets()
        self.InitObjectListView()
        wx.CallLater(1, self.InitModel)

    def InitModel(self):
        start = time.clock()
        path = os.path.join(wx.StandardPaths.Get().GetTempDir(), "VirtualListExample.sqlite")
        if os.path.exists(path):
            os.remove(path)

        # Open the database and create a table on it
        self.connection = sqlite.connect(path)
        self.connection.row_factory = sqlite.Row
        self.connection.execute(self.CREATE_STMT)
        self.connection.commit()

        baseData = [
            { "title":"Shiver", "artist": "Natalie Imbruglia", "album":"Counting Down the Days"},
            { "title":"Who's Gonna Ride Your Wild Horses", "artist": "U2",  "album":"Achtung Baby"},
            { "title":"So Cruel", "artist": "U2",  "album":"Achtung Baby"},
            { "title":"The Fly", "artist": "U2",  "album":"Achtung Baby"},
            { "title":"Fight For All The Wrong Reason", "artist": "Nickelback",  "album":"All The Right Reasons"},
            { "title":"Photograph", "artist": "Nickelback",  "album":"All The Right Reasons"},
            { "title":"Animals", "artist": "Nickelback",  "album":"All The Right Reasons"},
            { "title":"Savin' Me", "artist": "Nickelback",  "album":"All The Right Reasons"},
            { "title":"Far Away", "artist": "Nickelback",  "album":"All The Right Reasons"},
            { "title":"Next Contestant", "artist": "Nickelback",  "album":"All The Right Reasons"},
            { "title":"My Girl", "artist": "Hoodoo Gurus",  "album":"Ampology"},
            { "title":"Be My Guru", "artist": "Hoodoo Gurus",  "album":"Ampology"},
            { "title":"I Want You Back", "artist": "Hoodoo Gurus",  "album":"Ampology"},
            { "title":"Dare you to move", "artist": "Switchfoot",  "album":"The Beautiful Letdown"},
            { "title":"Redemption", "artist": "Switchfoot",  "album":"The Beautiful Letdown"},
            { "title":"The beautiful letdown", "artist": "Switchfoot",  "album":"The Beautiful Letdown"},
            { "title":"Death And All His Friends", "artist": "Coldplay",  "album":"Viva la Vida"},
        ]

        i = 0
        while i < self.NUMBER_OF_ROWS:
            for x in baseData:
                self.connection.execute(self.INSERT_STMT, [i, x["title"] + str(i), x["artist"], x["album"]])
                i += 1
        self.connection.commit()

        # We use a reorder map when the list is sorted
        self.reorderList = []

        # We have to tell the control how many rows are in the database?
        cur = self.connection.cursor()
        cur.execute(self.COUNT_ROWS_STMT)
        result = cur.fetchone()
        self.myOlv.SetItemCount(int(result[0]))

        print "Building database %d rows of took %2f seconds." % (self.myOlv.GetItemCount(), time.clock() - start)

    def InitWidgets(self):
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)

        self.myOlv = VirtualObjectListView(panel, -1, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.myOlv, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)

        self.Layout()

    def InitObjectListView(self):
        groupImage = self.myOlv.AddImages(ExampleImages.getGroup16Bitmap(), ExampleImages.getGroup32Bitmap())
        musicImage = self.myOlv.AddImages(ExampleImages.getMusic16Bitmap(), ExampleImages.getMusic32Bitmap())
        userImage = self.myOlv.AddImages(ExampleImages.getUser16Bitmap(), ExampleImages.getUser32Bitmap())

        soloArtists = ["Nelly Furtado", "Missy Higgins", "Moby", "Natalie Imbruglia"]
        def artistImageGetter(track):
            if track["artist"] in soloArtists:
                return userImage
            else:
                return groupImage

        self.myOlv.SetColumns([
            ColumnDefn("Title", "left", 150, "title", imageGetter=musicImage),
            ColumnDefn("Artist", "left", 150, "artist", imageGetter=artistImageGetter),
            ColumnDefn("Album", "center", 150, "album")
        ])

        # Fetch rows from the database when required
        # In a real app, this would cache a certain number of rows
        def fetchFromDatabase(rowIndex):
            cur = self.connection.cursor()
            if len(self.reorderList):
                rowIndex = self.reorderList[rowIndex]
            cur.execute(self.SELECT_ONE_STMT, (rowIndex,))
            return cur.fetchone()

        self.myOlv.SetObjectGetter(fetchFromDatabase)

        # We want to receive sort events for the virtual list
        self.myOlv.EnableSorting()
        self.myOlv.Bind(EVT_SORT, self.HandleSort)

        # Let the user know that we are building the database
        self.myOlv.SetEmptyListMsg("Building database...")
        self.myOlv.SetItemCount(0)


    def HandleSort(self, evt):
        """
        The user wants to sort the virtual list.
        """
        start = time.clock()

        columnName = evt.objectListView.columns[evt.sortColumnIndex].valueGetter
        if evt.sortAscending:
            sorting = "ASC"
        else:
            sorting = "DESC"
        cur = self.connection.cursor()
        cur.execute(self.SELECT_IDS_STMT % (columnName, sorting))
        self.reorderList = [x[0] for x in cur.fetchall()]
        self.myOlv.RefreshObjects()

        print "Sorting took %2f seconds." % (time.clock() - start)


if __name__ == '__main__':
    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "VirtualObjectListView Example")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
