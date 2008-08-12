.. -*- coding: UTF-8 -*-

.. _faq:

Frequently Asked Questions
==========================

Some questions and issues surface regularly on the Forums or in emails. This section has
several of the most common questions. Please read the questions before asking questions on
the Forum. Several people have been known to have blood pressure problems.


What platforms does it work on?
-------------------------------

ObjectListView has been extensively tested on Windows and somewhat tested on Linux (Ubuntu).

I have no experience on other platforms but would welcome feedback. I'd be especially
interested if someone from MacLand could test it, especially with native mode enabled.


Can an ObjectListView have rows of different heights? Can it word-wrap?
-----------------------------------------------------------------------

No.

ObjectListView is a wrapper for the underlying ListCtrl. It makes a ListCtrl much easier
to use, but it can't change the control's basic behaviour. One limitation of a ListCtrl is
it that cannot have rows of different heights. There is no way to make one row be taller
than other rows. It's just not possible. So there is no way to word wrap a long line on
just one row either.

If being able to have rows of different heights is essential to you, ObjectListView is not
your solution.


Why doesn't the ObjectListView auto-update when I change my model objects?
--------------------------------------------------------------------------

    *I have ObjectListView that's showing my model objects. But when I change the values in my
    model, the ObjectListView doesn't update. What's going wrong here?*

Nothing. That's what it is supposed to do.

The ObjectListView knows nothing about your model objects, and particularly it doesn't
know when they have been changed. Only you know that. When you know that a model object
has changed and needs to be updated, you can either call `RefreshObject()` to
update just one object, or you can call `RepopulateList()` to rebuild everything at once.


Why doesn't it do *some-feature-I-really-want*?
-----------------------------------------------

It could be that I simply haven't thought of it. Or it could be that I have thought of
it but it just isn't possible.

Remember that ObjectListView is just a wrapper around wx.ListCtrl. It can make the ListCtrl
a little easier to use, and can add some helper functions, but it can't change the basic
behaviour of the control.

One thing I would really like to add is owner drawing. But this is not supported by a
ListCtrl, so ObjectListView cannot have it either.


Why is the text of the first column indented by about 20 pixels?
----------------------------------------------------------------

This shows up when you have a ListCtrl that doesn't have an icon in the first column.
The control still leaves space for the icon, even when there isn't one.

If the ListCtrl doesn't have a small image list, this indent disappears. But as soon as
the control has a small image list, even an empty one, the text of the first column will
be indented. Unfortunately, almost all ObjectListViews have a small image list, since
showing sort indicators in the column headers uses the small image list.

So, if you really want to get rid of this indent, make an ObjectListView which isn't
sortable (pass "sortable=False" to the constructor) and don't add any images to the
control. The indent will disappear -- but the list will not be sortable.
