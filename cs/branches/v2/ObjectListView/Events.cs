/*
 * Events - All the events that can be triggered within an ObjectListView.
 *
 * Author: Phillip Piper
 * Date: 17/10/2008 9:15 PM
 *
 * Change log:
 * 2008-10-17   JPP  - Separated from ObjectListView.cs
 * 
 * Copyright (C) 2006-2008 Phillip Piper
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *
 * If you wish to use this code in a closed source application, please contact phillip_piper@bigfoot.com.
 */

using System;
using System.Collections;
using System.ComponentModel;
using System.Drawing;
using System.Windows.Forms;

namespace BrightIdeasSoftware
{
    partial class ObjectListView
    {
        //-----------------------------------------------------------------------------------
        #region Event delegates

        /// <summary>
        /// The callbacks for AfterSorting events
        /// </summary>
        public delegate void AfterSortingEventHandler(object sender, AfterSortingEventArgs e);

        /// <summary>
        /// The callbacks for BeforeSorting events
        /// </summary>
        public delegate void BeforeSortingEventHandler(object sender, BeforeSortingEventArgs e);

        /// <summary>
        /// The callbacks for CellEditing events
        /// </summary>
        public delegate void CellEditEventHandler(object sender, CellEditEventArgs e);

        /// <summary>
        /// The callbacks for ItemsAdding events
        /// </summary>
        public delegate void ItemsAddingEventHandler(object sender, ItemsAddingEventArgs e);

        /// <summary>
        /// The callbacks for ItemsChanged events
        /// </summary>
        public delegate void ItemsChangedEventHandler(object sender, ItemsChangedEventArgs e);

        /// <summary>
        /// The callbacks for ItemsChanging events
        /// </summary>
        public delegate void ItemsChangingEventHandler(object sender, ItemsChangingEventArgs e);

        /// <summary>
        /// The callbacks for ItemsRemoving events
        /// </summary>
        public delegate void ItemsRemovingEventHandler(object sender, ItemsRemovingEventArgs e);

        #endregion

        //-----------------------------------------------------------------------------------
        #region Events

        /// <summary>
        /// Triggered after a ObjectListView has been sorted
        /// </summary>
        [Category("Behavior")]
        public event AfterSortingEventHandler AfterSorting;

        /// <summary>
        /// Triggered before a ObjectListView is sorted
        /// </summary>
        /// <remarks>
        /// Set Cancelled to true to prevent the sort from taking place.
        /// Changing ColumnToSort or SortOrder will change the subsequent sort.
        /// </remarks>
        [Category("Behavior")]
        public event BeforeSortingEventHandler BeforeSorting;

        /// <summary>
        /// Triggered when a cell is about to be edited.
        /// </summary>
        /// <remarks>Set Cancel to true to prevent the cell being edited.
        /// You can change the the Control to be something completely different.</remarks>
        [Category("Behavior")]
        public event CellEditEventHandler CellEditStarting;

        /// <summary>
        /// Triggered when a cell editor needs to be validated
        /// </summary>
        /// <remarks>
        /// If this event is cancelled, focus will remain on the cell editor.
        /// </remarks>
        [Category("Behavior")]
        public event CellEditEventHandler CellEditValidating;

        /// <summary>
        /// Triggered when a cell is about to finish being edited.
        /// </summary>
        /// <remarks>If Cancel is already true, the user is cancelling the edit operation.
        /// Set Cancel to true to prevent the value from the cell being written into the model.
        /// You cannot prevent the editing from finishing.</remarks>
        [Category("Behavior")]
        public event CellEditEventHandler CellEditFinishing;

        /// <summary>
        /// Some new objects are about to be added to an ObjectListView.
        /// </summary>
        [Category("Behavior")]
        public event ItemsAddingEventHandler ItemsAdding;

        /// <summary>
        /// The contents of the ObjectListView has changed.
        /// </summary>
        [Category("Behavior")]
        public event ItemsChangedEventHandler ItemsChanged;

        /// <summary>
        /// Some objects are about to be removed from an ObjectListView.
        /// </summary>
        [Category("Behavior")]
        public event ItemsRemovingEventHandler ItemsRemoving;

        /// <summary>
        /// The contents of the ObjectListView is about to change via a SetObjects call
        /// </summary>
        /// <remarks>
        /// <para>Set Cancelled to true to prevent the contents of the list changing. This does not work with virtual lists.</para>
        /// </remarks>
        [Category("Behavior")]
        public event ItemsChangingEventHandler ItemsChanging;

        #endregion

        //-----------------------------------------------------------------------------------
        #region OnEvents

