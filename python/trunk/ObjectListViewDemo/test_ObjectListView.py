import unittest
import wx
from datetime import datetime, date, time
from ObjectListView import ObjectListView, ColumnDefn

class Person:

    def __init__(self, name, birthdate, sex):
        self.name = name
        self.birthdate = birthdate
        self.sex = sex

    def age(self):
        return datetime.now().year - self.birthdate.year

class TestObjectListView(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)

        global theObjectListView
        self.objectListView = theObjectListView

        self.personColumns = [
            ("Name", "left", -1, "name"),
            ("Age", "right", -1, "age"),
            ColumnDefn("Birthdate", "left", 100, "birthdate"),
            ColumnDefn("Sex", "centre", -1, "sex", isSpaceFilling=True),
        ]
        self.persons = [
            Person("Alex Bawling", datetime(1955, 1, 2), "Male"),
            Person("Cindy Dawn", datetime(1967, 3, 4), "Female"),
            Person("Eric Fandango", datetime(1957, 5, 6), "Male"),
            Person("Ginger Hawk", datetime(1977, 7, 8), "Female"),
            Person("Ian Janide", datetime(1931, 9, 10), "Male"),
            Person("Zoe Meliko", datetime(1974, 9, 10), "Female"),
            Person("ae cummings", datetime(1944, 9, 10), "Male"),
        ]

    def setUp(self):
        self.objectListView.ClearAll()
        self.objectListView.SetColumns(self.personColumns)
        self.objectListView.SetObjects(self.persons)

    #----------------------------------------------------------------------------
    # Tests

    def testInitialState(self):
        self.objectListView.ClearAll()
        self.assertEqual(self.objectListView.GetColumnCount(), 0)
        self.assertEqual(self.objectListView.GetItemCount(), 0)
        self.assertEqual(len(self.objectListView.objects), 0)

    def testBasics(self):
        self.assertEqual(self.objectListView.GetColumnCount(), len(self.personColumns))
        self.assertEqual(self.objectListView.GetItemCount(), len(self.persons))

    def testSelection(self):
        self.objectListView.SelectObject(self.persons[0])
        self.assertEqual(self.objectListView.GetSelectedObject(), self.persons[0])

        males = [x for x in self.persons if x.sex == "Male"]
        self.objectListView.SelectObjects(males)
        self.assertEqual(set(self.objectListView.GetSelectedObjects()), set(males))

    def testSorting(self):
        self.objectListView.SortBy(0, False)
        self.assertEqual(self.objectListView.GetItem(0).GetText(), "Zoe Meliko")
        self.objectListView.SortBy(0, True)
        self.assertEqual(self.objectListView.GetItem(0).GetText(), "ae cummings")
        self.objectListView.SortBy(2, False)
        self.assertEqual(self.objectListView.GetItem(0).GetText(), "Ginger Hawk")
        self.objectListView.SortBy(2, True)
        self.assertEqual(self.objectListView.GetItem(0).GetText(), "Ian Janide")

    def testColumnResizing(self):
        widths = [self.objectListView.GetColumnWidth(i) for i in range(len(self.objectListView.columns))]
        global theFrame
        theFrame.SetSize(theFrame.GetSize() + (100, 100))

        # The space filling columns should have increased in width, but the others should be the same
        for (colIndex, oldWidth) in enumerate(widths):
            if self.objectListView.columns[colIndex].isSpaceFilling:
                self.assertTrue(oldWidth < self.objectListView.GetColumnWidth(colIndex))
            else:
                self.assertEqual(oldWidth, self.objectListView.GetColumnWidth(colIndex))

    def testRditing(self):
        self.objectListView.SortBy(0, False)
        self.assertEqual(self.objectListView.GetItem(0).GetText(), "Zoe Meliko")
        self.objectListView.DeselectAll()
        self.objectListView.SetItemState(0, wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED, wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED)

        # Fake an F2, change the value of the edit, and then fake a Return to commit the change
        evt = wx.KeyEvent(wx.EVT_CHAR.evtType[0])
        evt.m_keyCode = wx.WXK_F2
        self.objectListView.HandleChar(evt)
        self.objectListView.cellEditor.SetValue("new name for Zoe")
        evt.m_keyCode = wx.WXK_RETURN
        self.objectListView.HandleChar(evt)
        self.assertEqual(self.objectListView.GetItem(0).GetText(), "new name for Zoe")

        # Put the original value back
        evt.m_keyCode = wx.WXK_F2
        self.objectListView.HandleChar(evt)
        self.objectListView.cellEditor.SetValue("Zoe Meliko")
        evt.m_keyCode = wx.WXK_RETURN
        self.objectListView.HandleChar(evt)
        self.assertEqual(self.objectListView.GetItem(0).GetText(), "Zoe Meliko")




if __name__ == '__main__':
    import wx

    class MyFrame(wx.Frame):
        def __init__(self, *args, **kwds):
            kwds["style"] = wx.DEFAULT_FRAME_STYLE
            wx.Frame.__init__(self, *args, **kwds)

            global theObjectListView, theFrame
            theFrame = self
            theObjectListView = ObjectListView(self, -1, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
            sizer_1 = wx.BoxSizer(wx.VERTICAL)
            sizer_1.Add(theObjectListView, 1, wx.ALL|wx.EXPAND, 4)
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
