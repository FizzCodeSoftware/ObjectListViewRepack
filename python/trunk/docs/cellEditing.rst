.. -*- coding: UTF-8 -*-

.. _cell-editing-label:

Editing Cell Values
===================

ListCtrls are normally used for displaying information. The standard ListCtrl allows the
value at column 0 (the primary cell) to be edited, but nothing beyond that. ObjectListView
allows all cells to be edited. Depending on how the data for a cell is sourced, the edited
values can be automagically written back into the model object.

The "editability" of an ObjectListView is controlled by the `cellEditMode` attribute. This
attribute can be set to one of the following values:

* ObjectListView.CELLEDIT_NONE
   Cell editing is not allowed on the control This is the default.

* ObjectListView.CELLEDIT_SINGLECLICK
   Single clicking on any subitem cell begins an edit operation on that cell.
   Single clicking on the primary cell does *not* start an edit operation.
   It simply selects the row. Pressing :kbd:`F2` edits the primary cell.

* ObjectListView.CELLEDIT_DOUBLECLICK
   Double clicking any cell starts an edit operation on that cell, including
   the primary cell. Pressing :kbd:`F2` edits the primary cell.

* ObjectListView.CELLEDIT_F2ONLY
   Pressing :kbd:`F2` edits the primary cell. :kbd:`Tab`/:kbd:`Shift-Tab` can be used to
   edit other cells. Clicking does not start any editing.

Individual columns can be marked as editable via the `isEditable` attribute (default value is
True), though this only has meaning once the ObjectListView itself is editable. If you
know that the user should not be allowed to change cells in a particular column, set
`isEditable` to False. Be aware, though, that this may create some surprises, resulting in
user complaints like "How come I can't edit this value by clicking on it like I can on all
the other cells?".

Once a cell editor is active, the normal editing conventions apply:

    * :kbd:`Enter` or :kbd:`Return` finishes the edit and commits the new value to the model object.
    * :kbd:`Escape` cancels the edit.
    * :kbd:`Tab` commits the current edit, and starts a new edit on the next editable cell.
    * :kbd:`Shift-Tab` commits the current end, and starts a new edit on the previous
      editable cell.

Deciding on a cell editor
-------------------------

When a cell is to be edited, we need to decide what sort of editor to use.

There are three ways this decision can be made:

1. Column based decision

Most simply, the column can be configured with a ``cellEditorCreator`` attribute.
When a cell in this column is to be edited, the ``cellEditorCreator`` will be invoked.
This attribute must be set to a "cell editor factory" callable. A "cell editor factory"
must be a callable that accepts three parameters:

   - the ObjectListView that needs the editor
   - the index of the row to be edited
   - the index of the subitem to be edited

This factory should return a fully configured widget that can edit the value at that cell.

2. Event based decision

If this is not enough, the programmer can have complete control over the process
by listening for a cell editing starting event
(``ObjectListView.EVT_CELL_EDIT_STARTING``). Within the handler for this event, the
programmer can create and configure any sort of widget they like and then return this
widget via the ``newEditor`` attribute of the event.

If the ``shouldConfigureEditor`` attribute of the event is True (this is the default), the
ObjectListView will perform all the normal default configuration of the cell editor. This
includes setting the controls value, positioning it correctly and hooking up any required
events. If ``shouldConfigureEditor`` is False, it is assumed that all configuration has
already been done and nothing else will be done to the widget.

3. Registry based decision

Most generally, you can register a "cell editor factory" for a type of object. This
is done using ``RegisterCreatorFunction`` method of the ``CellEditorRegistry``.

For example, there is no standard editor for a wx.Colour. To handle the editing of
colours, we would need a factory callable, and then to register it with the
``CellEditorRegistry``. Which migh look something like this::

    def makeColourEditor(olv, rowIndex, subItemIndex):
        odcb = OwnerDrawnEditor.ColourComboBox(olv)
        # OwnerDrawnComboxBoxes don't generate EVT_CHAR so look for keydown instead
        odcb.Bind(wx.EVT_KEY_DOWN, olv._HandleChar)
        return odcb

    CellEditorRegistry().RegisterCreatorFunction(type(wx.BLACK), makeColourEditor)

