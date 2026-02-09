"""
Populate test data for Go1 Commerce.

Usage (shell):
    bench --site <sitename> execute go1_commerce.go1_commerce.populate_test_data.run

Usage (browser console - logged in as Administrator):
    frappe.call({method: "go1_commerce.go1_commerce.populate_test_data.run", callback: function(r) { console.log(r); frappe.msgprint("Test data created!"); }})
"""

import frappe
import random
from datetime import datetime, timedelta


@frappe.whitelist()
def run():
    frappe.flags.in_test_data = True
    try:
        print("Starting test data population...")
        create_tax_categories()
        create_product_tags()
        create_product_brands()
        create_product_categories()
        create_product_attributes()
        create_products()
        create_customers()
        create_discounts()
        create_product_reviews()
        create_orders()
        frappe.db.commit()
        print("Test data population complete!")
    except Exception:
        frappe.db.rollback()
        frappe.log_error("Test data population failed")
        raise
    finally:
        frappe.flags.in_test_data = False


# ── Tax Categories ──────────────────────────────────────────────────

TAX_CATEGORIES = [
    {"tax_category_name": "GST 5%", "tax_percentage": 5.0},
    {"tax_category_name": "GST 12%", "tax_percentage": 12.0},
    {"tax_category_name": "GST 18%", "tax_percentage": 18.0},
    {"tax_category_name": "GST 28%", "tax_percentage": 28.0},
    {"tax_category_name": "Tax Free", "tax_percentage": 0.0},
]

def create_tax_categories():
    print("Creating tax categories...")
    for tc in TAX_CATEGORIES:
        if not frappe.db.exists("Tax Category", tc["tax_category_name"]):
            doc = frappe.get_doc({"doctype": "Tax Category", **tc})
            doc.insert(ignore_permissions=True)
    print(f"  Created {len(TAX_CATEGORIES)} tax categories")


# ── Product Tags ────────────────────────────────────────────────────

TAG_NAMES = [
    "New Arrival", "Best Seller", "Trending", "Sale", "Limited Edition",
    "Organic", "Eco Friendly", "Handmade", "Premium", "Budget Friendly",
    "Exclusive", "Clearance", "Featured", "Top Rated", "Most Viewed",
]

def create_product_tags():
    print("Creating product tags...")
    count = 0
    for tag in TAG_NAMES:
        if not frappe.db.exists("Product Tag", tag):
            doc = frappe.get_doc({"doctype": "Product Tag", "title": tag})
            doc.insert(ignore_permissions=True)
            count += 1
    print(f"  Created {count} product tags")


# ── Product Brands ──────────────────────────────────────────────────

BRAND_NAMES = [
    "TechVista", "GreenLeaf", "UrbanStyle", "PowerMax", "NaturePure",
    "SwiftGear", "HomeNest", "FitZone", "AquaFresh", "SolarEdge",
    "CloudNine", "EcoWear", "BrightStar", "ZenCraft", "VitalFoods",
    "PixelPro", "AeroFit", "PureBliss", "IronForge", "SilkTouch",
]

def create_product_brands():
    print("Creating product brands...")
    count = 0
    for name in BRAND_NAMES:
        if not frappe.db.exists("Product Brand", {"brand_name": name}):
            doc = frappe.get_doc({
                "doctype": "Product Brand",
                "brand_name": name,
                "published": 1,
                "warranty_information": f"{random.choice([1, 2, 3, 5])} year warranty",
            })
            doc.insert(ignore_permissions=True)
            count += 1
    print(f"  Created {count} product brands")


# ── Product Categories ──────────────────────────────────────────────

CATEGORIES = {
    "Electronics": ["Smartphones", "Laptops", "Tablets", "Headphones", "Cameras", "Smartwatches", "Speakers", "Chargers"],
    "Clothing": ["Men's Wear", "Women's Wear", "Kids Wear", "Sportswear", "Winter Wear", "Formal Wear"],
    "Home & Kitchen": ["Cookware", "Furniture", "Bedding", "Lighting", "Storage", "Cleaning"],
    "Health & Beauty": ["Skincare", "Haircare", "Supplements", "Personal Care", "Fragrances"],
    "Sports & Outdoors": ["Fitness Equipment", "Camping Gear", "Cycling", "Running", "Yoga"],
    "Books & Stationery": ["Fiction", "Non-Fiction", "Notebooks", "Art Supplies", "Pens"],
    "Food & Beverages": ["Snacks", "Beverages", "Organic Food", "Spices", "Dairy"],
    "Toys & Games": ["Board Games", "Action Figures", "Puzzles", "Educational Toys", "Dolls"],
}

