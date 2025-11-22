import json
import random
import string
import numpy as np
from datetime import datetime, timedelta

# Existing + 10 new categories with subcategories and package types
categories = {
    "Dairy": {"Milk": ["carton", "bottle"], "Cheese": ["block", "pack"], "Yogurt": ["cup", "bottle"]},
    "Bakery": {"Bread": ["bag", "pack"], "Pastry": ["box", "pack"], "Buns": ["bag", "box"]},
    "Beverages": {"Juice": ["bottle", "carton"], "Soda": ["can", "bottle"], "Water": ["bottle", "carton"]},
    "Snacks": {"Chips": ["bag"], "Nuts": ["bag", "box"], "Chocolate": ["bar", "box"]},
    # 10 new categories
    "Frozen": {"Ice Cream": ["tub", "cone"], "Frozen Pizza": ["box"], "Frozen Vegetables": ["bag", "box"]},
    "Meat": {"Chicken": ["pack", "tray"], "Beef": ["pack", "tray"], "Pork": ["pack", "tray"]},
    "Seafood": {"Fish": ["pack", "tray"], "Shrimp": ["pack"], "Crab": ["pack"]},
    "Cereals": {"Cornflakes": ["box"], "Oats": ["bag", "box"], "Granola": ["bag", "box"]},
    "Condiments": {"Ketchup": ["bottle"], "Mustard": ["bottle"], "Mayonnaise": ["jar", "tube"]},
    "Pasta": {"Spaghetti": ["bag"], "Macaroni": ["bag"], "Lasagna": ["box"]},
    "Sauces": {"Tomato Sauce": ["jar", "bottle"], "Pesto": ["jar"], "Soy Sauce": ["bottle"]},
    "Snacks_Healthy": {"Protein Bar": ["box"], "Trail Mix": ["bag"], "Dried Fruit": ["bag"]},
    "Beverages_Alcohol": {"Beer": ["bottle", "can"], "Wine": ["bottle"], "Whiskey": ["bottle"]},
    "Household": {"Detergent": ["bottle"], "Soap": ["bar", "pack"], "Paper Towels": ["rolls", "pack"]}
}

# Get the total number of subcategories
total_subcategories = sum(len(subcats) for subcats in categories.values())
print(f"Total subcategories: {total_subcategories}")

# Generate random number of brands (2 to 5) for each subcategory
subcategory_brands = {}
for category, subcats in categories.items():
    for sub in subcats:
        num_brands = random.randint(2, 5)
        brand_names = [f"{sub}Brand{letter}" for letter in string.ascii_uppercase[:num_brands]]
        subcategory_brands[sub] = brand_names

# Example: print generated brands
for sub, brands in subcategory_brands.items():
    print(f"{sub}: {brands}")

def generate_product_info(counter, sub, category, package_types, used_names):
    weight_unit = "L" if "Milk" in sub else "kg"
    
    # Ensure unique product_name
    while True:
        name_suffix = random.randint(1000, 9999)  # increased range to reduce collision
        product_name = f"{sub} {name_suffix}"
        if product_name not in used_names:
            used_names.add(product_name)
            break

    return {
        "product_id": f"P{counter}",
        "product_name": product_name,
        "brand": random.choice(subcategory_brands.get(sub, ["GenericBrand"])),
        "category": category,
        "subcategory": sub,
        "package": {
            "weight": round(random.uniform(0.2, 5.0), 2),
            "weight_unit": weight_unit,
            "package_type": random.choice(package_types)
        }
    }

# Generate product info only
all_products = []
counter = 1000
products_per_subcat = 50  # 50 products per subcategory

for category, subcats in categories.items():
    for sub, package_types in subcats.items():
        used_names = set()  # track unique names for this subcategory
        for _ in range(products_per_subcat):
            counter += 1
            product = generate_product_info(counter, sub, category, package_types, used_names)
            all_products.append(product)

# Save to JSON
with open("dataset/products.json", "w") as f:
    json.dump({"products": all_products}, f, indent=2)

print(f"Generated {products_per_subcat} unique products per subcategory for all categories.")

'''
---------------------------------------------------------------------------------------------------------------------
'''

# Load stores and products
with open("dataset/stores.json", "r") as f:
    stores_data = json.load(f)["stores"]

with open("dataset/products.json", "r") as f:
    products_data = json.load(f)["products"]

# Constants
COMMON_RATE = 0.7  # 70% of products common across stores
MIN_DISCOUNT = 0
MAX_DISCOUNT = 100
MEAN_DISCOUNT = 10
STD_DISCOUNT = 5

# Helper function to generate pricing
def generate_pricing():
    normal_price = round(random.uniform(1.0, 20.0), 2)
    discount_percentage = max(MIN_DISCOUNT, min(MAX_DISCOUNT, round(np.random.normal(loc=MEAN_DISCOUNT, scale=STD_DISCOUNT), 1)))
    real_price = round(normal_price * (1 - discount_percentage / 100), 2)
    return {
        "normal_price": normal_price,
        "discount_percentage": discount_percentage,
        "real_price": real_price
    }

# Helper function to generate stock info
def generate_stock_info():
    stock = random.randint(0, 50)
    availability_status = int(round(stock / 10))  # Scale stock to 0-5
    restock_date = (datetime.now() + timedelta(days=random.randint(1, 30))).isoformat()
    return {
        "stock": stock,
        "availability_status": availability_status,
        "restock_date": restock_date
    }

from collections import defaultdict

# Group products by subcategory
subcategory_products = defaultdict(list)
for product in products_data:
    subcategory_products[product["subcategory"]].append(product)

# Determine common products per subcategory
common_products = []
for subcat, products in subcategory_products.items():
    num_common_sub = max(1, int(len(products) * COMMON_RATE))  # at least 1 common per subcategory
    common_products.extend(random.sample(products, num_common_sub))

store_products_list = []

# Determine number of common products
num_products = len(products_data)
num_common = int(num_products * COMMON_RATE)
common_products = random.sample(products_data, num_common)

# Print a few common products to check
print("Sample of common products (first 10):")
for product in common_products[:10]:
    print(f"{product['product_id']} - {product['product_name']} - {product['subcategory']}")

store_products_list = []

for store in stores_data:
    store_id = store["store_id"]
    
    # Add common products with store-specific pricing and stock
    for product in common_products:
        store_products_list.append({
            "store_id": store_id,
            "product_id": product["product_id"],
            "pricing": generate_pricing(),
            "stock_info": generate_stock_info()
        })
    
    # Add unique products (not in common)
    remaining_products = [p for p in products_data if p not in common_products]
    num_unique = random.randint(5, 15)  # adjust as needed
    unique_products = random.sample(remaining_products, min(num_unique, len(remaining_products)))
    
    for product in unique_products:
        store_products_list.append({
            "store_id": store_id,
            "product_id": product["product_id"],
            "pricing": generate_pricing(),
            "stock_info": generate_stock_info()
        })

# Save to JSON
with open("dataset/store_products.json", "w") as f:
    json.dump({"store_products": store_products_list}, f, indent=2)

print(f"Generated store-products dataset with {len(store_products_list)} entries for {len(stores_data)} stores.")

