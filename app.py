from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set a secret key for session management

# Configure MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['location_app']
users_collection = db['users']
bookings_collection = db['bookings']

# Mock data for locations (can be replaced with MongoDB data in a real application)
locations = [
    {'id': 1, 'title': 'UAE', 'image': 'images/location1.jpg', 'rating': 4.5, 'price': '1000.EUR/NIGHT', 'reviews': 120, 'description': "Welcome to the United Arab Emirates (UAE), a land of contrasts where tradition and modernity collide to create a captivating tapestry of experiences. From the shimmering skyscrapers of Dubai to the serene desert landscapes of Abu Dhabi, the UAE offers a wealth of attractions waiting to be discovered. Let's embark on a journey to explore the charms of this dynamic country."},
    {'id': 2, 'title': 'Amsterdam', 'image': 'images/location2.jpg', 'rating': 4.8, 'price': '500.EUR/NIGHT', 'reviews': 200, 'description': " Nestled in the heart of the Netherlands, Amsterdam is a city that effortlessly blends history, culture, and modernity. From its picturesque canals to its vibrant neighborhoods, Amsterdam offers a unique experience for every visitor. Whether you're strolling along the cobblestone streets, admiring the iconic architecture, or indulging in the diverse culinary scene, there's no shortage of things to discover in this enchanting city. "},
    {'id': 3, 'title': 'Italy', 'image': 'images/location3.jpg', 'rating': 4.2, 'price': '600.EUR/NIGHT', 'reviews': 90, 'description': " Venice, the floating city of Italy, boasts an engineering marvel that has enchanted visitors for centuries - the Grand Canal. This iconic waterway winds its way through the heart of Venice, serving as both a vital transportation route and a captivating symbol of the city's rich history and culture. From its graceful bridges to its majestic palazzos, the Grand Canal offers a journey through time, revealing the secrets of Venice's past and the enduring allure of its Venetian charm."},
    {'id': 4, 'title': 'Japan', 'image': 'images/location4.jpg', 'rating': 4.6, 'price': '1500.EUR/NIGHT', 'reviews': 150, 'description': "Welcome to Japan, a land of ancient traditions, modern innovation, and breathtaking natural beauty. From the bustling streets of Tokyo to the serene temples of Kyoto, Japan offers a wealth of experiences waiting to be discovered. Let's embark on a journey to explore the beauty and culture of this fascinating country."},
    {'id': 5, 'title': 'Los Angeles', 'image': 'images/location5.jpg', 'rating': 4.7, 'price': '2000.EUR/NIGHT', 'reviews': 180, 'description': "Welcome to the City of Angels, where dreams are made and stars shine bright against the backdrop of palm trees and endless sunshine. Los Angeles, often hailed as the entertainment capital of the world, offers a dazzling array of experiences for visitors from around the globe. From its iconic landmarks to its diverse neighborhoods, LA beckons with promises of adventure, discovery, and unforgettable memories."},
    {'id': 6, 'title': 'Mexico', 'image': 'images/location6.jpg', 'rating': 4.4, 'price': '1000.EUR/NIGHT', 'reviews': 100, 'description': " Bienvenidos a México! A land of vibrant colors, rich traditions, and unparalleled natural beauty. From the bustling streets of its vibrant cities to the tranquil shores of its pristine beaches, Mexico offers an enchanting tapestry of experiences waiting to be explored. Let's embark on a journey to discover the wonders of this captivating country."}
]

@app.route('/')
def index():
    query = request.args.get('query', '')
    sort = request.args.get('sort')
    template = request.args.get('template', 'index') 

    if sort == 'title_asc':
        locations_sorted = sorted(locations, key=lambda x: x['title'])
    elif sort == 'title_desc':
        locations_sorted = sorted(locations, key=lambda x: x['title'], reverse=True)
    else:
        locations_sorted = locations

    if query:
        locations_filtered = [loc for loc in locations_sorted if query.lower() in loc['title'].lower()]
    else:
        locations_filtered = locations_sorted

    return render_template(f'{template}.html', locations=locations_filtered, query=query, sort=sort)



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users_collection.find_one({'username': username, 'password': password})
        if user:
            session['username'] = username  # Store username in session
            return redirect(url_for('user', username=username))
        else:
            return render_template('login.html', error='Invalid username or password.')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        if users_collection.find_one({'username': username}):
            return render_template('signup.html', error='Username already exists.')
        users_collection.insert_one({'username': username, 'password': password, 'email': email, 'favorites': []})
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/user/<username>', methods=['GET', 'POST'])
def user(username):
    query = request.args.get('query', '')
    sort = request.args.get('sort', '')

    user = users_collection.find_one({'username': username})
    if not user:
        return redirect(url_for('login'))

    # Ensure 'favorites' field exists
    if 'favorites' not in user:
        user['favorites'] = []
        users_collection.update_one({'username': username}, {'$set': {'favorites': user['favorites']}})

    if request.method == 'POST':
        location_id = int(request.form.get('location_id'))
        if location_id in user['favorites']:
            user['favorites'].remove(location_id)
        else:
            user['favorites'].append(location_id)
        users_collection.update_one({'username': username}, {'$set': {'favorites': user['favorites']}})

    # Fetch bookings for the current user
    user_bookings = list(bookings_collection.find({'username': username}))

    if sort == 'title_asc':
        locations_sorted = sorted(locations, key=lambda x: x['title'])
    elif sort == 'title_desc':
        locations_sorted = sorted(locations, key=lambda x: x['title'], reverse=True)
    elif sort == 'favourite':
        locations_sorted = sorted(locations, key=lambda x: x['id'] in user['favorites'], reverse=True)
    else:
        locations_sorted = locations

    if query:
        locations_filtered = [loc for loc in locations_sorted if query.lower() in loc['title'].lower()]
    else:
        locations_filtered = locations_sorted

    return render_template('user.html', username=username, locations=locations_filtered, user_favorites=user['favorites'], bookings=user_bookings, query=query)

@app.route('/favorites')
def favorites():
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))
    
    user = users_collection.find_one({'username': username})
    # Ensure 'favorites' field exists
    if 'favorites' not in user:
        user['favorites'] = []
        users_collection.update_one({'username': username}, {'$set': {'favorites': user['favorites']}})
    
    favorite_locations = [loc for loc in locations if loc['id'] in user['favorites']]
    return render_template('favorites.html', favorite_locations=favorite_locations)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/location/<int:location_id>')
def location_detail(location_id):
    location = next((loc for loc in locations if loc['id'] == location_id), None)
    if location:
        return render_template('location_detail.html', location=location)
    else:
        return "Location not found", 404

@app.route('/save_booking', methods=['POST'])
def save_booking():
    booking_data = request.json
    booking_data['username'] = session.get('username')  # Add username to booking data
    bookings_collection.insert_one(booking_data)
    return jsonify({'message': 'Booking saved successfully'}), 200

@app.route('/bookings')
def bookings():
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))
    
    bookings_data = list(bookings_collection.find({'username': username}))
    return render_template('bookings.html', bookings=bookings_data)

@app.route('/delete_booking/<booking_id>', methods=['POST'])
def delete_booking(booking_id):
    try:
        # Convert booking_id from string to ObjectId
        booking_id = ObjectId(booking_id)
        # Delete the booking document from MongoDB
        result = bookings_collection.delete_one({'_id': booking_id})
        if result.deleted_count == 1:
            return redirect(url_for('bookings'))
        else:
            return "Booking not found", 404
    except Exception as e:
        return f"An error occurred: {e}", 500

if __name__ == '__main__':
    app.run(debug=True)
