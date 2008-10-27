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
    public class TestOlvCheckBoxes
    {
        [Test]
        public void TestCheckedObject()
        {
            this.olv.SetObjects(PersonDb.All);
            this.olv.CheckedObject = PersonDb.All[1];
            Assert.AreEqual(PersonDb.All[1], this.olv.CheckedObject);
        }
        
        [Test]
        public void TestCheckedObjects()
        {
            this.olv.SetObjects(PersonDb.All);
            this.olv.CheckedObjects = null;
            Assert.IsEmpty(this.olv.CheckedObjects);
            this.olv.CheckedObjects = PersonDb.All;
            Assert.AreEqual(PersonDb.All, this.olv.CheckedObjects);
        }

        [Test]
        public void TestCheckStateGetter()
        {
            // TODO
        }

        [Test]
        public void TestCheckStatePutter()
        {
            // TODO
        }

        [TestFixtureSetUp]
        virtual public void Init()
        {
            this.olv = MyGlobals.mainForm.objectListView1;
        }
        protected ObjectListView olv;
    }

    [TestFixture]
    public class TestFastOlvCheckBoxes : TestOlvCheckBoxes
    {
        [TestFixtureSetUp]
        override public void Init()
        {
            this.olv = MyGlobals.mainForm.fastObjectListView1;
        }
    }

    [TestFixture]
    public class TestTreeListViewCheckBoxes : TestOlvCheckBoxes
    {
        [TestFixtureSetUp]
        override public void Init()
        {
            this.olv = MyGlobals.mainForm.treeListView1;
        }
    }
}
