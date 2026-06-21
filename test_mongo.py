from mongoengine import connect

try:
    # Connect to MongoDB Atlas
    mongo_uri = 'mongodb+srv://Tejasri:Teja2007@mobilerecharge.raj1zpx.mongodb.net/signbridge?retryWrites=true&w=majority'
    connect('signbridge', host=mongo_uri)
    print("✅ MongoDB Atlas Connected Successfully!")
except Exception as e:
    print(f"❌ Connection Failed: {e}")
