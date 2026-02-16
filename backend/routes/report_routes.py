from flask import Blueprint, request, jsonify, send_file
from utils.pdf_generator import MedicalReportGenerator,generate_single_report,generate_batch_report
from utils.auth import token_required
import os
from datetime import datetime
from reportlab.platypus import Paragraph, PageBreak
import os
import tempfile
import time

report_bp = Blueprint('report', __name__)

# ✅ Define output directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
BRAIN_TUMOR_OUTPUT_DIR = os.path.join(OUTPUT_DIR, 'brain_tumor')
COVID_19_OUTPUT_DIR = os.path.join(OUTPUT_DIR, 'covid_19')

# ✅ Create directories if they don't exist
os.makedirs(BRAIN_TUMOR_OUTPUT_DIR, exist_ok=True)
os.makedirs(COVID_19_OUTPUT_DIR, exist_ok=True)


@report_bp.route('/api/brain_tumor/predict/report', methods=['POST'])
@token_required
def download_brain_tumor_single_report():
    """Generate PDF report for single prediction"""
    try:
        data = request.json
                # Validate required fields
        if not all(k in data for k in ['username', 'prediction', 'confidence']):
            return jsonify({'error': 'Missing required fields: username, prediction, confidence'}), 400
        username = data.get('username', request.current_user['username'])
        prediction = data.get('prediction')
        confidence = data.get('confidence')
        image_path = data.get('image_path',None)

        print(f"\n{'='*50}")
        print(f"🔍 SINGLE REPORT REQUEST")
        print(f"📋 Prediction: {prediction}, Confidence: {confidence}%")
        print(f"📋 Received image_path: {image_path}")

         # ✅ FIX: Convert to absolute path
        if image_path:
            if not os.path.isabs(image_path):
                # Remove ./ or .\ prefixes
                image_path = image_path.replace('./', '').replace('.\\', '')
                # Convert to absolute path
                image_path = os.path.abspath(image_path)
            
            print(f"📁 Absolute image path: {image_path}")
            print(f"✅ File exists: {os.path.exists(image_path)}")
            if os.path.exists(image_path):
                print(f"📏 File size: {os.path.getsize(image_path)} bytes")

        # Create temporary file for PDF
        temp_dir = tempfile.gettempdir()
        # ✅ Save PDF in output/brain_tumor directory
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        pdf_filename = f"brain_tumor_report_{username}_{timestamp}.pdf"
        pdf_path = os.path.join(BRAIN_TUMOR_OUTPUT_DIR, pdf_filename)

        print(f"💾 Generating PDF: {pdf_path}")

        # Generate PDF with resolved image path
        success = generate_single_report(
            output_path=pdf_path,
            username=username,
            prediction=prediction,
            confidence=confidence,
            image_path=image_path,
            disease_type="brain_tumor"
        )
        
        if not success:
            print("❌ PDF generation returned False")
            return jsonify({'error': 'Failed to generate PDF report'}), 500
        
        # Check if file exists
        if not os.path.exists(pdf_path):
            print(f"❌ PDF file does not exist at: {pdf_path}")
            return jsonify({'error': 'PDF file not created'}), 500
        
        print(f"✅ PDF generated successfully: {os.path.getsize(pdf_path)} bytes")
        print(f"{'='*50}\n")
        
        # Send file
        return send_file(
            pdf_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=pdf_filename
        )
        
    except Exception as e:
        print(f"❌ Error generating single report: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@report_bp.route('/api/brain_tumor/batch/report', methods=['POST'])
@token_required
def download_brain_tumor_batch_report():
    """Generate PDF report for batch predictions"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not all(k in data for k in ['username', 'results']):
            return jsonify({'error': 'Missing required fields'}), 400
        
        username = data['username']
        results = data['results']
        
        if not isinstance(results, list) or len(results) == 0:
            return jsonify({'error': 'Results must be a non-empty list'}), 400
        
        print(f"\n{'='*50}")
        print(f"🔍 BATCH REPORT REQUEST")
        print(f"📊 Total images: {len(results)}")
        
        # ✅ FIX: Convert all image paths to absolute
        for result in results:
            if 'image_path' in result and result['image_path']:
                original_path = result['image_path']
                
                if not os.path.isabs(original_path):
                    # Remove ./ or .\ prefixes
                    clean_path = original_path.replace('./', '').replace('.\\', '')
                    # Convert to absolute path
                    result['image_path'] = os.path.abspath(clean_path)
                    
                    print(f"📋 {result.get('filename', 'unknown')}")
                    print(f"   Original: {original_path}")
                    print(f"   Absolute: {result['image_path']}")
                    print(f"   Exists: {os.path.exists(result['image_path'])}")
        
        # Create temporary file for PDF
        temp_dir = tempfile.gettempdir()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        pdf_filename = f"brain_tumor_batch_report_{username}_{timestamp}.pdf"
        pdf_path = os.path.join(BRAIN_TUMOR_OUTPUT_DIR, pdf_filename)

        print(f"💾 Generating batch PDF: {pdf_path}")
        
        # Generate PDF
        success = generate_batch_report(
            output_path=pdf_path,
            username=username,
            results=results,
            disease_type="brain_tumor"
        )
        
        if not success:
            print("❌ Batch PDF generation returned False")
            return jsonify({'error': 'Failed to generate batch PDF report'}), 500
        
        # Check if file exists
        if not os.path.exists(pdf_path):
            print(f"❌ Batch PDF file does not exist at: {pdf_path}")
            return jsonify({'error': 'PDF file not created'}), 500
        
        print(f"✅ Batch PDF generated successfully: {os.path.getsize(pdf_path)} bytes")
        print(f"{'='*50}\n")
        
        # Send file
        return send_file(
            pdf_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=pdf_filename
        )
        
    except Exception as e:
        print(f"❌ Error generating batch report: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Server error: {str(e)}'}), 500
    
@report_bp.route('/api/covid_19/predict/report', methods=['POST'])
@token_required
def download_covid_19_single_report():
    """Generate PDF report for single prediction"""
    try:
        data = request.json
                # Validate required fields
        if not all(k in data for k in ['username', 'prediction', 'confidence']):
            return jsonify({'error': 'Missing required fields: username, prediction, confidence'}), 400
        username = data.get('username', request.current_user['username'])
        prediction = data.get('prediction')
        confidence = data.get('confidence')
        image_path = data.get('image_path',None)

        print(f"\n{'='*50}")
        print(f"🔍 SINGLE REPORT REQUEST")
        print(f"📋 Prediction: {prediction}, Confidence: {confidence}%")
        print(f"📋 Received image_path: {image_path}")

         # ✅ FIX: Convert to absolute path
        if image_path:
            if not os.path.isabs(image_path):
                # Remove ./ or .\ prefixes
                image_path = image_path.replace('./', '').replace('.\\', '')
                # Convert to absolute path
                image_path = os.path.abspath(image_path)
            
            print(f"📁 Absolute image path: {image_path}")
            print(f"✅ File exists: {os.path.exists(image_path)}")
            if os.path.exists(image_path):
                print(f"📏 File size: {os.path.getsize(image_path)} bytes")

        # Create temporary file for PDF
        temp_dir = tempfile.gettempdir()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        pdf_filename = f"covid19_report_{username}_{timestamp}.pdf"
        pdf_path = os.path.join(COVID_19_OUTPUT_DIR, pdf_filename)


        print(f"💾 Generating PDF: {pdf_path}")

        # Generate PDF with resolved image path
        success = generate_single_report(
            output_path=pdf_path,
            username=username,
            prediction=prediction,
            confidence=confidence,
            image_path=image_path,
            disease_type="covid_19"
        )
        
        if not success:
            print("❌ PDF generation returned False")
            return jsonify({'error': 'Failed to generate PDF report'}), 500
        
        # Check if file exists
        if not os.path.exists(pdf_path):
            print(f"❌ PDF file does not exist at: {pdf_path}")
            return jsonify({'error': 'PDF file not created'}), 500
        
        print(f"✅ PDF generated successfully: {os.path.getsize(pdf_path)} bytes")
        print(f"{'='*50}\n")
        
        # Send file
        return send_file(
            pdf_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=pdf_filename
        )
        
    except Exception as e:
        print(f"❌ Error generating single report: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@report_bp.route('/api/covid_19/batch/report', methods=['POST'])
@token_required
def download_covid_19_batch_report():
    """Generate PDF report for batch predictions"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not all(k in data for k in ['username', 'results']):
            return jsonify({'error': 'Missing required fields'}), 400
        
        username = data['username']
        results = data['results']
        
        if not isinstance(results, list) or len(results) == 0:
            return jsonify({'error': 'Results must be a non-empty list'}), 400
        
        print(f"\n{'='*50}")
        print(f"🔍 BATCH REPORT REQUEST")
        print(f"📊 Total images: {len(results)}")
        
        # ✅ FIX: Convert all image paths to absolute
        for result in results:
            if 'image_path' in result and result['image_path']:
                original_path = result['image_path']
                
                if not os.path.isabs(original_path):
                    # Remove ./ or .\ prefixes
                    clean_path = original_path.replace('./', '').replace('.\\', '')
                    # Convert to absolute path
                    result['image_path'] = os.path.abspath(clean_path)
                    
                    print(f"📋 {result.get('filename', 'unknown')}")
                    print(f"   Original: {original_path}")
                    print(f"   Absolute: {result['image_path']}")
                    print(f"   Exists: {os.path.exists(result['image_path'])}")
        
        # Create temporary file for PDF
        temp_dir = tempfile.gettempdir()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        pdf_filename = f"covid19_batch_report_{username}_{timestamp}.pdf"
        pdf_path = os.path.join(COVID_19_OUTPUT_DIR, pdf_filename)

        print(f"💾 Generating batch PDF: {pdf_path}")
        
        # Generate PDF
        success = generate_batch_report(
            output_path=pdf_path,
            username=username,
            results=results,
            disease_type="covid_19"
        )
        
        if not success:
            print("❌ Batch PDF generation returned False")
            return jsonify({'error': 'Failed to generate batch PDF report'}), 500
        
        # Check if file exists
        if not os.path.exists(pdf_path):
            print(f"❌ Batch PDF file does not exist at: {pdf_path}")
            return jsonify({'error': 'PDF file not created'}), 500
        
        print(f"✅ Batch PDF generated successfully: {os.path.getsize(pdf_path)} bytes")
        print(f"{'='*50}\n")
        
        # Send file
        return send_file(
            pdf_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=pdf_filename
        )
        
    except Exception as e:
        print(f"❌ Error generating batch report: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Server error: {str(e)}'}), 500