def create_product_categories():
    print("Creating product categories...")
    count = 0
    for parent_name, children in CATEGORIES.items():
        if not frappe.db.exists("Product Category", {"category_name": parent_name}):
            parent = frappe.get_doc({
                "doctype": "Product Category",
                "category_name": parent_name,
                "is_active": 1,
                "is_group": 1,
                "display_order": count + 1,
            })
            parent.insert(ignore_permissions=True)
            count += 1

            for i, child_name in enumerate(children):
                if not frappe.db.exists("Product Category", {"category_name": child_name}):
                    child = frappe.get_doc({
                        "doctype": "Product Category",
                        "category_name": child_name,
                        "parent_product_category": parent.name,
                        "is_active": 1,
                        "is_group": 0,
                        "display_order": i + 1,
                    })
                    child.insert(ignore_permissions=True)
                    count += 1
    print(f"  Created {count} product categories")


# ── Product Attributes ──────────────────────────────────────────────

ATTRIBUTES = {
    "Color": ["Red", "Blue", "Green", "Black", "White", "Grey", "Navy", "Pink", "Brown", "Yellow"],
    "Size": ["XS", "S", "M", "L", "XL", "XXL"],
    "Material": ["Cotton", "Polyester", "Silk", "Leather", "Wool", "Linen", "Denim"],
    "Storage": ["32GB", "64GB", "128GB", "256GB", "512GB", "1TB"],
    "Weight": ["100g", "250g", "500g", "1kg", "2kg", "5kg"],
}

def create_product_attributes():
    print("Creating product attributes...")
    count = 0
    for attr_name, options in ATTRIBUTES.items():
        if not frappe.db.exists("Product Attribute", {"attribute_name": attr_name}):
            doc = frappe.get_doc({
                "doctype": "Product Attribute",
                "attribute_name": attr_name,
            })
            doc.insert(ignore_permissions=True)
            count += 1

            for opt in options:
                if not frappe.db.exists("Product Attribute Option", {"attribute": doc.name, "option_value": opt}):
                    opt_doc = frappe.get_doc({
                        "doctype": "Product Attribute Option",
                        "attribute": doc.name,
                        "option_value": opt,
                    })
                    opt_doc.insert(ignore_permissions=True)
    print(f"  Created {count} product attributes with options")


# ── Products ────────────────────────────────────────────────────────

