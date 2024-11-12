import pytest
from unittest.mock import patch, MagicMock, mock_open, ANY
import sqlite3
import textwrap

# Adjust the import statements according to your project structure
from meal_max.models.kitchen_model import (
    Meal,
    create_meal,
    clear_meals,
    delete_meal,
    get_leaderboard,
    get_meal_by_id,
    get_meal_by_name,
    update_meal_stats,
)


def test_meal_init_valid():
    meal = Meal(id=1, meal='Spaghetti', cuisine='Italian', price=10.0, difficulty='MED')
    assert meal.id == 1
    assert meal.meal == 'Spaghetti'
    assert meal.cuisine == 'Italian'
    assert meal.price == 10.0
    assert meal.difficulty == 'MED'


def test_meal_init_invalid_price():
    with pytest.raises(ValueError) as excinfo:
        Meal(id=1, meal='Spaghetti', cuisine='Italian', price=-5.0, difficulty='MED')
    assert str(excinfo.value) == "Price must be a positive value."


def test_meal_init_invalid_difficulty():
    with pytest.raises(ValueError) as excinfo:
        Meal(id=1, meal='Spaghetti', cuisine='Italian', price=10.0, difficulty='EASY')
    assert str(excinfo.value) == "Difficulty must be 'LOW', 'MED', or 'HIGH'."


@patch('meal_max.models.kitchen_model.get_db_connection')
def test_create_meal_success(mock_get_db_connection):
    mock_conn = MagicMock()
    mock_cursor = mock_conn.cursor.return_value
    mock_get_db_connection.return_value.__enter__.return_value = mock_conn

    create_meal('Spaghetti', 'Italian', 10.0, 'MED')

    sql_executed = mock_cursor.execute.call_args[0][0]
    params = mock_cursor.execute.call_args[0][1]

    expected_sql = """
        INSERT INTO meals (meal, cuisine, price, difficulty)
        VALUES (?, ?, ?, ?)
    """

    # Normalize whitespace by removing leading/trailing whitespace and collapsing internal whitespace
    sql_executed_clean = ' '.join(textwrap.dedent(sql_executed).split())
    expected_sql_clean = ' '.join(textwrap.dedent(expected_sql).split())

    assert sql_executed_clean == expected_sql_clean
    assert params == ('Spaghetti', 'Italian', 10.0, 'MED')

    mock_conn.commit.assert_called_once()


def test_create_meal_invalid_price():
    with pytest.raises(ValueError) as excinfo:
        create_meal('Spaghetti', 'Italian', -10.0, 'MED')
    assert str(excinfo.value) == "Invalid price: -10.0. Price must be a positive number."


def test_create_meal_invalid_difficulty():
    with pytest.raises(ValueError) as excinfo:
        create_meal('Spaghetti', 'Italian', 10.0, 'EASY')
    assert str(excinfo.value) == "Invalid difficulty level: EASY. Must be 'LOW', 'MED', or 'HIGH'."


@patch('meal_max.models.kitchen_model.get_db_connection')
def test_create_meal_duplicate_name(mock_get_db_connection):
    mock_conn = MagicMock()
    mock_cursor = mock_conn.cursor.return_value
    mock_cursor.execute.side_effect = sqlite3.IntegrityError()
    mock_get_db_connection.return_value.__enter__.return_value = mock_conn

    with pytest.raises(ValueError) as excinfo:
        create_meal('Spaghetti', 'Italian', 10.0, 'MED')
    assert str(excinfo.value) == "Meal with name 'Spaghetti' already exists"


@patch('meal_max.models.kitchen_model.get_db_connection')
def test_create_meal_database_error(mock_get_db_connection):
    mock_conn = MagicMock()
    mock_cursor = mock_conn.cursor.return_value
    mock_cursor.execute.side_effect = sqlite3.Error('Database error')
    mock_get_db_connection.return_value.__enter__.return_value = mock_conn

    with pytest.raises(sqlite3.Error) as excinfo:
        create_meal('Spaghetti', 'Italian', 10.0, 'MED')
    assert str(excinfo.value) == 'Database error'


