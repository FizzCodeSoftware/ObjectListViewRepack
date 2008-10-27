/*
 * [File purpose]
 * Author: Phillip Piper
 * Date: 10/21/2008 11:09 PM
 * 
 * CHANGE LOG:
 * when who what
 * 10/21/2008 JPP  Initial Version
 */

using System;
using System.Collections.Generic;

namespace BrightIdeasSoftware.Tests
{
	/// <summary>
	/// Description of Person.
	/// </summary>

	public class Person
	{
        public bool? IsActive = null;

		public Person(string name)
		{
			this.name = name;
		}

		public Person(string name, string occupation, int culinaryRating, DateTime birthDate, double hourlyRate, bool canTellJokes, string photo, string comments)
		{
			this.name = name;
			this.Occupation = occupation;
			this.culinaryRating = culinaryRating;
			this.birthDate = birthDate;
			this.hourlyRate = hourlyRate;
            this.CanTellJokes = canTellJokes;
            this.Comments = comments;
            this.Photo = photo;
		}

        public Person(Person other)
        {
            this.name = other.Name;
            this.Occupation = other.Occupation;
            this.culinaryRating = other.CulinaryRating;
            this.birthDate = other.BirthDate;
            this.hourlyRate = other.GetRate();
            this.CanTellJokes = other.CanTellJokes;
            this.Photo = other.Photo;
            this.Comments = other.Comments;
        }

        // Allows tests for properties.
        public string Name
        {
            get { return name; }
            set { name = value; }
        }
        private string name;

        public string Occupation
        {
            get { return occupation; }
            set { occupation = value; }
        }
        private string occupation;


        public Person Parent
        {
            get { return this; }
        }
	
		public int CulinaryRating {
			get { return culinaryRating; }
            set { culinaryRating = value; }
        }
        private int culinaryRating;

		public DateTime BirthDate {
			get { return birthDate; }
            set { birthDate = value; }
        }
        private DateTime birthDate;

        public int YearOfBirth
        {
            get { return this.BirthDate.Year; }
            set { this.BirthDate = new DateTime(value, birthDate.Month, birthDate.Day); }
        }

        // Allows tests for methods
        virtual public double GetRate()
        {
            return hourlyRate;
        }
        private double hourlyRate;

        public void SetRate(double value)
        {
            hourlyRate = value;
        }

		// Allows tests for fields.
        public string Photo;
        public string Comments;
        public bool CanTellJokes;
    }

    // Model class for testing virtual and overridden methods

    public class Person2 : Person
    {
        public Person2(string name, string occupation, int culinaryRating, DateTime birthDate, double hourlyRate, bool canTellJokes, string photo, string comments)
            : base(name, occupation, culinaryRating, birthDate, hourlyRate, canTellJokes, photo, comments)
        {
        }

        public override double GetRate()
        {
            return base.GetRate() * 2;
        }

        new public int CulinaryRating
        {
            get { return base.CulinaryRating * 2; }
            set { base.CulinaryRating = value; }
        }
    }

    public static class PersonDb
    {
        static PersonDb()
        {
            allPersons = new List<Person>(new Person[] {             
                new Person("name", "occupation", 100, DateTime.Now, 1.0, true, "  photo  ", "comments"),
                new Person2("name", "occupation", 100, DateTime.Now, 1.0, true, "  photo  ", "comments")
            });
        }
        static private List<Person> allPersons;

        static public List<Person> All
        {
            get { return allPersons; }
        }
    }
}