PRODUCTS = [
    # Electronics
    ("Pro Max Smartphone 15", "Electronics", "Smartphones", "TechVista", 79999, 89999, 50),
    ("Ultra Slim Laptop 14 inch", "Electronics", "Laptops", "PixelPro", 64999, 74999, 30),
    ("Wireless Noise Cancelling Headphones", "Electronics", "Headphones", "SwiftGear", 4999, 6999, 100),
    ("Smart Watch Pro Series", "Electronics", "Smartwatches", "TechVista", 12999, 15999, 75),
    ("Bluetooth Portable Speaker", "Electronics", "Speakers", "PowerMax", 2499, 3499, 120),
    ("Mirrorless Camera 4K", "Electronics", "Cameras", "PixelPro", 54999, 59999, 25),
    ("10.5 inch Tablet", "Electronics", "Tablets", "TechVista", 29999, 34999, 40),
    ("Fast Charger 65W USB-C", "Electronics", "Chargers", "PowerMax", 1299, 1999, 200),
    ("Gaming Laptop 16 inch", "Electronics", "Laptops", "PixelPro", 109999, 124999, 15),
    ("Wireless Earbuds Pro", "Electronics", "Headphones", "SwiftGear", 3499, 4499, 150),
    ("Smart Home Hub", "Electronics", "Speakers", "CloudNine", 7999, 9999, 60),
    ("Action Camera 5K", "Electronics", "Cameras", "PixelPro", 24999, 29999, 35),
    ("E-Reader 7 inch", "Electronics", "Tablets", "BrightStar", 8999, 10999, 80),
    ("USB-C Multiport Charger", "Electronics", "Chargers", "PowerMax", 2499, 2999, 180),
    ("Kids Smart Watch", "Electronics", "Smartwatches", "TechVista", 3999, 4999, 90),

    # Clothing
    ("Classic Cotton T-Shirt", "Clothing", "Men's Wear", "UrbanStyle", 599, 999, 500),
    ("Denim Slim Fit Jeans", "Clothing", "Men's Wear", "UrbanStyle", 1499, 2499, 300),
    ("Floral Print Summer Dress", "Clothing", "Women's Wear", "SilkTouch", 1999, 2999, 200),
    ("Kids Cartoon Hoodie", "Clothing", "Kids Wear", "EcoWear", 799, 1199, 400),
    ("Sports Dry Fit Running Tee", "Clothing", "Sportswear", "AeroFit", 899, 1299, 350),
    ("Wool Blend Winter Jacket", "Clothing", "Winter Wear", "EcoWear", 3499, 4999, 100),
    ("Formal Slim Fit Shirt", "Clothing", "Formal Wear", "UrbanStyle", 1299, 1799, 250),
    ("Women's Yoga Leggings", "Clothing", "Sportswear", "AeroFit", 999, 1499, 300),
    ("Printed Casual Kurta", "Clothing", "Women's Wear", "SilkTouch", 1199, 1699, 200),
    ("Leather Belt Premium", "Clothing", "Men's Wear", "IronForge", 699, 999, 400),
    ("Kids School Uniform Set", "Clothing", "Kids Wear", "EcoWear", 999, 1499, 500),
    ("Track Pants Jogger", "Clothing", "Sportswear", "AeroFit", 799, 1199, 350),
    ("Puffer Jacket Quilted", "Clothing", "Winter Wear", "EcoWear", 2999, 3999, 80),
    ("Silk Formal Tie", "Clothing", "Formal Wear", "SilkTouch", 499, 799, 450),

    # Home & Kitchen
    ("Non-Stick Cookware Set 5pcs", "Home & Kitchen", "Cookware", "HomeNest", 2999, 4499, 80),
    ("Ergonomic Office Chair", "Home & Kitchen", "Furniture", "HomeNest", 8999, 12999, 40),
    ("Memory Foam Pillow Set", "Home & Kitchen", "Bedding", "PureBliss", 1499, 1999, 150),
    ("LED Desk Lamp Adjustable", "Home & Kitchen", "Lighting", "BrightStar", 1299, 1799, 120),
    ("Modular Storage Boxes 6pcs", "Home & Kitchen", "Storage", "HomeNest", 899, 1299, 200),
    ("Microfiber Cleaning Kit", "Home & Kitchen", "Cleaning", "HomeNest", 499, 799, 300),
    ("Cast Iron Skillet 12 inch", "Home & Kitchen", "Cookware", "IronForge", 1999, 2499, 90),
    ("Wooden Bookshelf 5 Tier", "Home & Kitchen", "Furniture", "HomeNest", 5999, 7999, 30),
    ("Cotton Bedsheet King Size", "Home & Kitchen", "Bedding", "PureBliss", 1999, 2999, 100),
    ("Smart LED Bulb Pack of 4", "Home & Kitchen", "Lighting", "BrightStar", 799, 1199, 250),
    ("Vacuum Storage Bags 10pcs", "Home & Kitchen", "Storage", "HomeNest", 599, 899, 180),
    ("Floor Mop Spinner", "Home & Kitchen", "Cleaning", "HomeNest", 1299, 1799, 100),

    # Health & Beauty
    ("Vitamin C Face Serum 30ml", "Health & Beauty", "Skincare", "NaturePure", 599, 899, 300),
    ("Argan Oil Hair Treatment", "Health & Beauty", "Haircare", "NaturePure", 799, 1199, 200),
    ("Multivitamin Tablets 60pcs", "Health & Beauty", "Supplements", "VitalFoods", 499, 699, 500),
    ("Electric Toothbrush Sonic", "Health & Beauty", "Personal Care", "AquaFresh", 1999, 2999, 100),
    ("Luxury Perfume 100ml", "Health & Beauty", "Fragrances", "PureBliss", 2499, 3499, 80),
    ("Sunscreen SPF50 100ml", "Health & Beauty", "Skincare", "NaturePure", 399, 599, 400),
    ("Anti Dandruff Shampoo 300ml", "Health & Beauty", "Haircare", "NaturePure", 349, 499, 350),
    ("Protein Powder 1kg Chocolate", "Health & Beauty", "Supplements", "VitalFoods", 1999, 2499, 120),
    ("Beard Grooming Kit", "Health & Beauty", "Personal Care", "ZenCraft", 899, 1299, 150),
    ("Rose Body Mist 200ml", "Health & Beauty", "Fragrances", "PureBliss", 499, 799, 200),

    # Sports & Outdoors
    ("Adjustable Dumbbell Set 20kg", "Sports & Outdoors", "Fitness Equipment", "FitZone", 3999, 5999, 50),
    ("2 Person Camping Tent", "Sports & Outdoors", "Camping Gear", "SwiftGear", 4999, 6999, 30),
    ("Mountain Bike Helmet", "Sports & Outdoors", "Cycling", "AeroFit", 1499, 1999, 80),
    ("Running Shoes Lightweight", "Sports & Outdoors", "Running", "AeroFit", 2999, 3999, 100),
    ("Yoga Mat Non-Slip 6mm", "Sports & Outdoors", "Yoga", "FitZone", 999, 1499, 200),
    ("Resistance Band Set 5pcs", "Sports & Outdoors", "Fitness Equipment", "FitZone", 599, 899, 250),
    ("Sleeping Bag All Season", "Sports & Outdoors", "Camping Gear", "SwiftGear", 2499, 3499, 40),
    ("Cycling Jersey Breathable", "Sports & Outdoors", "Cycling", "AeroFit", 1299, 1799, 60),
    ("Running Armband Phone Holder", "Sports & Outdoors", "Running", "SwiftGear", 399, 599, 300),
    ("Yoga Block Set of 2", "Sports & Outdoors", "Yoga", "FitZone", 499, 699, 180),

    # Books & Stationery
    ("Mystery Novel Bestseller", "Books & Stationery", "Fiction", "ZenCraft", 299, 499, 300),
    ("Business Strategy Guide", "Books & Stationery", "Non-Fiction", "ZenCraft", 399, 599, 200),
    ("Premium Leather Notebook A5", "Books & Stationery", "Notebooks", "ZenCraft", 599, 799, 150),
    ("Watercolor Paint Set 24 Colors", "Books & Stationery", "Art Supplies", "BrightStar", 899, 1299, 100),
    ("Fountain Pen Gold Trim", "Books & Stationery", "Pens", "ZenCraft", 1299, 1799, 80),
    ("Sci-Fi Adventure Novel", "Books & Stationery", "Fiction", "ZenCraft", 349, 499, 250),
    ("Cooking Recipes Collection", "Books & Stationery", "Non-Fiction", "ZenCraft", 449, 649, 180),
    ("Spiral Notebook Set 3pcs", "Books & Stationery", "Notebooks", "ZenCraft", 249, 349, 400),
    ("Sketch Pencil Set 12pcs", "Books & Stationery", "Art Supplies", "BrightStar", 399, 599, 200),
    ("Gel Pen Multicolor Pack 10", "Books & Stationery", "Pens", "ZenCraft", 199, 299, 500),

    # Food & Beverages
    ("Mixed Nuts Premium 500g", "Food & Beverages", "Snacks", "VitalFoods", 599, 799, 300),
    ("Green Tea 100 Bags", "Food & Beverages", "Beverages", "GreenLeaf", 399, 549, 400),
    ("Organic Honey 500g", "Food & Beverages", "Organic Food", "GreenLeaf", 449, 649, 200),
    ("Garam Masala Blend 200g", "Food & Beverages", "Spices", "VitalFoods", 199, 299, 500),
    ("Greek Yogurt Plain 400g", "Food & Beverages", "Dairy", "NaturePure", 149, 199, 200),
    ("Protein Bar Pack of 6", "Food & Beverages", "Snacks", "VitalFoods", 499, 699, 250),
    ("Cold Press Coffee 250ml x4", "Food & Beverages", "Beverages", "GreenLeaf", 349, 499, 300),
    ("Quinoa Organic 1kg", "Food & Beverages", "Organic Food", "GreenLeaf", 599, 799, 150),
    ("Turmeric Powder 500g", "Food & Beverages", "Spices", "VitalFoods", 149, 249, 400),
    ("Almond Milk 1L", "Food & Beverages", "Dairy", "NaturePure", 199, 299, 350),

    # Toys & Games
    ("Strategy Board Game Classic", "Toys & Games", "Board Games", "CloudNine", 999, 1499, 100),
    ("Superhero Action Figure 12in", "Toys & Games", "Action Figures", "CloudNine", 799, 1199, 150),
    ("1000 Piece Jigsaw Puzzle", "Toys & Games", "Puzzles", "CloudNine", 499, 699, 200),
    ("STEM Building Kit 200pcs", "Toys & Games", "Educational Toys", "BrightStar", 1499, 1999, 80),
    ("Fashion Doll with Accessories", "Toys & Games", "Dolls", "CloudNine", 699, 999, 180),
    ("Card Game Family Fun", "Toys & Games", "Board Games", "CloudNine", 399, 599, 250),
    ("Dinosaur Figure Collection 6pcs", "Toys & Games", "Action Figures", "CloudNine", 599, 899, 120),
    ("Wooden Puzzle Toddler Set", "Toys & Games", "Puzzles", "CloudNine", 349, 499, 300),
    ("Science Experiment Kit", "Toys & Games", "Educational Toys", "BrightStar", 999, 1499, 90),
    ("Plush Teddy Bear 18in", "Toys & Games", "Dolls", "CloudNine", 599, 799, 200),
]