        protected virtual void OnAfterSorting(AfterSortingEventArgs e)
        {
            if (this.AfterSorting != null)
                this.AfterSorting(this, e);
        }

        protected virtual void OnBeforeSorting(BeforeSortingEventArgs e)
        {
            if (this.BeforeSorting != null)
                this.BeforeSorting(this, e);
        }

        protected virtual void OnItemsAdding(ItemsAddingEventArgs e)
        {
            if (this.ItemsAdding != null)
                this.ItemsAdding(this, e);
        }

        protected virtual void OnItemsChanged(ItemsChangedEventArgs e)
        {
            if (this.ItemsChanged != null)
                this.ItemsChanged(this, e);
        }

        protected virtual void OnItemsChanging(ItemsChangingEventArgs e)
        {
            if (this.ItemsChanging != null)
                this.ItemsChanging(this, e);
        }

        protected virtual void OnItemsRemoving(ItemsRemovingEventArgs e)
        {
            if (this.ItemsRemoving != null)
                this.ItemsRemoving(this, e);
        }

        /// <summary>
        /// Tell the world when a cell is about to be edited.
        /// </summary>
        protected virtual void OnCellEditStarting(CellEditEventArgs e)
        {
            if (this.CellEditStarting != null)
                this.CellEditStarting(this, e);
        }

        /// <summary>
        /// Tell the world when a cell is about to finish being edited.
        /// </summary>
        protected virtual void OnCellEditorValidating(CellEditEventArgs e)
        {
            // Hack. ListView is an imperfect control container. It does not manage validation
            // perfectly. If the ListView is part of a TabControl, and the cell editor loses
            // focus by the user clicking on another tab, the TabControl processes the click
            // and switches tabs, even if this Validating event cancels. This results in the
            // strange situation where the cell editor is active, but isn't visible. When the
            // user switches back to the tab with the ListView, composite controls like spin
            // controls, DateTimePicker and ComboBoxes do not work properly. Specifically,
            // keyboard input still works fine, but the controls do not respond to mouse
            // input. SO, if the validation fails, we have to specifically give focus back to
            // the cell editor. (this is the Select() call in the code below). 
            // But (there is always a 'but'), doing that changes the focus so the cell editor
            // triggers another Validating event -- which fails again. From the user's point
            // of view, they click away from the cell editor, and the validating code
            // complains twice. So we only trigger a Validating event if more than 0.1 seconds
            // has elapsed since the last validate event.
            // I know it's a hack. I'm very open to hear a neater solution.

            // Also, this timed response stops us from sending a series of validation events
            // if the user clicks and holds on the OLV scroll bar.
            if ((Environment.TickCount - lastValidatingEvent) < 500) {
                e.Cancel = true;
            } else {
                lastValidatingEvent = Environment.TickCount;
                if (this.CellEditValidating != null)
                    this.CellEditValidating(this, e);
            }
            lastValidatingEvent = Environment.TickCount;
        }
        private int lastValidatingEvent = 0;

        /// <summary>
        /// Tell the world when a cell is about to finish being edited.
        /// </summary>
        protected virtual void OnCellEditFinishing(CellEditEventArgs e)
        {
            if (this.CellEditFinishing != null)
                this.CellEditFinishing(this, e);
        }

        #endregion

        //-----------------------------------------------------------------------------------
        #region Event Parameter Blocks

        /// <summary>
        /// Let the world know that a cell edit operation is beginning or ending
        /// </summary>
        public class CellEditEventArgs : EventArgs
        {
            /// <summary>
            /// Create an event args
            /// </summary>
            /// <param name="column"></param>
            /// <param name="c"></param>
            /// <param name="r"></param>
            /// <param name="item"></param>
            /// <param name="subItemIndex"></param>
            public CellEditEventArgs(OLVColumn column, Control c, Rectangle r, OLVListItem item, int subItemIndex)
            {
                this.Cancel = false;
                this.Control = c;
                this.column = column;
                this.cellBounds = r;
                this.listViewItem = item;
                this.rowObject = item.RowObject;
                this.subItemIndex = subItemIndex;
                this.value = column.GetValue(item.RowObject);
            }

            /// <summary>
            /// Change this to true to cancel the cell editing operation.
            /// </summary>
            /// <remarks>
            /// <para>During the CellEditStarting event, setting this to true will prevent the cell from being edited.</para>
            /// <para>During the CellEditFinishing event, if this value is already true, this indicates that the user has
            /// cancelled the edit operation and that the handler should perform cleanup only. Setting this to true,
            /// will prevent the ObjectListView from trying to write the new value into the model object.</para>
            /// </remarks>
            public bool Cancel = false;

