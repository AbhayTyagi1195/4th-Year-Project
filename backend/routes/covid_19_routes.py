from flask import Blueprint, request, jsonify, render_template, send_from_directory
from werkzeug.utils import secure_filename
from tensorflow.keras.models import load_model
from keras.preprocessing.image import load_img, img_to_array
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os
import datetime
from io import BytesIO
import base64
from collections import Counter
from bson import ObjectId

from config.database import get_database
from utils.auth import token_required, optional_token

# Create Blueprint
covid_19_bp = Blueprint('covid_19', __name__)

# Load COVID-19 Model
MODEL_PATH = 'models/covid_19_model.h5'
covid_19_model = None

try:
    covid_19_model = load_model(MODEL_PATH)
    print("✅ COVID-19 Model loaded successfully from:", MODEL_PATH)
except Exception as e:
    print(f"❌ Error loading COVID-19 model: {e}")
    print("⚠️ COVID-19 predictions will fail")

# Class labels for COVID-19
class_labels = ['COVID-19','Lung_Opacity', 'Normal', 'Viral Pneumonia']

# Upload folder for COVID-19 images
COVID_19_UPLOAD_FOLDER = 'uploads/covid_19'

# Store prediction history (in-memory)
prediction_history = []

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_covid_information(prediction, confidence):
    """Generate medical information based on prediction and confidence"""
    confidence_value = float(confidence) if isinstance(confidence, (int, float)) else float(str(confidence).strip('%'))
    
    covid_descriptions = {
        'COVID-19': {
            'name': 'COVID-19 Detected',
            'description': 'The chest X-ray shows patterns consistent with COVID-19 infection.',
            'severity': 'High Risk',
            'color': 'danger',
            'icon': '🦠',
            'details': [
                'Bilateral ground-glass opacities typical of COVID-19',
                'May indicate viral pneumonia',
                'Requires immediate medical attention',
                'RT-PCR test recommended for confirmation'
            ]
        },
        'lung_opacity': {  # NEW
            'name': 'Lung Opacity Detected',
            'description': 'Lung opacity indicates areas of increased density in lung tissue...',
            'severity': 'Moderate Risk',
            'color': 'warning',
            'icon': '⚠️',
            'details': [
            'Non-specific finding requiring clinical correlation',
            'May indicate infection, inflammation, or fluid',
            'Can be caused by pneumonia, pulmonary edema, or fibrosis',
            'Further investigation needed to determine cause'
            ]
        },
        'Normal': {
            'name': 'Normal Chest X-ray',
            'description': 'The chest X-ray appears normal with no signs of infection.',
            'severity': 'Low Risk',
            'color': 'success',
            'icon': '✅',
            'details': [
                'No signs of pneumonia or infection',
                'Lung fields appear clear',
                'No abnormal opacities detected',
                'Continue preventive measures and monitoring'
            ]
        },
        'Viral Pneumonia': {
            'name': 'Viral Pneumonia Detected',
            'description': 'The chest X-ray shows signs of viral pneumonia.',
            'severity': 'Moderate to High Risk',
            'color': 'warning',
            'icon': '⚠️',
            'details': [
                'Viral infection affecting the lungs',
                'May or may not be COVID-19',
                'Additional testing recommended',
                'Medical consultation advised'
            ]
        }
    }
    
    # Determine infection type
    infection_type = 'Normal'
    for key in covid_descriptions.keys():
        if key.lower().replace('-', '').replace(' ', '') in prediction.lower().replace('-', '').replace(' ', ''):
            infection_type = key
            break
    
    info = covid_descriptions[infection_type]
    
    # Confidence-based recommendations
    if confidence_value >= 90:
        confidence_level = 'Very High Confidence'
        if infection_type != 'Normal':
            recommendations = [
                '🏥 Immediate Action Required: Schedule urgent medical consultation',
                '🔬 Additional diagnostic tests recommended for confirmation',
                '😷 Self-isolate if COVID-19 or viral infection suspected',
                '📋 Inform healthcare provider about symptoms',
                '📊 Follow up with pulmonologist for detailed evaluation'
            ]
        else:
            recommendations = [
                '✅ No Immediate Concerns: X-ray appears normal',
                '😷 Continue following COVID-19 safety guidelines',
                '📅 Routine health monitoring recommended',
                '🧼 Maintain hygiene and social distancing',
                '🏃 Continue healthy lifestyle habits'
            ]
    elif confidence_value >= 70:
        confidence_level = 'High Confidence'
        recommendations = [
             '🏥 Medical Consultation Advised: See a healthcare provider',
            '🔬 Additional diagnostic tests recommended',
            '📊 Compare with previous scans if available',
            '😷 Follow COVID-19 safety protocols',
            '👨‍⚕️ Clinical correlation with symptoms important'
        ]
    elif confidence_value >= 50:
        confidence_level = 'Moderate Confidence'
        recommendations = [
            '🔍 Further Investigation Needed',
            '📋 Additional imaging recommended',
            '👨‍⚕️ Consultation with pulmonologist advised',
            '🔬 RT-PCR or other confirmatory tests needed',
            '⚠️ Do not rely solely on this AI analysis'
        ]
    else:
        confidence_level = 'Low Confidence'
        recommendations = [
            '⚠️ Uncertain Results: AI analysis has low confidence',
            '🔄 Repeat chest X-ray recommended',
            '👨‍⚕️ Professional radiologist review essential',
            '🔬 Clinical correlation required',
            '🏥 Seek immediate medical attention if symptomatic'
        ]
    
    return {
        **info,
        'confidenceLevel': confidence_level,
        'recommendations': recommendations,
        'infectionType': infection_type
    }