def create_products():
    print("Creating products...")
    brands = {b.brand_name: b.name for b in frappe.get_all("Product Brand", fields=["name", "brand_name"])}
    categories = {c.category_name: c.name for c in frappe.get_all("Product Category", fields=["name", "category_name"])}

    count = 0
    for item_name, parent_cat, sub_cat, brand_name, price, old_price, stock in PRODUCTS:
        if frappe.db.exists("Product", {"item": item_name}):
            continue

        brand_id = brands.get(brand_name)
        category_id = categories.get(sub_cat)

        doc = frappe.get_doc({
            "doctype": "Product",
            "item": item_name,
            "price": price,
            "old_price": old_price,
            "stock": stock,
            "sku": f"SKU-{count + 1001:05d}",
            "is_active": 1,
            "weight": round(random.uniform(0.1, 10.0), 2),
            "short_description": f"High quality {item_name.lower()} from {brand_name}.",
            "product_categories": [{"category": category_id}] if category_id else [],
            "product_brands": [{"brand": brand_id}] if brand_id else [],
        })
        doc.insert(ignore_permissions=True)
        count += 1

    print(f"  Created {count} products")


# ── Customers ───────────────────────────────────────────────────────

FIRST_NAMES = [
    "Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Reyansh", "Ayaan", "Krishna", "Ishaan",
    "Ananya", "Diya", "Myra", "Sara", "Aadhya", "Isha", "Kiara", "Riya", "Priya", "Neha",
    "Rohan", "Karthik", "Vikram", "Rahul", "Amit", "Suresh", "Deepak", "Raj", "Nikhil", "Mohit",
    "Sneha", "Pooja", "Meera", "Kavya", "Shreya", "Divya", "Nisha", "Swati", "Anjali", "Lakshmi",
    "Manish", "Gaurav", "Sanjay", "Rajesh", "Arun", "Vijay", "Prakash", "Manoj", "Sunil", "Ramesh",
]

