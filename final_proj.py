import requests
import json
from bs4 import BeautifulSoup
import sqlite3
import csv
import plotly.plotly as py
import plotly.graph_objs as go
from plotly.graph_objs import *
import numpy as np

try:
    cache_file = open('cache.json', 'r')
    cache_contents = cache_file.read()
    CACHE_DICTION = json.loads(cache_contents)
    cache_file.close()

except:
    CACHE_DICTION = {}

def make_request_using_cache(url):
    unique_ident = url

    if url in CACHE_DICTION:
        return CACHE_DICTION[unique_ident]
    else:
        resp = requests.get(url)
        CACHE_DICTION[unique_ident] = resp.text
        fw = open('cache.json', 'w')
        dumped_json_cache = json.dumps(CACHE_DICTION)
        fw.write(dumped_json_cache)
        fw.close()
        return CACHE_DICTION[unique_ident]

class ConcertInfo:
    def __init__(self, name='No name', date_month='No date month', date_day = 'No date day', date_year= 'No date year', venue='No venue', city='No city', state='No state'):
        self.name_ = name
        self.date_month_ = date_month
        self.date_day_ = date_day
        self.date_year_ = date_year
        self.venue_ = venue
        self.city_ = city
        self.state_ = state

    def __str__(self):
        concert_details = ' Name of event: {} \n Date of event: {}-{}-{} \n Venue: {} \n City: {} \n State: {}'.format(self.name_, self.date_month_, self.date_day_, self.date_year_, self.venue_, self.city_, self.state_)

        return concert_details

class PopEventsInfo:
    def __init__(self, name='No name', date='No date', venue='No venue', city='No city', state='No state'):
        self.name_ = name
        self.date_ = date
        self.venue_ = venue
        self.city_ = city
        self.state_ = state

    def __str__(self):
        pop_event_details = ' Name of popular event: {} \n Date of popular event: {} \n Venue: {} \n City: {} \n State: {}'.format(self.name_, self.date_, self.venue_, self.city_, self.state_)

        return pop_event_details

def get_concert_info(genre='None'):
    global all_event_list
    all_event_list = []
    baseurl = 'https://www.bandsintown.com/?came_from=257&genre_filter='
    global details_url
    details_url = baseurl + genre
    page_html = make_request_using_cache(details_url)
    page_soup = BeautifulSoup(page_html, 'html.parser')

    event_list = page_soup.find_all('div', class_='eventList-b8bed728')
    for e in event_list:
        link = e.find('a')['href']
        about_events = make_request_using_cache(link)
        about_events_soup = BeautifulSoup(about_events, 'html.parser')
        all_divs = about_events_soup.find('div', class_='artistAndEventInfo-9c155137')

        event_name = all_divs.find('h1', class_='artistAndEventInfo-4ca59f7b').text.strip()

        full_event_location = all_divs.find('h2', class_='artistAndEventInfo-b26e489f').text.strip()
        split_location = full_event_location.split('@')
        event_date = split_location[0]
        event_date_split = event_date.split()
        event_month = event_date_split[0]
        event_day = event_date_split[1]
        event_year = event_date_split[2]
        event_venue = split_location[1]

        full_event_city_state = all_divs.find('a', class_='artistAndEventInfo-50ca688a').text.strip()
        split_city_state = full_event_city_state.split(',')
        event_city = split_city_state[0]
        event_state = split_city_state[1]

        class_events = ConcertInfo(name=event_name, date_month= event_month, date_day= event_day, date_year= event_year, venue=event_venue, city=event_city, state=event_state)

        detailed_events = [class_events.name_, class_events.date_day_, class_events.date_month_, class_events.date_year_, class_events.venue_, class_events.city_, class_events.state_]

        all_event_list.append(detailed_events)

    conn = sqlite3.connect('events_by_genre.db')
    cur = conn.cursor()

    process_genre_command(genre)

    return all_event_list

