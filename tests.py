from requests import get, post, delete
from threading import Thread
from datetime import datetime

PEOPLE_STRINGS = ['name', 'height', 'mass', 'hair_color', 'skin_color', 'eye_color', 'birth_year', 'gender',
                  'homeworld', 'created', 'edited', 'url']
PEOPLE_LISTS = ['films', 'species', 'vehicles', 'starships']
PEOPLE_GENDERS = ['male', 'female', 'hermaphrodite', 'none', 'n/a']


def test_methods():
    assert get('https://swapi.dev/api/starships').status_code == 200
    assert post('https://swapi.dev/api/starships', json={"amogus": "sus"}).status_code == 405
    assert delete('https://swapi.dev/api/starships').status_code == 405

    assert get('https://swapi.dev/api/imposters').status_code == 404
    assert post('https://swapi.dev/api/stars/1', json={"Lady": "Gaga"}).status_code == 404


def test_many_requests():
    def thread_fun():
        for _ in range(100):
            in_result = get('https://swapi.dev/api').status_code
            assert in_result == 200, in_result

    start = datetime.now()
    threads = []
    for _ in range(10):
        threads.append(Thread(target=thread_fun))
        threads[-1].start()
    for thread in threads:
        thread.join()
    return (datetime.now() - start).total_seconds()


def test_traverse_people():
    def test_structure(in_person):
        for key in PEOPLE_STRINGS:
            assert key in in_person, f'{key} is not in person.'
            assert type(in_person[key]) is str, f'{key} is not string.'

        for key in PEOPLE_LISTS:
            assert key in in_person, f'{key} is not in person.'
            assert type(in_person[key]) is list, f'{key} is not list.'

        assert len(in_person) == len(PEOPLE_STRINGS) + len(PEOPLE_LISTS), 'wrong key count.'

    def test_gender(in_person):
        assert in_person['gender'] in PEOPLE_GENDERS, f'{in_person["gender"]} is not a gender.'

    def test_url(in_person):
        assert get(in_person['url']).json() == in_person, 'person is not themselves.'

    url = 'https://swapi.dev/api/people'
    old_count = None
    true_count = 0

    while url is not None:
        response = get(url).json()

        assert response['count'] is not None
        if old_count is not None:
            assert response['count'] == old_count
        old_count = response['count']
        true_count += len(response['results'])

        assert type(response['results']) is list, 'results is not list.'
        for person in response['results']:
            test_structure(person)
            test_gender(person)
            test_url(person)
        url = response['next']

    assert (true_count == old_count), 'true_count != old_count'


def test_schema():
    # this test does not pass, even though (according to documentation) it should.
    response = get('https://swapi.dev/api').json()
    for key in response:
        assert get(response[key] + 'schema').status_code == 200, f'{key} has no schema (somewhy).'


functions = [test_methods, test_many_requests, test_traverse_people, test_schema]

for fun in functions:
    try:
        result = fun()
        if result is None:
            print(f'{fun.__name__} passed.')
        else:
            print(f'{fun.__name__} passed in', result, 'seconds.')
    except AssertionError as err:
        if f'{err}' == '':
            print(f'{fun.__name__} not passed.')
        else:
            print(f'{fun.__name__} not passed:', err)