@patch('meal_max.models.kitchen_model.get_db_connection')
@patch('builtins.open', new_callable=mock_open, read_data='CREATE TABLE meals...')
def test_clear_meals_success(mock_file, mock_get_db_connection):
    mock_conn = MagicMock()
    mock_cursor = mock_conn.cursor.return_value
    mock_get_db_connection.return_value.__enter__.return_value = mock_conn

    clear_meals()

    mock_file.assert_called_once_with('/app/sql/create_meal_table.sql', 'r')
    mock_cursor.executescript.assert_called_once_with('CREATE TABLE meals...')
    mock_conn.commit.assert_called_once()


@patch('meal_max.models.kitchen_model.get_db_connection')
@patch('builtins.open', new_callable=mock_open, read_data='CREATE TABLE meals...')
def test_clear_meals_database_error(mock_file, mock_get_db_connection):
    mock_conn = MagicMock()
    mock_cursor = mock_conn.cursor.return_value
    mock_cursor.executescript.side_effect = sqlite3.Error('Database error')
    mock_get_db_connection.return_value.__enter__.return_value = mock_conn

    with pytest.raises(sqlite3.Error) as excinfo:
        clear_meals()
    assert str(excinfo.value) == 'Database error'


@patch('meal_max.models.kitchen_model.get_db_connection')
def test_delete_meal_success(mock_get_db_connection):
    mock_conn = MagicMock()
    mock_cursor = mock_conn.cursor.return_value
    mock_cursor.fetchone.return_value = [False]
    mock_get_db_connection.return_value.__enter__.return_value = mock_conn

    delete_meal(1)

    calls = [
        (("SELECT deleted FROM meals WHERE id = ?", (1,)),),
        (("UPDATE meals SET deleted = TRUE WHERE id = ?", (1,)),)
    ]
    mock_cursor.execute.assert_has_calls(calls)
    mock_conn.commit.assert_called_once()


@patch('meal_max.models.kitchen_model.get_db_connection')
def test_delete_meal_already_deleted(mock_get_db_connection):
    mock_conn = MagicMock()
    mock_cursor = mock_conn.cursor.return_value
    mock_cursor.fetchone.return_value = [True]
    mock_get_db_connection.return_value.__enter__.return_value = mock_conn

    with pytest.raises(ValueError) as excinfo:
        delete_meal(1)
    assert str(excinfo.value) == "Meal with ID 1 has been deleted"


@patch('meal_max.models.kitchen_model.get_db_connection')
def test_delete_meal_not_found(mock_get_db_connection):
    mock_conn = MagicMock()
    mock_cursor = mock_conn.cursor.return_value
    mock_cursor.fetchone.return_value = None
    mock_get_db_connection.return_value.__enter__.return_value = mock_conn

    with pytest.raises(ValueError) as excinfo:
        delete_meal(1)
    assert str(excinfo.value) == "Meal with ID 1 not found"


@patch('meal_max.models.kitchen_model.get_db_connection')
def test_delete_meal_database_error(mock_get_db_connection):
    mock_conn = MagicMock()
    mock_cursor = mock_conn.cursor.return_value
    mock_cursor.execute.side_effect = sqlite3.Error('Database error')
    mock_get_db_connection.return_value.__enter__.return_value = mock_conn

    with pytest.raises(sqlite3.Error) as excinfo:
        delete_meal(1)
    assert str(excinfo.value) == 'Database error'


@patch('meal_max.models.kitchen_model.get_db_connection')
def test_get_leaderboard_sort_by_wins(mock_get_db_connection):
    mock_conn = MagicMock()
    mock_cursor = mock_conn.cursor.return_value

    sample_rows = [
        (1, 'Meal1', 'Italian', 10.0, 'MED', 5, 3, 0.6),
        (2, 'Meal2', 'French', 15.0, 'LOW', 4, 2, 0.5)
    ]
    mock_cursor.fetchall.return_value = sample_rows
    mock_get_db_connection.return_value.__enter__.return_value = mock_conn

    leaderboard = get_leaderboard(sort_by='wins')

    expected_leaderboard = [
        {'id': 1, 'meal': 'Meal1', 'cuisine': 'Italian', 'price': 10.0, 'difficulty': 'MED', 'battles': 5, 'wins': 3, 'win_pct': 60.0},
        {'id': 2, 'meal': 'Meal2', 'cuisine': 'French', 'price': 15.0, 'difficulty': 'LOW', 'battles': 4, 'wins': 2, 'win_pct': 50.0}
    ]
    assert leaderboard == expected_leaderboard


