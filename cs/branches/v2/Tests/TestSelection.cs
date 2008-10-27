/*
 * [File purpose]
 * Author: Phillip Piper
 * Date: 10/25/2008 11:06 PM
 * 
 * CHANGE LOG:
 * when who what
 * 10/25/2008 JPP  Initial Version
 */

using System;
using System.Windows.Forms;
using NUnit.Framework;
using NUnit.Framework.SyntaxHelpers;

namespace BrightIdeasSoftware.Tests
{
    [TestFixture]
    public class TestOlvSelection
    {
        [Test]
        public void TestSelectedObject()
        {
            this.olv.SetObjects(PersonDb.All);
            this.olv.SelectedObject = null;
            Assert.IsNull(this.olv.SelectedObject);
            this.olv.SelectedObject = PersonDb.All[1];
            Assert.AreEqual(PersonDb.All[1], this.olv.SelectedObject);
        }

        [Test]
        public void TestSelectedObjects()
        {
            this.olv.SetObjects(PersonDb.All);
            this.olv.SelectedObjects = null;
            Assert.IsEmpty(this.olv.SelectedObjects);
            this.olv.SelectedObjects = PersonDb.All;
            Assert.AreEqual(PersonDb.All, this.olv.SelectedObjects);
        }

        [Test]
        public void TestSelectionEvents()
        {
            this.olv.SetObjects(PersonDb.All);
            countSelectedIndexChanged = 0;
            countSelectionChanged = 0;
            this.olv.SelectedIndexChanged += new EventHandler(olv_SelectedIndexChanged);
            this.olv.SelectionChanged += new EventHandler(olv_SelectionChanged);
            this.olv.SelectedObjects = PersonDb.All;
            this.olv.SelectedObjects = null;

            // Force an idle cycle so the selection changed event is processed
            Application.RaiseIdle(new EventArgs());

            // We should get two selectedIndex event for each object, but only one selection changed
            Assert.AreEqual(PersonDb.All.Count * 2, countSelectedIndexChanged);
            Assert.AreEqual(1, countSelectionChanged);

            // Cleanup
            this.olv.SelectedIndexChanged -= new EventHandler(olv_SelectedIndexChanged);
            this.olv.SelectionChanged -= new EventHandler(olv_SelectionChanged);
        }

        void olv_SelectedIndexChanged(object sender, EventArgs e)
        {
            countSelectedIndexChanged++;
        }
        int countSelectedIndexChanged;

        void olv_SelectionChanged(object sender, EventArgs e)
        {
            countSelectionChanged++;
        }
        int countSelectionChanged;

        [TestFixtureSetUp]
        virtual public void Init()
        {
            this.olv = MyGlobals.mainForm.objectListView1;
        }
        protected ObjectListView olv;
    }

    [TestFixture]
    public class TestFastOlvSelection : TestOlvSelection
    {
        [TestFixtureSetUp]
        override public void Init()
        {
            this.olv = MyGlobals.mainForm.fastObjectListView1;
        }
    }

    [TestFixture]
    public class TestTreeListViewSelection : TestOlvSelection
    {
        [TestFixtureSetUp]
        override public void Init()
        {
            this.olv = MyGlobals.mainForm.treeListView1;
        }
    }
}
