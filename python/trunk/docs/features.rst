.. -*- coding: UTF-8 -*-

.. _features:

Features of an ObjectListView
=============================

Why take the time to learn how to use an ObjectListView? What's the benefit? The return on
investment? This page tries to document the useful features of an ObjectListView. Not all
features are equally useful, but its better to be aware of what's available so that you
can use it when the need arises.

Ease of use
-----------

**The** major goal of an ObjectListView is to make your life easier. All common ListCtrl
tasks should be easier -- or at least no more difficult -- with an ObjectListView. For the
investment of creating column definitions, you receive a great deal of convenience and
value added functions. See :ref:`getting-started-label` for an
introduction to the basics.

Automatically create the ListCtrl from model objects
----------------------------------------------------

The major way in which the ObjectListView makes your life easier is by being able to
automatically build the ListCtrl from a collection of model objects. Once the columns
are defined, an ObjectListView is able to build the rows of the ListCtrl without any
other help. It only takes a single method call: `SetObjects()`.

Editing cell values
-------------------

ListCtrls normally allow only the primary cell (column 0) to be edited.
An ObjectListView allows all cells to be edited. This editing knows to use different
editors for different data types. It also allows autocompletion based on existing values
for that column (pass `autoCompleteCellEditor=True` to a column constructor)

See :ref:`cell-editing-label` for more details.

Automatic sorting
-----------------

Once the column are defined, the ObjectListView will automatically sort the rows when the
user clicks on a column header. This sorting understands the data type of the column, so
sorting is always correct according to the data type. Sorting does not use the string
representation.

Supports all ListCtrl views
---------------------------

An ObjectListView supports all views: report, list, large and small icons. All functions
should work equally in all views: editing, check state, icons, selection.

More control over column width
------------------------------

An ObjectListView allows the programmer to have control over the width of columns after
the ListCtrl is created.

When a column is defined, it is normally given a width in pixels. This is the width of the
column when the ListCtrl is first shown. After creation, the user can resize that column
to be something else.

By using the `minimumWidth` and `maximumWidth` attributes, the programmer can control the
lower and upper limits of a column. The programmer can also use the `fixedWidth`
constructor parameter to indicate that a column should not be resizable by the user.

Finally, the programmer can specify that a column should resize automatically to be wider
when the ListCtrl is made wider and narrower when the ListCtrl is made narrower.
This type of column is a space filling column, and is created by passing the
`isSpaceFilling` parameter to the ColumnDefn constructor.

See these recipes:

* :ref:`recipe-column-width`
* :ref:`recipe-fixed-column`
* :ref:`recipe-column-filling`


Displays a "list is empty" message
----------------------------------

Sometimes, an empty ListCtrl could be confusing to the user: did something go wrong?
Do I need to wait longer and then something will appear?

An ObjectListView can show a "this list is empty" message when there is nothing
to show in the list, so that the user knows the control is supposed to be empty.

See this recipe: :ref:`recipe-emptymsg`

Checkboxes in any column
------------------------

An ObjectListView trivially supports checkboxes on rows. In fact, it supports multiple
checkboxes per row, if you are really keen. See this recipe for more details:
:ref:`recipe-checkbox`.

Alternate rows background colors
--------------------------------

Having subtly different row colours for even and odd rows can make a ListCtrl easier
for users to read. ObjectListView supports this alternating of background colours.
It is enabled by default, and the background colours are controlled by the `evenRowsBackColor`
and `oddRowsBackColor` attributes.

Custom row formatting
---------------------

An ObjectListView allows rows to be formatted with custom colours and fonts. For example,
you could draw clients with debts in red, or big spending customers could be given a gold
background. See here: :ref:`recipe-formatter`

Different flavours of ObjectListView for different purposes
-----------------------------------------------------------

An `ObjectListView` is the plain vanilla version of the control. It accepts a list of
model objects, and builds the control from those model objects.

A `FastObjectListView` requires a list of model objects, but it can deal with those
objects very quickly. Typically, it can build a list of 10,000 objects in less than 0.1 seconds.

A `VirtualObjectListView` does not require a list of model objects. Instead, it asks for
model objects as it requires them. In this way, it can support an unlimited number of rows.
A `VirtualObjectListView` must be given an `objectGetter` callable, which is called when
the list needs to display a particular model object.

Model object level operations
-----------------------------

The ObjectListView allows operations at the level that makes most sense to the
application: at the level of model objects. Operations like `SelectObjects()`,
`RefreshObjects()`, `GetSelectedObjects()` and `GetCheckedObjects()` provide a high-level
interface to the ListCtrl.

The VirtualObjectListView is an unfortunate exception to these features. It does not know
where any given model object is located in the control (since it never deals with the
whole list of objects), so these model level operations are not available to it.

Searching on the sort column
----------------------------

When a user types into a normal ListCtrl, the control tries to find the first row where
the value in cell 0 begins with the character that the user typed.

ObjectListView extends this idea so that the searching can be done on the column by which
the control is sorted (the "sort column"). If your music collection is sorted by "Album"
and the user presses "z", ObjectListView will move the selection to the first track of the
"Zooropa" album, rather than find the next track whose title starts with "z".

In many cases, this is behaviour is quite intuitive. iTunes works in this fashion on its
string value columns (e.g. Name, Artist, Album, Genre).

Fast searching on sorted column
-------------------------------

When the user types something into a control, the ObjectListView will use a binary search
(if possible) to find a match for what was typed. A binary search is normally possible if
the ObjectListView is sorted on a column that shows strings.

A binary search is able to handle very large collections: 10,000,000 rows can be searched
in about 24 comparisons. This makes it feasible to seach by typing even on large virtual
lists.
