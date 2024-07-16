from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)
app.secret_key = 'super_secret_key'  

# Configure MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['location_app']
users_collection = db['users']


# Mock data for locations 
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

if __name__ == '__main__':
    app.run(debug=True)