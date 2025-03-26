import os
import sys
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

# Load environment variables
load_dotenv()

# Get MongoDB URI from environment
mongodb_uri = os.getenv('MONGODB_URI')

print(f"Using connection string: {mongodb_uri}")

try:
    # Connect to MongoDB with a timeout
    print("Attempting to connect to MongoDB...")
    client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)  # 5 second timeout
    
    # Force a connection to verify it works
    print("Testing connection...")
    server_info = client.server_info()
    
    print("✅ Successfully connected to MongoDB!")
    print(f"Server version: {server_info.get('version')}")
    
    # Create a test document to verify write access
    db = client.get_database()  # This will use the database specified in the URI
    print(f"Database name: {db.name}")
    
    print("Testing write access...")
    result = db.test_collection.insert_one({"test": "document"})
    print(f"✅ Successfully wrote test document with ID: {result.inserted_id}")
    
    # Clean up the test document
    print("Cleaning up...")
    db.test_collection.delete_one({"_id": result.inserted_id})
    print("✅ Successfully deleted test document")
    
except ConnectionFailure as e:
    print(f"❌ Failed to connect to MongoDB: {e}")
    sys.exit(1)
except ServerSelectionTimeoutError as e:
    print(f"❌ Connection timed out: {e}")
    print("This could be due to network issues, incorrect credentials, or firewall settings.")
    sys.exit(1)
except Exception as e:
    print(f"❌ An error occurred: {e}")
    sys.exit(1)
finally:
    # Close connection
    if 'client' in locals():
        print("Closing connection...")
        client.close()
        print("Connection closed")

print("Script completed successfully")