def test_get_leaderboard_invalid_sort_by():
    with pytest.raises(ValueError) as excinfo:
        get_leaderboard(sort_by='invalid_sort')
    assert str(excinfo.value) == "Invalid sort_by parameter: invalid_sort"


@patch('meal_max.models.kitchen_model.get_db_connection')
def test_get_leaderboard_database_error(mock_get_db_connection):
    mock_conn = MagicMock()
    mock_cursor = mock_conn.cursor.return_value
    mock_cursor.execute.side_effect = sqlite3.Error('Database error')
    mock_get_db_connection.return_value.__enter__.return_value = mock_conn

    with pytest.raises(sqlite3.Error) as excinfo:
        get_leaderboard()
    assert str(excinfo.value) == 'Database error'


@patch('meal_max.models.kitchen_model.get_db_connection')
def test_get_meal_by_id_success(mock_get_db_connection):
    mock_conn = MagicMock()
    mock_cursor = mock_conn.cursor.return_value
    mock_cursor.fetchone.return_value = (1, 'Meal1', 'Italian', 10.0, 'MED', False)
    mock_get_db_connection.return_value.__enter__.return_value = mock_conn

    meal = get_meal_by_id(1)

    expected_meal = Meal(id=1, meal='Meal1', cuisine='Italian', price=10.0, difficulty='MED')
    assert meal == expected_meal


@patch('meal_max.models.kitchen_model.get_db_connection')
def test_get_meal_by_id_not_found(mock_get_db_connection):
    mock_conn = MagicMock()
    mock_cursor = mock_conn.cursor.return_value
    mock_cursor.fetchone.return_value = None
    mock_get_db_connection.return_value.__enter__.return_value = mock_conn

    with pytest.raises(ValueError) as excinfo:
        get_meal_by_id(1)
    assert str(excinfo.value) == "Meal with ID 1 not found"


@patch('meal_max.models.kitchen_model.get_db_connection')
def test_get_meal_by_id_deleted(mock_get_db_connection):
    mock_conn = MagicMock()
    mock_cursor = mock_conn.cursor.return_value
    mock_cursor.fetchone.return_value = (1, 'Meal1', 'Italian', 10.0, 'MED', True)
    mock_get_db_connection.return_value.__enter__.return_value = mock_conn

    with pytest.raises(ValueError) as excinfo:
        get_meal_by_id(1)
    assert str(excinfo.value) == "Meal with ID 1 has been deleted"


@patch('meal_max.models.kitchen_model.get_db_connection')
def test_get_meal_by_id_database_error(mock_get_db_connection):
    mock_conn = MagicMock()
    mock_cursor = mock_conn.cursor.return_value
    mock_cursor.execute.side_effect = sqlite3.Error('Database error')
    mock_get_db_connection.return_value.__enter__.return_value = mock_conn

    with pytest.raises(sqlite3.Error) as excinfo:
        get_meal_by_id(1)
    assert str(excinfo.value) == 'Database error'


@patch('meal_max.models.kitchen_model.get_db_connection')
def test_get_meal_by_name_success(mock_get_db_connection):
    mock_conn = MagicMock()
    mock_cursor = mock_conn.cursor.return_value
    mock_cursor.fetchone.return_value = (1, 'Meal1', 'Italian', 10.0, 'MED', False)
    mock_get_db_connection.return_value.__enter__.return_value = mock_conn

    meal = get_meal_by_name('Meal1')

    expected_meal = Meal(id=1, meal='Meal1', cuisine='Italian', price=10.0, difficulty='MED')
    assert meal == expected_meal


@patch('meal_max.models.kitchen_model.get_db_connection')
def test_get_meal_by_name_not_found(mock_get_db_connection):
    mock_conn = MagicMock()
    mock_cursor = mock_conn.cursor.return_value
    mock_cursor.fetchone.return_value = None
    mock_get_db_connection.return_value.__enter__.return_value = mock_conn

    with pytest.raises(ValueError) as excinfo:
        get_meal_by_name('Meal1')
    assert str(excinfo.value) == "Meal with name Meal1 not found"


@patch('meal_max.models.kitchen_model.get_db_connection')
def test_get_meal_by_name_deleted(mock_get_db_connection):
    mock_conn = MagicMock()
    mock_cursor = mock_conn.cursor.return_value
    mock_cursor.fetchone.return_value = (1, 'Meal1', 'Italian', 10.0, 'MED', True)
    mock_get_db_connection.return_value.__enter__.return_value = mock_conn

    with pytest.raises(ValueError) as excinfo:
        get_meal_by_name('Meal1')
    assert str(excinfo.value) == "Meal with name Meal1 has been deleted"


