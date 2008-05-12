import unittest
import wx
from datetime import datetime, date, time
from ObjectListView import ObjectListView, ColumnDefn

class TestColumnDefn(unittest.TestCase):

    def testInitialState(self):
        col = ColumnDefn("title")
        self.assertEqual(col.title, "title")
        self.assertEqual(col.align, "left")
        self.assertEqual(col.width, -1)
        self.assertEqual(col.valueGetter, None)
        self.assertEqual(col.imageGetter, None)
        self.assertEqual(col.stringConverter, None)
        self.assertEqual(col.minimumWidth, -1)
        self.assertEqual(col.maximumWidth, -1)
        self.assertEqual(col.IsFixedWidth(), False)

    def testAlignment(self):
        col = ColumnDefn("title", "left")
        self.assertEqual(col.GetAlignment(), wx.LIST_FORMAT_LEFT)
        col = ColumnDefn("title", "center")
        self.assertEqual(col.GetAlignment(), wx.LIST_FORMAT_CENTRE)
        col = ColumnDefn("title", "right")
        self.assertEqual(col.GetAlignment(), wx.LIST_FORMAT_RIGHT)
        col = ColumnDefn("title", "someStrangeValue")
        self.assertEqual(col.GetAlignment(), wx.LIST_FORMAT_LEFT)

    def testImageGetter(self):
        def imageGetterFunction(modelObject):
            return 99

        col1 = ColumnDefn(imageGetter=None)
        col2 = ColumnDefn(imageGetter="imageIndex")
        col3 = ColumnDefn(imageGetter=88)
        col4 = ColumnDefn(imageGetter=imageGetterFunction)
        col5 = ColumnDefn(imageGetter="unknownMethod")

        data = {"aspectToGet": "valueToGet", "imageIndex": 77}
        self.assertEqual(col1.GetImage(data), -1)
        self.assertEqual(col2.GetImage(data), 77)
        self.assertEqual(col3.GetImage(data), 88)
        self.assertEqual(col4.GetImage(data), 99)
        self.assertEqual(col5.GetImage(data), -1)

    def testColumnWidth(self):
        col = ColumnDefn(width=100)
        self.assertEqual(col.width, 100)
        self.assertEqual(col.IsFixedWidth(), False)

        col = ColumnDefn(width=100, minimumWidth=150)
        self.assertEqual(col.width, 150)
        self.assertEqual(col.IsFixedWidth(), False)

        col = ColumnDefn(width=200, maximumWidth=150)
        self.assertEqual(col.width, 150)
        self.assertEqual(col.IsFixedWidth(), False)

        col = ColumnDefn(width=100, minimumWidth=200, maximumWidth=250)
        self.assertEqual(col.width, 200)
        self.assertEqual(col.IsFixedWidth(), False)

        col = ColumnDefn(width=100, fixedWidth=32, minimumWidth=200, maximumWidth=250)
        self.assertEqual(col.width, 32)
        self.assertEqual(col.IsFixedWidth(), True)


