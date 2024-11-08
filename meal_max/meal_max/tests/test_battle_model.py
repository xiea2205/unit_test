import pytest

from music_collection.models.playlist_model import PlaylistModel
from music_collection.models.song_model import Song

@pytest.fixture
def battle_model():
    return BattleModel()

@pytest.fixture
def sample_meal():
    return Meal(1, "Pizza", "Italian", 15.0, "MED")

@pytest.fixture
def sample_meal2():
    return Meal(2, "Burger", "American", 12.0, "LOW")

@pytest.fixture
def sample_meal3():
    return Meal(3, "Sushi", "Japanese", 20.0, "HIGH")




##################################################
# Test cases get battle score
##################################################
def test_get_battle_score_standard(battle_model, sample_meal):
    """Test standard battle score calculation."""
    score = battle_model.get_battle_score(sample_meal)
    expected_score = (sample_meal.price * len(sample_meal.cuisine)) - 2  # MED difficulty
    assert score == expected_score

def test_get_battle_score_empty_cuisine(battle_model):
    """Test battle score with empty cuisine."""
    empty_cuisine_meal = Meal(2, "Empty Cuisine Meal", "", 10.0, "MED")
    score = battle_model.get_battle_score(empty_cuisine_meal)
    expected_score = (10.0 * 0) - 2
    assert score == expected_score

##################################################
# Test cases battle
##################################################
def test_battle_standard(battle_model, sample_meal, sample_meal2):
    """Test standard battle execution with a clear winner."""
    battle_model.prep_combatant(sample_meal)
    battle_model.prep_combatant(sample_meal2)
    winner = battle_model.battle()
    assert winner in [sample_meal.meal, sample_meal2.meal]

def test_battle_not_enough_combatants(battle_model, sample_meal):
    """Test battle raises ValueError if fewer than two combatants."""
    battle_model.prep_combatant(sample_meal)
    with pytest.raises(ValueError, match="Two combatants must be prepped for a battle"):
        battle_model.battle()

##################################################
# Test clear combatans
##################################################
def test_clear_combatants(battle_model, sample_meal, sample_meal2):
    """Test clearing the combatants list."""
    battle_model.prep_combatant(sample_meal)
    battle_model.prep_combatant(sample_meal2)
    battle_model.clear_combatants()
    assert len(battle_model.combatants) == 0

##################################################
# Test get combatans
##################################################
def test_get_combatants(battle_model, sample_meal, sample_meal2):
    """Test retrieving the current list of combatants."""
    battle_model.prep_combatant(sample_meal)
    battle_model.prep_combatant(sample_meal2)
    combatants = battle_model.get_combatants()
    assert combatants[0].meal == sample_meal.meal
    assert combatants[1].meal == sample_meal2.meal
