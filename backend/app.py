from flask import Flask, request, jsonify, render_template, Response
from flask_cors import CORS
from dotenv import load_dotenv
import os
import json

# Load environment variables
load_dotenv()

# Import blueprints
from routes.auth_routes import auth_bp
from routes.report_routes import report_bp
from routes.brain_tumor_routes import brain_tumor_bp
from routes.covid_19_routes import covid_19_bp
from config.database import get_database

# Initialize Flask app
app = Flask(__name__)

# Configuration from environment variables
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# CORS Configuration
allowed_origins = os.getenv('ALLOWED_ORIGINS', 'http://localhost:5173').split(',')
CORS(app, resources={
    r"/api/*": {
        "origins": allowed_origins,
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "expose_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

# Create necessary directories
os.makedirs('uploads/brain_tumor', exist_ok=True)
os.makedirs('uploads/covid_19', exist_ok=True)
os.makedirs('models', exist_ok=True)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(report_bp)
app.register_blueprint(brain_tumor_bp, url_prefix='/api/brain_tumor')
app.register_blueprint(covid_19_bp, url_prefix='/api/covid_19')

# ============================================================================
# ROOT ENDPOINT - API DOCUMENTATION
# ============================================================================

@app.route('/', methods=['GET'])
def index():
    """Complete API Documentation"""
    api_info = {
        "title": "Medical Image Analysis System API",
        "description": "Multi-Disease Classification System (Brain Tumor & COVID-19 Detection) with Authentication & Analytics",
        "version": "3.0.0",

        # ============================================================
        # AUTHENTICATION ENDPOINTS
        # ============================================================
        "authentication": {
            "required": "Yes - JWT Token required for prediction endpoints",
            "token_format": "Bearer <your_jwt_token>",
            "endpoints": {
                "POST /api/auth/register": {
                    "description": "Register new user account",
                    "body": {
                        "username": "string (required, min 3 chars)",
                        "email": "string (required, valid email)",
                        "password": "string (required, min 6 chars)",
                        "fullName": "string (required)"
                    },
                    "response": "User object with username, email",
                    "protected": False
                },
                "POST /api/auth/login": {
                    "description": "Login and receive JWT token",
                    "body": {
                        "username": "string (required)",
                        "password": "string (required)"
                    },
                    "response": "JWT token + user object",
                    "protected": False
                },
                "GET /api/auth/verify": {
                    "description": "Verify if JWT token is valid",
                    "headers": {"Authorization": "Bearer <token>"},
                    "response": "Token validity status",
                    "protected": True
                },
                "POST /api/auth/logout": {
                    "description": "Logout user (client-side token removal)",
                    "headers": {"Authorization": "Bearer <token>"},
                    "response": "Logout confirmation",
                    "protected": False
                },
                "PUT /api/auth/profile/update": {
                    "description": "Update user profile (email, fullName, password)",
                    "body": {
                        "email": "string (optional)",
                        "fullName": "string (optional)",
                        "oldPassword": "string (required if changing password)",
                        "newPassword": "string (required if changing password)"
                    },
                    "response": "Updated user object",
                    "protected": True
                },
                "DELETE /api/auth/account/delete": {
                    "description": "Permanently delete user account and all data",
                    "body": {"password": "string (required for confirmation)"},
                    "response": "Deletion confirmation",
                    "protected": True
                }
            }
        },
        
        # ============================================================
        # BRAIN TUMOR ENDPOINTS
        # ============================================================
        "brain_tumor_endpoints": {
            "prediction": {
                "POST /api/brain_tumor/predict": {
                    "description": "Single brain MRI scan analysis",
                    "body": "multipart/form-data with 'image' file",
                    "headers": {"Authorization": "Bearer <token>"},
                    "response": "Prediction, confidence, medical info",
                    "protected": True
                },
                "POST /api/brain_tumor/predict/batch": {
                    "description": "Batch brain MRI scan analysis (multiple images)",
                    "body": "multipart/form-data with 'images[]' files",
                    "headers": {"Authorization": "Bearer <token>"},
                    "response": "Array of predictions + batch summary",
                    "protected": True
                }
            },
            "history_and_analytics": {
                "GET /api/brain_tumor/history": {
                    "description": "Get user's prediction history",
                    "query_params": {"limit": "integer (default: 20)"},
                    "headers": {"Authorization": "Bearer <token>"},
                    "response": "Array of past predictions",
                    "protected": True
                },
                "GET /api/brain_tumor/analytics": {
                    "description": "Get user's analytics summary",
                    "headers": {"Authorization": "Bearer <token>"},
                    "response": "Statistics by tumor type, counts, trends",
                    "protected": True
                }
            },
            "research_and_visualization": {
                "GET /api/brain_tumor/results/charts": {
                    "description": "Generate research charts (bar, pie, timeline)",
                    "response": "Base64 encoded chart images",
                    "protected": False
                },
                "GET /api/brain_tumor/results/statistics": {
                    "description": "Get statistical analysis",
                    "response": "Mean, std, confidence distribution",
                    "protected": False
                }
            },
            "utility": {
                "GET /api/brain_tumor/classes": {
                    "description": "Get tumor class labels and descriptions",
                    "response": "Array of classes with descriptions",
                    "protected": False
                },
                "GET /api/brain_tumor/model/info": {
                    "description": "Get model architecture information",
                    "response": "Model type, parameters, input size",
                    "protected": False
                },
                "POST /api/brain_tumor/debug/prediction": {
                    "description": "Debug prediction with detailed output",
                    "body": "multipart/form-data with 'image' file",
                    "response": "Raw predictions, probabilities, debug info",
                    "protected": False
                },
                "GET /api/brain_tumor/debug/class-order": {
                    "description": "Show class interpretation order",
                    "response": "Class labels and indices",
                    "protected": False
                }
            },
            "reports": {
                "POST /api/brain_tumor/report": {
                    "description": "Generate PDF medical report",
                    "body": {
                        "username": "string (required)",
                        "prediction": "string (required)",
                        "confidence": "number (required)",
                        "image_path": "string (optional)"
                    },
                    "headers": {"Authorization": "Bearer <token>"},
                    "response": "PDF file download",
                    "protected": True
                }
            },
            "web_interface": {
                "GET /test/brain_tumor": {
                    "description": "Interactive web testing interface",
                    "response": "HTML page for testing predictions",
                    "protected": False
                },
                "GET /api/brain_tumor/uploads/<filename>": {
                    "description": "Serve uploaded brain tumor images",
                    "response": "Image file",
                    "protected": False
                }
            }
        },
        
        # ============================================================
        # COVID-19 ENDPOINTS
        # ============================================================
        "covid_19_endpoints": {
            "prediction": {
                "POST /api/covid_19/predict": {
                    "description": "Single chest X-ray analysis",
                    "body": "multipart/form-data with 'image' file",
                    "headers": {"Authorization": "Bearer <token>"},
                    "response": "Prediction (COVID/Normal/Viral Pneumonia/Lung Opacity), confidence, medical info",
                    "protected": True
                },
                "POST /api/covid_19/predict/batch": {
                    "description": "Batch chest X-ray analysis (multiple images)",
                    "body": "multipart/form-data with 'images[]' files",
                    "headers": {"Authorization": "Bearer <token>"},
                    "response": "Array of predictions + batch summary",
                    "protected": True
                }
            },
            "history_and_analytics": {
                "GET /api/covid_19/history": {
                    "description": "Get user's prediction history",
                    "query_params": {"limit": "integer (default: 20)"},
                    "headers": {"Authorization": "Bearer <token>"},
                    "response": "Array of past predictions",
                    "protected": True
                },
                "GET /api/covid_19/analytics": {
                    "description": "Get user's analytics summary",
                    "headers": {"Authorization": "Bearer <token>"},
                    "response": "Statistics by infection type, counts, trends",
                    "protected": True
                }
            },
            "research_and_visualization": {
                "GET /api/covid_19/results/charts": {
                    "description": "Generate research charts (bar, pie, timeline)",
                    "response": "Base64 encoded chart images",
                    "protected": False
                },
                "GET /api/covid_19/results/statistics": {
                    "description": "Get statistical analysis",
                    "response": "Mean, std, confidence distribution",
                    "protected": False
                }
            },
            "utility": {
                "GET /api/covid_19/classes": {
                    "description": "Get COVID-19 class labels and descriptions",
                    "response": "Array of classes with descriptions",
                    "protected": False
                },
                "GET /api/covid_19/model/info": {
                    "description": "Get model architecture information",
                    "response": "Model type, parameters, input size",
                    "protected": False
                },
                "POST /api/covid_19/debug/prediction": {
                    "description": "Debug prediction with detailed output",
                    "body": "multipart/form-data with 'image' file",
                    "response": "Raw predictions, probabilities, debug info",
                    "protected": False
                },
                "GET /api/covid_19/debug/class-order": {
                    "description": "Show class interpretation order",
                    "response": "Class labels and indices",
                    "protected": False
                }
            },
            "reports": {
                "POST /api/covid_19/report": {
                    "description": "Generate PDF medical report",
                    "body": {
                        "username": "string (required)",
                        "prediction": "string (required)",
                        "confidence": "number (required)",
                        "image_path": "string (optional)"
                    },
                    "headers": {"Authorization": "Bearer <token>"},
                    "response": "PDF file download",
                    "protected": True
                }
            },
            "web_interface": {
                "GET /test/covid_19": {
                    "description": "Interactive web testing interface",
                    "response": "HTML page for testing predictions",
                    "protected": False
                },
                "GET /api/covid_19/uploads/<filename>": {
                    "description": "Serve uploaded COVID-19 images",
                    "response": "Image file",
                    "protected": False
                }
            }
        },
        
        # ============================================================
        # SYSTEM ENDPOINTS
        # ============================================================
        "system_endpoints": {
            "GET /": {
                "description": "Complete API documentation (this page)",
                "response": "JSON with all endpoints",
                "protected": False
            },
            "GET /api/health": {
                "description": "System health check",
                "response": "Database status, model status, upload directories",
                "protected": False
            }
        },
        
        # ============================================================
        # MODEL INFORMATION
        # ============================================================
        "models": {
            "brain_tumor": {
                "name": "Brain Tumor Classification Model",
                "architecture": "VGG16 Transfer Learning",
                "classes": ["glioma", "meningioma", "notumor", "pituitary"],
                "input_size": "128x128 pixels (RGB)",
                "model_file": "brain_tumor_model.h5",
                "description": "Classifies MRI scans into 4 tumor types"
            },
            "covid_19": {
                "name": "COVID-19 Detection Model",
                "architecture": "Custom CNN",
                "classes": ["COVID-19", "Lung_Opacity", "Normal", "Viral Pneumonia"],
                "input_size": "224x224 pixels (RGB)",
                "model_file": "covid_19_model.h5",
                "description": "Classifies chest X-rays into 4 condition types"
            }
        },
        
        # ============================================================
        # USAGE GUIDE
        # ============================================================
        "usage_guide": {
            "authentication_flow": [
                "1. Register: POST /api/auth/register",
                "2. Login: POST /api/auth/login (receive token)",
                "3. Use token: Add 'Authorization: Bearer <token>' header",
                "4. Make predictions: POST /api/brain_tumor/predict or /api/covid_19/predict"
            ],
            "web_testing": [
                "Option 1: Visit /test/brain_tumor for brain tumor testing",
                "Option 2: Visit /test/covid_19 for COVID-19 testing",
                "Note: Web interfaces don't require authentication"
            ],
            "api_usage_example": {
                "curl_example": "curl -X POST http://localhost:5000/api/brain_tumor/predict -H 'Authorization: Bearer <token>' -F 'image=@scan.jpg'",
                "python_example": "import requests; files={'image': open('scan.jpg','rb')}; headers={'Authorization': 'Bearer <token>'}; response = requests.post('http://localhost:5000/api/brain_tumor/predict', files=files, headers=headers)"
            }
        },
        
        # ============================================================
        # DATABASE COLLECTIONS
        # ============================================================
        "database_collections": {
            "users": "User accounts and authentication data",
            "brain_tumor_predictions": "Brain tumor prediction history",
            "brain_tumor_batch_results": "Brain tumor batch results",
            "covid_19_predictions": "COVID-19 prediction history",
            "covid_19_batch_results": "COVID-19 batch results",
            "audit_logs": "System audit trail (login, predictions, changes)"
        },
        
        # ============================================================
        # RESPONSE FORMAT
        # ============================================================
        "response_format": {
            "success_response": {
                "status": 200,
                "body": {
                    "prediction": "string",
                    "confidence": "float (0-1)",
                    "confidence_percentage": "float (0-100)",
                    "medicalInfo": "object with details",
                    "recommendations": "array of strings"
                }
            },
            "error_response": {
                "status": "4xx or 5xx",
                "body": {
                    "error": "string (error message)"
                }
            }
        },
        
        # ============================================================
        # RATE LIMITS & CONSTRAINTS
        # ============================================================
        "constraints": {
            "max_file_size": "16 MB per image",
            "supported_formats": ["jpg", "jpeg", "png"],
            "batch_limit": "No hard limit, but recommended max 50 images",
            "token_expiry": "24 hours"
        }
    }
    
    return Response(
        json.dumps(api_info, indent=2, sort_keys=False),
        mimetype='application/json'
    )

# ============================================================================
# HEALTH CHECK ENDPOINT
# ============================================================================

@app.route('/api/health', methods=['GET'])
def api_health():
    """System health check"""
    from datetime import datetime
    
    db_status = "connected"
    try:
        db = get_database()
        db.command('ping')
    except:
        db_status = "disconnected"
    
    # Check model files
    brain_tumor_model_exists = os.path.exists('models/brain_tumor_model.h5')
    covid_model_exists = os.path.exists('models/covid_19_model.h5')
    
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database": db_status,
        "models": {
            "brain_tumor": "loaded" if brain_tumor_model_exists else "missing",
            "covid_19": "loaded" if covid_model_exists else "missing"
        },
        "upload_directories": {
            "brain_tumor": os.path.exists('uploads/brain_tumor'),
            "covid_19": os.path.exists('uploads/covid_19')
        },
        "version": "3.0.0"
    })


# ============================================================
# TEST PAGES (Add these routes)
# ============================================================

@app.route('/test/brain_tumor')
def brain_tumor_test_page():
    """Render brain tumor test interface"""
    return render_template('brain_tumor_test.html')

@app.route('/test/covid_19')
def covid_19_test_page():
    """Render COVID-19 test interface"""
    return render_template('covid_19_test.html')

# ============================================================================
# APPLICATION STARTUP
# ============================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Medical Image Analysis System Starting...")
    print("=" * 60)
    print(f"📁 Upload directories:")
    print(f"   - Brain Tumor: uploads/brain_tumor/")
    print(f"   - COVID-19: uploads/covid_19/")
    print(f"\n🔬 Available Models:")
    print(f"   - Brain Tumor: models/brain_tumor_model.h5")
    print(f"   - COVID-19: models/COVID19_Xray_Model.h5")
    print(f"\n📡 API Endpoints:")
    print(f"   - Documentation: http://localhost:5000/")
    print(f"   - Brain Tumor Test: http://localhost:5000/test/brain_tumor")
    print(f"   - COVID-19 Test: http://localhost:5000/test/covid_19")
    print(f"   - Health Check: http://localhost:5000/api/health")
    
    # Test database connection
    try:
        db = get_database()
        print(f"\n✅ Database connection successful")
        collections = db.list_collection_names()
        print(f"📊 Collections: {', '.join(collections)}")
    except Exception as e:
        print(f"\n❌ Database connection failed: {e}")
        print("⚠️ Application will run with limited functionality")
    
    print("=" * 60)
    
    # Run Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)