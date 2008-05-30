import unittest
import wx
import datetime
import time

import sys
sys.path.append("..")
from ObjectListView import ObjectListView, FastObjectListView, ColumnDefn

class Person:

    def __init__(self, name, birthdate, sex):
        self.name = name
        self.birthdate = birthdate
        self.sex = sex

    def age(self):
        return datetime.datetime.now().year - self.birthdate.year

class TestObjectListView(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)

        self.objectListView = None

        self.personColumns = [
            ("Name", "left", -1, "name"),
            ("Age", "right", -1, "age"),
            ColumnDefn("Birthdate", "left", 100, "birthdate"),
            ColumnDefn("Sex", "centre", -1, "sex", isSpaceFilling=True),
        ]
        self.persons = [
            Person("Alex Bawling", datetime.datetime(1955, 1, 2), "Male"),
            Person("Cindy Dawn", datetime.datetime(1967, 3, 4), "Female"),
            Person("Eric Fandango", datetime.datetime(1957, 5, 6), "Male"),
            Person("Ginger Hawk", datetime.datetime(1977, 7, 8), "Female"),
            Person("Ian Janide", datetime.datetime(1931, 9, 10), "Male"),
            Person("Zoe Meliko", datetime.datetime(1974, 9, 10), "Female"),
            Person("ae cummings", datetime.datetime(1944, 9, 10), "Male"),
        ]

    def setUp(self):
        self.objectListView.ClearAll()
        self.objectListView.SetColumns(self.personColumns)
        self.objectListView.SetObjects(self.persons)

    def run(self, result):
        # This class is really a base class for tests on a normal ObjectListView and for a
        # FastObjectListView. But I don't know a way to say that this is a base class and
        # shouldn't run any tests itself. So this hack stops the tests from running if a
        # specific ObjectListView hasn't been setup
        if self.objectListView is not None:
            unittest.TestCase.run(self, result)

    #----------------------------------------------------------------------------
    # Tests

    def testInitialState(self):
        self.objectListView.ClearAll()
        self.assertEqual(self.objectListView.GetColumnCount(), 0)
        self.assertEqual(self.objectListView.GetItemCount(), 0)
        self.assertEqual(len(self.objectListView.modelObjects), 0)

    def testBasics(self):
        self.assertEqual(self.objectListView.GetColumnCount(), len(self.personColumns))
        self.assertEqual(self.objectListView.GetItemCount(), len(self.persons))

    def testSelection(self):
        self.objectListView.SelectObject(self.persons[0])
        self.assertEqual(self.objectListView.GetSelectedObject(), self.persons[0])

        males = [x for x in self.persons if x.sex == "Male"]
        self.objectListView.SelectObjects(males)
        self.assertEqual(set(self.objectListView.GetSelectedObjects()), set(males))

    def testSelectAll(self):
        self.objectListView.SelectAll()
        self.assertEqual(set(self.objectListView.GetSelectedObjects()), set(self.persons))

    def testDeSelectAll(self):
        self.objectListView.SelectObject(self.persons[0])
        self.assertEqual(len(self.objectListView.GetSelectedObjects()), 1)

        self.objectListView.DeselectAll()
        self.assertEqual(len(self.objectListView.GetSelectedObjects()), 0)

    def testRefresh(self):
        rowIndex = 0
        person = self.objectListView[rowIndex]
        nameInList = self.objectListView.GetItem(rowIndex).GetText()
        self.assertEqual(nameInList, person.name)

        person.name = "Some different name"
        self.assertNotEqual(nameInList, person.name)

        self.objectListView.RefreshObject(person)
        self.assertEqual(self.objectListView.GetItem(rowIndex).GetText(), person.name)

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

    def testEditing(self):
        self.objectListView.cellEditMode = ObjectListView.CELLEDIT_F2ONLY
        self.objectListView.SortBy(0, False)
        self.assertEqual(self.objectListView.GetItem(0).GetText(), "Zoe Meliko")
        self.objectListView.DeselectAll()
        self.objectListView.SetItemState(0, wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED, wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED)

         # Fake an F2, change the value of the edit, and then fake a Return to commit the change
        evt = wx.KeyEvent(wx.EVT_CHAR.evtType[0])
        evt.m_keyCode = wx.WXK_F2
        self.objectListView._HandleChar(evt)
        self.objectListView.cellEditor.SetValue("new name for Zoe")
        evt.m_keyCode = wx.WXK_RETURN
        self.objectListView._HandleChar(evt)
        self.assertEqual(self.objectListView.GetItem(0).GetText(), "new name for Zoe")

        # Put the original value back
        evt.m_keyCode = wx.WXK_F2
        self.objectListView._HandleChar(evt)
        self.objectListView.cellEditor.SetValue("Zoe Meliko")
        evt.m_keyCode = wx.WXK_RETURN
        self.objectListView._HandleChar(evt)
        self.assertEqual(self.objectListView.GetItem(0).GetText(), "Zoe Meliko")

    def testLackOfCheckboxes(self):
        self.objectListView.InstallCheckStateColumn(None)

        firstObject = self.objectListView.modelObjects[0]
        self.assertEqual(self.objectListView.IsChecked(firstObject), False)

        self.assertEqual(self.objectListView.GetCheckedObjects(), list())

        self.objectListView.Check(firstObject)
        self.assertEqual(self.objectListView.IsChecked(firstObject), False)

    def testCreateCheckStateColumn(self):
        self.objectListView.InstallCheckStateColumn(None)

        firstObject = self.objectListView.modelObjects[0]
        self.assertEqual(self.objectListView.IsChecked(firstObject), False)

        self.objectListView.CreateCheckStateColumn()
        self.objectListView.Check(firstObject)
        self.assertEqual(self.objectListView.IsChecked(firstObject), True)

    def testAutoCheckboxes(self):
        col = ColumnDefn("Check")
        self.objectListView.AddColumnDefn(col)
        self.assertTrue(col.checkStateGetter == None)
        self.assertTrue(col.checkStateSetter == None)

        self.objectListView.InstallCheckStateColumn(col)
        self.assertTrue(col.checkStateGetter != None)
        self.assertTrue(col.checkStateSetter != None)

        object = self.objectListView.modelObjects[0]
        self.assertEqual(self.objectListView.IsChecked(object), False)

        self.objectListView.Check(object)
        self.assertEqual(self.objectListView.IsChecked(object), True)

    def testCheckboxes(self):
        def myGetter(modelObject):
            return getattr(modelObject, "isChecked", False)
        def mySetter(modelObject, newValue):
            modelObject.isChecked = newValue
        col = ColumnDefn("Check", checkStateGetter=myGetter, checkStateSetter=mySetter)
        self.objectListView.AddColumnDefn(col)
        self.assertEqual(self.objectListView.checkStateColumn, col)

        firstObject = self.objectListView.modelObjects[0]
        lastObject = self.objectListView.modelObjects[-1]
        self.assertEqual(self.objectListView.IsChecked(firstObject), False)
        self.assertEqual(self.objectListView.IsChecked(lastObject), False)

        self.objectListView.Check(firstObject)
        self.assertEqual(self.objectListView.IsChecked(firstObject), True)
        self.assertEqual(self.objectListView.IsChecked(lastObject), False)

        self.objectListView.Check(lastObject)
        self.assertEqual(self.objectListView.IsChecked(firstObject), True)
        self.assertEqual(self.objectListView.IsChecked(lastObject), True)
        self.assertEqual(self.objectListView.GetCheckedObjects(), [firstObject, lastObject])

        self.objectListView.Uncheck(firstObject)
        self.assertEqual(self.objectListView.IsChecked(firstObject), False)
        self.assertEqual(self.objectListView.IsChecked(lastObject), True)

        self.objectListView.ToggleCheck(lastObject)
        self.assertEqual(self.objectListView.IsChecked(firstObject), False)
        self.assertEqual(self.objectListView.IsChecked(lastObject), False)

    def testNoAlternateColours(self):
        # When there is no alternate colors, each row's background colour should be invalid
        self.objectListView.useAlternateBackColors = False
        self.objectListView.RepopulateList()
        bkgdColours = [self.getBackgroundColour(i) for i in range(self.objectListView.GetItemCount())]
        self.assertFalse(True in set(bkgdColours))

    def testAlternateColours(self):
        self.objectListView.useAlternateBackColors = True
        self.objectListView.RepopulateList()
        for i in range(self.objectListView.GetItemCount()):
            if i & 1:
                self.assertEqual(self.objectListView.oddRowsBackColor, self.getBackgroundColour(i))
            else:
                self.assertEqual(self.objectListView.evenRowsBackColor, self.getBackgroundColour(i))

    def getBackgroundColour(self, i):
        # There is no consistent way to get the background color of an item (i.e. one that
        # works on both normal and virtual lists) so we have to split this into a method
        # so we can change it for a virtual list
        return self.objectListView.GetItemBackgroundColour(i)

    def testEmptyListMsg(self):
        self.objectListView.SetObjects(None)
        self.assertTrue(self.objectListView.stEmptyListMsg.IsShown())

        self.objectListView.SetObjects(self.persons)
        self.assertFalse(self.objectListView.stEmptyListMsg.IsShown())