def save_prediction_to_db(user_info, prediction_data):
    """Save prediction to MongoDB - COVID-19 Collection"""
    try:
        db = get_database()
        
        # Add user information
        prediction_data['userId'] = ObjectId(user_info['user_id'])
        prediction_data['username'] = user_info['username']
        prediction_data['createdAt'] = datetime.datetime.utcnow()
        
        # Insert into covid_19_predictions collection
        result = db.covid_19_predictions.insert_one(prediction_data)
        
        # Log the prediction
        db.audit_logs.insert_one({
            'userId': ObjectId(user_info['user_id']),
            'username': user_info['username'],
            'action': 'covid_19_prediction',
            'ipAddress': request.remote_addr,
            'userAgent': request.headers.get('User-Agent'),
            'timestamp': datetime.datetime.utcnow(),
            'details': {
                'predictionId': str(result.inserted_id),
                'predictionType': prediction_data.get('predictionType'),
                'infectionType': prediction_data.get('infectionType')
            }
        })
        
        return str(result.inserted_id)
    except Exception as e:
        print(f"Error saving to database: {e}")
        return None

def predict_covid(image_path):
    """Predict COVID-19 from chest X-ray image"""
    if covid_19_model is None:
        raise Exception("COVID-19 Model not loaded")
    
    IMAGE_SIZE = 150  # Most COVID-19 models use 224x224
    img = load_img(image_path, target_size=(IMAGE_SIZE, IMAGE_SIZE))
    img_array = img_to_array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    predictions = covid_19_model.predict(img_array)
    predicted_class_index = np.argmax(predictions, axis=1)[0]
    confidence_score = np.max(predictions, axis=1)[0]

    predicted_label = class_labels[predicted_class_index]
    
    return predicted_label, confidence_score, predictions[0]