@patch('meal_max.models.kitchen_model.get_db_connection')
def test_get_meal_by_name_database_error(mock_get_db_connection):
    mock_conn = MagicMock()
    mock_cursor = mock_conn.cursor.return_value
    mock_cursor.execute.side_effect = sqlite3.Error('Database error')
    mock_get_db_connection.return_value.__enter__.return_value = mock_conn

    with pytest.raises(sqlite3.Error) as excinfo:
        get_meal_by_name('Meal1')
    assert str(excinfo.value) == 'Database error'


@patch('meal_max.models.kitchen_model.get_db_connection')
def test_update_meal_stats_win(mock_get_db_connection):
    mock_conn = MagicMock()
    mock_cursor = mock_conn.cursor.return_value
    mock_cursor.fetchone.return_value = [False]
    mock_get_db_connection.return_value.__enter__.return_value = mock_conn

    update_meal_stats(1, 'win')

    calls = [
        (("SELECT deleted FROM meals WHERE id = ?", (1,)),),
        (("UPDATE meals SET battles = battles + 1, wins = wins + 1 WHERE id = ?", (1,)),)
    ]
    mock_cursor.execute.assert_has_calls(calls)
    mock_conn.commit.assert_called_once()


@patch('meal_max.models.kitchen_model.get_db_connection')
def test_update_meal_stats_loss(mock_get_db_connection):
    mock_conn = MagicMock()
    mock_cursor = mock_conn.cursor.return_value
    mock_cursor.fetchone.return_value = [False]
    mock_get_db_connection.return_value.__enter__.return_value = mock_conn

    update_meal_stats(1, 'loss')

    calls = [
        (("SELECT deleted FROM meals WHERE id = ?", (1,)),),
        (("UPDATE meals SET battles = battles + 1 WHERE id = ?", (1,)),)
    ]
    mock_cursor.execute.assert_has_calls(calls)
    mock_conn.commit.assert_called_once()


@patch('meal_max.models.kitchen_model.get_db_connection')
def test_update_meal_stats_invalid_result(mock_get_db_connection):
    # Set up the mock connection and cursor
    mock_conn = MagicMock()
    mock_cursor = mock_conn.cursor.return_value
    # Configure the mock to return a non-deleted meal
    mock_cursor.fetchone.return_value = [False]
    mock_get_db_connection.return_value.__enter__.return_value = mock_conn

    with pytest.raises(ValueError) as excinfo:
        update_meal_stats(1, 'draw')
    assert str(excinfo.value) == "Invalid result: draw. Expected 'win' or 'loss'."


@patch('meal_max.models.kitchen_model.get_db_connection')
def test_update_meal_stats_meal_not_found(mock_get_db_connection):
    mock_conn = MagicMock()
    mock_cursor = mock_conn.cursor.return_value
    mock_cursor.fetchone.return_value = None
    mock_get_db_connection.return_value.__enter__.return_value = mock_conn

    with pytest.raises(ValueError) as excinfo:
        update_meal_stats(1, 'win')
    assert str(excinfo.value) == "Meal with ID 1 not found"


@patch('meal_max.models.kitchen_model.get_db_connection')
def test_update_meal_stats_meal_deleted(mock_get_db_connection):
    mock_conn = MagicMock()
    mock_cursor = mock_conn.cursor.return_value
    mock_cursor.fetchone.return_value = [True]
    mock_get_db_connection.return_value.__enter__.return_value = mock_conn

    with pytest.raises(ValueError) as excinfo:
        update_meal_stats(1, 'win')
    assert str(excinfo.value) == "Meal with ID 1 has been deleted"


@patch('meal_max.models.kitchen_model.get_db_connection')
def test_update_meal_stats_database_error(mock_get_db_connection):
    mock_conn = MagicMock()
    mock_cursor = mock_conn.cursor.return_value
    mock_cursor.execute.side_effect = sqlite3.Error('Database error')
    mock_get_db_connection.return_value.__enter__.return_value = mock_conn

    with pytest.raises(sqlite3.Error) as excinfo:
        update_meal_stats(1, 'win')
    assert str(excinfo.value) == 'Database error'
