#!/bin/bash

BASE_URL="http://localhost:5001/api"

ECHO_JSON=false

# Parse command-line arguments
while [ "$#" -gt 0 ]; do
  case $1 in
    --echo-json) ECHO_JSON=true ;;
    *) echo "Unknown parameter passed: $1"; exit 1 ;;
  esac
  shift
done


# Function to check the health of the service
check_health() {
  echo "Checking health status..."
  response=$(curl -s -w "%{http_code}" -X GET "$BASE_URL/health")
  http_status=${response: -3}
  response_body=${response::-3}

  if [ "$http_status" -eq 200 ]; then
    echo "Service is healthy."
  else
    echo "Health check failed. HTTP Status: $http_status"
    echo "Response: $response_body"
    exit 1
  fi
}

# Function to check the database connection
check_db() {
  echo "Checking database connection..."
  response=$(curl -s -w "%{http_code}" -X GET "$BASE_URL/db-check")
  http_status=${response: -3}
  response_body=${response::-3}

  if [ "$http_status" -eq 200 ]; then
    echo "Database connection is healthy."
  else
    echo "Database check failed. HTTP Status: $http_status"
    echo "Response: $response_body"
    exit 1
  fi
}


# Function to clear all meals
clear_meals() {
  echo "Clearing all meals..."
  response=$(curl -s -w "%{http_code}" -X DELETE "$BASE_URL/clear-meals")
  http_status=${response: -3}
  response_body=${response::-3}

  if [ "$http_status" -eq 200 ]; then
    echo "All meals cleared successfully."
  else
    echo "Failed to clear meals. HTTP Status: $http_status"
    echo "Response: $response_body"
    exit 1
  fi
}

# Function to create a meal
create_meal() {
  meal_name=$1
  cuisine=$2
  price=$3
  difficulty=$4

  echo "Creating meal: $meal_name..."
  response=$(curl -s -w "%{http_code}" -X POST "$BASE_URL/create-meal" -H "Content-Type: application/json" \
    -d "{\"meal\":\"$meal_name\", \"cuisine\":\"$cuisine\", \"price\":$price, \"difficulty\":\"$difficulty\"}")
  http_status=${response: -3}
  response_body=${response::-3}

  if [ "$http_status" -eq 201 ]; then
    echo "Meal created successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Meal JSON:"
      echo "$response_body" | jq .
    fi
  else
    echo "Failed to create meal. HTTP Status: $http_status"
    echo "Response: $response_body"
    exit 1
  fi
}

# Function to delete a meal by ID
delete_meal_by_id() {
  meal_id=$1

  echo "Deleting meal by ID ($meal_id)..."
  response=$(curl -s -w "%{http_code}" -X DELETE "$BASE_URL/delete-meal/$meal_id")
  http_status=${response: -3}
  response_body=${response::-3}

  if [ "$http_status" -eq 200 ]; then
    echo "Meal deleted successfully."
  else
    echo "Failed to delete meal. HTTP Status: $http_status"
    echo "Response: $response_body"
    exit 1
  fi
}

# Function to get a meal by ID
get_meal_by_id() {
  meal_id=$1

  echo "Getting meal by ID ($meal_id)..."
  response=$(curl -s -w "%{http_code}" -X GET "$BASE_URL/get-meal-by-id/$meal_id")
  http_status=${response: -3}
  response_body=${response::-3}

  if [ "$http_status" -eq 200 ]; then
    echo "Meal ID $meal_id retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Meal JSON:"
      echo "$response_body" | jq .
    fi
  else
    echo "Failed to get meal with ID $meal_id. HTTP Status: $http_status"
    echo "Response: $response_body"
    exit 1
  fi
}


# Function to prepare a combatant
prep_combatant() {
  meal_name=$1

  echo "Preparing combatant with Meal Name ($meal_name)..."
  response=$(curl -s -w "%{http_code}" -X POST "$BASE_URL/prep-combatant" \
    -H "Content-Type: application/json" \
    -d "{\"meal\": \"$meal_name\"}")
  http_status=${response: -3}
  response_body=${response::-3}

  if [ "$http_status" -eq 200 ]; then
    echo "Combatant prepared successfully."
  else
    echo "Failed to prepare combatant. HTTP Status: $http_status"
    echo "Response: $response_body"
    exit 1
  fi
}

# Function to start a battle
start_battle() {
  echo "Starting a battle..."
  response=$(curl -s -w "%{http_code}" -X GET "$BASE_URL/battle")
  http_status=${response: -3}
  response_body=${response::-3}

  if [ "$http_status" -eq 200 ]; then
    echo "Battle completed successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Battle Result JSON:"
      echo "$response_body" | jq .
    fi
  else
    echo "Failed to start battle. HTTP Status: $http_status"
    echo "Response: $response_body"
    exit 1
  fi
}

# Function to clear combatants
clear_combatants() {
  echo "Clearing combatants..."
  response=$(curl -s -w "%{http_code}" -X POST "$BASE_URL/clear-combatants")
  http_status=${response: -3}
  response_body=${response::-3}

  if [ "$http_status" -eq 200 ]; then
    echo "Combatants cleared successfully."
  else
    echo "Failed to clear combatants. HTTP Status: $http_status"
    echo "Response: $response_body"
    exit 1
  fi
}


# Function to get the leaderboard
get_leaderboard() {
  sort_by=$1
  echo "Getting leaderboard sorted by $sort_by..."
  response=$(curl -s -w "%{http_code}" -X GET "$BASE_URL/leaderboard?sort=$sort_by")
  http_status=${response: -3}
  response_body=${response::-3}

  if [ "$http_status" -eq 200 ]; then
    echo "Leaderboard retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Leaderboard JSON:"
      echo "$response_body" | jq .
    fi
  else
    echo "Failed to get leaderboard. HTTP Status: $http_status"
    echo "Response: $response_body"
    exit 1
  fi
}



check_health
check_db

clear_meals

create_meal "Spaghetti Bolognese" "Italian" 12.5 "MED"
create_meal "Sushi" "Japanese" 15.0 "HIGH"
create_meal "Tacos" "Mexican" 8.0 "LOW"
create_meal "Curry" "Indian" 10.0 "MED"
create_meal "Burger" "American" 9.0 "LOW"

get_meal_by_id 1
get_meal_by_id 2
get_meal_by_id 3
get_meal_by_id 4
get_meal_by_id 5

prep_combatant "Spaghetti Bolognese"
prep_combatant "Sushi"

start_battle

get_leaderboard "wins"

clear_combatants

prep_combatant "Tacos"
prep_combatant "Curry"

start_battle

get_leaderboard "win_pct"

delete_meal_by_id 5

get_meal_by_id 5 || echo "Meal ID 5 has been deleted successfully."

echo "Smoketest completed successfully!"