LAST_NAMES = [
    "Kumar", "Sharma", "Singh", "Patel", "Reddy", "Nair", "Verma", "Gupta", "Joshi", "Iyer",
    "Das", "Pillai", "Rao", "Menon", "Bhat", "Chauhan", "Mishra", "Pandey", "Tiwari", "Yadav",
]

CITIES = ["Chennai", "Mumbai", "Delhi", "Bangalore", "Hyderabad", "Kolkata", "Pune", "Ahmedabad", "Jaipur", "Lucknow"]
ADDRESSES = [
    "12, MG Road", "45, Park Street", "78, Anna Nagar", "23, Gandhi Street",
    "56, Lake View Road", "89, Temple Road", "34, Nehru Nagar", "67, Station Road",
    "90, Hill View Colony", "11, Market Street", "44, Ring Road", "77, Civil Lines",
]

def create_customers():
    print("Creating customers...")
    count = 0
    for i in range(100):
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        email = f"{first.lower()}.{last.lower()}{i}@example.com"
        phone = f"9{random.randint(100000000, 999999999)}"

        if frappe.db.exists("Customers", {"email": email}):
            continue

        doc = frappe.get_doc({
            "doctype": "Customers",
            "first_name": first,
            "last_name": last,
            "email": email,
            "phone": phone,
            "naming_series": "CUST-",
            "customer_status": "Approved",
            "customer_type": random.choice(["Individual", "Company"]),
            "address": random.choice(ADDRESSES),
            "zipcode": str(random.randint(100000, 999999)),
            "table_6": [{
                "first_name": first,
                "last_name": last,
                "address": random.choice(ADDRESSES),
                "city": random.choice(CITIES),
                "zipcode": str(random.randint(100000, 999999)),
                "phone": phone,
                "is_default": 1,
            }],
        })
        doc.insert(ignore_permissions=True)
        count += 1

    print(f"  Created {count} customers")