def clean_for_json(obj):
    """Convert numpy types to Python types for JSON serialization"""
    if isinstance(obj, dict):
        return {key: clean_for_json(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [clean_for_json(item) for item in obj]
    elif hasattr(obj, 'item'):
        return obj.item()
    elif isinstance(obj, (np.float32, np.float64)):
        return float(obj)
    elif isinstance(obj, (np.int32, np.int64)):
        return int(obj)
    return obj

# ============================================================================
# TEST INTERFACE ROUTE
# ============================================================================

@covid_19_bp.route('/test', methods=['GET', 'POST'])
def test_interface():
    """Web interface for testing COVID-19 predictions"""
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            file_location = os.path.join(COVID_19_UPLOAD_FOLDER, filename)
            file.save(file_location)

            result, confidence, all_predictions = predict_covid(file_location)
            
            prediction_history.append({
                "timestamp": datetime.datetime.now().isoformat(),
                "filename": filename,
                "result": result,
                "confidence": float(confidence),
                "method": "web_interface"
            })

            return render_template('covid_19_test.html', 
                                 result=result, 
                                 confidence=f"{confidence*100:.2f}%", 
                                 file_path=f'/api/covid_19/uploads/{filename}')

    return render_template('covid_19_test.html', result=None)

@covid_19_bp.route('/uploads/<filename>')
def get_uploaded_file(filename):
    """Serve uploaded COVID-19 images"""
    return send_from_directory(COVID_19_UPLOAD_FOLDER, filename)

# ============================================================================
# PREDICTION ENDPOINTS
# ============================================================================

@covid_19_bp.route('/predict', methods=['POST'])
@token_required
def predict():
    """Single image prediction - PROTECTED"""
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        filename = secure_filename(file.filename)
        filepath = os.path.join(COVID_19_UPLOAD_FOLDER, filename)
        file.save(filepath)

        print(f"💾 COVID-19 Upload: Saved to {filepath}")
        print(f"✅ File exists: {os.path.exists(filepath)}")

        file_size = os.path.getsize(filepath)

        start_time = datetime.datetime.now()
        result, confidence, all_predictions = predict_covid(filepath)
        end_time = datetime.datetime.now()
        processing_time = (end_time - start_time).total_seconds()

        confidence_percentage = float(confidence * 100)
        covid_info = get_covid_information(result, confidence_percentage)

        prediction_data = {
            'predictionType': 'single',
            'filename': filename,
            'fileSize': file_size,
            'prediction': result,
            'infectionType': covid_info['infectionType'],
            'confidence': float(confidence),
            'confidencePercentage': confidence_percentage,
            'confidenceLevel': covid_info['confidenceLevel'],
            'severity': covid_info['severity'],
            'medicalDescription': covid_info['description'],
            'recommendations': covid_info['recommendations'],
            'processingTime': f"{processing_time:.3f}s",
            'modelVersion': 'covid_19_model_v1',
            'analysisDate': datetime.datetime.utcnow(),
            'probabilities': {
                class_labels[i]: float(all_predictions[i]) 
                for i in range(len(class_labels))
            }
        }

        prediction_id = save_prediction_to_db(request.current_user, prediction_data)

        prediction_history.append({
            'prediction': result,
            'confidence': float(confidence),
            'result': result,
            'method': 'api',
            'timestamp': datetime.datetime.now().isoformat(),
            'filename': filename
        })

        response_data = {
            'prediction': result,
            'confidence': float(confidence),
            'confidence_percentage': round(confidence_percentage, 2),
            'covidInfo': covid_info,
            'all_predictions': {
                class_labels[i]: float(all_predictions[i]) 
                for i in range(len(class_labels))
            },
            'filename': filename,
            'image_path': os.path.abspath(filepath),
            'timestamp': datetime.datetime.now().isoformat(),
            'processing_time': f"{processing_time:.3f}s",
            'predictionId': prediction_id
        }

        return jsonify(response_data)

    except Exception as e:
        print(f"ERROR in COVID-19 predict endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

@covid_19_bp.route('/predict/batch', methods=['POST'])
@token_required
def predict_batch():
    """Batch prediction - PROTECTED"""
    try:
        files = request.files.getlist('images')
        
        if not files or len(files) == 0:
            return jsonify({"error": "No images provided"}), 400
        
        results = []
        infection_types = []
        batch_id = ObjectId()
        
        for file in files:
            if file.filename == '':
                continue
            
            filename = secure_filename(file.filename)
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_filename = f"batch_{timestamp}_{filename}"
            file_location = os.path.join(COVID_19_UPLOAD_FOLDER, unique_filename)
            file.save(file_location)
            
            file_size = os.path.getsize(file_location)
            
            start_time = datetime.datetime.now()
            result, confidence, all_predictions = predict_covid(file_location)
            end_time = datetime.datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            confidence_percentage = float(confidence * 100)
            covid_info = get_covid_information(result, confidence_percentage)
            
            if covid_info['infectionType'] != 'Normal':
                infection_types.append(covid_info['infectionType'])
            
            # Save to covid_19_batch_results collection
            try:
                db = get_database()
                db.covid_19_batch_results.insert_one({
                    'batchId': batch_id,
                    'userId': ObjectId(request.current_user['user_id']),
                    'username': request.current_user['username'],
                    'filename': filename,
                    'fileSize': file_size,
                    'prediction': result,
                    'infectionType': covid_info['infectionType'],
                    'confidence': float(confidence),
                    'confidencePercentage': confidence_percentage,
                    'severity': covid_info['severity'],
                    'processingTime': f"{processing_time:.3f}s",
                    'image_path': os.path.abspath(file_location),
                    'createdAt': datetime.datetime.utcnow()
                })
            except Exception as db_error:
                print(f"Error saving batch result: {db_error}")
            
            prediction_history.append({
                "timestamp": datetime.datetime.now().isoformat(),
                "filename": filename,
                "result": result,
                "confidence": float(confidence),
                "method": "batch_api"
            })
            
            results.append({
                "filename": filename,
                "prediction": result,
                "confidence": f"{confidence*100:.2f}%",
                "confidence_percentage": confidence_percentage,
                "confidence_score": float(confidence),
                "processing_time": f"{processing_time:.3f}s",
                "image_path": os.path.abspath(file_location),
                "probabilities": {
                    class_labels[i]: float(all_predictions[i]) 
                    for i in range(len(class_labels))
                }
            })
        
        covid_detected = sum(1 for r in results if "COVID" in r["prediction"])
        lung_opacity_detected = sum(1 for r in results if "Lung_Opacity" in r["prediction"])
        infection_type_counts = {}
        for infection_type in infection_types:
            infection_type_counts[infection_type] = infection_type_counts.get(infection_type, 0) + 1
        
        avg_confidence = sum(r["confidence_score"] for r in results) / len(results) if results else 0
        
        batch_summary = {
            "covid_detected": covid_detected,
            "lung_opacity_detected": lung_opacity_detected,
            "normal": sum(1 for r in results if "Normal" in r["prediction"]),
            "viral_pneumonia": sum(1 for r in results if "Viral Pneumonia" in r["prediction"]),
            "average_confidence": f"{avg_confidence*100:.2f}%",
            "by_infection_type": infection_type_counts
        }
        
        # Save batch summary
        try:
            batch_data = {
                'predictionType': 'batch',
                'batchId': batch_id,
                'totalImages': len(results),
                'batchSummary': batch_summary,
                'processingTime': sum(float(r['processing_time'].replace('s', '')) for r in results),
                'modelVersion': 'covid_19_model_v1',
                'analysisDate': datetime.datetime.utcnow()
            }
            save_prediction_to_db(request.current_user, batch_data)
        except Exception as db_error:
            print(f"Error saving batch summary: {db_error}")
        
        return jsonify({
            "total_images": len(results),
            "results": results,
            "batch_summary": batch_summary,
            "batchId": str(batch_id)
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============================================================================
# ANALYTICS ENDPOINTS
# ============================================================================

@covid_19_bp.route('/history', methods=['GET'])
@token_required
def get_history():
    """Get user's COVID-19 prediction history"""
    try:
        db = get_database()
        limit = int(request.args.get('limit', 20))
        
        predictions = list(db.covid_19_predictions.find(
            {'userId': ObjectId(request.current_user['user_id'])},
            {'password': 0}
        ).sort('createdAt', -1).limit(limit))
        
        for pred in predictions:
            pred['_id'] = str(pred['_id'])
            pred['userId'] = str(pred['userId'])
            if 'batchId' in pred:
                pred['batchId'] = str(pred['batchId'])
        
        return jsonify({
            'total': len(predictions),
            'predictions': predictions
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@covid_19_bp.route('/analytics', methods=['GET'])
@token_required
def get_analytics():
    """Get user's COVID-19 analytics summary"""
    try:
        db = get_database()
        user_id = ObjectId(request.current_user['user_id'])
        
        total_predictions = db.covid_19_predictions.count_documents({'userId': user_id})
        
        pipeline = [
            {'$match': {'userId': user_id, 'infectionType': {'$exists': True}}},
            {'$group': {'_id': '$infectionType', 'count': {'$sum': 1}}}
        ]
        infection_distribution = list(db.covid_19_predictions.aggregate(pipeline))
        
        recent = list(db.covid_19_predictions.find(
            {'userId': user_id}
        ).sort('createdAt', -1).limit(5))
        
        for item in recent:
            item['_id'] = str(item['_id'])
            item['userId'] = str(item['userId'])
        
        return jsonify({
            'totalPredictions': total_predictions,
            'infectionDistribution': {item['_id']: item['count'] for item in infection_distribution},
            'recentActivity': recent
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# CHART AND STATISTICS ENDPOINTS
# ============================================================================

@covid_19_bp.route('/results/charts', methods=['GET'])
def get_charts():
    """Generate COVID-19 charts"""
    try:
        if not prediction_history:
            return jsonify({"error": "No prediction data available"}), 404
        
        charts = {}
        charts['class_distribution'] = generate_class_distribution_chart()
        charts['confidence_distribution'] = generate_confidence_distribution_chart()
        charts['predictions_timeline'] = generate_timeline_chart()
        charts['method_usage'] = generate_method_usage_chart()
        charts['confidence_trend'] = generate_confidence_trend_chart()
        
        return jsonify({
            "charts": charts,
            "metadata": {
                "total_predictions": len(prediction_history),
                "generated_at": datetime.datetime.now().isoformat(),
                "chart_count": len(charts)
            }
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@covid_19_bp.route('/results/statistics', methods=['GET'])
def get_statistics():
    """Get COVID-19 statistics"""
    try:
        if not prediction_history:
            return jsonify({"error": "No prediction data available"}), 404
        
        confidences = [pred['confidence'] for pred in prediction_history]
        results = [pred['result'] for pred in prediction_history]
        methods = [pred['method'] for pred in prediction_history]
        
        stats = {
            "overall_statistics": {
                "total_predictions": len(prediction_history),
                "average_confidence": float(np.mean(confidences)),
                "confidence_std": float(np.std(confidences)),
                "min_confidence": float(np.min(confidences)),
                "max_confidence": float(np.max(confidences)),
                "median_confidence": float(np.median(confidences))
            },
            "class_statistics": dict(Counter(results)),
            "method_statistics": dict(Counter(methods)),
            "confidence_by_class": {},
            "performance_metrics": {
                "high_confidence_predictions": len([c for c in confidences if c > 0.8]),
                "low_confidence_predictions": len([c for c in confidences if c < 0.5]),
                "covid_detection_rate": len([r for r in results if 'COVID' in r]) / len(results)
            }
        }
        
        for result in set(results):
            class_confidences = [pred['confidence'] for pred in prediction_history if pred['result'] == result]
            if class_confidences:
                stats["confidence_by_class"][result] = {
                    "mean": float(np.mean(class_confidences)),
                    "std": float(np.std(class_confidences)),
                    "count": len(class_confidences)
                }
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============================================================================
# CHART GENERATION FUNCTIONS
# ============================================================================

def generate_class_distribution_chart():
    """Generate class distribution bar chart"""
    results = [pred['result'] for pred in prediction_history]
    result_counts = Counter(results)
    
    plt.figure(figsize=(10, 6))
    classes = list(result_counts.keys())
    counts = list(result_counts.values())
    
    colors = ['#ff6b6b', '#feca57', '#4ecdc4', '#45b7d1']
    bars = plt.bar(classes, counts, color=colors[:len(classes)])
    
    plt.title('COVID-19 Prediction Distribution', fontsize=16, fontweight='bold')
    plt.xlabel('Prediction Classes', fontsize=12)
    plt.ylabel('Number of Predictions', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    
    for bar, count in zip(bars, counts):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                str(count), ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
    buffer.seek(0)
    chart_base64 = base64.b64encode(buffer.getvalue()).decode()
    plt.close()
    
    return chart_base64

def generate_confidence_distribution_chart():
    """Generate confidence distribution histogram"""
    confidences = [pred['confidence'] for pred in prediction_history]
    
    plt.figure(figsize=(10, 6))
    plt.hist(confidences, bins=20, color='#45b7d1', alpha=0.7, edgecolor='black')
    plt.axvline(np.mean(confidences), color='red', linestyle='--', 
               label=f'Mean: {np.mean(confidences):.3f}')
    
    plt.title('Prediction Confidence Distribution', fontsize=16, fontweight='bold')
    plt.xlabel('Confidence Score', fontsize=12)
    plt.ylabel('Frequency', fontsize=12)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
    buffer.seek(0)
    chart_base64 = base64.b64encode(buffer.getvalue()).decode()
    plt.close()
    
    return chart_base64

def generate_timeline_chart():
    """Generate predictions timeline"""
    timestamps = [datetime.datetime.fromisoformat(pred['timestamp']) for pred in prediction_history]
    hourly_counts = Counter([ts.strftime('%Y-%m-%d %H:00') for ts in timestamps])
    sorted_hours = sorted(hourly_counts.keys())
    counts = [hourly_counts[hour] for hour in sorted_hours]
    
    plt.figure(figsize=(12, 6))
    plt.plot(range(len(sorted_hours)), counts, marker='o', linewidth=2, markersize=6, color='#4ecdc4')
    plt.fill_between(range(len(sorted_hours)), counts, alpha=0.3, color='#4ecdc4')
    
    plt.title('Predictions Over Time', fontsize=16, fontweight='bold')
    plt.xlabel('Time Period', fontsize=12)
    plt.ylabel('Number of Predictions', fontsize=12)
    plt.xticks(range(0, len(sorted_hours), max(1, len(sorted_hours)//10)), 
              [sorted_hours[i] for i in range(0, len(sorted_hours), max(1, len(sorted_hours)//10))], 
              rotation=45, ha='right')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
    buffer.seek(0)
    chart_base64 = base64.b64encode(buffer.getvalue()).decode()
    plt.close()
    
    return chart_base64

def generate_method_usage_chart():
    """Generate method usage pie chart"""
    methods = [pred['method'] for pred in prediction_history]
    method_counts = Counter(methods)
    
    plt.figure(figsize=(8, 8))
    colors = ['#ff6b6b', '#feca57', '#4ecdc4', '#45b7d1']
    
    wedges, texts, autotexts = plt.pie(method_counts.values(), 
                                      labels=method_counts.keys(), 
                                      autopct='%1.1f%%',
                                      colors=colors,
                                      startangle=90,
                                      explode=[0.05] * len(method_counts))
    
    plt.title('API Usage Methods', fontsize=16, fontweight='bold')
    
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
    
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
    buffer.seek(0)
    chart_base64 = base64.b64encode(buffer.getvalue()).decode()
    plt.close()
    
    return chart_base64

def generate_confidence_trend_chart():
    """Generate confidence trend"""
    timestamps = [datetime.datetime.fromisoformat(pred['timestamp']) for pred in prediction_history]
    confidences = [pred['confidence'] for pred in prediction_history]
    results = [pred['result'] for pred in prediction_history]
    
    plt.figure(figsize=(12, 6))
    
    unique_results = list(set(results))
    colors = ['#ff6b6b', '#feca57', '#4ecdc4', '#45b7d1']
    
    for i, result in enumerate(unique_results):
        result_indices = [j for j, r in enumerate(results) if r == result]
        result_timestamps = [timestamps[j] for j in result_indices]
        result_confidences = [confidences[j] for j in result_indices]
        
        plt.scatter(result_timestamps, result_confidences, 
                   label=result, alpha=0.7, s=50, 
                   color=colors[i % len(colors)])
    
    plt.title('Prediction Confidence Over Time', fontsize=16, fontweight='bold')
    plt.xlabel('Time', fontsize=12)
    plt.ylabel('Confidence Score', fontsize=12)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
    buffer.seek(0)
    chart_base64 = base64.b64encode(buffer.getvalue()).decode()
    plt.close()
    
    return chart_base64

# ============================================================================
# UTILITY ENDPOINTS
# ============================================================================

@covid_19_bp.route('/classes', methods=['GET'])
def get_classes():
    """Get COVID-19 class labels"""
    return jsonify({
        "classes": class_labels,
        "total_classes": len(class_labels),
        "description": {
            "COVID-19": "Chest X-ray showing patterns consistent with COVID-19 infection",
            "Lung_Opacity": "Abnormal lung opacity indicating potential infection, inflammation, or fluid accumulation",
            "Normal": "Normal chest X-ray with no signs of infection",
            "Viral Pneumonia": "Viral pneumonia detected in chest X-ray"
        }
    })

@covid_19_bp.route('/model/info', methods=['GET'])
def get_model_info():
    """Get COVID-19 model information"""
    return jsonify({
        "model_type": "COVID-19 Detection CNN",
        "input_size": [224, 224, 3],
        "classes": class_labels,
        "total_parameters": covid_19_model.count_params() if covid_19_model and hasattr(covid_19_model, 'count_params') else "Unknown",
        "model_format": "Keras H5",
        "preprocessing": "Normalization (0-1 range)",
        "framework": "TensorFlow/Keras"
    })

@covid_19_bp.route('/debug/prediction', methods=['POST'])
@optional_token
def debug_prediction():
    """Debug COVID-19 prediction"""
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image provided"}), 400
        
        file = request.files['image']
        filename = secure_filename(file.filename)
        file_location = os.path.join(COVID_19_UPLOAD_FOLDER, f"debug_{filename}")
        file.save(file_location)
        
        result, confidence, all_predictions = predict_covid(file_location)
        
        user_info = None
        if hasattr(request, 'current_user'):
            user_info = request.current_user
        
        return jsonify({
            "filename": filename,
            "prediction": result,
            "confidence": float(confidence),
            "raw_predictions": all_predictions.tolist(),
            "class_probabilities": {
                class_labels[i]: {
                    "probability": float(all_predictions[i]),
                    "percentage": f"{all_predictions[i]*100:.2f}%"
                } for i in range(len(class_labels))
            },
            "predicted_class_index": int(np.argmax(all_predictions)),
            "debug_info": {
                "max_probability": float(np.max(all_predictions)),
                "min_probability": float(np.min(all_predictions)),
                "prediction_spread": float(np.max(all_predictions) - np.min(all_predictions))
            },
            "authenticated": user_info is not None,
            "user": user_info['username'] if user_info else 'anonymous'
        })
        
    except Exception as e:
        return jsonify({"error": str(e), "debug": True}), 500

@covid_19_bp.route('/debug/class-order', methods=['GET'])
def debug_class_order():
    """Debug class order"""
    return jsonify({
        "current_class_order": class_labels,
        "class_indices": {class_labels[i]: i for i in range(len(class_labels))},
        "note": "This shows the current class interpretation order used by the model"
    })