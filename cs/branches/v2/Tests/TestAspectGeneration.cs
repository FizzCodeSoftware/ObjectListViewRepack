/*
 * [File purpose]
 * Author: Phillip Piper
 * Date: 10/21/2008 11:04 PM
 * 
 * CHANGE LOG:
 * when who what
 * 10/21/2008 JPP  Initial Version
 */

using System;
using NUnit.Framework;
using NUnit.Framework.SyntaxHelpers;

namespace BrightIdeasSoftware.Tests
{
	[TestFixture]
	public class TestAspectGeneration
	{
        [Test]
        public void TestMethod()
        {
            OLVColumn column = new OLVColumn();
            column.AspectName = "Photo";
            Assert.AreEqual(column.GetValue(this.person1), "photo");

            TypedColumn<Person> tcolumn = new TypedColumn<Person>(column);
            Assert.IsNull(column.AspectGetter);
            tcolumn.GenerateAspectGetter();
            Assert.IsNotNull(column.AspectGetter);
            Assert.AreEqual(column.GetValue(this.person1), "photo");
        }

        [Test]
        public void TestMethod2()
        {
            OLVColumn column = new OLVColumn();
            column.AspectName = "Photo.Length";
            Assert.AreEqual(column.GetValue(this.person1), 5);

            TypedColumn<Person> tcolumn = new TypedColumn<Person>(column);
            Assert.IsNull(column.AspectGetter);
            tcolumn.GenerateAspectGetter();
            Assert.IsNotNull(column.AspectGetter);
            Assert.AreEqual(column.GetValue(this.person1), 5);
        }
		
		[TestFixtureSetUp]
		public void Init()
		{
			this.person1 = new Person("name", "occupation", 100, DateTime.Now, 1.0, true, "photo", "comments");
		}
		
		Person person1;
	}
}
