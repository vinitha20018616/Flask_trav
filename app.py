from flask import Flask
from pymongo import MongoClient

app = Flask(__name__)

# Setup MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['mydatabase']
collection = db['mycollection']

@app.route('/')
def home():
    return "Welcome to the Flask MongoDB app!"

@app.route('/test_db_connection')
def test_db_connection():
    try:
        # Test the MongoDB connection
        client.admin.command('ping')
        return "MongoDB connection successful!", 200
    except Exception as e:
        return f"Failed to connect to MongoDB: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True)
