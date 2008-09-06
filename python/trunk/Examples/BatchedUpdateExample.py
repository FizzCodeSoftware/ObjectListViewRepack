# -*- coding: utf-8 -*-
#!/usr/bin/env python
#----------------------------------------------------------------------------
# Name:         BatchedUpdateExample.py
# Author:       Phillip Piper
# Created:      31 August 2008
# SVN-ID:       $Id$
# Copyright:    (c) 2008 by Phillip Piper, 2008
# License:      wxWindows license
#----------------------------------------------------------------------------
# Change log:
# 2008/08/31  JPP   Initial version
#----------------------------------------------------------------------------
# To do:

"""
This example shows how to use a BatchedUpdate adapter.

"""

import datetime
import os
import os.path
import threading
import time
import wx

# Where can we find the ObjectListView module?
import sys
sys.path.append("..")

from ObjectListView import FastObjectListView, ObjectListView, ColumnDefn, BatchedUpdate

# We store our images as python code
import ExampleImages

class MyFrame(wx.Frame):

    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        self.Init()

    def Init(self):
        self.InitWidgets()
        self.InitObjectListView()
        wx.CallLater(1, self.InitModel)

    def InitWidgets(self):

        # Widget creations
        self.statusbar = self.CreateStatusBar(1, 0)

        panel1 = wx.Panel(self, -1)

        panel12 = wx.Panel(panel1, -1)
        self.olv = FastObjectListView(panel1, -1, style=wx.LC_REPORT|wx.SUNKEN_BORDER)

        rootText = wx.StaticText(panel12, -1, "&Tree walk from:")
        self.tcRoot = wx.DirPickerCtrl(panel12, style=wx.DIRP_USE_TEXTCTRL)
        self.btnStart = wx.Button(panel12, -1, "&Start")
        secondsText = wx.StaticText(panel12, -1, "Seconds &between updates:")
        self.scSeconds = wx.SpinCtrl(panel12, -1, "")

        # Layout
        sizer_3 = wx.FlexGridSizer(2, 3, 4, 4)
        sizer_3.AddGrowableCol(1)
        sizer_3.Add(rootText, 1, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_3.Add(self.tcRoot, 1, wx.ALL|wx.EXPAND, 0)
        sizer_3.Add(self.btnStart, 1, wx.ALL|wx.EXPAND, 0)
        sizer_3.Add(secondsText, 1, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_3.Add(self.scSeconds, 1)
        panel12.SetSizer(sizer_3)
        panel12.Layout()

        sizer_2 = wx.FlexGridSizer(3, 1, 4, 4)
        sizer_2.Add(panel12, 1, wx.ALL|wx.EXPAND, 4)
        sizer_2.Add(self.olv, 1, wx.ALL|wx.EXPAND, 4)
        sizer_2.AddGrowableCol(0)
        sizer_2.AddGrowableRow(1)
        panel1.SetSizer(sizer_2)
        panel1.Layout()

        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel1, 1, wx.EXPAND)
        self.SetSizer(sizer_1)
        self.Layout()

        # Event handling
        self.Bind(wx.EVT_CLOSE, self.HandleClose)
        self.btnStart.Bind(wx.EVT_BUTTON, self.HandleStart)
        self.tcRoot.Bind(wx.EVT_DIRPICKER_CHANGED, self.HandleRootText)

        # Widget initialization
        self.btnStart.SetDefault()
        self.scSeconds.SetRange(0, 15)
        self.scSeconds.SetValue(2)
        self.tcRoot.SetPath(wx.StandardPaths.Get().GetDocumentsDir())

        # OK, This is the whole point of the example. Wrap the ObjectListView in a batch updater
        self.olv = BatchedUpdate(self.olv, 2)

    def InitModel(self):
        self.backgroundProcess = None

    def InitObjectListView(self):

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

        self.olv.SetColumns([
            ColumnDefn("Path", "left", 150, "GetPath"),
            ColumnDefn("Files", "left", 100, "countFiles"),
            ColumnDefn("File Size", "left", 100, "sizeFiles"),
            ColumnDefn("Total Directories", "left", 100, "CountAllDirectories"),
            ColumnDefn("Total Files", "left", 100, "CountAllFiles"),
            ColumnDefn("Total File Size", "left", 100, "SizeAllFiles", stringConverter=sizeToNiceString),
        ])
        self.olv.SetSortColumn(0)

    def HandleClose(self, evt):
        if self.backgroundProcess:
            self.backgroundProcess.cancel()
        self.Destroy()
        return True

    def HandleStart(self, evt):
        if self.backgroundProcess:
            self.backgroundProcess.cancel()
        else:
            self.btnStart.SetLabel("&Stop")
            self.olv.SetObjects(None)
            self.olv.SetEmptyListMsg("Scanning...")
            self.statusbar.SetStatusText("Scanning...")

            # Configure the update period. 0 means unbatched
            if self.scSeconds.GetValue():
                if isinstance(self.olv, BatchedUpdate):
                    self.olv.updatePeriod = self.scSeconds.GetValue()
                else:
                    self.olv = BatchedUpdate(olv, self.scSeconds.GetValue())
            else:
                if isinstance(self.olv, BatchedUpdate):
                    self.olv = self.olv.objectListView

            self.backgroundProcess = BackgroundProcess(work=self.Walker, done=self.DoneWalking)
            self.backgroundProcess.path = self.tcRoot.GetPath()
            self.backgroundProcess.runAsync()

    def HandleRootText(self, evt):
        pass
        #if os.path.isdir(self.tcRoot.GetValue()):
        #    self.tcRoot.SetBackgroundColour(wx.WHITE)
        #else:
        #    self.tcRoot.SetBackgroundColour(wx.Colour(255, 255, 0))

    def Walker(self, backgroundProcess):
        backgroundProcess.start = time.clock()
        backgroundProcess.stats = list()
        stats = [DirectoryStats(None, backgroundProcess.path)]
        wx.CallAfter(self.olv.SetObjects, stats)
        for stat in stats:
            if backgroundProcess.isCancelled():
                return
            stat.startScan = time.clock()
            names = os.listdir(stat.GetPath())
            names.sort(key=unicode.lower)
            for name in names:
                if backgroundProcess.isCancelled():
                    return
                subPath = os.path.join(stat.GetPath(), name)
                if os.path.isdir(subPath):
                    stats.append(DirectoryStats(stat, name))
                else:
                    stat.countFiles += 1
                    try:
                        stat.sizeFiles += os.path.getsize(subPath)
                    except WindowsError:
                        pass
            stat.endScan = time.clock()
            if not backgroundProcess.isCancelled():
                wx.CallAfter(self.olv.AddObjects, stat.children)
                wx.CallAfter(self.olv.RefreshObjects, stat.SelfPlusAncestors())
                #wx.SafeYield()
        #for x in stats:
        #    print x.GetPath(), x.CountAllDirectories(), x.CountAllFiles(), x.SizeAllFiles(), x.ElapsedScanTime()
        backgroundProcess.stats = stats

    def DoneWalking(self, backgroundProcess):
        self.btnStart.SetLabel("&Start")
        if backgroundProcess.isCancelled():
            self.statusbar.SetStatusText("Tree walk was cancelled")
        else:
            backgroundProcess.end = time.clock()
            self.olv.SetObjects(backgroundProcess.stats)
            self.statusbar.SetStatusText("%d directories scanned in %.2f seconds" %
                                         (len(backgroundProcess.stats), backgroundProcess.end - backgroundProcess.start))
        self.backgroundProcess = None


class DirectoryStats(object):
    """
    """

    def __init__(self, parent, name):
        self.parent = parent
        self.name = name
        self.children = list()
        self.countFiles = 0
        self.sizeFiles = 0
        if self.parent:
            self.parent.children.append(self)
        self.startScan = None
        self.endScan = None

    def GetName(self):
        return self.name

    def GetPath(self):
        if self.parent:
            return os.path.join(self.parent.GetPath(), self.name)
        else:
            return self.name

    def SelfPlusAncestors(self):
        """
        Return a collection containing this object plus all its ancestors
        """
        if self.parent:
            return self.parent.SelfPlusAncestors() + [self]
        else:
            return [self]

    def CountAllDirectories(self):
        """
        Return the total number of directories in this directory, recursively
        """
        if self.children:
            return len(self.children) + sum(x.CountAllDirectories() for x in self.children)
        else:
            return 0

    def CountAllFiles(self):
        """
        Return the total number of files in this directory, recursively
        """
        if self.children:
            return self.countFiles + sum(x.CountAllFiles() for x in self.children)
        else:
            return self.countFiles

    def SizeAllFiles(self):
        """
        Return the total number of byes of all files in this directory, recursively
        """
        if self.children:
            return self.sizeFiles + sum(x.SizeAllFiles() for x in self.children)
        else:
            return self.sizeFiles

    def ElapsedScanTime(self):
        """
        Return the number of seconds it took to scan just this directory (not its descendents)
        """
        if self.endScan and self.startScan:
            return self.endScan - self.startScan
        else:
            return 0


class BackgroundProcess(object):
    """
    A BackgroundProcess is a long-running, cancellable thread that can
    report progress and done events.

    This object can be used by:
    1) subclassing and overriding 'doWork' method
    2) passing a callable as the "work" parameter to the constructor
    """

    __author__ = "Phillip Piper"
    __date__ = "19 April 2008"
    __version__ = "0.1"

    def __init__(self, work=None, progress=None, done=None):
        """
        Initialize a background process.

        Parameters:
            work
                A callable that accepts a single parameter: the process itself. This
                callable executes the long running process. This should periodically check
                to see if the process has been cancelled (using the isCancelled method),
                as well as reporting its progress (using the notifyProgress method). If
                this is None, the process will do nothing. Subclasses that override the
                "doWork" method should not use this parameter
            progress
                A callable that accepts two parameters: the process itself, and a value
                given to the notifyProgress method (often an int representing percentage done).
            done
                A callable that accepts a single parameter: the process itself. If not None,
                this is called when the process finishes.
        """
        self.thread = None
        self.abortEvent = threading.Event()
        self.workCallback = work
        self.progressCallback = progress
        self.doneCallback = done

    #----------------------------------------------------------------------------
    # Commands

    def run(self):
        """
        Run the process synchronously
        """
        self.runAsync()
        self.wait()

    def runAsync(self):
        """
        Start a process to run asynchronously
        """
        if self.isRunning():
            return

        self.abortEvent.clear()
        self.thread = threading.Thread(target=self._worker)
        self.thread.setDaemon(True)
        self.thread.start()

    def wait(self):
        """
        Wait until the process is finished
        """
        self.thread.join()

    def cancel(self):
        """
        Cancel the process
        """
        self.abortEvent.set()

    def isCancelled(self):
        """
        Has this process been cancelled?
        """
        return self.abortEvent.isSet()

    def isRunning(self):
        """
        Return true if the process is still running
        """
        return self.thread is not None and self.thread.isAlive()

    #----------------------------------------------------------------------------
    # Implementation

    def _worker(self):
        """
        This is the actual thread process
        """
        self.doWork()
        self.reportDone()

    def doWork(self):
        """
        Do the real work of the thread.

        Subclasses should override this method to perform the long-running task.
        That task should call "isCancelled" regularly and "reportProgress" periodically.
        """
        if self.workCallback:
            self.workCallback(self)

    def reportProgress(self, value):
        """
        Report that some progress has been made
        """
        time.sleep(0.001) # Force a switch to other threads
        if self.progressCallback and not self.isCancelled():
            self.progressCallback(self, value)

    def reportDone(self):
        """
        Report that the thread has finished
        """
        if self.doneCallback:
            self.doneCallback(self)


if __name__ == '__main__':
    #walker("c:\\temp")
    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "BatchedUpdate Example")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
