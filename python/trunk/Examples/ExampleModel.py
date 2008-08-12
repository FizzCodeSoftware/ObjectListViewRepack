# -*- coding: utf-8 -*-
#!/usr/bin/env python

# Simple minded model objects for our examples

import datetime
import time

class Track(object):
    """
    Simple minded object that represents a song in a music library
    """
    def __init__(self, title, artist, album, sizeInBytes, lastPlayed, rating):
        self.title = title
        self.artist = artist
        self.album = album
        self.lastPlayed = datetime.datetime(*(time.strptime(lastPlayed, "%d/%m/%Y %H:%M")[0:6]))
        self.sizeInBytes = sizeInBytes
        self.rating = rating

    def GetSizeInMb(self):
        return self.sizeInBytes / (1024.0*1024.0)


def GetTracks():
    """
    Return a collection of tracks
    """
    return [
        Track("shiver", "Natalie Imbruglia", "Counting Down the Days", 8.6*1024*1024*1024, "9/03/2008 9:51", 80),
        Track("Who's Gonna Ride Your Wild Horses", "U2", "Achtung Baby", 6.3*1024*1024, "9/10/2007 11:32", 80),
        Track("So Cruel", "U2", "Achtung Baby", 6.9*1024*1024, "9/10/2007 11:38", 60),
        Track("The Fly", "U2", "Achtung Baby", 5.4*1024*1024, "9/10/2007 11:42", 60),
        Track("Tryin' To Throw Your Arms Around The World", "U2", "Achtung Baby", 4.7*1024*1024, "9/10/2007 11:46", 60),
        Track("Ultraviolet (Light My Way)", "U2", "Achtung Baby", 6.6*1024*1024, "9/10/2007 11:52", 60),
        Track("Acrobat", "U2", "Achtung Baby", 5.4*1024*1024, "9/10/2007 11:56", 60),
        Track("Love Is Blindness", "U2", "Achtung Baby", 5.3*1024, "9/10/2007 12:00", 60),
        Track("Elevation", "U2", "All That You Can't Leave Behind", 459, "25/01/2008 11:46", 60),
        Track("Walk On", "U2", "All That You Can't Leave Behind", 5.8*1024*1024, "18/03/2008 11:39", 100),
        Track("Kite", "U2", "All That You Can't Leave Behind", 5.2*1024*1024, "23/01/2008 10:36", 40),
        Track("In A Little While", "U2", "All That You Can't Leave Behind", 4.3*1024*1024, "20/01/2008 7:48", 60),
        Track("Wild Honey", "U2", "All That You Can't Leave Behind", 4.5*1024*1024, "13/04/2007 11:50", 40),
        Track("Peace On Earth", "U2", "All That You Can't Leave Behind", 5.6*1024*1024, "22/12/2007 2:51", 40),
        Track("When I Look At The World", "U2", "All That You Can't Leave Behind", 5.1*1024*1024, "22/12/2007 2:55", 40),
        Track("New York", "U2", "All That You Can't Leave Behind", 6.4*1024*1024, "22/12/2007 3:01", 60),
        Track("Grace", "U2", "All That You Can't Leave Behind", 6.5*1024*1024, "22/12/2007 3:06", 40),
        Track("The Ground Beneath Her Feet(Bonus Track)", "U2", "All That You Can't Leave Behind", 4.4*1024*1024, "22/12/2007 3:10", 40),
        Track("Follow You Home", "Nickelback", "All The Right Reasons", 6*1024*1024, "6/03/2008 10:42", 40),
        Track("Fight For All The Wrong Reason", "Nickelback", "All The Right Reasons", 5.2*1024*1024, "15/03/2008 5:04", 60),
        Track("Photograph", "Nickelback", "All The Right Reasons", 6*1024*1024, "15/03/2008 5:08", 60),
        Track("Animals", "Nickelback", "All The Right Reasons", 4.3*1024*1024, "16/02/2008 12:12", 40),
        Track("Savin' Me", "Nickelback", "All The Right Reasons", 5.1*1024*1024, "24/03/2008 10:41", 80),
        Track("Far Away", "Nickelback", "All The Right Reasons", 5.5*1024*1024, "15/03/2008 5:30", 40),
        Track("Next Contestant", "Nickelback", "All The Right Reasons", 5*1024*1024, "24/03/2008 9:47", 80),
        Track("Side Of A Bullet", "Nickelback", "All The Right Reasons", 4.2*1024*1024, "6/03/2008 11:00", 40),
        Track("If Everyone Cared", "Nickelback", "All The Right Reasons", 5*1024*1024, "6/03/2008 11:03", 60),
        Track("Someone That You're With", "Nickelback", "All The Right Reasons", 5.6*1024*1024, "16/02/2008 12:34", 40),
        Track("Rockstar", "Nickelback", "All The Right Reasons", 5.9*1024*1024, "16/02/2008 12:38", 60),
        Track("Lelani", "Hoodoo Gurus", "Ampology", 5.9*1024*1024, "22/10/2007 8:45", 60),
        Track("Tojo", "Hoodoo Gurus", "Ampology", 4.1*1024*1024, "22/10/2007 8:48", 60),
        Track("My Girl", "Hoodoo Gurus", "Ampology", 3.3*1024*1024, "12/11/2007 7:57", 80),
        Track("Be My Guru", "Hoodoo Gurus", "Ampology", 3.3*1024*1024, "20/03/2008 12:15", 100),
        Track("I Want You Back", "Hoodoo Gurus", "Ampology", 3.9*1024*1024, "12/11/2007 7:42", 80),
        Track("I Was A Kamikaze Pilot", "Hoodoo Gurus", "Ampology", 3.9*1024*1024, "22/10/2007 9:00", 60),
        Track("Bittersweet", "Hoodoo Gurus", "Ampology", 4.7*1024*1024, "22/10/2007 9:04", 60),
        Track("Poison Pen", "Hoodoo Gurus", "Ampology", 5*1024*1024, "22/10/2007 9:11", 60),
        Track("In The Wild", "Hoodoo Gurus", "Ampology", 3.9*1024*1024, "22/10/2007 9:14", 60),
        Track("Whats My Scene?", "Hoodoo Gurus", "Ampology", 4.6*1024*1024, "12/11/2007 7:51", 100),
        Track("Heart Of Darkness", "Hoodoo Gurus", "Ampology", 3.8*1024*1024, "22/10/2007 9:21", 60),
        Track("Good Times", "Hoodoo Gurus", "Ampology", 3.7*1024*1024, "20/03/2008 12:18", 80),
        Track("Cajun Country", "Hoodoo Gurus", "Ampology", 4.9*1024*1024, "22/10/2007 9:28", 60),
        Track("Axegrinder", "Hoodoo Gurus", "Ampology", 4.2*1024*1024, "22/10/2007 9:32", 60),
        Track("Another World", "Hoodoo Gurus", "Ampology", 4*1024*1024, "20/03/2008 12:21", 80),
        Track("Meant To Live", "Switchfoot", "The Beautiful Letdown", 4*1024*1024, "3/03/2008 1:46", 100),
        Track("This Is Your Life", "Switchfoot", "The Beautiful Letdown", 4*1024*1024, "3/03/2008 2:11", 100),
        Track("More than fine", "Switchfoot", "The Beautiful Letdown", 4.9*1024*1024, "3/03/2008 2:16", 60),
        Track("Ammunition", "Switchfoot", "The Beautiful Letdown", 4.4*1024*1024, "3/03/2008 1:58", 40),
        Track("Dare you to move", "Switchfoot", "The Beautiful Letdown", 4.9*1024*1024, "3/03/2008 2:20", 80),
        Track("Redemption", "Switchfoot", "The Beautiful Letdown", 3.6*1024*1024, "19/03/2008 5:19", 80),
        Track("The beautiful letdown", "Switchfoot", "The Beautiful Letdown", 6.2*1024*1024, "3/03/2008 2:29", 60),
    ]
