# Import necessary modules
from flask import Flask, render_template, request, jsonify
from pulp import LpVariable, LpProblem, lpSum, LpMinimize, LpStatus, value, LpContinuous
import requests

# Create a Flask app instance
app = Flask(__name__)

# My Google API key
GOOGLE_API_KEY = '<Enter API Key>'

# Function to get coordinates for a given address using Google Maps API
def get_coordinates(address):
    url = f'https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={GOOGLE_API_KEY}'
    response = requests.get(url)
    data = response.json()
    if 'results' in data and data['results']:
        location = data['results'][0]['geometry']['location']
        coordinates = location['lat'], location['lng']
        return coordinates
    else:
        print(f"Unable to find coordinates for address: {address}")
        return None

# Function to get driving distance in miles between two sets of coordinates using Google Maps API
def get_driving_distance_in_miles(origin, destination):
    url = f"https://maps.googleapis.com/maps/api/directions/json?origin={origin[0]},{origin[1]}&destination={destination[0]},{destination[1]}&key={GOOGLE_API_KEY}"
    response = requests.get(url)
    data = response.json()
    if 'routes' in data and data['routes'] and 'legs' in data['routes'][0] and data['routes'][0]['legs']:
        return data['routes'][0]['legs'][0]['distance']['value'] * 0.000621371
    else:
        print("Unable to retrieve driving distance.")
        return None

# Function to get driving duration between two sets of coordinates using Google Maps API
def get_driving_duration(origin, destination):
    url = f"https://maps.googleapis.com/maps/api/directions/json?origin={origin[0]},{origin[1]}&destination={destination[0]},{destination[1]}&key={GOOGLE_API_KEY}"
    response = requests.get(url)
    data = response.json()
    if 'routes' in data and data['routes'] and 'legs' in data['routes'][0] and data['routes'][0]['legs']:
        return data['routes'][0]['legs'][0]['duration']['value']
    else:
        print("Unable to retrieve driving duration.")
        return None

# Function to calculate estimated fuel cost
def calculate_estimated_fuel_cost(total_distance, vehicle_mpg, gas_price):
    return round((total_distance / vehicle_mpg) * gas_price, 2)

# Function to generate Google Maps URL based on the ordered path
def generate_map_url(ordered_path):
    waypoints = []
    for address, _ in ordered_path:
        coords = get_coordinates(address)
        if coords:
            waypoints.append(f"{coords[0]},{coords[1]}")

    origin = waypoints[0]
    waypoints_str = "|".join(waypoints[1:])
    url = f"https://www.google.com/maps/embed/v1/directions?key={GOOGLE_API_KEY}&origin={origin}&destination={origin}&waypoints={waypoints_str}&mode=driving"
    return url

# Function to get turn-by-turn directions between two sets of coordinates using Google Maps API
def get_turn_by_turn_directions(origin, destination):
    url = f"https://maps.googleapis.com/maps/api/directions/json?origin={origin[0]},{origin[1]}&destination={destination[0]},{destination[1]}&key={GOOGLE_API_KEY}"
    response = requests.get(url)
    data = response.json()
    if 'routes' in data and data['routes'] and 'legs' in data['routes'][0] and data['routes'][0]['legs']:
        directions = []
        for step in data['routes'][0]['legs'][0]['steps']:
            direction_text = step['html_instructions']
            distance_text = step['distance']['text']
            directions.append((direction_text, distance_text))  # Append direction and distance tuple
        return directions
    else:
        print("Unable to retrieve turn-by-turn directions.")
        return None


# Define the default route to render the index.html template
@app.route('/')
def index():
    return render_template('index.html')

