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
        public void ExecuteAspect(string aspectName, object expectedResult, Person person)
        {
            OLVColumn column = new OLVColumn();
            column.AspectName = aspectName;
            Assert.AreEqual(expectedResult, column.GetValue(person));

            TypedColumn<Person> tcolumn = new TypedColumn<Person>(column);
            Assert.IsNull(column.AspectGetter);
            tcolumn.GenerateAspectGetter();
            Assert.IsNotNull(column.AspectGetter);
            Assert.AreEqual(expectedResult, column.GetValue(person));
        }

        public void ExecuteAspect(string aspectName, object expectedResult)
        {
            this.ExecuteAspect(aspectName, expectedResult, this.person1);
        }

        public void ExecuteAspect2(string aspectName, object expectedResult)
        {
            this.ExecuteAspect(aspectName, expectedResult, this.person2);
        }

        [Test]
        public void TestSimpleField()
        {
            this.ExecuteAspect("Comments", "comments");
        }

        [Test]
        public void TestSimpleProperty()
        {
            this.ExecuteAspect("Occupation", "occupation");
        }

        [Test]
        public void TestSimpleMethod()
        {
            this.ExecuteAspect("GetRate", 1.0);
        }

        [Test]
        public void TestChainedField()
        {
            this.ExecuteAspect("Comments.ToUpper", "COMMENTS");
        }

        [Test]
        public void TestReturningValueType()
        {
            this.ExecuteAspect("CulinaryRating.ToString.Length", 3);
        }

        [Test]
        public void TestReturningValueType2()
        {
            this.ExecuteAspect("BirthDate.Year", this.person1.BirthDate.Year);
        }

        [Test]
        public void TestChainingValueTypes()
        {
            this.ExecuteAspect("BirthDate.Year.ToString.Length", 4);
        }

        [Test]
        public void TestChainedMethod()
        {
            this.ExecuteAspect("Photo.ToString.Trim", "photo");
        }

        [Test]
        public void TestVirtualMethod()
        {
            this.ExecuteAspect2("GetRate", 2.0);
        }

        [Test]
        public void TestOverriddenProperty()
        {
            OLVColumn column = new OLVColumn();
            column.AspectName = "CulinaryRating";
            Assert.AreEqual(200, column.GetValue(this.person2));

            TypedColumn<Person2> tcolumn = new TypedColumn<Person2>(column);
            Assert.IsNull(column.AspectGetter);
            tcolumn.GenerateAspectGetter();
            Assert.IsNotNull(column.AspectGetter);
            Assert.AreEqual(200, column.GetValue(this.person2));
        }

        [Test]
        public void TestWrongName()
        {
            OLVColumn column = new OLVColumn();
            column.AspectName = "Photo.Unknown";

            TypedColumn<Person> tcolumn = new TypedColumn<Person>(column);
            tcolumn.GenerateAspectGetter();
            Assert.AreEqual("'Unknown' is not a parameter-less method, property or field of type 'System.String'", column.GetValue(this.person1));
        }		
        
		[TestFixtureSetUp]
		public void Init()
		{
            this.person1 = new Person("name", "occupation", 100, DateTime.Now, 1.0, true, "  photo  ", "comments");
            this.person2 = new Person2("name", "occupation", 100, DateTime.Now, 1.0, true, "  photo  ", "comments");
		}

        Person person1;
        Person2 person2;
	}
}