# ── Discounts ───────────────────────────────────────────────────────

def create_discounts():
    print("Creating discounts...")
    today = datetime.now().date()
    discount_data = [
        {"name1": "Summer Sale 10%", "discount_type": "Assigned to Sub Total", "percent_or_amount": "Discount Percentage", "discount_percentage": "10", "start_date": today, "end_date": today + timedelta(days=90)},
        {"name1": "Flat 200 Off", "discount_type": "Assigned to Sub Total", "percent_or_amount": "Discount Amount", "discount_amount": "200", "start_date": today, "end_date": today + timedelta(days=60)},
        {"name1": "Free Shipping", "discount_type": "Assigned to Delivery Charges", "percent_or_amount": "Discount Percentage", "discount_percentage": "100", "start_date": today, "end_date": today + timedelta(days=30)},
        {"name1": "Electronics 15% Off", "discount_type": "Assigned to Products", "percent_or_amount": "Discount Percentage", "discount_percentage": "15", "start_date": today, "end_date": today + timedelta(days=45)},
        {"name1": "Winter Clearance 25%", "discount_type": "Assigned to Categories", "percent_or_amount": "Discount Percentage", "discount_percentage": "25", "start_date": today, "end_date": today + timedelta(days=30)},
        {"name1": "New User Flat 500 Off", "discount_type": "Assigned to Sub Total", "percent_or_amount": "Discount Amount", "discount_amount": "500", "requires_coupon_code": 1, "coupon_code": "WELCOME500", "start_date": today, "end_date": today + timedelta(days=120)},
        {"name1": "Buy More Save 20%", "discount_type": "Assigned to Sub Total", "percent_or_amount": "Discount Percentage", "discount_percentage": "20", "min_qty": 3, "start_date": today, "end_date": today + timedelta(days=60)},
        {"name1": "Weekend Special 12%", "discount_type": "Assigned to Sub Total", "percent_or_amount": "Discount Percentage", "discount_percentage": "12", "start_date": today, "end_date": today + timedelta(days=14)},
        {"name1": "Flash Sale 30% Off", "discount_type": "Assigned to Products", "percent_or_amount": "Discount Percentage", "discount_percentage": "30", "start_date": today, "end_date": today + timedelta(days=7)},
        {"name1": "Loyalty Reward 500", "discount_type": "Assigned to Sub Total", "percent_or_amount": "Discount Amount", "discount_amount": "500", "requires_coupon_code": 1, "coupon_code": "LOYAL500", "start_date": today, "end_date": today + timedelta(days=180)},
    ]

    count = 0
    for d in discount_data:
        if frappe.db.exists("Discounts", {"name1": d["name1"]}):
            continue
        doc = frappe.get_doc({
            "doctype": "Discounts",
            "naming_series": "D-",
            "price_or_product_discount": "Price",
            "limitations": "Unlimited",
            **d,
        })
        doc.insert(ignore_permissions=True)
        count += 1

    print(f"  Created {count} discounts")


# ── Product Reviews ─────────────────────────────────────────────────

REVIEW_TITLES = [
    "Excellent product!", "Very good quality", "Worth the price", "Average product",
    "Good but could be better", "Amazing experience", "Highly recommended",
    "Not bad at all", "Superb quality", "Decent purchase", "Love it!",
    "Great value for money", "Impressive quality", "Satisfied customer",
    "Would buy again", "Perfect gift", "Exactly as described", "Fast delivery too",
    "Better than expected", "Solid product",
]

