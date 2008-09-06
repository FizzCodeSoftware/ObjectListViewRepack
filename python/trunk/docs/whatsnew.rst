.. -*- coding: UTF-8 -*-

What's New?
===========

For the (mostly) complete change log, :ref:`see here <changelog>`.

v1.2 - September 2008
---------------------

* Big new feature: :ref:`ListCtrlPrinter <using-listctrlprinter>`
* Added ``AddObjects()`` and ``RemoveObjects()`` and friends
* Added :ref:`filtering`
* Added :ref:`batched updates adapter <recipe-batched-updates>`
* Made ``GroupListView`` a subclass of ``FastObjectListView``. More speed; less flicker.

Small things
^^^^^^^^^^^^

- Correctly handle model objects that cannot be hashed
- Added ``CELL_EDIT_STARTED`` and ``CELL_EDIT_FINISHED`` events
- Added *ensureVisible* parameter to ``SelectObject()``
- Remove flicker from some more ``FastObjectListView`` operations

v1.1 - July 2008
----------------

* Added :ref:`GroupListView <using-grouplistview>`
* Column headers can now have their own images

v1.0.1 - June 2008
------------------

* Sorting can now be customised throught the ``EVT_SORT`` event
* Added searching by sort column
* Added binary search
* ``VirtualObjectListView`` can now be sorted, using the ``EVT_SORT`` event. By default, they are still not sortable
* Fixed some bugs on Mac and Linux

v1.0 - June 2008
----------------

* First true public release.
* Offical website up and running
* Added check state support
* Added named image support
* Added more examples

v0.9 - May 2008
----------------

* Released on wxWiki -- to thunderous silence :-)
* Added cell editing

v0.5 - March 2008
-----------------

* Converted to use straight wxPython now that wax appears dead
* Added column width management (minimum, maximum, space filling)

v0.1 - November 2006
--------------------

* First version. Written to work with wax.
* Used internally only