def get_popular_event_info(popluar_search='None'):
    global popular_event_list
    popular_event_list = []
    global baseurl_pop
    baseurl_pop = 'https://www.bandsintown.com/?came_from=257&sort_by_filter=Number+of+RSVPs'
    page_html = make_request_using_cache(baseurl_pop)
    page_soup = BeautifulSoup(page_html, 'html.parser')

    pop_event_list = page_soup.find('div', class_='eventList-3690f1e3')
    all_pop_info = pop_event_list.find_all('div', class_='eventList-b8bed728')
    for p in all_pop_info:
        link = p.find('a')['href']
        about_pop_events = make_request_using_cache(link)
        about_pop_events_soup = BeautifulSoup(about_pop_events, 'html.parser')
        all_divs = about_pop_events_soup.find('div', class_='artistAndEventInfo-9c155137')

        pop_event_name = all_divs.find('h1', class_='artistAndEventInfo-4ca59f7b').text.strip()

        full_pop_event_location = all_divs.find('h2', class_='artistAndEventInfo-b26e489f').text.strip()
        split_location = full_pop_event_location.split('@')
        pop_event_date = split_location[0]
        pop_event_venue = split_location[1]

        full_pop_event_city_state = all_divs.find('a', class_='artistAndEventInfo-50ca688a').text.strip()
        split_city_state = full_pop_event_city_state.split(',')
        event_city = split_city_state[0]
        event_state = split_city_state[1]

        global class_pop_events
        class_pop_events = PopEventsInfo(name=pop_event_name, date=pop_event_date, venue=pop_event_venue, city=event_city, state=event_state)

        detailed_pop_events = [class_pop_events.name_, class_pop_events.date_, class_pop_events.venue_, class_pop_events.city_, class_pop_events.state_]

        popular_event_list.append(detailed_pop_events)

    conn = sqlite3.connect('events_by_genre.db')
    cur = conn.cursor()

    process_popular_command(users_choice2)

    for x in popular_event_list:
        print(x)
        print('-' * 20)

    return popular_event_list

def init_db():
    try:
        conn = sqlite3.connect('events_by_genre.db')
        cur = conn.cursor()
    except Error as e:
        print(e)

    statement = '''
            DROP TABLE IF EXISTS "Genre";
            '''
    cur.execute(statement)
    conn.commit()
    statement = '''
        CREATE TABLE "Genre" (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'GenreName' TEXT NOT NULL,
            'EventName' TEXT NOT NULL,
            'DateDay' REAL NOT NULL,
            'DateMonth' TEXT NOT NULL,
            'DateYear' TEXT NOT NULL,
            'EventVenue' TEXT NOT NULL,
            'EventCity' TEXT NOT NULL,
            'EventState' TEXT NOT NULL
        );
    '''
    cur.execute(statement)

    statement = '''
            DROP TABLE IF EXISTS 'GenreList';
            '''
    cur.execute(statement)
    conn.commit()
    statement = '''
        CREATE TABLE IF NOT EXISTS "GenreList" (
        'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
        'SpecifcGenre' TEXT NOT NULL
        );
    '''
    cur.execute(statement)

    statement = '''
            DROP TABLE IF EXISTS "PopularEvents";
            '''
    cur.execute(statement)
    conn.commit()
    statement = '''
        CREATE TABLE "PopularEvents" (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'PopChoice' TEXT NOT NULL,
            'PopPerformer' TEXT NOT NULL,
            'PopEventDate' TEXT NOT NULL,
            'PopVenue' TEXT NOT NULL,
            'PopCity' TEXT NOT NULL,
            'PopState' TEXT NOT NULL
        );
    '''

    cur.execute(statement)

    statement = '''
            DROP TABLE IF EXISTS 'PopularList';
            '''
    cur.execute(statement)
    conn.commit()
    statement = '''
        CREATE TABLE IF NOT EXISTS "PopularList" (
        'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
        'SpecificPop' TEXT NOT NULL
        );
    '''
    cur.execute(statement)

    conn.commit()

    conn.close()

