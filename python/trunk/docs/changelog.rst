.. -*- coding: UTF-8 -*-

.. _changelog:

Change Log
==========

2008-05-29 14:17 (#106) - Phillip
  - Finally clean up of documentation before v1.0 release


2008-05-29 14:16 (#105) - Phillip
  - Used named images internally
  - Better handling of missing image lists
  - Cleaned up some more documentation


2008-05-29 00:25 (#104) - Phillip
  - Changed to use "isinstance(x, basestring)" rather than "isinstance(x, (str, unicode)"


2008-05-28 00:22 (#102) - Phillip
  - Better documentation in Demo.py
  - Tidied up docs for v1.0 release
  - Allow sorting by column created by CreateCheckStateColumn()


2008-05-27 13:38 (#101) - Phillip
  - Added ".." to python path so that ObjectListView will be found even if it hasn't been installed


2008-05-27 13:37 (#100) - Phillip
  - Prepare for v1.0 release


2008-05-27 13:30 (#99) - Phillip
  - Added images to generated html
  - Prepare documentation for v1.0 release


2008-05-26 17:37 (#98) - Phillip
  - Remove "dummy" tab


2008-05-26 00:39 (#95) - Phillip
  - Did all work to create proper package with distutils (setup.py)


2008-05-26 00:35 (#93) - Phillip
  - Corrected for new directory structure


2008-05-26 00:35 (#92) - Phillip
  - Fixed pyLint annoyances


2008-05-26 00:34 (#91) - Phillip
  - Fixed pyLint annoyances


2008-05-26 00:34 (#90) - Phillip
  - Fixed pyLint annoyances


2008-05-26 00:33 (#89) - Phillip
  - Cleaned up a litte


2008-05-24 01:57 (#67) - Phillip
  - Documentation near completion


2008-05-24 01:55 (#65) - Phillip
  - Added ability to name images
  - Used _ to hide "private" methods
  - Improved docs
  - Correctly calculate subitem rect when in ICON view
  - Implemented HitTestSubItem for all platforms
  - Make sure empty list msg is shown on virtual lists


2008-05-24 01:51 (#64) - Phillip
  - Change editor style when listctrl is in ICON view


2008-05-24 01:51 (#63) - Phillip
  - Made sure all buttons worked
  - Uses named images


2008-05-24 01:49 (#62) - Phillip
  - Added tests for checkboxes, SelectAll, DeselectAll, Refresh


2008-05-19 21:34 (#61) - Phillip
  - Added support for checkboxes
  - Used "modelObject(s)" name instead of "object(s)"
  - Made sure all public methods have docstrings


2008-05-19 21:32 (#60) - Phillip
  - Added ".." to sys.path to demo and tests
  - Added demo for checkboxes
  - Added tests for check boxes


2008-05-19 21:30 (#59) - Phillip
  - Added Sphinx based documentation (in progress)


2008-05-12 11:29 (#44) - Phillip
  - Minor changes and add svn property


2008-05-12 11:28 (#43) - Phillip
  - Add some svn property


2008-05-12 11:26 (#41) - Phillip
  - Massively improved documentation. Generates reasonable docs using epydoc now.


2008-04-23 20:13 (#40) - Phillip
  - Added $Id$


2008-04-18 22:57 (#39) - Phillip
  - Updated documentation


2008-04-18 00:00 (#38) - Phillip
  - Added List Empty msg
  - Cleaned up code


2008-04-17 23:59 (#36) - Phillip
  - Added "Clear List" buttons
  - Set cell edit mode
  - Made more columns non-auto sizing


2008-04-16 22:54 (#35) - Phillip
  - Modularized ObjectListView
  - Reorganised code within ObjectListView.py


2008-04-14 16:29 (#29) - Phillip
  - Added test for cell editing


2008-04-14 16:28 (#27) - Phillip
  - Added Complex tab
  - Made Simple tab to show what is possible with only ColumnDefns
  - Give colour and font to model objects


2008-04-14 16:26 (#26) - Phillip
  - Allow columns to have a cell editor creator function
  - Handle horizontal scrolling when cell editing
  - Added cell edit modes
  - Handle edit during non-report views
  - Correctly update slots with a previous value of None
  - First cleanup of cell editing code


2008-04-08 00:24 (#25) - Phillip
  - Cell editing finished, including model updating
  - Changed manner of rebuilding list to use ListItems
  - Unified rowFormatter to use ListItems. Now virtual lists use the same logic
  - Improved documentation on ColumnDefn
  - Lists can now be used a model objects.
  - Removed sortable parameter to ObjectListView


2008-04-08 00:18 (#24) - Phillip
  - Added tests for value setting
  - Added tests of list accessing
  - Reorganized tests


2008-04-08 00:17 (#23) - Phillip
  - Changed to handle new unified rowFormatter
  - Allow dateLastPlayed to be updated


2008-04-08 00:15 (#22) - Phillip
  - Allow cell value to be changed in FinishingCellEdit event


2008-04-08 00:15 (#21) - Phillip
  - Validate keys in the numeric editors


2008-04-07 11:13 (#20) - Phillip
  - Made to work under Linux (still needs work)


2008-04-07 11:12 (#19) - Phillip
  - Added the source listview as a parameter


2008-04-07 11:12 (#18) - Phillip
  - Make work under Linux
  - Autocomplete no longer choke on large lists


2008-04-06 01:02 (#17) - Phillip
  - Cell editing in progress: F2 triggers, Tabbing works
  - Improved docs in ObjectListView.py
  - Added example of cell editing events to demo


2008-04-06 00:59 (#16) - Phillip
  - Initial check in


2008-04-06 00:59 (#15) - Phillip
  - Separated column tests from list tests
  - Added sorting tests and space filling tests
  - Added basic tests for all editors


2008-04-06 00:57 (#14) - Phillip
  - Initial checkin.
  - Editors for all basic types working
  - Autocomplete textbox and combobox working
  - Editor registry working


2008-04-02 00:42 (#13) - Phillip
  - Added free space filling columns


2008-03-29 22:44 (#12) - Phillip
  - Added minimum, maximum and fixed widths for columns
  - unified 'stringFormat' and 'stringConverter'
  - Added/update unit tests


2008-03-28 23:54 (#11) - Phillip
  - Added VirtualObjectListView and FastObjectListView
  - Changed sort indicator icons
  - Changed demo to use track information, and to show new classes


2008-03-06 12:20 (#10) - Phillip
  - Call SetObjects() after assigning a rowFormatter


2008-03-06 12:19 (#9) - Phillip
  - Improved docs
  - Removed some duplicate code


2008-03-02 11:02 (#8) - Phillip
  - Added alternate row colors
  - Added rowFormatter


2008-03-02 09:33 (#6) - Phillip
  - Added Update Selected
  - Added examples of lowercase and Unicode


2008-03-02 09:31 (#5) - Phillip
  - Test selections
  - Use PySimpleApp


2008-03-02 09:30 (#4) - Phillip
  - Added RefreshObject() and friends
  - Do sorting within python when possible, rather than using SortItems(). 5-10x faster!
  - Optimized RepopulateList()


2008-02-29 10:34 (#2) - Phillip
  - Unit tests in progress
  - Demo complete


