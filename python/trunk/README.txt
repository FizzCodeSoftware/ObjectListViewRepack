.. -*- coding: UTF-8 -*-

ObjectListView
==============

*An ObjectListView is a wrapper around the wx.ListCtrl that makes the
list control easier to use. It also provides some useful extra functionality.*

Larry Wall, the author of Perl, once wrote that the three essential character flaws of any
good programmer were sloth, impatience and hubris. Good programmers want to do the minimum
amount of work (sloth). They want their programs to run quickly (impatience). They take
inordinate pride in what they have written (hubris).

ObjectListView encourages the vices of sloth and hubris, by allowing programmers to do far
less work but still produce great looking results.


Without wasting my time, just tell me what it does!
---------------------------------------------------

OK, here's the bullet point feature list:

* Automatically sorts rows.
* Easily edits the cell values.
* Supports all ListCtrl views (report, list, large and small icons).
* Columns can be fixed-width, have a minimum and/or maximum width, or be space-filling.
* Displays a “list is empty” message when the list is empty (obviously).
* Supports checkboxes in any column
* Supports alternate rows background colors.
* Supports custom formatting of rows.
* The `FastObjectListView` version can build a list of 10,000 objects in less than 0.1 seconds.
* The `VirtualObjectListView` version supports millions of rows through ListCtrl's virtual mode.


OK, I'm interested. What do I do next?
--------------------------------------

You can download a `demonstration of the ObjectListView
<http://objectlistview.sourceforge.net/samples/PyObjectListViewDemo.zip>`_ in action. This
demo includes ObjectListView module, which you need to include in your project.

You can also look at the documentation and other information available at the
website: http://objectlistview.sourceforge.net/python.