# Define the route to handle the optimization problem
@app.route('/solve', methods=['POST'])
def solve():
    # Get form data from the request
    minimize_choice = request.form['minimizeChoice']
    starting_address = request.form['startingAddress']
    addresses = {key: request.form[f'address{key}'] for key in range(2, 10) if request.form.get(f'address{key}')}

    # Convert addresses to coordinates for processing
    coords = {1: (starting_address, get_coordinates(starting_address))}
    coords.update({key: (address, get_coordinates(address)) for key, address in addresses.items()})

    # Create binary variables for each pair of coordinates
    x = LpVariable.dicts("x", [(i, j) for i in coords for j in coords if i != j], cat="Binary")

    # Create the Linear Programming problem
    prob = LpProblem("ShortestPath", LpMinimize)
    
    # Calculate driving distance and duration for each pair of coordinates
    distances = {(i, j): get_driving_distance_in_miles(coords[i][1], coords[j][1]) for i in coords for j in coords if i != j}
    durations = {(i, j): get_driving_duration(coords[i][1], coords[j][1]) for i in coords for j in coords if i != j}

    # Define variables for total distance and total duration
    total_distance = LpVariable("TotalDistance", lowBound=0, cat="Continuous")
    total_duration = LpVariable("TotalDuration", lowBound=0, cat="Continuous")

    # Objective function: minimize total driving time or distance
    if minimize_choice == 'time':
        prob += total_duration
        for i, j in distances:
            prob += total_duration >= durations[i, j] * x[i, j]  # Minimize total driving time
    elif minimize_choice == 'distance':
        prob += total_distance
        for i, j in distances:
            prob += total_distance >= distances[i, j] * x[i, j]  # Minimize total driving distance

    # Constraints for outgoing and incoming edges
    for j in coords:
        outgoing_sum = lpSum([x[i, j] for i in coords if i != j])
        prob += outgoing_sum == 1
        incoming_sum = lpSum([x[j, i] for i in coords if i != j])
        prob += incoming_sum == 1

    # Subtour elimination constraints
    n = len(coords)
    u = LpVariable.dicts("u", [i for i in coords], lowBound=1, upBound=n, cat="Integer")
    for i in coords:
        for j in coords:
            if i != j and (i != 1 and j != 1):
                prob += u[i] - u[j] + n * x[i, j] <= n - 1

    # Solve the Linear Programming problem
    prob.solve()

    # Extract the ordered path from the solution
    current_node = 1
    ordered_path = []
    turn_by_turn_directions = []
    while True:
        next_node = [j for j in coords if j != current_node and x[current_node, j].value() == 1][0]
        ordered_path.append((coords[current_node][0], coords[next_node][0]))

        # Fetch turn-by-turn directions from Google Maps API
        directions = get_turn_by_turn_directions(coords[current_node][1], coords[next_node][1])
        turn_by_turn_directions.append(directions)

        current_node = next_node
        if current_node == 1:
            break

    # Calculate total distance and duration
    total_distance_value = sum(distances[i, j] for i, j in distances if x[i, j].value() == 1)
    total_duration_value = sum(durations[i, j] for i, j in durations if x[i, j].value() == 1)

    # Calculate estimated fuel cost
    vehicle_mpg = float(request.form['vehicleMPG'])
    gas_price = float(request.form['gasPrice'])
    estimated_fuel_cost = calculate_estimated_fuel_cost(total_distance_value, vehicle_mpg, gas_price)

    # Get the Google Maps URL for displaying the route
    map_url = generate_map_url(ordered_path)

    # Prepare the result as a JSON object
    result = {
        "status": LpStatus[prob.status],
        "total_distance": round(total_distance_value, 2),
        "total_duration": round(total_duration_value / 3600, 2),  # convert seconds to hours
        "estimated_fuel_cost": estimated_fuel_cost,
        "ordered_path": ordered_path,
        "turn_by_turn_directions": turn_by_turn_directions,
        "map_url": map_url,
    }

    # Return the result as JSON
    return jsonify(result)

# Run the Flask app if this script is executed
if __name__ == '__main__':
    app.run(debug=True, port=5003)