class TestColumnValueGetting(unittest.TestCase):

    def testValueGetterAttribute(self):

        def getterFunction(modelObject):
            return modelObject.otherAspectToGet * 2

        class DataObject:
            def __init__(self, value1, value2):
                self.aspectToGet = value1
                self.otherAspectToGet = value2

        col = ColumnDefn(valueGetter="aspectToGet")
        col2 = ColumnDefn(valueGetter="otherAspectToGet")
        col3 = ColumnDefn(valueGetter="missingAspect")
        col4 = ColumnDefn(valueGetter=getterFunction)

        data = DataObject("valueToGet", 2)
        self.assertEqual(col.GetValue(data), "valueToGet")
        self.assertEqual(col2.GetValue(data), 2)
        self.assertEqual(col3.GetValue(data), None)
        self.assertEqual(col4.GetValue(data), 4)

    def testValueGetterFunction(self):

        def getterFunction1(modelObject):
            return "constant"

        def getterFunction2(modelObject):
            return modelObject.otherAspectToGet * 2

        class DataObject:
            def __init__(self, value1, value2):
                self.aspectToGet = value1
                self.otherAspectToGet = value2

        col1 = ColumnDefn(valueGetter=getterFunction1)
        col2 = ColumnDefn(valueGetter=getterFunction2)

        data = DataObject("valueToGet", 2)
        self.assertEqual(col1.GetValue(data), "constant")
        self.assertEqual(col2.GetValue(data), 4)

    def testValueGetterMethod(self):
        col = ColumnDefn("title", valueGetter="aspectToGet")
        col2 = ColumnDefn("title", valueGetter="otherAspectToGet")
        col3 = ColumnDefn("title", valueGetter="missingAspect")

        class DataObject:
            def aspectToGet(self):
                return "valueToGet"
            def otherAspectToGet(self):
                return 2

        data = DataObject()
        self.assertEqual(col.GetValue(data), "valueToGet")
        self.assertEqual(col2.GetValue(data), 2)
        self.assertEqual(col3.GetValue(data), None)

    def testValueGetterDictionaryAccess(self):
        col = ColumnDefn("title", valueGetter="aspectToGet")
        col2 = ColumnDefn("title", valueGetter="otherAspectToGet")
        col3 = ColumnDefn("title", valueGetter="missingAspect")

        data = {"aspectToGet": "valueToGet", "otherAspectToGet": 2}
        self.assertEqual(col.GetValue(data), "valueToGet")
        self.assertEqual(col2.GetValue(data), 2)
        self.assertEqual(col3.GetValue(data), None)

    def testValueGetterListAccess(self):
        col = ColumnDefn("title", valueGetter=1)
        col2 = ColumnDefn("title", valueGetter=2)
        col3 = ColumnDefn("title", valueGetter=99)

        data = ["zero", "first", 2, "third"]
        self.assertEqual(col.GetValue(data), "first")
        self.assertEqual(col2.GetValue(data), 2)
        self.assertEqual(col3.GetValue(data), None)

        data = ("zero1", "first1", 21, "third1")
        self.assertEqual(col.GetValue(data), "first1")
        self.assertEqual(col2.GetValue(data), 21)
        self.assertEqual(col3.GetValue(data), None)


class TestStringConverter(unittest.TestCase):

    def testStringConverterFunction(self):
        def converterFunction(value):
            if value == 2:
                return "Two"
            else:
                return "Other"
        colWithoutConverter = ColumnDefn(valueGetter="aspectToGet")
        colWithConverter = ColumnDefn(valueGetter="aspectToGet", stringConverter=converterFunction)

        data = {"aspectToGet": 2}
        self.assertEqual(colWithoutConverter.GetStringValue(data), "2")
        self.assertEqual(colWithConverter.GetStringValue(data), "Two")

        data = {"aspectToGet": 3}
        self.assertEqual(colWithoutConverter.GetStringValue(data), "3")
        self.assertEqual(colWithConverter.GetStringValue(data), "Other")

    def testStringConverterFormat(self):
        col1 = ColumnDefn(valueGetter="aspectToGet")
        col2 = ColumnDefn(valueGetter="aspectToGet", stringConverter="%02X")
        col3 = ColumnDefn(valueGetter="dateTimeCreated", stringConverter="%Y-%m-%d %H:%M:%S")
        col4 = ColumnDefn(valueGetter="dateCreated", stringConverter="%Y-%m-%d")
        col5 = ColumnDefn(valueGetter="timeCreated", stringConverter="%H:%M:%S")

        data = {"aspectToGet": 15 }
        data["dateTimeCreated"] = datetime(1965, 10, 29, 12, 13, 14)
        data["dateCreated"] = date(1965, 10, 29)
        data["timeCreated"] = time(12, 13, 14)

        self.assertEqual(col1.GetStringValue(data), "15")
        self.assertEqual(col2.GetStringValue(data), "0F")
        self.assertEqual(col3.GetStringValue(data), "1965-10-29 12:13:14")
        self.assertEqual(col4.GetStringValue(data), "1965-10-29")
        self.assertEqual(col5.GetStringValue(data), "12:13:14")


