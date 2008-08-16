# -*- coding: utf-8 -*-
#!/usr/bin/env python

import datetime
import wx

# Where can we find the ObjectListView module?
import sys
sys.path.append("..")

from ObjectListView import GroupListView, ColumnDefn

import ExampleModel
import ExampleImages # We store our images as python code


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

        self.myOlv = GroupListView(panel, -1, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.myOlv, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)

        self.Layout()

    def InitObjectListView(self):
        groupImage = self.myOlv.AddImages(ExampleImages.getGroup16Bitmap(), ExampleImages.getGroup32Bitmap())
        userImage = self.myOlv.AddImages(ExampleImages.getUser16Bitmap(), ExampleImages.getUser32Bitmap())
        musicImage = self.myOlv.AddImages(ExampleImages.getMusic16Bitmap(), ExampleImages.getMusic32Bitmap())

        soloArtists = ["Nelly Furtado", "Missy Higgins", "Moby", "Natalie Imbruglia",
                       "Dido", "Paul Simon", "Bruce Cockburn"]
        def artistImageGetter(track):
            if track.artist in soloArtists:
                return userImage
            else:
                return groupImage

        def sizeToNiceString(byteCount):
            """
            Convert the given byteCount into a string like: 9.9bytes/KB/MB/GB
            """
            for (cutoff, label) in [(1024*1024*1024, "GB"), (1024*1024, "MB"), (1024, "KB")]:
                if byteCount >= cutoff:
                    return "%.1f %s" % (byteCount * 1.0 / cutoff, label)

            if byteCount == 1:
                return "1 byte"
            else:
                return "%d bytes" % byteCount

        def lastPlayedGroupKey(track):
            """
            Return the grouping key for the given track when group by last played column
            """
            # We only want to group tracks by the month in which they were played
            return datetime.date(track.lastPlayed.year, track.lastPlayed.month, 1)

        def lastPlayedGroupKeyConverter(groupKey):
            # Convert the given group key (which is a date) into a representation string
            return groupKey.strftime("%B %Y")

        self.myOlv.useExpansionColumn = True
        self.myOlv.SetColumns([
            ColumnDefn("Title", "left", 120, "title", imageGetter=musicImage, useInitialLetterForGroupKey=True),
            ColumnDefn("Artist", "left", 120, "artist", imageGetter=artistImageGetter),
            ColumnDefn("Size", "center", 100, "sizeInBytes", stringConverter=sizeToNiceString),
            ColumnDefn("Last Played", "left", 100, "lastPlayed", groupKeyGetter=lastPlayedGroupKey,
                       groupKeyConverter=lastPlayedGroupKeyConverter),
            ColumnDefn("Rating", "center", 100, "rating")
        ])
        #self.myOlv.CreateCheckStateColumn()
        self.myOlv.SetSortColumn(self.myOlv.columns[2])
        self.myOlv.SetObjects(self.songs)
        #self.myOlv.cellEditMode = ObjectListView.CELLEDIT_F2ONLY


if __name__ == '__main__':
    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "GroupListView Example")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