def process_genre(command):
    try:
        conn = sqlite3.connect('events_by_genre.db')
        cur = conn.cursor()
    except:
        print('Sorry. There was an error.')

    if 'genre' in command:
        query = command.split('=')[0]
        genre_search = command.split('=')[1]

        if query == 'genre':
            statement = 'SELECT GenreName, EventName, EventCity, EventState, DateDay, DateYear '
            statement += 'FROM Genre '
            statement += 'WHERE GenreName = "{}" '.format(genre_search)
            statement += 'GROUP BY EventName '
            cur.execute(statement)
            return_list = []
            for x in cur:
                return_list.append((x[0], x[1], x[2], x[3], x[4], x[5]))
                print(x)
                print('-' * 20)
            return return_list

    elif 'artist' in command:
        query = command.split('=')[0]
        artist_search = command.split('=')[1]

        if query == 'artist':
            statement = 'SELECT EventName, EventCity, EventState, DateDay, DateYear '
            statement += 'FROM Genre '
            statement +=  'WHERE EventName = "{}" '.format(artist_search)
            statement += 'ORDER BY DateDay '
            cur.execute(statement)
            return_list = []
            for x in cur:
                return_list.append((x[0], x[1], x[2], x[3], x[4]))
            print(return_list[0])
            print('-' * 20)
            return return_list

    elif 'month' in command:
        query = command.split('=')[0]
        month_search = command.split('=')[1]

        if query == 'month':
            statement = 'SELECT EventName, DateDay, DateMonth '
            statement += 'FROM Genre '
            statement += 'WHERE DateMonth = "{}" '.format(month_search)
            statement += 'ORDER BY DateDay '
            cur.execute(statement)
            return_list = []
            for x in cur:
                return_list.append((x[0], x[1], x[2]))
                print(x)
                print('-' * 20)
            return return_list

    elif 'city' in command:
        query = command.split('=')[0]
        city_search = command.split('=')[1]

        if query == 'city':
            statement = 'SELECT EventName, EventCity, EventState '
            statement += 'FROM Genre '
            statement += 'WHERE EventCity = "{}" '.format(city_search)
            cur.execute(statement)
            return_list = []
            for x in cur:
                return_list.append((x[0], x[1], x[2]))
                print(x)
                print('-' * 20)
            return return_list


def process_popular(command):
    try:
        conn = sqlite3.connect('events_by_genre.db')
        cur = conn.cursor()
    except:
        print('Sorry. There was an error.')

    if 'city' in command:
        query = command.split('=')[0]
        city_search = command.split('=')[1]

        if query == 'city':
            statement = 'SELECT PopPerformer, PopVenue, PopEventDate, PopCity '
            statement += 'FROM PopularEvents '
            statement += 'WHERE PopCity = "{}" '.format(city_search)
            cur.execute(statement)
            return_list = []
            for x in cur:
                return_list.append((x[0], x[1], x[2], x[3]))
                print(x)
                print('-' * 20)
            return return_list

    elif 'state' in command:
        query = command.split('=')[0]
        state_search = command.split('=')[1]

        if query == 'state':
            statement = 'SELECT PopPerformer, PopVenue, PopEventDate, PopState '
            statement += 'FROM PopularEvents '
            statement += 'WHERE PopState LIKE "%{}" '.format(state_search)
            cur.execute(statement)
            return_list = []
            for x in cur:
                return_list.append((x[0], x[1], x[2], x[3]))
                print(x)
                print('-' * 20)
            return return_list

def general_processor(command):
    if 'type' in command:
        command_split = command[5:]
        results = process_genre(command_split)
        return results
    elif 'pop' in command:
        command_split = command[4:]
        results = process_popular(command_split)
        return results
    else:
        print('Invalid command. Enter help for directions.')

def process_genre_command(genre_param):
    response = make_request_using_cache(details_url)
    try:
        conn = sqlite3.connect('events_by_genre.db')
        cur = conn.cursor()
    except Error in e:
        print(e)
    insertion = (None, genre_param)
    statement1 = 'INSERT INTO "GenreList" '
    statement1 += 'VALUES (?, ?)'
    cur.execute(statement1, insertion)
    conn.commit()

    statement = 'SELECT * FROM GenreList '
    statement += 'WHERE SpecifcGenre="{}" '.format(genre_param)
    x = cur.execute(statement)

    if len(x.fetchall()) == 1:
        unique_ident = details_url
        resp = requests.get(details_url)
        CACHE_DICTION[unique_ident] = resp.text
        fw = open('cache.json', 'w')
        dumped_json_cache = json.dumps(CACHE_DICTION)
        fw.write(dumped_json_cache)

        with open('genres_table.csv', 'w') as g:
            writer = csv.writer(g)
            for row in all_event_list:
                writer.writerow(row)

        with open('genres_table.csv', encoding='utf-8') as csvfile:
            reading_csv = csv.reader(csvfile, delimiter=',')
            genre_choice = users_choice
            count = 0
            for row in reading_csv:
                if count == 0:
                    count += 1
                    continue
                name = row[0]
                date_month = row[1]
                date_day = row[2]
                date_year = row[3]
                venue = row[4]
                city = row[5]
                state = row[6]
                insertion = (None, genre_choice, name, date_month, date_day, date_year, venue, city, state)
                statement = 'INSERT INTO "Genre" '
                statement += 'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)'
                cur.execute(statement, insertion)
            conn.commit()
        fw.close()

