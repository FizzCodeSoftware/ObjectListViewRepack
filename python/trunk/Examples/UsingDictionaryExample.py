#!/usr/bin/env python

"""
This example shows how to use a list of dictionaries as the
datasource for an ObjectListView
"""

import datetime
import time
import wx

# Where can we find the ObjectListView module?
import sys
sys.path.append("..")

from ObjectListView import ObjectListView, ColumnDefn

# We store our images as python code
import ExampleImages

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        self.Init()

    def Init(self):
        self.InitModel()
        self.InitWidgets()
        self.InitObjectListView()

    def InitModel(self):
        self.listOfDictionaries = [
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
        ]

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
        groupImage = self.myOlv.AddImages(ExampleImages.getGroup16Bitmap(), ExampleImages.getGroup32Bitmap())
        userImage = self.myOlv.AddImages(ExampleImages.getUser16Bitmap(), ExampleImages.getUser32Bitmap())
        musicImage = self.myOlv.AddImages(ExampleImages.getMusic16Bitmap(), ExampleImages.getMusic32Bitmap())

        soloArtists = ["Nelly Furtado", "Missy Higgins", "Moby", "Natalie Imbruglia"]
        def artistImageGetter(track):
            if track["artist"] in soloArtists:
                return userImage
            else:
                return groupImage

        self.myOlv.SetColumns([
            ColumnDefn("Title", "left", -1, "title", imageGetter=musicImage),
            ColumnDefn("Artist", "left", -1, "artist", imageGetter=artistImageGetter),
            ColumnDefn("Album", "center", -1, "album")
        ])
        self.myOlv.SetObjects(self.listOfDictionaries)

if __name__ == '__main__':
    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "ObjectListView Dictionary Example")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
