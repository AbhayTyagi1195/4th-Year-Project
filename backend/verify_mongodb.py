"""
MongoDB Connection Verification Script
Tests actual read/write operations to verify cluster is active
"""

import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

def verify_mongodb_connection():
    """Comprehensive MongoDB verification"""
    print("=" * 60)
    print("🔍 MongoDB Connection Verification")
    print("=" * 60)
    
    mongodb_uri = os.getenv('MONGODB_URI')
    db_name = os.getenv('MONGODB_DB_NAME', 'medical_image_analysis_db')
    
    if not mongodb_uri:
        print("❌ MONGODB_URI not found in .env file")
        return False
    
    print(f"\n📋 Configuration:")
    print(f"   Database Name: {db_name}")
    print(f"   Connection String: {mongodb_uri[:30]}...{mongodb_uri[-20:]}")
    
    try:
        print("\n🔌 Step 1: Attempting connection...")
        client = MongoClient(
            mongodb_uri,
            serverSelectionTimeoutMS=15000,  # 15 seconds timeout
            connectTimeoutMS=15000,
            socketTimeoutMS=15000
        )
        
        print("✅ Client created")
        
        # Test 1: Ping server
        print("\n🏓 Step 2: Pinging MongoDB server...")
        result = client.admin.command('ping')
        print(f"✅ Ping successful: {result}")
        
        # Test 2: Get server info
        print("\n📊 Step 3: Fetching server information...")
        server_info = client.server_info()
        print(f"✅ MongoDB Version: {server_info.get('version')}")
        
        # Test 3: Access database
        print(f"\n💾 Step 4: Accessing database '{db_name}'...")
        db = client[db_name]
        print("✅ Database accessed")
        
        # Test 4: List collections
        print("\n📚 Step 5: Listing collections...")
        collections = db.list_collection_names()
        if collections:
            print(f"✅ Found {len(collections)} collections:")
            for coll in collections:
                count = db[coll].count_documents({})
                print(f"   - {coll}: {count} documents")
        else:
            print("⚠️ No collections found (database might be new)")
        
        # Test 5: Write test
        print("\n✍️ Step 6: Testing WRITE operation...")
        test_collection = db.connection_test
        test_doc = {
            'test': True,
            'timestamp': datetime.utcnow(),
            'message': 'Connection verification test'
        }
        insert_result = test_collection.insert_one(test_doc)
        print(f"✅ Write successful! Document ID: {insert_result.inserted_id}")
        
        # Test 6: Read test
        print("\n📖 Step 7: Testing READ operation...")
        read_doc = test_collection.find_one({'_id': insert_result.inserted_id})
        print(f"✅ Read successful! Document: {read_doc}")
        
        # Test 7: Delete test
        print("\n🗑️ Step 8: Testing DELETE operation...")
        delete_result = test_collection.delete_one({'_id': insert_result.inserted_id})
        print(f"✅ Delete successful! Deleted count: {delete_result.deleted_count}")
        
        # Test 8: Check cluster status
        print("\n🔍 Step 9: Checking cluster status...")
        build_info = client.admin.command('buildInfo')
        print(f"✅ Cluster is ACTIVE and responding")
        print(f"   Build Info: {build_info.get('version')}")
        
        # Final summary
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED - MongoDB is FULLY OPERATIONAL")
        print("=" * 60)
        
        # Database statistics
        print("\n📊 Database Statistics:")
        stats = db.command('dbStats')
        print(f"   Collections: {stats.get('collections', 0)}")
        print(f"   Data Size: {stats.get('dataSize', 0) / 1024:.2f} KB")
        print(f"   Storage Size: {stats.get('storageSize', 0) / 1024:.2f} KB")
        
        client.close()
        return True
        
    except ServerSelectionTimeoutError as e:
        print("\n❌ CONNECTION TIMEOUT")
        print("⚠️ Cluster might be PAUSED or network issue")
        print(f"   Error: {e}")
        print("\n💡 Solutions:")
        print("   1. Go to MongoDB Atlas dashboard")
        print("   2. Check if cluster shows as 'Paused'")
        print("   3. Click 'Resume' to activate the cluster")
        print("   4. Wait 1-2 minutes for cluster to wake up")
        return False
        
    except ConnectionFailure as e:
        print("\n❌ CONNECTION FAILED")
        print(f"   Error: {e}")
        print("\n💡 Check:")
        print("   1. MongoDB URI in .env file")
        print("   2. Network connectivity")
        print("   3. MongoDB Atlas IP whitelist (0.0.0.0/0 for testing)")
        return False
        
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {type(e).__name__}")
        print(f"   Details: {e}")
        return False

if __name__ == "__main__":
    verify_mongodb_connection()
