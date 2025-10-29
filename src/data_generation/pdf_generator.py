"""
PDF Product Manual Generator
Creates realistic product manuals in PDF format
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from pathlib import Path
import json
import random

class PDFManualGenerator:
    """Generate product manuals as PDFs"""

    def __init__(self, output_dir="data/raw/pdfs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Create custom text styles"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a5490'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))

        self.styles.add(ParagraphStyle(
            name='SectionTitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2c5aa0'),
            spaceAfter=12,
            spaceBefore=12
        ))

    def generate_laptop_manual(self, product):
        """Generate laptop product manual"""
        filename = f"{product['product_id']}_manual.pdf"
        filepath = self.output_dir / filename

        doc = SimpleDocTemplate(str(filepath), pagesize=letter,
                              rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=18)

        story = []

        # Title
        title = Paragraph(f"{product['model']}<br/>User Manual", self.styles['CustomTitle'])
        story.append(title)
        story.append(Spacer(1, 0.3*inch))

        # Product Overview
        story.append(Paragraph("Product Overview", self.styles['SectionTitle']))
        overview_text = f"""
        Thank you for purchasing the {product['model']}. This premium laptop combines
        cutting-edge technology with sleek design to deliver exceptional performance for
        your daily computing needs. Whether you're working, creating, or entertaining,
        this device offers the power and versatility you need.
        """
        story.append(Paragraph(overview_text, self.styles['BodyText']))
        story.append(Spacer(1, 0.2*inch))

        # Technical Specifications
        story.append(Paragraph("Technical Specifications", self.styles['SectionTitle']))

        spec_data = [
            ['Specification', 'Details'],
            ['Processor', product.get('processor', 'N/A')],
            ['Memory (RAM)', f"{product.get('ram_gb', 'N/A')} GB"],
            ['Storage', f"{product.get('storage_gb', 'N/A')} GB SSD"],
            ['Display', f"{product.get('screen_size_inches', 'N/A')}\" {product.get('screen_resolution', 'N/A')}"],
            ['Graphics', product.get('graphics', 'N/A')],
            ['Battery Life', f"Up to {product.get('battery_hours', 'N/A')} hours"],
            ['Operating System', product.get('operating_system', 'N/A')],
            ['Weight', f"{product.get('weight_kg', 'N/A')} kg"],
            ['Warranty', f"{product.get('warranty_years', 'N/A')} years"]
        ]

        spec_table = Table(spec_data, colWidths=[2.5*inch, 3.5*inch])
        spec_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5aa0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(spec_table)
        story.append(Spacer(1, 0.3*inch))

        # Key Features
        story.append(Paragraph("Key Features", self.styles['SectionTitle']))
        features = [
            f"<b>High-Performance Processing:</b> Powered by {product.get('processor', 'advanced processor')} for seamless multitasking",
            f"<b>Ample Memory:</b> {product.get('ram_gb', 'N/A')} GB RAM ensures smooth operation of multiple applications",
            f"<b>Fast Storage:</b> {product.get('storage_gb', 'N/A')} GB SSD provides quick boot times and file access",
            f"<b>Stunning Display:</b> {product.get('screen_size_inches', 'N/A')}-inch screen with vibrant colors and sharp details",
            f"<b>All-Day Battery:</b> Up to {product.get('battery_hours', 'N/A')} hours of battery life",
            f"<b>Premium Build:</b> Sleek design weighing only {product.get('weight_kg', 'N/A')} kg"
        ]

        for feature in features:
            story.append(Paragraph(f"• {feature}", self.styles['BodyText']))
            story.append(Spacer(1, 0.1*inch))

        story.append(PageBreak())

        # Setup Guide
        story.append(Paragraph("Quick Setup Guide", self.styles['SectionTitle']))
        setup_text = """
        <b>1. Unboxing:</b> Carefully remove your laptop from the packaging. Ensure all accessories are present.<br/><br/>
        <b>2. Charging:</b> Connect the power adapter and charge the battery fully before first use (approximately 2-3 hours).<br/><br/>
        <b>3. Power On:</b> Press the power button located on the keyboard. The system will boot up automatically.<br/><br/>
        <b>4. Initial Setup:</b> Follow the on-screen instructions to configure language, region, and user account.<br/><br/>
        <b>5. Updates:</b> Connect to Wi-Fi and install any available system updates for optimal performance.
        """
        story.append(Paragraph(setup_text, self.styles['BodyText']))
        story.append(Spacer(1, 0.3*inch))

        # Care and Maintenance
        story.append(Paragraph("Care and Maintenance", self.styles['SectionTitle']))
        care_text = """
        <b>Cleaning:</b> Use a soft, lint-free cloth to clean the screen and body. Avoid harsh chemicals.<br/><br/>
        <b>Ventilation:</b> Ensure air vents are not blocked. Use on hard, flat surfaces for optimal cooling.<br/><br/>
        <b>Battery Care:</b> Avoid complete discharge. Keep battery level between 20-80% for longevity.<br/><br/>
        <b>Software Updates:</b> Regularly update your operating system and applications for security and performance.<br/><br/>
        <b>Backup:</b> Regularly backup important data to external storage or cloud services.
        """
        story.append(Paragraph(care_text, self.styles['BodyText']))
        story.append(Spacer(1, 0.3*inch))

        # Troubleshooting
        story.append(Paragraph("Troubleshooting", self.styles['SectionTitle']))
        troubleshoot_data = [
            ['Issue', 'Solution'],
            ['Device won\'t power on', 'Ensure battery is charged. Try holding power button for 10 seconds.'],
            ['Screen is dim', 'Adjust brightness using Fn + brightness keys.'],
            ['Wi-Fi not connecting', 'Toggle airplane mode on/off. Restart router if needed.'],
            ['Device running slow', 'Close unused applications. Check for malware. Free up storage space.'],
            ['Battery draining quickly', 'Reduce screen brightness. Close background apps. Check battery health in settings.']
        ]

        troubleshoot_table = Table(troubleshoot_data, colWidths=[2*inch, 4*inch])
        troubleshoot_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5aa0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ]))
        story.append(troubleshoot_table)
        story.append(Spacer(1, 0.3*inch))

        # Warranty Information
        story.append(Paragraph("Warranty Information", self.styles['SectionTitle']))
        warranty_text = f"""
        This product includes a {product.get('warranty_years', 'N/A')}-year limited warranty covering manufacturing defects.
        The warranty does not cover physical damage, liquid damage, or damage from unauthorized repairs.
        For warranty service, please contact customer support with your proof of purchase and product serial number.
        <br/><br/>
        <b>Customer Support:</b> support@techstore.com | 1-800-TECH-HELP
        <br/>
        <b>Website:</b> www.techstore.com/support
        """
        story.append(Paragraph(warranty_text, self.styles['BodyText']))

        # Build PDF
        doc.build(story)
        return filepath

    def generate_phone_manual(self, product):
        """Generate smartphone product manual"""
        filename = f"{product['product_id']}_manual.pdf"
        filepath = self.output_dir / filename

        doc = SimpleDocTemplate(str(filepath), pagesize=letter,
                              rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=18)

        story = []

        # Title
        title = Paragraph(f"{product['model']}<br/>Quick Start Guide", self.styles['CustomTitle'])
        story.append(title)
        story.append(Spacer(1, 0.3*inch))

        # Welcome
        welcome_text = f"""
        Welcome to your new {product['model']}! This guide will help you get started with your device
        and explore its amazing features. With its powerful {product.get('processor', 'processor')},
        stunning display, and advanced camera system, you're holding cutting-edge technology in your hands.
        """
        story.append(Paragraph(welcome_text, self.styles['BodyText']))
        story.append(Spacer(1, 0.2*inch))

        # Specifications
        story.append(Paragraph("Device Specifications", self.styles['SectionTitle']))

        spec_data = [
            ['Feature', 'Specification'],
            ['Processor', product.get('processor', 'N/A')],
            ['RAM', f"{product.get('ram_gb', 'N/A')} GB"],
            ['Storage', f"{product.get('storage_gb', 'N/A')} GB"],
            ['Display', f"{product.get('screen_size_inches', 'N/A')}\" {product.get('screen_resolution', 'N/A')}"],
            ['Camera', product.get('camera_mp', 'N/A')],
            ['Battery', f"{product.get('battery_mah', 'N/A')} mAh"],
            ['5G Support', 'Yes' if product.get('5g_support') else 'No'],
            ['OS', product.get('operating_system', 'N/A')]
        ]

        spec_table = Table(spec_data, colWidths=[2*inch, 4*inch])
        spec_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5aa0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(spec_table)
        story.append(Spacer(1, 0.3*inch))

        # Getting Started
        story.append(Paragraph("Getting Started", self.styles['SectionTitle']))
        getting_started = """
        <b>1. Insert SIM Card:</b> Use the SIM ejector tool to open the SIM tray. Insert your nano-SIM card.<br/><br/>
        <b>2. Power On:</b> Hold the power button for 3 seconds until the screen lights up.<br/><br/>
        <b>3. Setup Wizard:</b> Follow on-screen prompts to select language, connect to Wi-Fi, and sign in.<br/><br/>
        <b>4. Security Setup:</b> Configure face unlock, fingerprint, or PIN for device security.<br/><br/>
        <b>5. App Installation:</b> Download essential apps from the app store.
        """
        story.append(Paragraph(getting_started, self.styles['BodyText']))
        story.append(Spacer(1, 0.3*inch))

        # Key Features
        story.append(Paragraph("Key Features", self.styles['SectionTitle']))
        features_text = f"""
        <b>Professional Camera System:</b> Capture stunning photos with {product.get('camera_mp', 'advanced')} camera
        featuring night mode, portrait mode, and 4K video recording.<br/><br/>
        <b>Lightning-Fast Performance:</b> {product.get('processor', 'Powerful processor')} ensures smooth gaming
        and multitasking.<br/><br/>
        <b>All-Day Battery:</b> {product.get('battery_mah', 'Large')} mAh battery with fast charging support.<br/><br/>
        <b>Immersive Display:</b> {product.get('screen_size_inches', 'Large')} inch display with HDR10+ support
        for vivid colors.<br/><br/>
        <b>5G Connectivity:</b> {'Experience blazing-fast 5G speeds for streaming and downloads.' if product.get('5g_support') else '4G LTE connectivity for reliable mobile data.'}
        """
        story.append(Paragraph(features_text, self.styles['BodyText']))

        # Build PDF
        doc.build(story)
        return filepath

    def generate_all_manuals(self, products):
        """Generate manuals for all products"""
        print("\nGenerating product manuals...")
        generated_files = []

        for product in products:
            try:
                if product['category'] == 'Laptop':
                    filepath = self.generate_laptop_manual(product)
                    generated_files.append(filepath)
                elif product['category'] == 'Smartphone':
                    filepath = self.generate_phone_manual(product)
                    generated_files.append(filepath)
                # Tablets can use phone manual template
                elif product['category'] == 'Tablet':
                    filepath = self.generate_phone_manual(product)
                    generated_files.append(filepath)

            except Exception as e:
                print(f"Error generating manual for {product.get('model', 'unknown')}: {e}")
                continue

        print(f"✓ Generated {len(generated_files)} product manuals")
        return generated_files

def main():
    """Generate all product manuals"""
    # Load products from JSON
    with open('data/raw/text/product_catalog.json', 'r') as f:
        data = json.load(f)
        products = data if isinstance(data, list) else data.get('products', [])

    generator = PDFManualGenerator()
    generator.generate_all_manuals(products[:20])  # Generate first 20 for demo

if __name__ == "__main__":
    main()