REVIEW_MESSAGES = [
    "I've been using this for a week now and it's been great. Highly recommend to anyone looking for quality.",
    "The product arrived well packaged and looks exactly like the photos. Very happy with my purchase.",
    "Good product overall. The quality is decent for the price point. Would consider buying again.",
    "Exceeded my expectations! The build quality is premium and it works perfectly.",
    "Solid purchase. Nothing fancy but gets the job done reliably. Good value.",
    "This is my second purchase from this brand and they never disappoint. Excellent quality.",
    "The product is okay. Not the best I've used but acceptable for daily use.",
    "Fantastic product! My family loves it. Will definitely order more.",
    "Great quality materials and well designed. Looks premium and feels durable.",
    "Bought this as a gift and the recipient was thrilled. Packaging was nice too.",
]

def create_product_reviews():
    print("Creating product reviews...")
    products = frappe.get_all("Product", fields=["name", "item"], limit=0)
    if not products:
        print("  No products found. Skipping reviews.")
        return

    count = 0
    for product in products:
        num_reviews = random.randint(1, 4)
        for _ in range(num_reviews):
            first = random.choice(FIRST_NAMES)
            last = random.choice(LAST_NAMES)
            doc = frappe.get_doc({
                "doctype": "Product Review",
                "product": product.name,
                "customer": f"{first} {last}",
                "email": f"{first.lower()}.{last.lower()}@example.com",
                "review_title": random.choice(REVIEW_TITLES),
                "review_message": random.choice(REVIEW_MESSAGES),
                "rating": random.choice([0.6, 0.8, 1.0, 0.4, 0.2]),
                "is_approved": random.choice([0, 1, 1, 1]),
            })
            doc.insert(ignore_permissions=True)
            count += 1

    print(f"  Created {count} product reviews")


# ── Orders ──────────────────────────────────────────────────────────

PAYMENT_STATUSES = ["Pending", "Paid", "Partially Paid"]

def create_orders():
    print("Creating orders...")
    customers = frappe.get_all("Customers", fields=["name", "first_name", "last_name", "email"], limit=0)
    products = frappe.get_all("Product", fields=["name", "item", "price"], limit=0)
    order_statuses = frappe.get_all("Order Status", fields=["name"], limit=0)
    shipping_methods = frappe.get_all("Shipping Method", fields=["name"], limit=0)
    payment_methods = frappe.get_all("Payment Method", fields=["name"], limit=0)

    if not customers or not products:
        print("  No customers or products found. Skipping orders.")
        return

    status_names = [s.name for s in order_statuses] if order_statuses else ["Pending"]
    shipping_names = [s.name for s in shipping_methods] if shipping_methods else []
    payment_names = [p.name for p in payment_methods] if payment_methods else []

    count = 0
    today_date = datetime.now().date()

    for i in range(150):
        customer = random.choice(customers)
        num_items = random.randint(1, 5)
        order_items = random.sample(products, min(num_items, len(products)))

        items = []
        subtotal = 0
        for prod in order_items:
            qty = random.randint(1, 3)
            price = prod.price or random.randint(200, 5000)
            amount = price * qty
            subtotal += amount
            items.append({
                "item": prod.name,
                "item_name": prod.item,
                "quantity": qty,
                "price": price,
                "amount": amount,
            })

        shipping = random.choice([0, 49, 99, 149, 199])
        tax = round(subtotal * 0.18, 2)
        total = subtotal + shipping + tax
        order_date = today_date - timedelta(days=random.randint(0, 180))

        order_doc = {
            "doctype": "Order",
            "naming_series": "ORD-",
            "customer_name": f"{customer.first_name} {customer.last_name}",
            "customer_email": customer.email,
            "order_date": order_date,
            "payment_status": random.choice(PAYMENT_STATUSES),
            "order_subtotal": subtotal,
            "shipping_charges": shipping,
            "total_tax_amount": tax,
            "total_amount": total,
            "outstanding_amount": total if random.random() > 0.5 else 0,
            "paid_amount": 0 if random.random() > 0.5 else total,
            "order_item": items,
        }

        if status_names:
            order_doc["status"] = random.choice(status_names)
        if shipping_names:
            order_doc["shipping_method"] = random.choice(shipping_names)
        if payment_names:
            order_doc["payment_method"] = random.choice(payment_names)

        try:
            doc = frappe.get_doc(order_doc)
            doc.insert(ignore_permissions=True)
            count += 1
        except Exception as e:
            print(f"  Warning: Failed to create order {i + 1}: {str(e)[:80]}")
            continue

    print(f"  Created {count} orders")