class TestNormalObjectListView(TestObjectListView):

    def __init__(self, *args, **kwargs):
        TestObjectListView.__init__(self, *args, **kwargs)

        global theObjectListView
        self.objectListView = theObjectListView

class TestFastObjectListView(TestObjectListView):

    def __init__(self, *args, **kwargs):
        TestObjectListView.__init__(self, *args, **kwargs)

        global theFastObjectListView
        self.objectListView = theFastObjectListView

    def getBackgroundColour(self, i):
        # There is no direct way to get the background colour of an item in a virtual
        # list, so we have to cheat by approximating the process of building a list item
        attr = self.objectListView.OnGetItemAttr(i)
        if attr is None or not attr.HasBackgroundColour():
            return self.objectListView.GetItemBackgroundColour(i) # this returns an invalid color
        else:
            return attr.GetBackgroundColour()


if __name__ == '__main__':
    import wx

    class MyFrame(wx.Frame):
        def __init__(self, *args, **kwds):
            kwds["style"] = wx.DEFAULT_FRAME_STYLE
            wx.Frame.__init__(self, *args, **kwds)

            global theObjectListView, theFastObjectListView, theFrame
            theFrame = self
            theObjectListView = ObjectListView(self, -1, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
            theFastObjectListView = FastObjectListView(self, -1, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
            sizer_1 = wx.BoxSizer(wx.VERTICAL)
            sizer_1.Add(theObjectListView, 1, wx.ALL|wx.EXPAND, 4)
            sizer_1.Add(theFastObjectListView, 1, wx.ALL|wx.EXPAND, 4)
            self.SetSizer(sizer_1)
            self.Layout()

            wx.CallAfter(self.runTests)

        def runTests(self):
            unittest.main()

    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
