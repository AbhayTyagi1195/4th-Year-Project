from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
import os

class MedicalReportGenerator:
    def __init__(self, output_path, disease_type='brain_tumor'):
        """
        Initialize PDF generator
        
        Args:
            output_path: Path where PDF will be saved
            disease_type: 'brain_tumor' or 'covid_19'
        """
        self.output_path = output_path
        self.disease_type = disease_type  # ✅ Store disease_type
        self.doc = SimpleDocTemplate(output_path, pagesize=A4)
        self.styles = getSampleStyleSheet()
        self.story = []
        self._create_custom_styles()

    def _create_custom_styles(self):
        """Create custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2c3e50'),
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=18,
            textColor=colors.HexColor('#e74c3c'),
            fontName='Helvetica-Bold',
            spaceBefore=20,
            spaceAfter=10
        ))
        self.styles.add(ParagraphStyle(
            name='InfoHeader',
            parent=self.styles['Heading3'],
            fontSize=14,
            textColor=colors.HexColor('#3498db'),
            spaceAfter=15,
            spaceBefore=8,
            fontName='Helvetica-Bold'
        ))

    def _get_system_name(self):
        """Get system name based on disease type"""
        if self.disease_type == 'covid_19':
            return "Advanced COVID-19 Detection System with AI"
        else:
            return "Advanced Brain Tumor Detection with AI"
    
    def _get_analysis_type(self):
        """Get analysis type based on disease type"""
        if self.disease_type == 'covid_19':
            return "Single Chest X-ray Analysis"
        else:
            return "Single MRI Analysis"
    
    def add_header(self, username, report_type="Single Analysis"):
        """Add report header"""
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1976d2'),
            alignment=TA_CENTER,
            spaceAfter=30
        )

        # ✅ Use disease_type instead of analysis_type
        system_name = self._get_system_name()
        analysis_type = self._get_analysis_type()
        
        self.story.append(Paragraph(f"Medical Image Analysis Report - {report_type}", title_style))
        self.story.append(Spacer(1, 0.2*inch))
        
        # Patient/User info
        info_data = [
            ['Generated For:', username],
            ['Date:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
            ['System:', system_name],
            ['Report Type:', report_type],
            ['Analysis Type:', analysis_type]
        ]
        
        info_table = Table(info_data, colWidths=[2*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e3f2fd')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        
        self.story.append(info_table)
        self.story.append(Spacer(1, 0.3*inch))
        
    def add_analysis_result(self, prediction, confidence, image_path=None):
        """Add single analysis result"""
        result_style = ParagraphStyle(
            'ResultHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#d32f2f') if self.disease_type == 'brain_tumor' else colors.HexColor('#1976d2'),
            spaceAfter=12
        )
        
        self.story.append(Paragraph("Analysis Result", result_style))
        self.story.append(Spacer(1, 0.2*inch))
        
        # Add image before the table
        if image_path:
            print(f"🖼️ Attempting to add image: {image_path}")
            print(f"📁 File exists: {os.path.exists(image_path)}")
            
            if os.path.exists(image_path):
                try:
                    print(f"✅ Loading image from: {image_path}")
                    img = Image(image_path, width=3*inch, height=3*inch)
                    self.story.append(img)
                    self.story.append(Spacer(1, 0.2*inch))
                    print(f"✅ Image added successfully to PDF")
                except Exception as e:
                    print(f"❌ Error loading image: {str(e)}")
                    error_msg = Paragraph(
                        f"<i>[Image could not be loaded: {str(e)}]</i>", 
                        self.styles['Normal']
                    )
                    self.story.append(error_msg)
                    self.story.append(Spacer(1, 0.1*inch))
            else:
                print(f"❌ Image file not found at: {image_path}")
                warning_msg = Paragraph(
                    f"<i>[Image file not found at: {image_path}]</i>", 
                    self.styles['Normal']
                )
                self.story.append(warning_msg)
                self.story.append(Spacer(1, 0.1*inch))
        else:
            print("⚠️ No image path provided")

        # Result data
        severity = self._get_severity(confidence)

        # ✅ Get dynamic color based on disease_type
        if self.disease_type == 'brain_tumor':
            table_color = self._get_tumor_color(prediction)
        else:
            table_color = self._get_covid_color(prediction)

        # Extract just filename from image_path
        filename_only = os.path.basename(image_path) if image_path else 'N/A'

        result_data = [
            ['Prediction:', prediction],
            ['Confidence Level:', f'{confidence:.2f}%'],
            ['Severity:', severity],
            ['Filename:', filename_only]
        ]
        
        result_table = Table(result_data, colWidths=[2*inch, 4*inch])
        result_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), table_color),
            ('BACKGROUND', (1, 0), (1, -1), colors.white),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        
        self.story.append(result_table)
        self.story.append(Spacer(1, 0.3*inch))

    def add_batch_summary(self, results):
        """Add batch analysis summary"""
        summary_style = ParagraphStyle(
            'SummaryHeader',
            parent=self.styles['Heading2'],
            fontSize=18,
            textColor=colors.HexColor('#d32f2f') if self.disease_type == 'brain_tumor' else colors.HexColor('#1976d2'),
            spaceAfter=12
        )
        
        self.story.append(Paragraph("Batch Analysis Summary", summary_style))

        # Calculate statistics
        total_images = len(results)
        prediction_types = {}
        high_risk_count = 0
        
        for result in results:
            pred = result.get('prediction', 'Unknown')
            conf = float(result.get('confidence', 0))
            
            prediction_types[pred] = prediction_types.get(pred, 0) + 1
            if conf > 90:
                high_risk_count += 1
        
        prediction_types_text = '<br/>'.join([f"{k}: {v}" for k, v in prediction_types.items()])
        
        # ✅ Dynamic label based on disease_type
        types_label = 'Tumor Types Detected:' if self.disease_type == 'brain_tumor' else 'Infection Types Detected:'
        
        # Summary table
        summary_data = [
            ['Total Images Analyzed:', str(total_images)],
            ['High Risk Cases (>90% confidence):', str(high_risk_count)],
            [types_label, Paragraph(prediction_types_text, self.styles['Normal'])]
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 3*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e1f5fe')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))

        self.story.append(summary_table)
        self.story.append(Spacer(1, 0.4*inch))

    def add_batch_results(self, results):
        """Add detailed batch results"""
        detail_style = ParagraphStyle(
            'DetailHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#0288d1'),
            spaceAfter=12
        )
        
        self.story.append(Paragraph("Detailed Results", detail_style))
        self.story.append(Spacer(1, 0.2*inch))
        
        for i, result in enumerate(results, 1):
            prediction = result.get('prediction', 'Unknown')
            confidence = float(result.get('confidence', 0))
            filename = result.get('filename', 'N/A')
            image_path = result.get('image_path', None)
            
            # Result header
            result_header = Paragraph(f"<b>Image {i}: {filename}</b>", self.styles['Heading3'])
            self.story.append(result_header)
            self.story.append(Spacer(1, 0.1*inch))

            # Add image if available
            if image_path:
                clean_path = str(image_path).strip().strip('"').strip("'")
                
                if os.path.exists(clean_path):
                    try:
                        print(f"✅ Adding image to PDF: {clean_path}")
                        img = Image(clean_path, width=3*inch, height=3*inch)
                        self.story.append(img)
                        self.story.append(Spacer(1, 0.2*inch))
                    except Exception as e:
                        print(f"❌ Error adding image {clean_path}: {str(e)}")
                        error_msg = Paragraph(
                            f"<i>[Image could not be loaded: {str(e)}]</i>", 
                            self.styles['Normal']
                        )
                        self.story.append(error_msg)
                        self.story.append(Spacer(1, 0.1*inch))
                else:
                    print(f"⚠️ Image not found: {clean_path}")
                    warning_msg = Paragraph(
                        f"<i>[Image file not found at: {clean_path}]</i>", 
                        self.styles['Normal']
                    )
                    self.story.append(warning_msg)
                    self.story.append(Spacer(1, 0.1*inch))
            else:
                print(f"⚠️ No image path provided for result {i}")

            # Result data
            result_data = [
                ['Prediction:', prediction],
                ['Confidence:', f'{confidence:.2f}%'],
                ['Severity:', self._get_severity(confidence)],
                ['Filename:', filename]
            ]
            
            result_table = Table(result_data, colWidths=[2*inch, 4*inch])

            # ✅ Get dynamic color based on disease_type
            if self.disease_type == 'brain_tumor':
                table_color = self._get_tumor_color(prediction)
            else:
                table_color = self._get_covid_color(prediction)
            
            result_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), table_color),
                ('BACKGROUND', (1, 0), (1, -1), colors.white),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey)
            ]))
            
            self.story.append(result_table)
            self.story.append(Spacer(1, 0.2*inch))
            
            # Add page break after every 3 results
            if i % 3 == 0 and i < len(results):
                self.story.append(PageBreak())
        
        self.story.append(Spacer(1, 0.3*inch))
            
    def add_medical_info(self, prediction_type):
        """Add medical information section - supports both brain tumor and COVID-19"""
        info_style = ParagraphStyle(
            'InfoHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#0288d1'),
            spaceAfter=12
        )
        
        self.story.append(Paragraph("Medical Information", info_style))
        
        # ✅ Check disease_type and provide appropriate medical info
        if self.disease_type == 'brain_tumor':
            medical_info = {
                'Glioma Tumor': [
                    'Most common primary brain tumor in adults',
                    'Can be slow-growing (low-grade) or fast-growing (high-grade)',
                    'May cause headaches, seizures, and neurological symptoms',
                    'Treatment options include surgery, radiation, and chemotherapy'
                ],
                'Meningioma Tumor': [
                    'Usually benign and slow-growing',
                    'Arises from meninges (protective layers around brain)',
                    'Often asymptomatic until large enough to cause pressure',
                    'Treatment typically involves surgical removal'
                ],
                'No Tumor': [
                    'No abnormal growth detected',
                    'Brain tissue appears within normal parameters',
                    'Continue regular health monitoring',
                    'Consult healthcare provider for any symptoms'
                ],
                'Pituitary Tumor': [
                    'Usually benign adenomas',
                    'Can affect hormone production',
                    'May cause vision problems and hormonal imbalances',
                    'Treatment includes medication, surgery, or radiation'
                ]
            }
            
            # Normalize brain tumor type
            normalized_type = prediction_type
            if 'glioma' in prediction_type.lower():
                normalized_type = 'Glioma Tumor'
            elif 'meningioma' in prediction_type.lower():
                normalized_type = 'Meningioma Tumor'
            elif 'pituitary' in prediction_type.lower():
                normalized_type = 'Pituitary Tumor'
            elif 'no' in prediction_type.lower() or 'notumor' in prediction_type.lower():
                normalized_type = 'No Tumor'
        
        else:  # covid_19
            medical_info = {
                'COVID-19': [
                    'Viral respiratory infection caused by SARS-CoV-2',
                    'Can cause bilateral ground-glass opacities visible on chest X-ray',
                    'Common symptoms include fever, cough, shortness of breath, fatigue',
                    'RT-PCR test recommended for confirmation of diagnosis',
                    'Self-isolation and medical monitoring required if positive'
                ],
                'Lung_Opacity': [
                    'Areas of increased density in lung tissue visible on X-ray',
                    'Non-specific finding that requires clinical correlation',
                    'Can indicate infection, inflammation, fluid accumulation, or other conditions',
                    'May be caused by pneumonia, pulmonary edema, or fibrosis',
                    'Further investigation with CT scan or additional tests may be needed'
                ],
                'Normal': [
                    'No signs of pneumonia or respiratory infection detected',
                    'Lung fields appear clear with no abnormal opacities',
                    'Continue preventive measures (mask, hygiene, social distancing)',
                    'Monitor for any respiratory symptoms (cough, fever, breathing difficulty)',
                    'Maintain routine health check-ups as per doctor\'s schedule'
                ],
                'Viral Pneumonia': [
                    'Viral infection causing inflammation in the lungs',
                    'May or may not be caused by COVID-19 - further testing needed',
                    'Can cause fever, cough, chest pain, and breathing difficulties',
                    'Additional diagnostic tests recommended for specific viral identification',
                    'Medical consultation and treatment advised - may require hospitalization'
                ]
            }
            
            # Normalize COVID-19 prediction type
            normalized_type = prediction_type
            pred_lower = prediction_type.lower()
            if 'covid' in pred_lower:
                normalized_type = 'COVID-19'
            elif 'lung' in pred_lower and 'opacity' in pred_lower:
                normalized_type = 'Lung_Opacity'
            elif 'viral' in pred_lower and 'pneumonia' in pred_lower:
                normalized_type = 'Viral Pneumonia'
            elif 'normal' in pred_lower:
                normalized_type = 'Normal'
        
        info_list = medical_info.get(normalized_type, ['No specific information available'])
        
        for item in info_list:
            bullet = Paragraph(f"• {item}", self.styles['Normal'])
            self.story.append(bullet)
            self.story.append(Spacer(1, 0.1*inch))
        
        self.story.append(Spacer(1, 0.2*inch))
        
    def add_recommendations(self, confidence, has_condition=True):
        """Add recommendations section - supports both brain tumor and COVID-19"""
        rec_style = ParagraphStyle(
            'RecHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#c62828'),
            spaceAfter=12
        )
        
        self.story.append(Paragraph("Recommendations", rec_style))

        # ✅ Check disease_type and provide appropriate recommendations
        if self.disease_type == 'brain_tumor':
            if confidence >= 90 and has_condition:
                recommendations = [
                    'Immediate Action Required: Schedule urgent consultation with a neurologist or neurosurgeon',
                    'Bring complete medical history and all previous scans to the appointment',
                    'Additional diagnostic tests (biopsy, advanced imaging) may be recommended',
                    'Seek second opinion from specialized brain tumor center',
                    'Do not delay - early intervention improves treatment outcomes'
                ]
            elif confidence >= 90 and not has_condition:
                recommendations = [
                    'No Immediate Concerns: Results indicate healthy brain tissue',
                    'Continue routine health check-ups as per your doctor\'s schedule',
                    'Maintain brain health through proper diet, exercise, and sleep',
                    'Monitor for any new symptoms (headaches, vision changes, seizures)',
                    'Contact healthcare provider if any concerns arise'
                ]
            elif confidence >= 70:
                recommendations = [
                    'Medical Consultation Advised: See a neurologist within 1-2 weeks',
                    'Request additional MRI sequences or CT scan for confirmation',
                    'Prepare questions about treatment options and next steps',
                    'Compare with previous scans if available',
                    'Consider consultation at specialized center'
                ]
            else:
                recommendations = [
                    'Further Investigation Needed: Results are inconclusive',
                    'Additional imaging with different MRI sequences recommended',
                    'Consultation with radiologist and neurologist advised',
                    'Consider advanced imaging (fMRI, PET scan) if symptoms present',
                    'Do not ignore symptoms - seek medical evaluation'
                ]
        
        else:  # covid_19
            if confidence >= 90 and has_condition:
                recommendations = [
                    'Immediate Action Required: Schedule urgent medical consultation',
                    'Get RT-PCR test for COVID-19 confirmation as soon as possible',
                    'Self-isolate immediately and follow COVID-19 safety protocols',
                    'Inform close contacts and healthcare provider about potential exposure',
                    'Monitor oxygen saturation levels and seek emergency care if breathing worsens',
                    'Follow local health authority guidelines for quarantine and testing'
                ]
            elif confidence >= 90 and not has_condition:
                recommendations = [
                    'No Immediate Concerns: Chest X-ray appears normal',
                    'Continue following COVID-19 preventive measures (mask, hygiene, distancing)',
                    'Get vaccinated if not already done - check for booster eligibility',
                    'Maintain routine health check-ups and monitor for symptoms',
                    'Contact healthcare provider if respiratory symptoms develop',
                    'Continue healthy lifestyle practices to maintain respiratory health'
                ]
            elif confidence >= 70:
                recommendations = [
                    'Medical Consultation Advised: See a healthcare provider within 24-48 hours',
                    'Additional diagnostic tests (CT scan, RT-PCR) may be recommended',
                    'Monitor symptoms closely (fever, cough, breathing difficulty)',
                    'Practice self-isolation as a precautionary measure',
                    'Compare with previous chest X-rays if available',
                    'Follow COVID-19 safety protocols until diagnosis is confirmed'
                ]
            else:
                recommendations = [
                    'Uncertain Results: AI analysis has low confidence',
                    'Repeat chest X-ray recommended with better image quality',
                    'Professional radiologist review is essential for accurate diagnosis',
                    'Clinical correlation required - inform doctor of all symptoms',
                    'Consider additional imaging (CT scan) if symptoms are present',
                    'Seek immediate medical attention if experiencing severe respiratory distress'
                ]
        
        for i, rec in enumerate(recommendations, 1):
            bullet = Paragraph(f"{i}. {rec}", self.styles['Normal'])
            self.story.append(bullet)
            self.story.append(Spacer(1, 0.1*inch))
        
        self.story.append(Spacer(1, 0.3*inch))
        
    def add_disclaimer(self):
        """Add disclaimer"""
        disclaimer_style = ParagraphStyle(
            'Disclaimer',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#ff6f00'),
            alignment=TA_LEFT,
            leftIndent=20,
            rightIndent=20,
            borderColor=colors.HexColor('#ff6f00'),
            borderWidth=1,
            borderPadding=10
        )
        
        disclaimer_text = """
        <b>Important Disclaimer:</b> This AI analysis is a screening tool and NOT a definitive diagnosis. 
        Always consult qualified healthcare professionals for proper medical evaluation and treatment decisions. 
        This report should not be used as the sole basis for medical decisions. The AI model has limitations 
        and may produce false positives or false negatives. Professional radiologist review is essential for 
        accurate diagnosis and treatment planning.
        """
        
        self.story.append(Spacer(1, 0.3*inch))
        self.story.append(Paragraph(disclaimer_text, disclaimer_style))

    def _get_severity(self, confidence):
        """Determine severity based on confidence"""
        if confidence >= 90:
            return "Very High Confidence"
        elif confidence >= 70:
            return "High Confidence"
        elif confidence >= 50:
            return "Moderate Confidence"
        else:
            return "Low Confidence"
    
    def _get_tumor_color(self, prediction):
        """Get color based on tumor type"""
        pred_lower = prediction.lower()
        if 'glioma' in pred_lower:
            return colors.HexColor('#ffcdd2')  # 🔴 Light Red (danger)
        elif 'meningioma' in pred_lower:
            return colors.HexColor('#fff9c4')  # 🟡 Light Yellow (warning)
        elif 'pituitary' in pred_lower:
            return colors.HexColor('#e1f5fe')  # 🔵 Light Blue (info)
        elif 'no' in pred_lower or 'notumor' in pred_lower:
            return colors.HexColor('#c8e6c9')  # 🟢 Light Green (success)
        else:
            return colors.HexColor('#f5f5f5')  # ⚪ Grey (default)
    
    def _get_covid_color(self, prediction):
        """Get color based on COVID-19 prediction (4 classes including Lung Opacity)"""
        pred_lower = prediction.lower()
        if 'covid' in pred_lower:
            return colors.HexColor('#ffcdd2')  # 🔴 Light Red (COVID-19 - High Risk)
        elif 'lung' in pred_lower or 'opacity' in pred_lower:
            return colors.HexColor('#fff9c4')  # 🟡 Light Yellow (Lung Opacity - Moderate Risk)
        elif 'viral' in pred_lower or 'pneumonia' in pred_lower:
            return colors.HexColor('#ffe0b2')  # 🟠 Light Orange (Viral Pneumonia - Moderate Risk)
        elif 'normal' in pred_lower:
            return colors.HexColor('#c8e6c9')  # 🟢 Light Green (Normal - Low Risk)
        else:
            return colors.HexColor('#f5f5f5')  # ⚪ Grey (Unknown)
        
    def generate(self):
        """Generate the PDF"""
        try:
            self.doc.build(self.story)
            return True
        except Exception as e:
            print(f"Error generating PDF: {str(e)}")
            return False

# ============================================================================
# HELPER FUNCTIONS FOR BRAIN TUMOR
# ============================================================================

def generate_brain_tumor_single_report(output_path, username, prediction, confidence, image_path=None):
    """Generate a single brain tumor analysis report"""
    generator = MedicalReportGenerator(output_path, disease_type='brain_tumor')
    
    generator.add_header(username, "Single Image Analysis")
    generator.add_analysis_result(prediction, confidence, image_path)
    generator.add_medical_info(prediction)
    
    has_tumor = 'no' not in prediction.lower() and 'notumor' not in prediction.lower()
    generator.add_recommendations(confidence, has_tumor)
    generator.add_disclaimer()
    
    return generator.generate()

def generate_brain_tumor_batch_report(output_path, username, results):
    """Generate a batch brain tumor analysis report"""
    generator = MedicalReportGenerator(output_path, disease_type='brain_tumor')
    
    generator.add_header(username, "Batch Image Analysis")
    generator.add_batch_summary(results)
    generator.add_batch_results(results)
    generator.add_disclaimer()
    
    return generator.generate()

# ============================================================================
# HELPER FUNCTIONS FOR COVID-19
# ============================================================================

def generate_covid_single_report(output_path, username, prediction, confidence, image_path=None):
    """Generate a single COVID-19 analysis report"""
    generator = MedicalReportGenerator(output_path, disease_type='covid_19')
    
    generator.add_header(username, "Single Image Analysis")
    generator.add_analysis_result(prediction, confidence, image_path)
    generator.add_medical_info(prediction)
    
    has_infection = 'normal' not in prediction.lower()
    generator.add_recommendations(confidence, has_infection)
    generator.add_disclaimer()
    
    return generator.generate()

def generate_covid_batch_report(output_path, username, results):
    """Generate a batch COVID-19 analysis report"""
    generator = MedicalReportGenerator(output_path, disease_type='covid_19')
    
    generator.add_header(username, "Batch Image Analysis")
    generator.add_batch_summary(results)
    generator.add_batch_results(results)
    generator.add_disclaimer()
    
    return generator.generate()

# ============================================================================
# LEGACY SUPPORT (For backward compatibility with existing brain tumor routes)
# ============================================================================

def generate_single_report(output_path, username, prediction, confidence, image_path=None, disease_type='brain_tumor'):
    """Legacy function - supports both brain tumor and COVID-19"""
    if disease_type == 'covid_19':
        return generate_covid_single_report(output_path, username, prediction, confidence, image_path)
    else:
        return generate_brain_tumor_single_report(output_path, username, prediction, confidence, image_path)

def generate_batch_report(output_path, username, results, disease_type='brain_tumor'):
    """Legacy function - supports both brain tumor and COVID-19"""
    if disease_type == 'covid_19':
        return generate_covid_batch_report(output_path, username, results)
    else:
        return generate_brain_tumor_batch_report(output_path, username, results)