By default, the cell registry is configured with editors for the following standard
types: ``bool``, ``int``, ``long``, ``str``, ``unicode``, ``float``,
``datetime``, ``date``, ``time``.

You can replace the standard editors with editors of your own devising using the
registry. So if someone make a better date-time editor (yes, please!), they could
use it to edit all ``datetime`` values by doing this::

    import datetime
    ...
    CellEditorRegistry().RegisterCreatorFunction(datetime.datetime, makeBetterDateTimeEditor)


Getting and Setting the Editors value
-------------------------------------

A cell editor must implement both ``GetValue`` and ``SetValue`` methods.

Once the cell editor has been created, it is given the cell's value via the control's
``SetValue`` method.

When the user has finished editing the value, the new value in the editor is retrieved via
the ``GetValue`` method.



Updating the Model Object
-------------------------

Once the user has entered a new value into a cell and pressed :kbd:`Enter`, the ObjectListView
tries to store the modified value back into the model object. There are three ways this
can happen:

1. ObjectListView.EVT_CELL_EDIT_FINISHING Event Handler
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can create an event handler for the EVT_CELL_EDIT_FINISHING event (see below). In that
handler, you would write the code to get the modified value from the editor, put that new
value into the model object, and then call ``Veto`` on the event, so that the ObjectListView knows that
it doesn't have to do anything else. You will also need to call at least ``RefreshItem()`` or
``RefreshObject()``, so that the changes to the model object are shown in the ObjectListView.

There are cases where this is necessary, but as a general solution, it doesn't fit my philosophy of slothfulness.

2. Via the Column's ``valueSetter`` attribute
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can set the ``valueSetter`` attribute on the corresponding ColumnDefn. Like ``valueGetter``, this
attribute is quite flexible:

* It can be a callable that accepts the model object and the new value::

    def updateSalary(person, newValue):
        person.SetSalary(newValue)
        if person.userId == self.currentUser.userId:
            self.NotifySupervisorOfSalaryChange()

    ColumnDefn("Salary", ... valueSetter=updateSalary)

* It can be the name of a method to be invoked,. This method must accept the new value
  as its sole parameter. Example::

    class Track():
        ...
        def SetDateLastPlayed(self, newValue):
            self.dateLastPlayed = newValue

    ColumnDefn("Last Played", ... valueSetter="SetDateLastPlayed")

* It can be the name of an attribute to be updated. This attribute will not be
  created: it must already exist. Example::

    ColumnDefn("Last Played", ... valueSetter="dateLastPlayed")

* For dictionary like model objects, it can be the key into the dictionary. The key
  would commonly be a string, but it doesn't have to be.


3. Via the Column's ``valueGetter`` attribute
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Updating the value through the *value-GETTER* attribute seems wrong somehow. In practice, it is neat and commonly used.

If the ``valueGetter`` attribute is the name of an attribute, or the key into a dictionary, it will very commonly
be the same place where any modified value should be written.

So if a value needs to be written back into the model, and there is no ``valueSetter`` attribute, the ObjectListView
will try to use the ``valueGetter`` attribute to decide how to update the model.

After the update
----------------

If the model is updated, the row will be automatically refreshed to display the new data.

If the user enters a new value, presses :kbd:`Enter`, and the value in the ObjectListView doesn't change,
then almost certainly the ObjectListView could not automagically update the model object.

In that case, you will need to track down, which of the above three strategies should be
being used, and why it is not.

How Can You Customise The Editing
---------------------------------

To do something other than the default processing, you can listen for two events:
ObjectListView.EVT_CELL_EDIT_STARTING and ObjectListView.EVT_CELL_EDIT_FINISHING.

## MORE HERE ##
