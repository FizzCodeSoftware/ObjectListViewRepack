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
    public class TestOlvBasics
    {
        [Test]
        public void TestSetObjects()
        {
            this.olv.SetObjects(PersonDb.All);
            Assert.AreEqual(PersonDb.All.Count, this.olv.GetItemCount());
            this.olv.SetObjects(null);
            Assert.AreEqual(0, this.olv.GetItemCount());
        }

        [TestFixtureSetUp]
        virtual public void Init()
        {
            this.olv = MyGlobals.mainForm.objectListView1;
        }
        protected ObjectListView olv;
    }

    [TestFixture]
    public class TestFastOlvBasics : TestOlvBasics
    {
        [TestFixtureSetUp]
        override public void Init()
        {
            this.olv = MyGlobals.mainForm.fastObjectListView1;
        }
    }

    [TestFixture]
    public class TestTreeListViewBasics : TestOlvBasics
    {
        [TestFixtureSetUp]
        override public void Init()
        {
            this.olv = MyGlobals.mainForm.treeListView1;
        }
    }
}
