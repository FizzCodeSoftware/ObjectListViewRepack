.. -*- coding: UTF-8 -*-

==============
ObjectListView
==============

.. rubric:: An ObjectListView is a wrapper around the wx.ListCtrl that makes the
   list control easier to use. It also provides some useful extra functionality.

Larry Wall, the author of Perl, once wrote that the three essential character flaws of any
good programmer were sloth, impatience and hubris. Good programmers want to do the minimum
amount of work (sloth). They want their programs to run quickly (impatience). They take
inordinate pride in what they have written (hubris).

ObjectListView encourages the vices of sloth and hubris, by allowing programmers to do far
less work but still produce great looking results.

Without wasting my time, just tell me what it does!
---------------------------------------------------

OK, here's the bullet point feature list:

* Automatically transforms a collection of model objects into a fully functional wx.ListCtrl.
* Automatically sorts rows.
* Easily edits the cell values.
* Supports all ListCtrl views (report, list, large and small icons).
* Columns can be fixed-width, have a minimum and/or maximum width, or be space-filling.
* Displays a "list is empty" message when the list is empty (obviously).
* Supports checkboxes in any column
* Supports alternate rows background colors.
* Supports custom formatting of rows.
* Supports searching (by typing) on any column, even on massive lists.
* Supports custom sorting
* The `FastObjectListView` version can build a list of 10,000 objects in less than 0.1 seconds.
* The `VirtualObjectListView` version supports millions of rows through ListCtrl's virtual mode.
* The `GroupListView` version supports arranging rows into collapsible groups.

OK, I'm interested. What do I do next?
--------------------------------------

You can download a `source package of the ObjectListView
<https://sourceforge.net/project/showfiles.php?group_id=225207&package_id=280564>`_ which includes
the ObjectListView module, as well as some demo applications showing ObjectListView in
action.

After that, you might want to look at the :ref:`Getting Started
<getting-started-label>` and the :ref:`Cookbook <cookbook-label>` sections. Please make
sure you have read and understood these sections before asking questions in the Forums.

At some point, you will want to do something with an ObjectListView and it won't be
immediately obvious how to make it happen. After dutifully scouring the :ref:`Getting
Started <getting-started-label>` and the :ref:`Cookbook <cookbook-label>` sections, you
decide that is is still not obvious. The `Forum
<https://sourceforge.net/forum/forum.php?forum_id=825500>`_ section is the place to find
all your as-yet-unasked questions.

It may even be possible that you might find some undocumented features in the code (also
known as bugs). These "features" can be reported to the `project's Issue Tracker
<https://sourceforge.net/tracker/?func=add&group_id=225207&atid=1064157>`_ and the status
of your "feature" report can be `tracked here
<https://sourceforge.net/tracker/?group_id=225207&atid=1064157>`_.

If you would like to ask me a question or suggest an improvement, you can contact me here:
jppx1@bigfoot.com.

Bleeding-edge source
--------------------

If you are a very keen developer, you can access the SVN repository directly for this
project. The following SVN command will fetch the most recent version from the repository::

 svn co https://objectlistview.svn.sourceforge.net/svnroot/objectlistview/python/trunk objectlistview

There are details on `how to use Subversion here <https://sourceforge.net/docs/E09>`_ on SourceForge.

Please remember that code within the SVN is bleeding edge. It has not been well-tested and
is almost certainly full of bugs. If you just want to play with the ObjectListView, it's
better to stay with the official releases, where the bugs are (hopefully) less obvious.

Site contents
-------------

.. toctree::
   :maxdepth: 1

   whatsnew
   features
   gettingStarted
   recipes
   Recipe - Cell Editing <cellEditing>
   groupListView
   faq
   majorClasses
   changelog
