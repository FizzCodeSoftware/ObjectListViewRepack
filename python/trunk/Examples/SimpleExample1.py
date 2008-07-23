# -*- coding: utf-8 -*-
#!/usr/bin/env python

import wx

# Where can we find the ObjectListView module?
import sys
sys.path.append("..")

from ObjectListView import ObjectListView, ColumnDefn

import ExampleModel

class Track(object):
    """
    Simple minded object that represents a song in a music library
    """
    def __init__(self, title, artist, album, sizeInBytes, lastPlayed, rating):
        self.title = title
        self.artist = artist
        self.album = album
        self.lastPlayed = datetime.datetime(*(time.strptime(lastPlayed, "%d/%m/%Y %I:%M %p")[0:6]))
        self.sizeInBytes = sizeInBytes
        self.rating = rating

    def GetSizeInMb(self):
        return self.sizeInBytes / (1024.0*1024.0)

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        self.Init()

    def Init(self):
        self.InitModel()
        self.InitWidgets()
        self.InitObjectListView()

    def InitModel(self):
        self.songs = ExampleModel.GetTracks()

    def InitWidgets(self):
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)

        self.myOlv = ObjectListView(panel, -1, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.myOlv, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)

        self.Layout()

    def InitObjectListView(self):
        self.myOlv.SetColumns([
            ColumnDefn("Title", "left", 120, "title"),
            ColumnDefn("Size (MB)", "center", 100, "GetSizeInMb", stringConverter="%.1f"),
            ColumnDefn("Last Played", "left", 100, "lastPlayed", stringConverter="%d-%m-%Y"),
            ColumnDefn("Rating", "center", 100, "rating")
        ])
        self.myOlv.SetObjects(self.songs)

if __name__ == '__main__':
    app = wx.PySimpleApp(1)
    wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "ObjectListView Simple Example1")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
