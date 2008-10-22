/*
 * TypedObjectListView - A wrapper around an ObjectListView that provides type-safe delegates.
 *
 * Author: Phillip Piper
 * Date: 27/09/2008 9:15 AM
 *
 * Change log:
 * 2008-10-21   JPP  - Generate dynamic methods
 * 2008-09-27   JPP  - Separated from ObjectListView.cs
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
using System.Collections.Generic;
using System.Text;
using System.Windows.Forms;
using System.Reflection;
using System.Reflection.Emit;

namespace BrightIdeasSoftware
{
    /// <summary>
    /// A TypedObjectListView is a type-safe wrapper around an ObjectListView.
    /// </summary>
    /// <remarks>
    /// <para>VCS does not support generics on controls. It can be faked to some degree, but it
    /// cannot be completely overcome. In our case in particular, there is no way to create
    /// the custom OLVColumn's that we need to truly be generic. So this wrapper is an 
    /// experiment in providing some type-safe access in a way that is useful and available today.</para>
    /// <para>A TypedObjectListView is not more efficient than a normal ObjectListView.
    /// Underneath, the same name of casts are performed. But it is easier to use since you
    /// do not have to write the casts yourself.
    /// </para>
    /// </remarks>
    /// <typeparam name="T">The class of model object that the list will manage</typeparam>
    /// <example>
    /// To use a TypedObjectListView, you write code like this:
    /// <code>
    /// TypedObjectListView<Person> tlist = new TypedObjectListView<Person>(this.listView1);
    /// tlist.CheckStateGetter = delegate(Person x) { return x.IsActive; };
    /// tlist.GetColumn(0).AspectGetter = delegate(Person x) { return x.Name; };
    /// ...
    /// </code>
    /// To iterate over the selected objects, you can write something elegant like this:
    /// <code>
    /// foreach (Person x in tlist.SelectedObjects {
    ///     x.GrantSalaryIncrease();
    /// }
    /// </code>
    /// </example>
    public class TypedObjectListView<T> where T : class
    {
        /// <summary>
        /// Create a typed wrapper around the given list.
        /// </summary>
        /// <param name="olv">The listview to be wrapped</param>
        public TypedObjectListView(ObjectListView olv)
        {
            this.olv = olv;
        }

        //--------------------------------------------------------------------------------------
        // Properties

        /// <summary>
        /// Return the model object that is checked, if only one row is checked.
        /// If zero rows are checked, or more than one row, null is returned.
        /// </summary>
        public T CheckedObject
        {
            get { return (T)this.olv.CheckedObject; }
        }

        /// <summary>
        /// Return the list of all the checked model objects
        /// </summary>
        public IList<T> CheckedObjects
        {
            get
            {
                IList checkedObjects = this.olv.CheckedObjects;
                List<T> objects = new List<T>(checkedObjects.Count);
                foreach (object x in checkedObjects)
                    objects.Add((T)x);

                return objects;
            }
            set { this.olv.CheckedObjects = (IList)value; }
        }

        /// <summary>
        /// The ObjectListView that is being wrapped
        /// </summary>
        public ObjectListView ListView
        {
            get { return olv; }
            set { olv = value; }
        }
        private ObjectListView olv;

        /// <summary>
        /// Return the model object that is selected, if only one row is selected.
        /// If zero rows are selected, or more than one row, null is returned.
        /// </summary>
        public T SelectedObject
        {
            get { return (T)this.olv.GetSelectedObject(); }
            set { this.olv.SelectObject(value, true); }
        }

        /// <summary>
        /// The list of model objects that are selected.
        /// </summary>
        public IList<T> SelectedObjects
        {
            get
            {
                List<T> objects = new List<T>(this.olv.SelectedIndices.Count);
                foreach (int index in this.olv.SelectedIndices)
                    objects.Add((T)this.olv.GetModelObject(index));

                return objects;
            }
            set { this.olv.SelectObjects((IList)value); }
        }

        //--------------------------------------------------------------------------------------
        // Accessors

        /// <summary>
        /// Return a typed wrapper around the column at the given index
        /// </summary>
        /// <param name="i">The index of the column</param>
        /// <returns>A typed column or null</returns>
        public TypedColumn<T> GetColumn(int i)
        {
            return new TypedColumn<T>(this.olv.GetColumn(i));
        }

        /// <summary>
        /// Return a typed wrapper around the column with the given name
        /// </summary>
        /// <param name="i">The name of the column</param>
        /// <returns>A typed column or null</returns>
        public TypedColumn<T> GetColumn(string name)
        {
            return new TypedColumn<T>(this.olv.GetColumn(name));
        }

        /// <summary>
        /// Return the model object at the given index
        /// </summary>
        /// <param name="index">The index of the model object</param>
        /// <returns>The model object or null</returns>
        public T GetModelObject(int index)
        {
            return (T)this.olv.GetModelObject(index);
        }

        //--------------------------------------------------------------------------------------
        // Delegates

        public delegate bool? TypedCheckStateGetterDelegate(T rowObject);

        public TypedCheckStateGetterDelegate CheckStateGetter
        {
            get { return checkStateGetter; }
            set
            {
                this.checkStateGetter = value;
                if (value == null)
                    this.olv.CheckStateGetter = null;
                else
                    this.olv.CheckStateGetter = delegate(object x) {
                        return this.checkStateGetter((T)x);
                    };
            }
        }
        private TypedCheckStateGetterDelegate checkStateGetter;

        public delegate void TypedCheckStatePutterDelegate(T rowObject, CheckState newValue);

        public TypedCheckStatePutterDelegate CheckStatePutter
        {
            get { return checkStatePutter; }
            set
            {
                this.checkStatePutter = value;
                if (value == null)
                    this.olv.CheckStatePutter = null;
                else
                    this.olv.CheckStatePutter = delegate(object x, CheckState newValue) {
                        this.checkStatePutter((T)x, newValue);
                    };
            }
        }
        private TypedCheckStatePutterDelegate checkStatePutter;

        //--------------------------------------------------------------------------------------
        // Commands

        /// <summary>
        /// This method will generate AspectGetters for any column that has an AspectName.
        /// </summary>
        public void GenerateAspectGetters()
        {
            for (int i = 0; i < this.ListView.Columns.Count; i++)
                this.GetColumn(i).GenerateAspectGetter();
        }
    }

    /// <summary>
    /// A type-safe wrapper around an OLVColumn
    /// </summary>
    /// <typeparam name="T"></typeparam>
    public class TypedColumn<T> where T : class
    {
        public TypedColumn(OLVColumn column)
        {
            this.column = column;
        }
        private OLVColumn column;

        public delegate Object TypedAspectGetterDelegate(T rowObject);
        public delegate void TypedAspectPutterDelegate(T rowObject, Object newValue);
        public delegate Object TypedGroupKeyGetterDelegate(T rowObject);
        public delegate Object TypedImageGetterDelegate(T rowObject);

        public TypedAspectGetterDelegate AspectGetter
        {
            get { return this.aspectGetter; }
            set
            {
                this.aspectGetter = value;
                if (value == null)
                    this.column.AspectGetter = null;
                else
                    this.column.AspectGetter = delegate(object x) {
                        return this.aspectGetter((T)x);
                    };
            }
        }
        private TypedAspectGetterDelegate aspectGetter;

        public TypedAspectPutterDelegate AspectPutter
        {
            get { return aspectPutter; }
            set
            {
                this.aspectPutter = value;
                if (value == null)
                    this.column.AspectPutter = null;
                else
                    this.column.AspectPutter = delegate(object x, object newValue) {
                        this.aspectPutter((T)x, newValue);
                    };
            }
        }
        private TypedAspectPutterDelegate aspectPutter;

        public TypedImageGetterDelegate ImageGetter
        {
            get { return imageGetter; }
            set
            {
                this.imageGetter = value;
                if (value == null)
                    this.column.ImageGetter = null;
                else
                    this.column.ImageGetter = delegate(object x) {
                        return this.imageGetter((T)x);
                    };
            }
        }
        private TypedImageGetterDelegate imageGetter;

        public TypedGroupKeyGetterDelegate GroupKeyGetter
        {
            get { return groupKeyGetter; }
            set
            {
                this.groupKeyGetter = value;
                if (value == null)
                    this.column.GroupKeyGetter = null;
                else
                    this.column.GroupKeyGetter = delegate(object x) {
                        return this.groupKeyGetter((T)x);
                    };
            }
        }
        private TypedGroupKeyGetterDelegate groupKeyGetter;

        #region Dynamic methods

        /// <summary>
        /// Generate an aspect getter that does the same thing as the AspectName,
        /// except without using reflection.
        /// </summary>
        /// <remarks>
        /// <para>
        /// If you have an AspectName of "Owner.Address.Postcode", this will generate
        /// the equivilent of: <code>this.AspectGetter = delegate (object x) {
        ///     return x.Owner.Address.Postcode;
        /// }
        /// </code>
        /// </para>
        /// <para>
        /// If AspectName is empty, this method will do nothing, otherwise 
        /// this will replace any existing AspectGetter.
        /// </para>
        /// </remarks>
        public void GenerateAspectGetter()
        {
            if (!String.IsNullOrEmpty(this.column.AspectName))
                this.AspectGetter = this.GenerateAspectGetter(typeof(T), this.column.AspectName);
        }

        public int GenerateAspectGetter2(Type t)
        {
            return t.Name.Length;
        }

        private TypedAspectGetterDelegate GenerateAspectGetter(Type type, string path)
        {
            DynamicMethod accessor = new DynamicMethod(String.Empty,
                typeof(Object), new Type[] { typeof(T) }, typeof(TypedColumn<T>), true);
            ILGenerator il = accessor.GetILGenerator();
            il.Emit(OpCodes.Ldarg_0);

            foreach (string pathPart in path.Split('.')) {
                type = this.GeneratePart(il, type, pathPart);
                if (type == null)
                    break;
            }

            if (type != null && type.IsValueType && !typeof(T).IsValueType)
                il.Emit(OpCodes.Box, type);

            il.Emit(OpCodes.Ret);

            return (TypedAspectGetterDelegate)accessor.CreateDelegate(typeof(TypedAspectGetterDelegate));
        }

        private Type GeneratePart(ILGenerator il, Type type, string pathPart)
        {
        	BindingFlags flags = BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance |
                BindingFlags.InvokeMethod | BindingFlags.GetProperty | BindingFlags.GetField;

            MethodInfo methodInfo = type.GetMethod(pathPart);
            if (methodInfo != null) {
                il.Emit(OpCodes.Callvirt, methodInfo);
                return methodInfo.ReturnType;
            }

            PropertyInfo propInfo = type.GetProperty(pathPart);
            if (propInfo != null) {
                il.Emit(OpCodes.Callvirt, propInfo.GetGetMethod());
                return propInfo.PropertyType;
            }

            FieldInfo fieldInfo = type.GetField(pathPart, flags);
            if (fieldInfo != null) {
                il.Emit(OpCodes.Ldfld, fieldInfo);
                return fieldInfo.FieldType;
            }

            il.Emit(OpCodes.Ldstr, String.Format(
                "No method, property or field '{0}' found for type '{1}'",
                pathPart, type.FullName));
            return null;
        }

        //private static Type GeneratePathIL(Type type, ILGenerator il, string[] path)
        //{
        //    foreach (string fieldOrProperty in path) {
        //        PropertyInfo property = type.GetProperty(fieldOrProperty);
                
        //        if (property != null) {
        //            il.Emit(OpCodes.Callvirt, property.GetGetMethod());
        //            type = property.PropertyType;
        //        } else {
        //            FieldInfo field = type.GetField(fieldOrProperty);

        //            if (field != null) {
        //                il.Emit(OpCodes.Ldfld, field);
        //                type = field.FieldType;
        //            } else {
        //                throw new InvalidOperationException(string.Format(
        //                    "No field or property {0} found for type {1}",
        //                    fieldOrProperty, type.FullName));
        //            }
        //        }
        //    }

        //    return type;
        //}

        #endregion
    }
}
