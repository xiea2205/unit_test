import pytest
from unittest.mock import patch

from meal_max.models.battle_model import BattleModel
from meal_max.models.kitchen_model import Meal

def test_prep_combatant_adds_combatant_correctly():
    battle_model = BattleModel()
    meal1 = Meal(id=1, meal='Meal1', price=10.0, cuisine='Italian', difficulty='MED')
    battle_model.prep_combatant(meal1)
    assert battle_model.get_combatants() == [meal1]


def test_prep_combatant_allows_two_combatants():
    battle_model = BattleModel()
    meal1 = Meal(id=1, meal='Meal1', price=10.0, cuisine='Italian', difficulty='MED')
    meal2 = Meal(id=2, meal='Meal2', price=15.0, cuisine='French', difficulty='LOW')
    battle_model.prep_combatant(meal1)
    battle_model.prep_combatant(meal2)
    assert battle_model.get_combatants() == [meal1, meal2]


def test_prep_combatant_raises_error_when_full():
    battle_model = BattleModel()
    meal1 = Meal(id=1, meal='Meal1', price=10.0, cuisine='Italian', difficulty='MED')
    meal2 = Meal(id=2, meal='Meal2', price=15.0, cuisine='French', difficulty='LOW')
    meal3 = Meal(id=3, meal='Meal3', price=12.0, cuisine='Mexican', difficulty='HIGH')
    battle_model.prep_combatant(meal1)
    battle_model.prep_combatant(meal2)
    with pytest.raises(ValueError) as excinfo:
        battle_model.prep_combatant(meal3)
    assert str(excinfo.value) == "Combatant list is full, cannot add more combatants."


def test_get_battle_score():
    battle_model = BattleModel()
    meal = Meal(id=1, meal='Meal1', price=10.0, cuisine='Italian', difficulty='MED')
    expected_score = (10.0 * len('Italian')) - 2 
    assert battle_model.get_battle_score(meal) == expected_score


def test_clear_combatants():
    battle_model = BattleModel()
    meal1 = Meal(id=1, meal='Meal1', price=10.0, cuisine='Italian', difficulty='MED')
    battle_model.prep_combatant(meal1)
    battle_model.clear_combatants()
    assert battle_model.get_combatants() == []


@patch('meal_max.models.battle_model.get_random')
@patch('meal_max.models.battle_model.update_meal_stats')
def test_battle_winner_when_delta_greater_than_random_number(mock_update_meal_stats, mock_get_random):
    battle_model = BattleModel()
    meal1 = Meal(id=1, meal='Meal1', price=10.0, cuisine='Italian', difficulty='MED')
    meal2 = Meal(id=2, meal='Meal2', price=15.0, cuisine='French', difficulty='LOW')
    battle_model.prep_combatant(meal1)
    battle_model.prep_combatant(meal2)

    # Mock get_random to return a value less than delta
    mock_get_random.return_value = 0.05  

    winner_name = battle_model.battle()

    # Expected winner is combatant_1 (meal1)
    assert winner_name == meal1.meal
    mock_update_meal_stats.assert_any_call(meal1.id, 'win')
    mock_update_meal_stats.assert_any_call(meal2.id, 'loss')
    assert battle_model.get_combatants() == [meal1]


@patch('meal_max.models.battle_model.get_random')
@patch('meal_max.models.battle_model.update_meal_stats')
def test_battle_winner_when_delta_less_than_random_number(mock_update_meal_stats, mock_get_random):
    battle_model = BattleModel()
    meal1 = Meal(id=1, meal='Meal1', price=10.0, cuisine='Italian', difficulty='MED')
    meal2 = Meal(id=2, meal='Meal2', price=15.0, cuisine='French', difficulty='LOW')
    battle_model.prep_combatant(meal1)
    battle_model.prep_combatant(meal2)

    # Mock get_random to return a value greater than delta
    mock_get_random.return_value = 0.2  

    winner_name = battle_model.battle()

    # Expected winner is combatant_2 (meal2)
    assert winner_name == meal2.meal
    mock_update_meal_stats.assert_any_call(meal2.id, 'win')
    mock_update_meal_stats.assert_any_call(meal1.id, 'loss')
    assert battle_model.get_combatants() == [meal2]


def test_battle_raises_error_with_less_than_two_combatants():
    battle_model = BattleModel()
    meal1 = Meal(id=1, meal='Meal1', price=10.0, cuisine='Italian', difficulty='MED')
    battle_model.prep_combatant(meal1)

    with pytest.raises(ValueError) as excinfo:
        battle_model.battle()
    assert str(excinfo.value) == "Two combatants must be prepped for a battle."


def test_battle_raises_error_with_no_combatants():
    battle_model = BattleModel()

    with pytest.raises(ValueError) as excinfo:
        battle_model.battle()
    assert str(excinfo.value) == "Two combatants must be prepped for a battle."
