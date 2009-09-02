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
using System.Drawing;
using System.Windows.Forms;
using NUnit.Framework;
using NUnit.Framework.SyntaxHelpers;

namespace BrightIdeasSoftware.Tests
{
    [TestFixture]
    public class TestOlvFormatting
    {
        [SetUp]
        public void InitEachTest() {
            this.olv.UseAlternatingBackColors = false;
            this.olv.RowFormatter = null;
            this.olv.HyperlinkStyle = null;
            foreach (OLVColumn column in this.olv.Columns)
                column.Hyperlink = false;
        }

        [Test]
        public void TestNoFormatting() {
            this.olv.HyperlinkStyle = null;
            this.olv.SetObjects(PersonDb.All);
            for (int i = 0; i < this.olv.GetItemCount(); i++) {
                Assert.AreEqual(this.olv.ForeColor, this.olv.GetItem(i).ForeColor);
                Assert.AreEqual(this.olv.BackColor, this.olv.GetItem(i).BackColor);
            }
        }

        [Test]
        public void TestAlternateBackColors() {
            this.olv.UseAlternatingBackColors = true;
            this.olv.AlternateRowBackColor = Color.Pink;

            this.olv.SetObjects(PersonDb.All);
            for (int i = 0; i < this.olv.GetItemCount(); i++) {
                if ((i % 2) == 0)
                    Assert.AreEqual(this.olv.BackColor, this.olv.GetItem(i).BackColor);
                else
                    Assert.AreEqual(this.olv.AlternateRowBackColor, this.olv.GetItem(i).BackColor);
            }
        }

        [Test]
        public void TestRowFormatter() {
            Color testForeColor = Color.Yellow;
            Color testBackColor = Color.Violet;

            this.olv.RowFormatter = delegate(OLVListItem olvi) {
                olvi.ForeColor = testForeColor;
                olvi.BackColor = testBackColor;
            };
            this.olv.SetObjects(PersonDb.All);
            for (int i = 0; i < this.olv.GetItemCount(); i++) {
                Assert.AreEqual(testForeColor, this.olv.GetItem(i).ForeColor);
                Assert.AreEqual(testBackColor, this.olv.GetItem(i).BackColor);
            }
        }

        [Test]
        public void TestFormatRowEvent() {
            this.olv.FormatRow += new EventHandler<FormatRowEventArgs>(olv_FormatRow1);
            this.olv.SetObjects(PersonDb.All);
            for (int i = 0; i < this.olv.GetItemCount(); i++) {
                Assert.AreEqual(this.testForeColor, this.olv.GetItem(i).ForeColor);
                Assert.AreEqual(this.testBackColor, this.olv.GetItem(i).BackColor);
            }
            this.olv.FormatRow -= new EventHandler<FormatRowEventArgs>(olv_FormatRow1);
        }
        Color testForeColor = Color.Yellow;
        Color testBackColor = Color.Violet;

        void olv_FormatRow1(object sender, FormatRowEventArgs e) {
            e.Item.ForeColor = this.testForeColor;
            e.Item.BackColor = this.testBackColor;
        }

        [Test]
        public void TestFormatCellEvent() {
            this.olv.FormatRow += new EventHandler<FormatRowEventArgs>(olv_FormatRow2);
            this.olv.FormatCell += new EventHandler<FormatCellEventArgs>(olv_FormatCell);
            this.olv.SetObjects(PersonDb.All);
            for (int i = 0; i < this.olv.GetItemCount(); i++) {
                if (i % 2 == 0) {
                    Assert.IsFalse(this.olv.GetItem(i).UseItemStyleForSubItems);
                    for (int j = 0; j < this.olv.Columns.Count; j++) {
                        Assert.AreEqual(this.testCellForeColor, this.olv.GetItem(i).SubItems[j].ForeColor);
                        Assert.AreEqual(this.testCellBackColor, this.olv.GetItem(i).SubItems[j].BackColor);
                    }
                } else {
                    Assert.IsTrue(this.olv.GetItem(i).UseItemStyleForSubItems);
                    Assert.AreEqual(this.olv.ForeColor, this.olv.GetItem(i).ForeColor);
                    Assert.AreEqual(this.olv.BackColor, this.olv.GetItem(i).BackColor);
                }
            }
            this.olv.FormatRow -= new EventHandler<FormatRowEventArgs>(olv_FormatRow2);
            this.olv.FormatCell -= new EventHandler<FormatCellEventArgs>(olv_FormatCell);
        }
        Color testCellForeColor = Color.Aquamarine;
        Color testCellBackColor = Color.BlanchedAlmond;

        void olv_FormatCell(object sender, FormatCellEventArgs e) {
            e.SubItem.ForeColor = this.testCellForeColor;
            e.SubItem.BackColor = this.testCellBackColor;
        }

        void olv_FormatRow2(object sender, FormatRowEventArgs e) {
            e.UseCellFormatEvents = (e.RowIndex % 2 == 0);
        }

        [Test]
        public void TestHyperlinks() {
            this.olv.HyperlinkStyle = new HyperlinkStyle();
            this.olv.HyperlinkStyle.Normal.ForeColor = Color.Thistle;
            this.olv.HyperlinkStyle.Normal.BackColor = Color.SpringGreen;
            this.olv.HyperlinkStyle.Normal.FontStyle = FontStyle.Bold;

            foreach (OLVColumn column in this.olv.Columns) {
                column.Hyperlink = (column.Index < 2);
            }

            this.olv.SetObjects(PersonDb.All);
            for (int j = 0; j < this.olv.GetItemCount(); j++) {
                OLVListItem item = this.olv.GetItem(j);
                Assert.IsFalse(item.UseItemStyleForSubItems);
                for (int i = 0; i < this.olv.Columns.Count; i++) {
                    OLVColumn column = this.olv.GetColumn(i);
                    if (column.Hyperlink) {
                        Assert.AreEqual(this.olv.HyperlinkStyle.Normal.ForeColor, item.SubItems[i].ForeColor);
                        Assert.AreEqual(this.olv.HyperlinkStyle.Normal.BackColor, item.SubItems[i].BackColor);
                        Assert.IsTrue(item.SubItems[i].Font.Bold);
                    } else {
                        Assert.AreEqual(this.olv.ForeColor, item.SubItems[i].ForeColor);
                        Assert.AreEqual(this.olv.BackColor, item.SubItems[i].BackColor);
                        Assert.IsFalse(item.SubItems[i].Font.Bold);
                    }
                }
            }
        }

        [TestFixtureSetUp]
        public void Init() {
            this.olv = MyGlobals.mainForm.objectListView1;
        }
        protected ObjectListView olv;
    }

    [TestFixture]
    public class TestFastOlvFormatting : TestOlvFormatting
    {
        [TestFixtureSetUp]
        new public void Init() {
            this.olv = MyGlobals.mainForm.fastObjectListView1;
        }
    }

    [TestFixture]
    public class TestTreeListViewFormatting : TestOlvFormatting
    {
        [TestFixtureSetUp]
        new public void Init() {
            this.olv = MyGlobals.mainForm.treeListView1;
        }
    }
}