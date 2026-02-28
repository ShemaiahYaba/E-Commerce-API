"""
Seed the database with rich demo products across multiple categories.
Run AFTER: flask db upgrade  AND  py scripts/seed.py  (which creates categories + admin)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def seed_products():
    from app import create_app
    from database import db
    from models import Product, Category
    from decimal import Decimal

    app = create_app("development")
    with app.app_context():
        if Product.query.count() > 0:
            print("Products already seeded; skip.")
            return

        cats = {c.name: c for c in Category.query.all()}
        elec = cats.get("Electronics")
        cloth = cats.get("Clothing")

        if not elec or not cloth:
            print("ERROR: Run 'py scripts/seed.py' first to create base categories.")
            sys.exit(1)

        products = [
            # Electronics
            Product(name="Wireless Noise-Cancelling Headphones", description="Premium over-ear headphones with 30h battery and ANC.", price=Decimal("149.99"), stock=42, sku="ELEC-001", category_id=elec.id),
            Product(name="Smart 4K UHD Monitor 27\"", description="IPS panel, 144Hz refresh rate, USB-C, HDR400 certified.", price=Decimal("399.00"), stock=18, sku="ELEC-002", category_id=elec.id),
            Product(name="Mechanical Gaming Keyboard", description="TKL layout, hot-swappable switches, RGB backlight.", price=Decimal("89.95"), stock=65, sku="ELEC-003", category_id=elec.id),
            Product(name="Ergonomic Wireless Mouse", description="Vertical grip, 4000 DPI, silent clicks, 70-day battery.", price=Decimal("54.99"), stock=80, sku="ELEC-004", category_id=elec.id),
            Product(name="USB-C 100W GaN Charger", description="Compact 4-port charger, charges laptop + 3 devices.", price=Decimal("34.99"), stock=120, sku="ELEC-005", category_id=elec.id),
            Product(name="Portable Bluetooth Speaker", description="360° sound, IPX7 waterproof, 24h playtime.", price=Decimal("79.00"), stock=55, sku="ELEC-006", category_id=elec.id),
            Product(name="Smart LED Desk Lamp", description="10 brightness levels, 3 colour temps, USB charging port.", price=Decimal("39.99"), stock=33, sku="ELEC-007", category_id=elec.id),
            Product(name="1TB External SSD", description="540 MB/s read/write, USB 3.2, shock-resistant.", price=Decimal("109.99"), stock=27, sku="ELEC-008", category_id=elec.id),
            Product(name="Webcam 4K 60fps", description="Auto-focus, background blur, ring light built-in.", price=Decimal("129.00"), stock=0, sku="ELEC-009", category_id=elec.id),
            Product(name="Wireless Charging Pad (15W)", description="Qi-certified, charges iPhone, Android and earbuds.", price=Decimal("24.99"), stock=200, sku="ELEC-010", category_id=elec.id),

            # Clothing
            Product(name="Classic Slim-Fit T-Shirt", description="100% organic cotton, pre-shrunk, available in 12 colours.", price=Decimal("22.00"), stock=300, sku="CLTH-001", category_id=cloth.id),
            Product(name="Technical Running Jacket", description="Windproof, packable, reflective strips, 3-pocket.", price=Decimal("89.99"), stock=45, sku="CLTH-002", category_id=cloth.id),
            Product(name="Slim Chinos", description="Stretch twill fabric, stain-resistant, 4 neutral tones.", price=Decimal("59.95"), stock=72, sku="CLTH-003", category_id=cloth.id),
            Product(name="Premium Hoodie", description="400gsm French terry, kangaroo pocket, preshrunk.", price=Decimal("64.00"), stock=88, sku="CLTH-004", category_id=cloth.id),
            Product(name="Merino Wool Crew-Neck Sweater", description="Extra-fine merino, machine washable, anti-pilling.", price=Decimal("99.99"), stock=5, sku="CLTH-005", category_id=cloth.id),
            Product(name="Athletic Shorts", description="4-way stretch, moisture-wicking, lined, 5\" inseam.", price=Decimal("34.99"), stock=150, sku="CLTH-006", category_id=cloth.id),
            Product(name="Canvas Sneakers", description="Vegan canvas upper, padded collar, rubber sole.", price=Decimal("49.00"), stock=0, sku="CLTH-007", category_id=cloth.id),
            Product(name="Leather Belt", description="Full-grain leather, 35mm width, brushed silver buckle.", price=Decimal("39.99"), stock=60, sku="CLTH-008", category_id=cloth.id),
            Product(name="Puffer Vest", description="80g insulation, helmet-compatible collar, 2 zip pockets.", price=Decimal("74.99"), stock=22, sku="CLTH-009", category_id=cloth.id),
            Product(name="Beanie Hat", description="Chunky ribbed knit, 100% acrylic, one-size-fits-all.", price=Decimal("18.00"), stock=95, sku="CLTH-010", category_id=cloth.id),
        ]

        db.session.add_all(products)
        db.session.commit()
        print(f"Seeded {len(products)} demo products across Electronics & Clothing.")


if __name__ == "__main__":
    seed_products()
