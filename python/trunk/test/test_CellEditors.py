import unittest
import wx
from datetime import datetime, date, time

import sys
sys.path.append("..")
from ObjectListView.CellEditor import BooleanEditor, DateEditor, DateTimeEditor, TimeEditor

#----------------------------------------------------------------------------

class TestBooleanEditor(unittest.TestCase):

    def setUp(self):
        global gBooleanEditor
        self.editor = gBooleanEditor

    def testBasics(self):
        self.editor.SetValue(False)
        self.assertEqual(self.editor.GetValue(), False)
        self.editor.SetValue(True)
        self.assertEqual(self.editor.GetValue(), True)

#----------------------------------------------------------------------------

class TestDateEditor(unittest.TestCase):

    def setUp(self):
        global gDateEditor
        self.editor = gDateEditor

    def testBasics(self):
        dt = date.today()
        self.editor.SetValue(dt)
        self.assertEqual(self.editor.GetValue(), dt)

#----------------------------------------------------------------------------

class TestDateTimeEditor(unittest.TestCase):

    def setUp(self):
        global gDateTimeEditor
        self.editor = gDateTimeEditor

    def testBasics(self):
        dt = datetime.now().replace(microsecond=0)
        self.editor.SetValue(dt)
        self.assertEqual(self.editor.GetValue(), dt)

    def testParsingWithYear(self):
        tests = [
            ("31/12/2007 23:59:59", datetime(2007, 12, 31, 23, 59, 59)),
            ("31/12/2007 11:59:59 pm", datetime(2007, 12, 31, 23, 59, 59)),
            ("31/12/2007 23:59", datetime(2007, 12, 31, 23, 59)),
            ("31/12/2007 11:59 pm", datetime(2007, 12, 31, 23, 59)),
            ("12/31/2007 23:59:59", datetime(2007, 12, 31, 23, 59, 59)),
            ("12/31/2007 11:59:59 pm", datetime(2007, 12, 31, 23, 59, 59)),
            ("12/31/2007 23:59", datetime(2007, 12, 31, 23, 59)),
            ("12/31/2007 11:59 pm", datetime(2007, 12, 31, 23, 59)),
            ("31-Dec-2007 23:59:59", datetime(2007, 12, 31, 23, 59, 59)),
            ("31-Dec-2007 11:59:59 pm", datetime(2007, 12, 31, 23, 59, 59)),
            ("31-Dec-2007 23:59", datetime(2007, 12, 31, 23, 59)),
            ("31-Dec-2007 11:59 pm", datetime(2007, 12, 31, 23, 59)),
            ("31 December 2007 23:59:59", datetime(2007, 12, 31, 23, 59, 59)),
            ("31 December 2007 11:59:59 pm", datetime(2007, 12, 31, 23, 59, 59)),
            ("31 December 2007 23:59", datetime(2007, 12, 31, 23, 59)),
            ("31 December 2007 11:59 pm", datetime(2007, 12, 31, 23, 59)),
            ("Dec 31, 2007 23:59:59", datetime(2007, 12, 31, 23, 59, 59)),
            ("Dec 31, 2007 11:59:59 pm", datetime(2007, 12, 31, 23, 59, 59)),
            ("Dec 31, 2007 23:59", datetime(2007, 12, 31, 23, 59)),
            ("Dec 31, 2007 11:59 pm", datetime(2007, 12, 31, 23, 59)),
        ]
        for (txt, dt) in tests:
            #print txt
            self.editor.SetValue(txt)
            self.assertEqual(self.editor.GetValue(), dt)

    def testParsingWithoutYear(self):
        tests = [
            ("31/12 23:59:59", datetime(2007, 12, 31, 23, 59, 59)),
            ("31/12 11:59:59 pm", datetime(2007, 12, 31, 23, 59, 59)),
            ("31/12 23:59", datetime(2007, 12, 31, 23, 59)),
            ("31/12 11:59 pm", datetime(2007, 12, 31, 23, 59)),
            ("12/31 23:59:59", datetime(2007, 12, 31, 23, 59, 59)),
            ("12/31 11:59:59 pm", datetime(2007, 12, 31, 23, 59, 59)),
            ("12/31 23:59", datetime(2007, 12, 31, 23, 59)),
            ("12/31 11:59 pm", datetime(2007, 12, 31, 23, 59)),
            ("31-Dec 23:59:59", datetime(2007, 12, 31, 23, 59, 59)),
            ("31-Dec 11:59:59 pm", datetime(2007, 12, 31, 23, 59, 59)),
            ("31-Dec 23:59", datetime(2007, 12, 31, 23, 59)),
            ("31-Dec 11:59 pm", datetime(2007, 12, 31, 23, 59)),
            ("31 December 23:59:59", datetime(2007, 12, 31, 23, 59, 59)),
            ("31 December 11:59:59 pm", datetime(2007, 12, 31, 23, 59, 59)),
            ("31 December 23:59", datetime(2007, 12, 31, 23, 59)),
            ("31 December 11:59 pm", datetime(2007, 12, 31, 23, 59)),
            ("Dec 31 23:59:59", datetime(2007, 12, 31, 23, 59, 59)),
            ("Dec 31 11:59:59 pm", datetime(2007, 12, 31, 23, 59, 59)),
            ("Dec 31 23:59", datetime(2007, 12, 31, 23, 59)),
            ("Dec 31 11:59 pm", datetime(2007, 12, 31, 23, 59)),
        ]
        thisYear = datetime.now().year
        for (txt, dt) in tests:
            #print txt
            self.editor.SetValue(txt)
            self.assertEqual(self.editor.GetValue(), dt.replace(year=thisYear))

#----------------------------------------------------------------------------

class TestTimeEditor(unittest.TestCase):

    def setUp(self):
        global gTimeEditor
        self.editor = gTimeEditor

    def testBasics(self):
        t = datetime.now().time().replace(microsecond=0)
        self.editor.SetValue(t)
        self.assertEqual(self.editor.GetValue(), t)

#======================================================================
# MAINLINE

if __name__ == '__main__':
    import wx

    class MyFrame(wx.Frame):
        def __init__(self, *args, **kwds):
            kwds["style"] = wx.DEFAULT_FRAME_STYLE
            wx.Frame.__init__(self, *args, **kwds)

            global gBooleanEditor, gDateEditor, gDateTimeEditor, gTimeEditor
            gBooleanEditor = BooleanEditor(self)
            gDateEditor = DateEditor(self)
            gDateTimeEditor = DateTimeEditor(self, 0)
            gTimeEditor = TimeEditor(self, 0)
            sizer_1 = wx.BoxSizer(wx.VERTICAL)
            sizer_1.Add(gBooleanEditor, 1, wx.ALL|wx.EXPAND, 4)
            sizer_1.Add(gDateEditor, 1, wx.ALL|wx.EXPAND, 4)
            sizer_1.Add(gDateTimeEditor, 1, wx.ALL|wx.EXPAND, 4)
            sizer_1.Add(gTimeEditor, 1, wx.ALL|wx.EXPAND, 4)
            self.SetSizer(sizer_1)
            self.Layout()

            wx.CallAfter(self.runTests)

        def runTests(self):
            unittest.main()
#            self.Close()

    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