def process_popular_command(popular_param):
    response = make_request_using_cache(baseurl_pop)
    try:
        conn = sqlite3.connect('events_by_genre.db')
        cur = conn.cursor()
    except Error in e:
        print(e)
    insertion = (None, popular_param)
    statement1 = 'INSERT INTO "PopularList" '
    statement1 += 'VALUES (?, ?)'
    cur.execute(statement1, insertion)
    conn.commit()

    statement = 'SELECT * FROM PopularList '
    statement += 'WHERE SpecificPop="{}" '.format(popular_param)
    x = cur.execute(statement)

    if len(x.fetchall()) == 1:
        unique_ident = baseurl_pop
        resp = requests.get(baseurl_pop)
        CACHE_DICTION[unique_ident] = resp.text
        fw = open('cache.json', 'w')
        dumped_json_cache = json.dumps(CACHE_DICTION)
        fw.write(dumped_json_cache)

        with open('popular_events.csv', 'w') as p:
            writer = csv.writer(p)
            for row in popular_event_list:
                writer.writerow(row)

        with open('popular_events.csv', encoding='utf-8') as csvfile:
            reading_csv = csv.reader(csvfile, delimiter=',')
            pop_event_choice = users_choice2
            count = 0
            for row in reading_csv:
                if count == 0:
                    count += 1
                    continue
                name = row[0]
                date = row[1]
                venue = row[2]
                city = row[3]
                state = row[4]
                insertion = (None, pop_event_choice, name, date, venue, city, state)
                statement = 'INSERT INTO "PopularEvents" '
                statement += 'VALUES (?, ?, ?, ?, ?, ?, ?)'
                cur.execute(statement, insertion)
            conn.commit()
        fw.close()

def data_visualization1():
    mapbox_access_token = 'pk.eyJ1Ijoic29maWFsbzE0IiwiYSI6ImNqZzVoM2c0bTFjYW8yemxqZ3JkZzRobGQifQ.otqygvuRAt1QXW6HEjPsWQ'

    data = Data([
    Scattermapbox(
        lat=['42.2808','42.3314','41.6528',
             '42.5467','42.7370','42.4606',
             '42.4895','42.6389','42.4806'],
        lon=['-83.7430','-83.0458','-83.5379',
             '-83.2113','-84.4839','-83.1346',
             '-83.1446','-83.2910','-83.4755'],
        mode='markers',
        marker=Marker(
            size=9,
            color='rgb(218,36,54)',
        ),
        text=["Ann Arbor","Detroit","Toledo",
             "Birmingham","East Lansing","Ferndale",
             "Royal Oak","Pontiac","Novi"],
       )
    ])
    layout = Layout(
        autosize=True,
        hovermode='closest',
        mapbox=dict(
            accesstoken=mapbox_access_token,
            bearing=0,
            center=dict(
                lat=45,
                lon=-73
            ),
            pitch=0,
            zoom=5
        ),
    )

    fig = dict(data=data, layout=layout)
    py.plot(fig, filename='Cities Mapbox')

def data_visualization2():
    mapbox_access_token = 'pk.eyJ1Ijoic29maWFsbzE0IiwiYSI6ImNqZzVoM2c0bTFjYW8yemxqZ3JkZzRobGQifQ.otqygvuRAt1QXW6HEjPsWQ'
    data = Data([
    Scattermapbox(
        lat=['42.3410','42.5647','42.3400',
             '42.6763','42.7451','42.3378',
             '41.5927'],
        lon=['-83.0552','-82.9758','-83.0456',
             '-83.2030','-83.3723','-83.0517',
             '-83.6518'],
        mode='markers',
        marker=Marker(
            size=9,
            color='rgb(218,36,54)',
        ),
        text=["Little Caesar's Arena","Freedom Hill","Ford Field",
             "MEADOW BROOK AMPHITHEATRE","DTE Energy Music Theatre","The Fillmore Detroit",
             "Stranahan Theater & Great Hall"],
       )
    ])
    layout = Layout(
        autosize=True,
        hovermode='closest',
        mapbox=dict(
            accesstoken=mapbox_access_token,
            bearing=0,
            center=dict(
                lat=45,
                lon=-73
            ),
            pitch=0,
            zoom=5
        ),
    )

    fig = dict(data=data, layout=layout)
    py.plot(fig, filename='Popular Venues Mapbox')

