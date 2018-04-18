import unittest
import final_proj as final
from final_proj import *
import sqlite3

# TOTAL: At least 3 test cases, 15 assertions

# Tests for data storage (AKA seeing if databases populated correctly)
class TestDataStorage(unittest.TestCase):
    def test_genre_table(self):
        conn = sqlite3.connect('events_by_genre.db')
        cur = conn.cursor()

        sql = 'SELECT EventName FROM Genre '
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertIn(('Trumpet',), result_list)
        self.assertIn(('3TEETH',), result_list)

        sql = 'SELECT EventName FROM Genre WHERE GenreName = "Rock" '
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertEqual(len(result_list), 17)
        self.assertIn(('Eyes Set to Kill',), result_list)

        conn.close()

    def test_popular_events_table(self):
        conn = sqlite3.connect('events_by_genre.db')
        cur = conn.cursor()

        sql = 'SELECT PopPerformer FROM PopularEvents WHERE PopEventDate LIKE "%May%" '
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertIn(('Post Malone',), result_list)
        self.assertEqual(len(result_list), 4)

        sql = 'SELECT PopEventDate FROM PopularEvents WHERE PopVenue = " Little Caesars Arena" '
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertIn(('Jul 14th 2018 ',), result_list)
        self.assertEqual(len(result_list), 4)

        conn.close()

# Tests for data processing & to see if queries satisfied
class TestDataInput(unittest.TestCase):
    def test_general_processor(self):
        results = general_processor('type genre=Rock')
        self.assertEqual(results[0][1], ('3TEETH'))

        results = general_processor('type artist=Gooding')
        self.assertEqual(results[0][1], 'Birmingham')

        results = general_processor('pop city=Detroit')
        self.assertEqual(results[0][0], 'Maroon 5')
        self.assertEqual(results[2][1], ' Ford Field')

        results = general_processor('pop state=OH')
        self.assertEqual(results[0][0], 'Brett Eldredge')

# Tests to show accessing data from sources (AKA bandsintown)
class TestAccessSources(unittest.TestCase):
    def test_Constructor_ConcertClass(self):
        c1 = final.ConcertInfo()
        c2 = final.ConcertInfo("Flush", "Apr", "14th", "2018", "Frankies", "Toledo", "Ohio")

        self.assertEqual(c1.name_, "No name")
        self.assertEqual(c1.date_month_ , "No date month")
        self.assertEqual(c1.venue_ , "No venue")
        self.assertEqual(c2.name_, "Flush")
        self.assertEqual(c2.date_month_, "Apr")
        self.assertEqual(c2.venue_, "Frankies")

    def test_Constructor_PopEventsClass(self):
        p1 = final.PopEventsInfo()
        p2 = final.PopEventsInfo("Khalid", "Jun 1st 2018", "MEADOW BROOK AMPHITHEATRE", "Detroit", "MI")

        self.assertEqual(p1.name_, "No name")
        self.assertEqual(p1.city_, "No city")
        self.assertEqual(p1.state_, "No state")
        self.assertEqual(p1.venue_, "No venue")
        self.assertEqual(p2.name_, "Khalid")
        self.assertEqual(p2.city_, "Detroit")
        self.assertEqual(p2.state_, "MI")
        self.assertEqual(p2.venue_, "MEADOW BROOK AMPHITHEATRE")

unittest.main()
