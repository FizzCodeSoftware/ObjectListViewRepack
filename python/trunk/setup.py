import sys

NAME = "ObjectListView"
VERSION = "1.2"
URL = "http://objectlistview.sourceforge.net/python"
DOWNLOAD_URL = "http://objectlistview.sourceforge.net/samples/ObjectListView-1.2.zip"
LICENSE = "wxWindows"
AUTHOR = "Phillip Piper"
AUTHOR_EMAIL = "phillip.piper@gmail.com"
YEAR = 2008
DESCRIPTION = "An ObjectListView is a wrapper around the wx.ListCtrl that makes the list control easier to use"

LONG_DESCRIPTION = \
r"""
ObjectListView
==============

An ObjectListView is a wrapper around the wx.ListCtrl that makes the
list control easier to use. It also provides some useful extra functionality.

* Automatically transforms a collection of model objects into a fully functional wx.ListCtrl.
* Automatically sorts rows.
* Easily edit the cell values.
* Supports all ListCtrl views (report, list, large and small icons).
* Columns can be fixed-width, have a minimum and/or maximum width, or be space-filling
* Displays a "list is empty" message  when the list is empty (obviously).
* Supports checkboxes in any column.
* Supports alternate rows background colors.
* Supports custom formatting of rows .
* Supports searching (by typing) on any column, even on massive lists.
* Supports custom sorting
* Supports filtering and batched updates
* The ``FastObjectListView`` version can build a list of 10,000 objects in less than 0.1 seconds.
* The ``VirtualObjectListView`` version supports millions of rows through ListCtrl's virtual mode.
* The ``GroupListView`` version supports arranging rows into collapsible groups.
* Effortlessly produce professional-looking reports using a ``ListCtrlPrinter``.

Seriously, after using an ObjectListView, you will never go back to using a plain wx.ListCtrl.


Dependancies
============

  * Python 2.4+
  * wxPython 2.8+

"""
CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: User Interfaces',
]

if 'bdist_egg' in sys.argv:
    try:
        from setuptools import setup
    except ImportError:
        print "To build an egg setuptools must be installed"
else:
    from distutils.core import setup

setup(
    name = NAME,
    version = VERSION,
    description = DESCRIPTION,
    long_description = LONG_DESCRIPTION,
    author = AUTHOR,
    author_email = AUTHOR_EMAIL,
    maintainer = AUTHOR,
    maintainer_email = AUTHOR_EMAIL,
    url = URL,
    download_url = DOWNLOAD_URL,
    license = LICENSE,
    platforms = [ "Many" ],
    packages = [ NAME ],
    classifiers= CLASSIFIERS,
)