            /// <summary>
            /// During the CellEditStarting event, this can be modified to be the control that you want
            /// to edit the value. You must fully configure the control before returning from the event,
            /// including its bounds and the value it is showing.
            /// During the CellEditFinishing event, you can use this to get the value that the user
            /// entered and commit that value to the model. Changing the control during the finishing
            /// event has no effect.
            /// </summary>
            public Control Control = null;

            /// <summary>
            /// The column of the cell that is going to be or has been edited.
            /// </summary>
            public OLVColumn Column
            {
                get { return this.column; }
            }
            private OLVColumn column;

            /// <summary>
            /// The model object of the row of the cell that is going to be or has been edited.
            /// </summary>
            public Object RowObject
            {
                get { return this.rowObject; }
            }
            private Object rowObject;

            /// <summary>
            /// The listview item of the cell that is going to be or has been edited.
            /// </summary>
            public OLVListItem ListViewItem
            {
                get { return this.listViewItem; }
            }
            private OLVListItem listViewItem;

            /// <summary>
            /// The index of the cell that is going to be or has been edited.
            /// </summary>
            public int SubItemIndex
            {
                get { return this.subItemIndex; }
            }
            private int subItemIndex;

            /// <summary>
            /// The data value of the cell before the edit operation began.
            /// </summary>
            public Object Value
            {
                get { return this.value; }
            }
            private Object value;

            /// <summary>
            /// The bounds of the cell that is going to be or has been edited.
            /// </summary>
            public Rectangle CellBounds
            {
                get { return this.cellBounds; }
            }
            private Rectangle cellBounds;
        }

        public class CancellableEvent : EventArgs
        {
            /// <summary>
            /// Has this event been cancelled by the event handler?
            /// </summary>
            public bool Cancelled;
        }

        public class BeforeSortingEventArgs : CancellableEvent
        {
            public BeforeSortingEventArgs(OLVColumn column, SortOrder order)
            {
                this.ColumnToSort = column;
                this.SortOrder = order;
            }

            public OLVColumn ColumnToSort;
            public SortOrder SortOrder;
        }

        public class AfterSortingEventArgs : EventArgs
        {
            public AfterSortingEventArgs(OLVColumn column, SortOrder order)
            {
                this.ColumnToSort = column;
                this.SortOrder = order;
            }

            public readonly OLVColumn ColumnToSort;
            public readonly SortOrder SortOrder;
        }

        /// <summary>
        /// This event is triggered after the items in the list have been changed,
        /// either through SetObjects, AddObjects or RemoveObjects.
        /// </summary>
        public class ItemsChangedEventArgs : EventArgs
        {
            public ItemsChangedEventArgs()
            {
            }

            /// <summary>
            /// Constructor for this event when used by a virtual list
            /// </summary>
            /// <param name="oldObjectCount"></param>
            /// <param name="newObjectCount"></param>
            public ItemsChangedEventArgs(int oldObjectCount, int newObjectCount)
            {
                this.OldObjectCount = oldObjectCount;
                this.NewObjectCount = newObjectCount;
            }

            public readonly int OldObjectCount;
            public readonly int NewObjectCount;          
        }

        /// <summary>
        /// This event is triggered by AddObjects before any change has been made to the list.
        /// </summary>
        public class ItemsAddingEventArgs : CancellableEvent
        {
            public ItemsAddingEventArgs(ICollection objectsToAdd)
            {
                this.ObjectsToAdd = objectsToAdd;
            }

            public ICollection ObjectsToAdd;
        }

        /// <summary>
        /// This event is triggered by SetObjects before any change has been made to the list.
        /// </summary>
        /// <remarks>
        /// When used with a virtual list, OldObjects will always be null.
        /// </remarks>
        public class ItemsChangingEventArgs : CancellableEvent
        {
            public ItemsChangingEventArgs(IEnumerable oldObjects, IEnumerable newObjects)
            {
                this.OldObjects = oldObjects;
                this.NewObjects = newObjects;
            }

            public readonly IEnumerable OldObjects;
            public IEnumerable NewObjects;
        }

        /// <summary>
        /// This event is triggered by RemoveObjects before any change has been made to the list.
        /// </summary>
        public class ItemsRemovingEventArgs : CancellableEvent
        {
            public ItemsRemovingEventArgs(ICollection objectsToRemove)
            {
                this.ObjectsToRemove = objectsToRemove;
            }

            public ICollection ObjectsToRemove;
        }

        #endregion

    }

}
