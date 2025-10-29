"""
Synthetic Product Data Generator
Creates realistic product catalogs for tech products (laptops, smartphones, tablets)
"""

import json
import csv
import random
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd

class ProductDataGenerator:
    """Generate synthetic product data"""

    def __init__(self, output_dir="data/raw"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Product categories and specifications
        self.laptop_brands = ["Dell", "HP", "Lenovo", "Apple", "ASUS", "Acer", "Microsoft"]
        self.phone_brands = ["Apple", "Samsung", "Google", "OnePlus", "Xiaomi"]
        self.tablet_brands = ["Apple", "Samsung", "Microsoft", "Lenovo", "Amazon"]

        self.processors = {
            "laptop": ["Intel Core i5-13th Gen", "Intel Core i7-13th Gen", "Intel Core i9-13th Gen",
                      "AMD Ryzen 5 7000", "AMD Ryzen 7 7000", "AMD Ryzen 9 7000",
                      "Apple M2", "Apple M2 Pro", "Apple M2 Max"],
            "phone": ["Snapdragon 8 Gen 2", "Snapdragon 8+ Gen 1", "Apple A16 Bionic",
                     "Apple A17 Pro", "Google Tensor G3", "MediaTek Dimensity 9200"],
            "tablet": ["Apple M2", "Snapdragon 8 Gen 2", "MediaTek Helio G99"]
        }

        self.ram_options = [4, 8, 16, 32, 64]
        self.storage_options = [128, 256, 512, 1000, 2000]
        self.screen_sizes_laptop = [13.3, 14.0, 15.6, 16.0, 17.3]
        self.screen_sizes_phone = [6.1, 6.4, 6.7, 6.8]
        self.screen_sizes_tablet = [8.3, 10.2, 10.9, 11.0, 12.9]

    def generate_laptop(self, product_id):
        """Generate a laptop product"""
        brand = random.choice(self.laptop_brands)
        series = random.choice(["Pro", "Plus", "Elite", "Inspiron", "Pavilion", "ThinkPad", "VivoBook"])
        model_num = random.randint(13, 17)

        processor = random.choice(self.processors["laptop"])
        ram = random.choice(self.ram_options)
        storage = random.choice(self.storage_options)
        screen = random.choice(self.screen_sizes_laptop)

        # Calculate realistic price based on specs
        base_price = 500
        if "i7" in processor or "Ryzen 7" in processor or "M2" in processor:
            base_price += 300
        if "i9" in processor or "Ryzen 9" in processor or "M2 Pro" in processor:
            base_price += 600
        base_price += (ram / 8) * 100
        base_price += (storage / 256) * 80
        base_price += (screen - 13) * 50

        price = round(base_price + random.uniform(-100, 200), 2)

        return {
            "product_id": f"LAP-{product_id:04d}",
            "category": "Laptop",
            "brand": brand,
            "model": f"{brand} {series} {model_num}",
            "processor": processor,
            "ram_gb": ram,
            "storage_gb": storage,
            "screen_size_inches": screen,
            "screen_resolution": random.choice(["1920x1080", "2560x1440", "3840x2160"]),
            "graphics": random.choice(["Integrated", "NVIDIA GTX 1650", "NVIDIA RTX 3050", "NVIDIA RTX 4060", "AMD Radeon", "Apple GPU"]),
            "battery_hours": random.randint(8, 24),
            "weight_kg": round(random.uniform(1.2, 2.5), 2),
            "operating_system": random.choice(["Windows 11", "Windows 11 Pro", "macOS Sonoma", "Linux Ubuntu"]),
            "price_usd": price,
            "in_stock": random.choice([True, True, True, False]),
            "rating": round(random.uniform(3.5, 5.0), 1),
            "release_date": (datetime.now() - timedelta(days=random.randint(30, 730))).strftime("%Y-%m-%d"),
            "warranty_years": random.choice([1, 2, 3])
        }

    def generate_smartphone(self, product_id):
        """Generate a smartphone product"""
        brand = random.choice(self.phone_brands)
        series = random.choice(["Pro", "Max", "Plus", "Ultra", "Note"])
        model_num = random.randint(12, 15)

        processor = random.choice(self.processors["phone"])
        ram = random.choice([6, 8, 12, 16])
        storage = random.choice([128, 256, 512, 1000])
        screen = random.choice(self.screen_sizes_phone)

        # Price calculation
        base_price = 400
        if "Pro" in processor or "A17" in processor:
            base_price += 400
        base_price += (ram / 6) * 100
        base_price += (storage / 128) * 100

        price = round(base_price + random.uniform(-50, 150), 2)

        return {
            "product_id": f"PHN-{product_id:04d}",
            "category": "Smartphone",
            "brand": brand,
            "model": f"{brand} {series} {model_num}",
            "processor": processor,
            "ram_gb": ram,
            "storage_gb": storage,
            "screen_size_inches": screen,
            "screen_resolution": random.choice(["2532x1170", "2778x1284", "3088x1440"]),
            "camera_mp": random.choice(["48MP", "50MP", "108MP", "200MP"]),
            "battery_mah": random.randint(3500, 5500),
            "5g_support": random.choice([True, True, False]),
            "operating_system": random.choice(["iOS 17", "Android 14", "Android 13"]),
            "price_usd": price,
            "in_stock": random.choice([True, True, True, False]),
            "rating": round(random.uniform(4.0, 5.0), 1),
            "release_date": (datetime.now() - timedelta(days=random.randint(30, 365))).strftime("%Y-%m-%d"),
            "warranty_years": random.choice([1, 2])
        }

    def generate_tablet(self, product_id):
        """Generate a tablet product"""
        brand = random.choice(self.tablet_brands)
        series = random.choice(["Pro", "Air", "Tab", "Surface"])

        processor = random.choice(self.processors["tablet"])
        ram = random.choice([4, 6, 8, 16])
        storage = random.choice([64, 128, 256, 512])
        screen = random.choice(self.screen_sizes_tablet)

        base_price = 300
        if "M2" in processor:
            base_price += 400
        base_price += (ram / 4) * 80
        base_price += (storage / 64) * 50

        price = round(base_price + random.uniform(-30, 100), 2)

        return {
            "product_id": f"TAB-{product_id:04d}",
            "category": "Tablet",
            "brand": brand,
            "model": f"{brand} {series}",
            "processor": processor,
            "ram_gb": ram,
            "storage_gb": storage,
            "screen_size_inches": screen,
            "screen_resolution": random.choice(["2048x1536", "2360x1640", "2732x2048"]),
            "battery_hours": random.randint(8, 14),
            "stylus_support": random.choice([True, False]),
            "keyboard_included": random.choice([True, False, False]),
            "operating_system": random.choice(["iPadOS 17", "Android 13", "Windows 11"]),
            "price_usd": price,
            "in_stock": random.choice([True, True, True, False]),
            "rating": round(random.uniform(4.0, 5.0), 1),
            "release_date": (datetime.now() - timedelta(days=random.randint(60, 500))).strftime("%Y-%m-%d"),
            "warranty_years": random.choice([1, 2])
        }

    def generate_catalog(self, num_products=100):
        """Generate complete product catalog"""
        products = []

        # Generate mix of products
        for i in range(1, num_products + 1):
            category = random.choice(["laptop", "smartphone", "tablet"])

            if category == "laptop":
                product = self.generate_laptop(i)
            elif category == "smartphone":
                product = self.generate_smartphone(i)
            else:
                product = self.generate_tablet(i)

            products.append(product)

        return products

    def save_as_csv(self, products, filename="product_catalog.csv"):
        """Save products as CSV"""
        df = pd.DataFrame(products)
        output_path = self.output_dir / "csvs" / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False)
        print(f"Saved {len(products)} products to {output_path}")
        return output_path

    def save_as_json(self, products, filename="product_catalog.json"):
        """Save products as JSON"""
        output_path = self.output_dir / "text" / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(products, f, indent=2)
        print(f"Saved {len(products)} products to {output_path}")
        return output_path

    def generate_pricing_table(self, products):
        """Generate pricing and discount table"""
        pricing_data = []

        for product in products:
            original_price = product['price_usd']
            discount_pct = random.choice([0, 5, 10, 15, 20, 25])
            discounted_price = original_price * (1 - discount_pct / 100)

            pricing_data.append({
                "product_id": product['product_id'],
                "product_name": product['model'],
                "category": product['category'],
                "original_price_usd": round(original_price, 2),
                "discount_percent": discount_pct,
                "sale_price_usd": round(discounted_price, 2),
                "promotion": random.choice(["None", "Holiday Sale", "Black Friday", "Clearance", "New Year"]),
                "valid_until": (datetime.now() + timedelta(days=random.randint(7, 90))).strftime("%Y-%m-%d"),
                "minimum_quantity": random.choice([1, 1, 1, 2, 5]),
                "bulk_discount_available": random.choice([True, False])
            })

        df = pd.DataFrame(pricing_data)
        output_path = self.output_dir / "csvs" / "pricing.csv"
        df.to_csv(output_path, index=False)
        print(f"Saved pricing data to {output_path}")
        return output_path

    def generate_faqs(self):
        """Generate FAQ dataset"""
        faqs = [
            {"question": "What is your return policy?",
             "answer": "We offer a 30-day return policy for all products. Items must be in original condition with all accessories and packaging."},

            {"question": "Do you offer international shipping?",
             "answer": "Yes, we ship to over 100 countries worldwide. Shipping costs and delivery times vary by location."},

            {"question": "What payment methods do you accept?",
             "answer": "We accept all major credit cards (Visa, MasterCard, American Express), PayPal, and bank transfers."},

            {"question": "How long is the warranty?",
             "answer": "Most products come with a 1-2 year manufacturer warranty. Extended warranty options are available at checkout."},

            {"question": "Can I upgrade RAM or storage after purchase?",
             "answer": "Most laptops allow RAM and storage upgrades. However, Apple products typically have soldered components. Check product specifications for upgrade options."},

            {"question": "Do you price match competitors?",
             "answer": "Yes, we offer price matching for identical products sold by authorized retailers. Terms and conditions apply."},

            {"question": "What's included in the box?",
             "answer": "Each product includes the device, power adapter, quick start guide, and warranty card. Additional accessories vary by model."},

            {"question": "How do I track my order?",
             "answer": "You'll receive a tracking number via email once your order ships. You can track your package on our website or the carrier's site."},

            {"question": "Can I cancel or modify my order?",
             "answer": "Orders can be cancelled or modified within 24 hours of placement. Contact customer service immediately for assistance."},

            {"question": "Do you offer student discounts?",
             "answer": "Yes, verified students and educators receive 10-15% discount on eligible products. Verification required through our education portal."},

            {"question": "What's the difference between refurbished and new?",
             "answer": "Refurbished products are professionally restored to like-new condition, tested, and come with warranty. New products are factory sealed."},

            {"question": "How do I choose the right laptop?",
             "answer": "Consider your use case: For basic tasks, 8GB RAM and i5 processor suffice. For gaming/video editing, opt for 16GB+ RAM and dedicated graphics."},

            {"question": "Which smartphone has the best camera?",
             "answer": "Currently, iPhone 15 Pro Max and Samsung Galaxy S24 Ultra offer the best camera systems with 48MP+ sensors and advanced computational photography."},

            {"question": "Is 5G worth it?",
             "answer": "5G provides faster speeds and lower latency. If available in your area and you stream/game frequently, it's worth the investment."},

            {"question": "How much storage do I need?",
             "answer": "256GB suits most users. Choose 512GB+ if you store many photos/videos or large apps. Cloud storage can supplement device storage."}
        ]

        output_path = self.output_dir / "text" / "faqs.json"
        with open(output_path, 'w') as f:
            json.dump({"faqs": faqs}, f, indent=2)
        print(f"Saved {len(faqs)} FAQs to {output_path}")
        return output_path

def main():
    """Generate all synthetic data"""
    print("Starting synthetic data generation...\n")

    generator = ProductDataGenerator()

    # Generate products
    print("Generating product catalog...")
    products = generator.generate_catalog(num_products=150)

    # Save in multiple formats
    generator.save_as_csv(products)
    generator.save_as_json(products)

    # Generate pricing data
    print("\nGenerating pricing data...")
    generator.generate_pricing_table(products)

    # Generate FAQs
    print("\nGenerating FAQs...")
    generator.generate_faqs()

    print("\n✓ Data generation complete!")
    print(f"  - {len(products)} products generated")
    print(f"  - Files saved to: data/raw/")

if __name__ == "__main__":
    main()