def data_visualization3():
    trace = go.Bar(
        x=["Little Caesar's Arena","Freedom Hill","Ford Field",
             "MEADOW BROOK AMPHITHEATRE","DTE Energy Music Theatre","The Fillmore Detroit",
             "Stranahan Theater & Great Hall"],
        y=[4, 1, 3, 1, 1, 2, 1],
        marker=dict(
            color='rgb(218,36,97)',
            line=dict(
                    color='rgb(16,13,17)',
                    width=1.5),
        )
    )

    data = [trace]
    layout = go.Layout(
        xaxis=dict(tickangle=-45),

    )

    fig = go.Figure(data=data, layout=layout)
    py.plot(fig, filename='Popular-Concerts-Venue-Count-Bar-Chart')

def data_visualization4():
    labels = ["Little Caesar's Arena","Freedom Hill","Ford Field",
         "MEADOW BROOK AMPHITHEATRE","DTE Energy Music Theatre","The Fillmore Detroit",
         "Stranahan Theater & Great Hall"]
    values = [2352,588,1764,588,588,1176,588]

    trace = go.Pie(labels=labels, values=values)

    py.plot([trace], filename='Popular-Concerts-Venue-Count-Pie-Chart')

def load_help_text():
    with open('help.txt') as f:
        return f.read()

def interactive_prompt():
    help_text = load_help_text()
    print("ENTER ONE OF THESE GENRES: \n Rock \n Electronic \n Pop \n Alternative \n Folk \n Hip Hop \n Punk \n R&B/Soul \n Country \n Jazz \n Reggae \n Blues \n Metal \n Latin \n Christian/Gospel \n Classical")
    global users_choice
    users_choice = input('Enter a genre to start your search: ')
    while users_choice != 'next':
        get_concert_info(users_choice)
        user_input_again= input('To search by more specifics, enter yes. Otherwise to move on, enter next. If need further directions, enter help: ')
        print('-' * 20)
        if user_input_again == 'yes':
            info = input('Enter "type" followed by one of these commands for more specific information: \n "genre=" \n "artist=" \n "month=" \n "city=" \n  -- Note: enter the 3-letter month abbrevation if specifying by "month=" (ex. month=Apr) -- \n Enter response here: ')
            general_processor(info)
        elif user_input_again == 'next':
            break
        elif user_input_again == 'help':
            print(help_text)
            continue
    global users_choice2
    users_choice2 = input('Enter "popular" for a list of all popular events near you: ')
    while users_choice2 != 'exit':
        get_popular_event_info(users_choice2)
        break
    users_choice3 = input('To search for more specific information, enter "pop" followed by one of these commands: \n "city=" \n "state=" \n Otherwise, enter "next" to see data visualization options: ')
    while users_choice3 != 'exit':
        if 'pop' in users_choice3:
            general_processor(users_choice3)
            print('MOVING TO DATA VISUALIZATION OPTIONS')
            print('-' * 20)
            break
        elif 'next' == users_choice3:
            print('-' * 20)
            break
        else:
            print('Invalid command, try entering "pop" followed by "city=" or "state=" ')
            continue
    users_choice4 = input(' To see a map of cities with concerts happening soon, enter: 1 \n To see a map of the locations of venues for concerts happening soon, enter: 2 \n To see a bar chart for the amount of popular events occurring at certain venues, enter: 3 \n To see a pie chart for the distribution of popular events occurring at certain venues, enter 4: \n To finish, enter, exit: ')
    while users_choice4 != 'exit':
        if users_choice4 == '1':
            data_visualization1()
            users_choice4 = input('If want more visualizations, follow the previous instructions (i.e. enter 1, 2, 3, 4 for the desired visualization). Otherwise, if done, enter exit: ')
        elif users_choice4 == '2':
            data_visualization2()
            users_choice4 = input('If want more visualizations, follow the previous instructions (i.e. enter 1, 2, 3, 4 for the desired visualization). Otherwise, if done, enter exit: ')
        elif users_choice4 == '3':
            data_visualization3()
            users_choice4 = input('If want more visualizations, follow the previous instructions (i.e. enter 1, 2, 3, 4 for the desired visualization). Otherwise, if done, enter exit: ')
        elif users_choice4 == '4':
            data_visualization4()
            users_choice4 = input('If want more visualizations, follow the previous instructions (i.e. enter 1, 2, 3, 4 for the desired visualization). Otherwise, if done, enter exit: ')
        elif users_choice4 == 'exit':
            break
        else:
            print('Invalid command. Try again.')
            users_choice4 = input('If done, enter exit: ')
    users_choice4 = input('If done, enter exit: ')
    print('Bye!')

if __name__ == '__main__':
    # init_db()
    interactive_prompt()
    # data_visualization1()
    # data_visualization2()
    # data_visualization3()
    # data_visualization4()