class TestValueSettingWithSetter(unittest.TestCase):

    def testValueSetterFunction(self):

        def setterFunction(modelObject, value):
            modelObject.someAttribute = value

        class DataObject:
            def __init__(self, value1, value2):
                   self.someAttribute = value1
                   self.someOtherAttribute = value2

        data = DataObject("firstValue", "secondValue")
        col = ColumnDefn(valueSetter=setterFunction)

        self.assertEqual(data.someAttribute, "firstValue")
        col.SetValue(data, "newValue")
        self.assertEqual(data.someAttribute, "newValue")

    def testValueSetterMethod(self):

        class DataObject:
            def __init__(self, value1, value2):
                   self.someAttribute = value1
                   self.someOtherAttribute = value2

            def SetSomeAttribute(self, value):
                self.someAttribute = value

        data = DataObject("firstValue", "secondValue")
        col = ColumnDefn(valueSetter="SetSomeAttribute")

        self.assertEqual(data.someAttribute, "firstValue")
        col.SetValue(data, "newValue")
        self.assertEqual(data.someAttribute, "newValue")

    def testValueSetterAttributeName(self):

        class DataObject:
            def __init__(self, value1, value2):
                   self.someAttribute = value1
                   self.someOtherAttribute = value2

        data = DataObject("firstValue", "secondValue")
        col = ColumnDefn(valueSetter="someAttribute")

        self.assertEqual(data.someAttribute, "firstValue")
        col.SetValue(data, "newValue")
        self.assertEqual(data.someAttribute, "newValue")

    def testValueSetterWrongName(self):

        class DataObject:
            def __init__(self, value1, value2):
                   self.someAttribute = value1
                   self.someOtherAttribute = value2

        data = DataObject("firstValue", "secondValue")
        col = ColumnDefn(valueSetter="aNameThatIsntAnAttribute")

        self.assertEqual(data.someAttribute, "firstValue")
        col.SetValue(data, "newValue")
        self.assertEqual(data.someAttribute, "firstValue")


class TestValueSettingWithGetter(unittest.TestCase):

    def testValueGetterAttribute(self):

        class DataObject:
            def __init__(self, value1, value2):
                self.aspectToGet = value1
                self.otherAspectToGet = value2

        data = DataObject("firstValue", "secondValue")

        col = ColumnDefn(valueGetter="aspectToGet")
        self.assertEqual(data.aspectToGet, "firstValue")
        col.SetValue(data, "newValue")
        self.assertEqual(data.aspectToGet, "newValue")

        col = ColumnDefn(valueGetter="otherAspectToGet")
        self.assertEqual(data.otherAspectToGet, "secondValue")
        col.SetValue(data, "newValue")
        self.assertEqual(data.otherAspectToGet, "newValue")

    def testValueGetterWrongName(self):

        def getterFunction(modelObject):
            return modelObject.otherAspectToGet * 2

        class DataObject:
            def __init__(self, value1, value2):
                self.aspectToGet = value1
                self.otherAspectToGet = value2

        data = DataObject("firstValue", "secondValue")

        col = ColumnDefn(valueGetter="missingAspect")
        self.assertEqual(data.aspectToGet, "firstValue")
        col.SetValue(data, "newValue")
        self.assertEqual(data.aspectToGet, "firstValue")

    def testValueGetterFunction(self):

        def getterFunction(modelObject):
            return modelObject.otherAspectToGet * 2

        class DataObject:
            def __init__(self, value1, value2):
                self.aspectToGet = value1
                self.otherAspectToGet = value2

        data = DataObject("firstValue", "secondValue")

        col = ColumnDefn(valueGetter=getterFunction)
        self.assertEqual(data.aspectToGet, "firstValue")
        col.SetValue(data, "newValue")
        self.assertEqual(data.aspectToGet, "firstValue")

    def testValueGetterMethod(self):

        class DataObject:
            def aspectToGet(self):
                return "firstValue"
            def otherAspectToGet(self):
                return 2

        data = DataObject()

        col = ColumnDefn("title", valueGetter="aspectToGet")
        self.assertEqual(data.aspectToGet(), "firstValue")
        col.SetValue(data, "newValue")
        self.assertEqual(data.aspectToGet(), "firstValue")


    def testValueGetterDictionaryModifying(self):
        data = {"aspectToGet": "firstValue", "otherAspectToGet": 2}

        col = ColumnDefn("title", valueGetter="aspectToGet")
        self.assertEqual(col.GetValue(data), "firstValue")
        col.SetValue(data, "newValue")
        self.assertEqual(data["aspectToGet"], "newValue")

        col = ColumnDefn("title", valueGetter="otherAspectToGet")
        self.assertEqual(col.GetValue(data), 2)
        col.SetValue(data, 3)
        self.assertEqual(data["otherAspectToGet"], 3)

    def testValueGetterListModifying(self):
        data = ["zero", "first", 2, "third"]

        col = ColumnDefn("title", valueGetter=1)
        self.assertEqual(col.GetValue(data), "first")
        col.SetValue(data, "newValue")
        self.assertEqual(data[1], "newValue")

    def testValueGetterListMiss(self):
        data = ["zero", "first", 2, "third"]
        col = ColumnDefn("title", valueGetter=99)
        self.assertEqual(col.GetValue(data), None)
        col.SetValue(data, 3)
        self.assertEqual(data, ["zero", "first", 2, "third"])

#======================================================================

if __name__ == '__main__':
    unittest.main()
