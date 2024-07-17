from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)
app.secret_key = 'super_secret_key'  


client = MongoClient('mongodb://localhost:27017/')
db = client['location_app']
users_collection = db['users']
bookings_collection = db['bookings']


locations = [
    {'id': 1, 'title': 'America', 'image': 'images/location1.jpg', 'rating': 4.5, 'price': '$$', 'reviews': 120, 'description': "1111111111111111111111111111111111111111"},
    {'id': 2, 'title': 'Italy', 'image': 'images/location2.jpg', 'rating': 4.8, 'price': '$$$', 'reviews': 200, 'description': "2222222222222222222222222222222222222222222"},
    {'id': 3, 'title': 'Turkey', 'image': 'images/location3.jpg', 'rating': 4.2, 'price': '$$', 'reviews': 90, 'description': "3333333333333333333333333333333333333333333333"},
    {'id': 4, 'title': 'Germany', 'image': 'images/location4.jpg', 'rating': 4.6, 'price': '$$', 'reviews': 150, 'description': "44444444444444444444444444444444444444444444"},
    {'id': 5, 'title': 'Japan', 'image': 'images/location5.jpg', 'rating': 4.7, 'price': '$$$', 'reviews': 180, 'description': "55555555555555555555555555555555555555555555555"},
    {'id': 6, 'title': 'India', 'image': 'images/location6.jpg', 'rating': 4.4, 'price': '$', 'reviews': 100, 'description': "666666666666666666666666666666666666666666666666666666"}
]

@app.route('/')
def index():
    query = request.args.get('query', '')
    sort = request.args.get('sort')

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

    return render_template('index.html', locations=locations_filtered, query=query)

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
        return "Location not found", 

@app.route('/save_booking', methods=['POST'])
def save_booking():
    booking_data = request.json
    booking_data['username'] = session.get('username')  
    bookings_collection.insert_one(booking_data)
    return jsonify({'message': 'Booking saved successfully'}), 

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
        
        booking_id = ObjectId(booking_id)
        
        result = bookings_collection.delete_one({'_id': booking_id})
        if result.deleted_count == 1:
            return redirect(url_for('bookings'))
        else:
            return "Booking not found", 
    except Exception as e:
        return f"An error occurred: {e}", 

if __name__ == '__main__':
    app.run(debug=True)
