from flask import Blueprint, request, jsonify
from datetime import datetime
from bson import ObjectId
import re
from config.database import get_database
from utils.auth import hash_password, verify_password, generate_token

auth_bp = Blueprint('auth', __name__)

# Email validation regex
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['username', 'email', 'password', 'fullName']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field} is required'}), 400
        
        username = data['username'].strip()
        email = data['email'].strip().lower()
        password = data['password']
        full_name = data['fullName'].strip()
        
        # Validate username
        if len(username) < 3:
            return jsonify({'error': 'Username must be at least 3 characters long'}), 400
        
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            return jsonify({'error': 'Username can only contain letters, numbers, and underscores'}), 400
        
        # Validate email
        if not EMAIL_REGEX.match(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Validate password
        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters long'}), 400
        
        # Get database
        db = get_database()
        
        # Check if username already exists
        if db.users.find_one({'username': username}):
            return jsonify({'error': 'Username already exists'}), 409
        
        # Check if email already exists
        if db.users.find_one({'email': email}):
            return jsonify({'error': 'Email already registered'}), 409
        
        # Hash password
        hashed_password = hash_password(password)
        
        # Create user document
        user_doc = {
            'username': username,
            'email': email,
            'password': hashed_password,
            'fullName': full_name,
            'role': 'user',
            'isActive': True,
            'createdAt': datetime.utcnow(),
            'lastLogin': None
        }
        
        # Insert user
        result = db.users.insert_one(user_doc)
        user_id = result.inserted_id
        
        # Log registration
        db.audit_logs.insert_one({
            'userId': user_id,
            'username': username,
            'action': 'register',
            'ipAddress': request.remote_addr,
            'userAgent': request.headers.get('User-Agent'),
            'timestamp': datetime.utcnow(),
            'details': {'email': email}
        })
        
        return jsonify({
            'message': 'Registration successful! Please login.',
            'username': username,
            'email': email
        }), 201
        
    except Exception as e:
        print(f"Registration error: {e}")
        return jsonify({'error': 'Registration failed. Please try again.'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user and return JWT token"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('username') or not data.get('password'):
            return jsonify({'error': 'Username and password are required'}), 400
        
        username = data['username'].strip()
        password = data['password']
        
        # Get database
        db = get_database()
        
        # Find user
        user = db.users.find_one({'username': username})
        
        if not user:
            return jsonify({'error': 'Invalid username or password'}), 401
        
        # Check if account is active
        if not user.get('isActive', True):
            return jsonify({'error': 'Account is deactivated. Please contact support.'}), 403
        
        # Verify password
        if not verify_password(password, user['password']):
            return jsonify({'error': 'Invalid username or password'}), 401
        
        # Update last login
        db.users.update_one(
            {'_id': user['_id']},
            {'$set': {'lastLogin': datetime.utcnow()}}
        )
        
        # Generate JWT token
        token = generate_token(user['_id'], user['username'], user['email'])
        
        # Log login
        db.audit_logs.insert_one({
            'userId': user['_id'],
            'username': user['username'],
            'action': 'login',
            'ipAddress': request.remote_addr,
            'userAgent': request.headers.get('User-Agent'),
            'timestamp': datetime.utcnow(),
            'details': {}
        })
        
        return jsonify({
            'message': 'Login successful!',
            'token': token,
            'user': {
                'id': str(user['_id']),
                'username': user['username'],
                'email': user['email'],
                'fullName': user['fullName'],
                'role': user.get('role', 'user')
            }
        }), 200
        
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({'error': 'Login failed. Please try again.'}), 500

@auth_bp.route('/verify', methods=['GET'])
def verify_token():
    """Verify if token is valid"""
    from utils.auth import decode_token
    
    try:
        # Get token from header
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'valid': False, 'error': 'No token provided'}), 401
        
        try:
            token = auth_header.split(" ")[1]
        except IndexError:
            return jsonify({'valid': False, 'error': 'Invalid token format'}), 401
        
        # Decode token
        payload = decode_token(token)
        
        if not payload:
            return jsonify({'valid': False, 'error': 'Invalid or expired token'}), 401
        
        return jsonify({
            'valid': True,
            'user': {
                'id': payload['user_id'],
                'username': payload['username'],
                'email': payload['email']
            }
        }), 200
        
    except Exception as e:
        return jsonify({'valid': False, 'error': str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logout user (client-side token removal)"""
    from utils.auth import decode_token
    
    try:
        # Get token if available
        auth_header = request.headers.get('Authorization')
        if auth_header:
            try:
                token = auth_header.split(" ")[1]
                payload = decode_token(token)
                
                if payload:
                    # Log logout
                    db = get_database()
                    db.audit_logs.insert_one({
                        'userId': ObjectId(payload['user_id']),
                        'username': payload['username'],
                        'action': 'logout',
                        'ipAddress': request.remote_addr,
                        'userAgent': request.headers.get('User-Agent'),
                        'timestamp': datetime.utcnow(),
                        'details': {}
                    })
            except:
                pass
        
        return jsonify({'message': 'Logout successful'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    # ...existing code...

@auth_bp.route('/profile/update', methods=['PUT'])
def update_profile():
    """Update user profile (email, fullName, password)"""
    from utils.auth import token_required
    
    @token_required
    def _update():
        try:
            data = request.get_json()
            user_id = ObjectId(request.current_user['user_id'])
            
            db = get_database()
            user = db.users.find_one({'_id': user_id})
            
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            update_data = {}
            
            # Update fullName if provided
            if 'fullName' in data and data['fullName']:
                full_name = data['fullName'].strip()
                if len(full_name) < 2:
                    return jsonify({'error': 'Full name must be at least 2 characters'}), 400
                update_data['fullName'] = full_name
            
            # Update email if provided
            if 'email' in data and data['email']:
                new_email = data['email'].strip().lower()
                
                if not EMAIL_REGEX.match(new_email):
                    return jsonify({'error': 'Invalid email format'}), 400
                
                if new_email != user['email']:
                    if db.users.find_one({'email': new_email}):
                        return jsonify({'error': 'Email already registered'}), 409
                
                update_data['email'] = new_email
            
            # Update password if provided
            if 'oldPassword' in data and 'newPassword' in data:
                old_password = data['oldPassword']
                new_password = data['newPassword']
                
                if not verify_password(old_password, user['password']):
                    return jsonify({'error': 'Current password is incorrect'}), 401
                
                if len(new_password) < 6:
                    return jsonify({'error': 'Password must be at least 6 characters'}), 400
                
                update_data['password'] = hash_password(new_password)
            
            if not update_data:
                return jsonify({'error': 'No fields to update'}), 400
            
            update_data['updatedAt'] = datetime.utcnow()
            
            result = db.users.update_one(
                {'_id': user_id},
                {'$set': update_data}
            )
            
            db.audit_logs.insert_one({
                'userId': user_id,
                'username': user['username'],
                'action': 'profile_update',
                'ipAddress': request.remote_addr,
                'userAgent': request.headers.get('User-Agent'),
                'timestamp': datetime.utcnow(),
                'details': {'fieldsUpdated': list(update_data.keys())}
            })
            
            updated_user = db.users.find_one({'_id': user_id})
            
            return jsonify({
                'message': 'Profile updated successfully',
                'user': {
                    'id': str(updated_user['_id']),
                    'username': updated_user['username'],
                    'email': updated_user['email'],
                    'fullName': updated_user['fullName'],
                    'role': updated_user.get('role', 'user')
                }
            }), 200
            
        except Exception as e:
            print(f"Profile update error: {e}")
            return jsonify({'error': 'Failed to update profile'}), 500
    
    return _update()


@auth_bp.route('/account/delete', methods=['DELETE'])
def delete_account():
    """Delete user account and all associated data"""
    from utils.auth import token_required
    
    @token_required
    def _delete():
        try:
            data = request.get_json() or {}
            user_id = ObjectId(request.current_user['user_id'])
            
            db = get_database()
            user = db.users.find_one({'_id': user_id})
            
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            if 'password' not in data:
                return jsonify({'error': 'Password required to delete account'}), 400
            
            password = data['password']
            
            if not verify_password(password, user['password']):
                return jsonify({'error': 'Invalid password. Account deletion cancelled.'}), 401
            
            username = user['username']
            
            db.audit_logs.insert_one({
                'userId': user_id,
                'username': username,
                'action': 'account_deleted',
                'ipAddress': request.remote_addr,
                'userAgent': request.headers.get('User-Agent'),
                'timestamp': datetime.utcnow(),
                'details': {
                    'email': user['email'],
                    'fullName': user['fullName']
                }
            })
            
            db.predictions.delete_many({'userId': user_id})
            db.batch_results.delete_many({'userId': user_id})
            db.users.delete_one({'_id': user_id})
            
            return jsonify({
                'message': 'Account deleted successfully. All associated data has been removed.',
                'deletedData': {
                    'username': username,
                    'email': user['email'],
                    'deletionTime': datetime.utcnow().isoformat()
                }
            }), 200
            
        except Exception as e:
            print(f"Account deletion error: {e}")
            return jsonify({'error': 'Failed to delete account'}), 500
    
    return _delete()