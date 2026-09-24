import pytest

import app


@pytest.fixture()
def client():
    app.app.config.update(TESTING=True)
    with app.app.test_client() as test_client:
        yield test_client


def test_index_returns_game_page(client):
    response = client.get('/')

    assert response.status_code == 200
    assert b'Sudoku' in response.data


def test_index_includes_difficulty_selector(client):
    response = client.get('/')

    assert b'<select id="difficulty">' in response.data
    assert b'<option value="easy">Easy</option>' in response.data
    assert b'<option value="medium" selected>Medium</option>' in response.data
    assert b'<option value="hard">Hard</option>' in response.data


def test_index_includes_instant_feedback_toggle(client):
    response = client.get('/')

    assert b'id="instant-feedback"' in response.data
    assert b'type="checkbox" checked' in response.data
    assert b'role="status"' in response.data


def test_new_game_returns_requested_number_of_clues(client):
    response = client.get('/new?clues=45')

    assert response.status_code == 200
    puzzle = response.get_json()['puzzle']
    assert sum(cell != 0 for row in puzzle for cell in row) == 45
    assert app.CURRENT['solution'] is not None


@pytest.mark.parametrize('difficulty, expected_clues', [
    ('easy', 45),
    ('medium', 35),
    ('hard', 25),
])
def test_new_game_uses_difficulty_clue_count(client, difficulty, expected_clues):
    response = client.get(f'/new?difficulty={difficulty}')

    assert response.status_code == 200
    puzzle = response.get_json()['puzzle']
    assert sum(cell != 0 for row in puzzle for cell in row) == expected_clues


def test_new_game_rejects_unknown_difficulty(client):
    response = client.get('/new?difficulty=expert')

    assert response.status_code == 400
    assert response.get_json() == {'error': 'Invalid difficulty'}


def test_check_requires_game_in_progress(client):
    app.CURRENT['solution'] = None

    response = client.post('/check', json={'board': []})

    assert response.status_code == 400
    assert response.get_json() == {'error': 'No game in progress'}


def test_check_identifies_incorrect_cells(client):
    client.get('/new?clues=81')
    solution = app.CURRENT['solution']
    board = [row[:] for row in solution]
    board[0][0] = (board[0][0] % 9) + 1

    response = client.post('/check', json={'board': board})

    assert response.status_code == 200
    assert response.get_json()['incorrect'] == [[0, 0]]