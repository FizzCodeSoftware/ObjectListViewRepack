/*
 * DesignSupport - Design time support for the various classes within ObjectListView
 *
 * Author: Phillip Piper
 * Date: 12/08/2009 8:36 PM
 *
 * Change log:
 * 2009-08-12   JPP  - Initial version
 *
 * To do:
 *
 * Copyright (C) 2009 Phillip Piper
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
using System.ComponentModel;
using System.Collections;
using System.Collections.Generic;
using System.Windows.Forms;
using System.Windows.Forms.Design;

namespace BrightIdeasSoftware.Design
{
    internal class ObjectListViewDesigner : ControlDesigner
    {
        protected override void PreFilterProperties(IDictionary properties) {
            // Always call the base PreFilterProperties implementation 
            // before you modify the properties collection.
            base.PreFilterProperties(properties);

            // I'd like to just remove the redundant properties, but that would
            // break backward compatibility. The deserialiser that handles the XXX.Designer.cs file
            // works off the designer, so even if the property exists in the class, the deserialiser will
            // throw an error if the associated designer removes that property.
            // So we shadow the unwanted properties, and give the replacement properties
            // non-browsable attributes so that they are hidden from the user

            string[] unwantedProperties = new string[] { "BackgroundImage", "BackgroundImageTiled",
                "HotTracking", "HoverSelection", "LabelEdit", "VirtualListSize", "VirtualMode" };
            foreach (string unwantedProperty in unwantedProperties) {
                PropertyDescriptor propertyDesc = TypeDescriptor.CreateProperty(
                    typeof(ObjectListViewDesigner),
                    (PropertyDescriptor)properties[unwantedProperty],
                    new BrowsableAttribute(false));
                properties[unwantedProperty] = propertyDesc;
            }
        }
    }

    /// <summary>
    /// This class works in conjunction with the OLVColumns property to allow OLVColumns
    /// to be added to the ObjectListView.
    /// </summary>
    internal class OLVColumnCollectionEditor : System.ComponentModel.Design.CollectionEditor
    {
        public OLVColumnCollectionEditor(Type t)
            : base(t) {
        }

        protected override Type CreateCollectionItemType() {
            return typeof(OLVColumn);
        }

        public override object EditValue(ITypeDescriptorContext context, IServiceProvider provider, object value) {
            // Figure out which ObjectListView we are working on. This should be the Instance of the context.
            ObjectListView olv = null;
            if (context != null)
                olv = context.Instance as ObjectListView;

            if (olv == null) {
                //THINK: Can this ever happen?
                System.Diagnostics.Debug.WriteLine("context.Instance was NOT an ObjectListView");

                // Hack to figure out which ObjectListView we are working on
                ListView.ColumnHeaderCollection cols = (ListView.ColumnHeaderCollection)value;
                if (cols.Count == 0) {
                    cols.Add(new OLVColumn());
                    olv = (ObjectListView)cols[0].ListView;
                    cols.Clear();
                    olv.AllColumns.Clear();
                } else
                    olv = (ObjectListView)cols[0].ListView;
            }

            // Edit all the columns, not just the ones that are visible
            base.EditValue(context, provider, olv.AllColumns);

            // Calculate just the visible columns
            List<OLVColumn> newColumns = olv.GetFilteredColumns(View.Details);
            olv.Columns.Clear();
            olv.Columns.AddRange(newColumns.ToArray());

            return olv.Columns;
        }

        protected override string GetDisplayText(object value) {
            OLVColumn col = value as OLVColumn;
            if (col == null || String.IsNullOrEmpty(col.AspectName))
                return base.GetDisplayText(value);

            return base.GetDisplayText(value) + " (" + col.AspectName + ")";
        }
    }


    /// <summary>
    /// Control how the overlay is presented in the IDE
    /// </summary>
    internal class OverlayConverter : ExpandableObjectConverter
    {
        public override bool CanConvertTo(ITypeDescriptorContext context, Type destinationType) {
            if (destinationType == typeof(string))
                return true;
            else
                return base.CanConvertTo(context, destinationType);
        }

        public override object ConvertTo(ITypeDescriptorContext context, System.Globalization.CultureInfo culture, object value, Type destinationType) {
            if (destinationType == typeof(string)) {
                ImageOverlay imageOverlay = value as ImageOverlay;
                if (imageOverlay != null) {
                    if (imageOverlay.Image == null)
                        return "(none)";
                    else
                        return "(set)";
                }
                TextOverlay textOverlay = value as TextOverlay;
                if (textOverlay != null) {
                    if (String.IsNullOrEmpty(textOverlay.Text))
                        return "(none)";
                    else
                        return "(set)";
                }
            }

            return base.ConvertTo(context, culture, value, destinationType);
        }
    }
}
