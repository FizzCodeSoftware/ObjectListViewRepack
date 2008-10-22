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

namespace BrightIdeasSoftware.Tests
{
	/// <summary>
	/// Description of Person.
	/// </summary>

	class Person
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

        public string Name
        {
            get { return name; }
            set { name = value; }
        }
        private string name;

        // Allows tests for fields.
        public string Occupation
        {
            get { return occupation; }
            set { occupation = value; }
        }
        private string occupation;

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

        public double GetRate()
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
		public int serialNumber;
        public bool CanTellJokes;
}
}
