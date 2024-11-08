import pytest
from meal_max.models.kitchen_model import Meal
from meal_max.models.kitchen_model import create_meal, clear_meals, delete_meal, get_leaderboard, get_meal_by_id, get_meal_by_name, update_meal_stats
from meal_max.utils.sql_utils import get_db_connection


##################################################
# Fixtures
##################################################

@pytest.fixture
def sample_meal():
    """Fixture for a sample meal."""
    return Meal(1, "Pizza", "Italian", 15.0, "MED")


@pytest.fixture
def sample_meal2():
    """Fixture for another sample meal."""
    return Meal(2, "Burger", "American", 12.0, "LOW")


@pytest.fixture
def db_connection():
    """Fixture to provide a database connection."""
    return get_db_connection()


##################################################
# Test Meal Dataclass Validation
##################################################

def test_meal_validation_valid():
    """Test that a valid Meal object can be created."""
    meal = Meal(1, "Sushi", "Japanese", 20.0, "HIGH")
    assert meal.meal == "Sushi"
    assert meal.price == 20.0
    assert meal.difficulty == "HIGH"


def test_meal_validation_invalid_price():
    """Test that a negative price raises a ValueError."""
    with pytest.raises(ValueError, match="Price must be a positive value"):
        Meal(1, "Sushi", "Japanese", -10.0, "HIGH")


def test_meal_validation_invalid_difficulty():
    """Test that an invalid difficulty raises a ValueError."""
    with pytest.raises(ValueError, match="Difficulty must be 'LOW', 'MED', or 'HIGH'"):
        Meal(1, "Sushi", "Japanese", 20.0, "EASY")


##################################################
# Test Database Operations
##################################################

def test_create_meal(db_connection):
    """Test creating a new meal in the database."""
    create_meal("Pasta", "Italian", 10.0, "LOW")
    with db_connection as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT meal FROM meals WHERE meal = 'Pasta'")
        result = cursor.fetchone()
        assert result[0] == "Pasta"


def test_create_meal_duplicate(db_connection):
    """Test creating a duplicate meal raises a ValueError."""
    create_meal("Pizza", "Italian", 15.0, "MED")
    with pytest.raises(ValueError, match="Meal with name 'Pizza' already exists"):
        create_meal("Pizza", "Italian", 15.0, "MED")


def test_clear_meals(db_connection):
    """Test clearing all meals."""
    create_meal("Pizza", "Italian", 15.0, "MED")
    clear_meals()
    with db_connection as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM meals")
        result = cursor.fetchone()
        assert result[0] == 0


def test_delete_meal(db_connection, sample_meal):
    """Test marking a meal as deleted."""
    create_meal(sample_meal.meal, sample_meal.cuisine, sample_meal.price, sample_meal.difficulty)
    delete_meal(1)
    with db_connection as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT deleted FROM meals WHERE id = 1")
        result = cursor.fetchone()
        assert result[0] is True


##################################################
# Test Leaderboard
##################################################

def test_get_leaderboard_sorted_by_wins(db_connection):
    """Test retrieving the leaderboard sorted by wins."""
    create_meal("Pizza", "Italian", 15.0, "MED")
    create_meal("Burger", "American", 12.0, "LOW")
    update_meal_stats(1, "win")
    update_meal_stats(1, "win")
    update_meal_stats(2, "win")
    leaderboard = get_leaderboard(sort_by="wins")
    assert leaderboard[0]["meal"] == "Pizza"
    assert leaderboard[1]["meal"] == "Burger"


def test_get_leaderboard_sorted_by_win_pct(db_connection):
    """Test retrieving the leaderboard sorted by win percentage."""
    create_meal("Pizza", "Italian", 15.0, "MED")
    create_meal("Burger", "American", 12.0, "LOW")
    update_meal_stats(1, "win")
    update_meal_stats(2, "loss")
    leaderboard = get_leaderboard(sort_by="win_pct")
    assert leaderboard[0]["meal"] == "Pizza"


##################################################
# Test Meal Retrieval
##################################################

def test_get_meal_by_id(db_connection, sample_meal):
    """Test retrieving a meal by its ID."""
    create_meal(sample_meal.meal, sample_meal.cuisine, sample_meal.price, sample_meal.difficulty)
    meal = get_meal_by_id(1)
    assert meal.meal == "Pizza"
    assert meal.price == 15.0

def test_get_meal_by_name(db_connection, sample_meal):
    """Test retrieving a meal by its name."""
    # Arrange: Create the sample meal in the database
    create_meal(sample_meal.meal, sample_meal.cuisine, sample_meal.price, sample_meal.difficulty)
    
    # Act: Retrieve the meal by its name
    meal = get_meal_by_name("Pizza")
    
    # Assert: Verify that the retrieved meal matches the created meal
    assert meal.meal == "Pizza"
    assert meal.cuisine == "Italian"
    assert meal.price == 15.0
    assert meal.difficulty == "MED"

                
def test_get_meal_by_name_not_found(db_connection):
    """Test retrieving a meal by name that does not exist raises a ValueError."""
    with pytest.raises(ValueError, match="Meal with name 'Nonexistent' not found"):
        get_meal_by_name("Nonexistent")

##################################################
# Test Update Meal Stats
##################################################

def test_update_meal_stats_win(db_connection, sample_meal):
    """Test updating the stats of a meal with a win."""
    create_meal(sample_meal.meal, sample_meal.cuisine, sample_meal.price, sample_meal.difficulty)
    update_meal_stats(1, "win")
    with db_connection as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT battles, wins FROM meals WHERE id = 1")
        result = cursor.fetchone()
        assert result[0] == 1  # Battles
        assert result[1] == 1  # Wins


def test_update_meal_stats_loss(db_connection, sample_meal):
    """Test updating the stats of a meal with a loss."""
    create_meal(sample_meal.meal, sample_meal.cuisine, sample_meal.price, sample_meal.difficulty)
    update_meal_stats(1, "loss")
    with db_connection as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT battles, wins FROM meals WHERE id = 1")
        result = cursor.fetchone()
        assert result[0] == 1  # Battles
        assert result[1] == 0  # Wins


def test_update_meal_stats_invalid_result(db_connection, sample_meal):
    """Test updating the stats of a meal with an invalid result raises a ValueError."""
    create_meal(sample_meal.meal, sample_meal.cuisine, sample_meal.price, sample_meal.difficulty)
    with pytest.raises(ValueError, match="Invalid result: invalid. Expected 'win' or 'loss'"):
        update_meal_stats(1, "invalid")