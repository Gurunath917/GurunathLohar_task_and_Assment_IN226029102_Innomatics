from fastapi import FastAPI

# Create FastAPI app
app = FastAPI()

# Temporary product database (list of dictionaries)
products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": False},
    {"id": 4, "name": "USB Cable", "price": 199, "category": "Electronics", "in_stock": True},

    # Added products (Assignment Q1)
    {"id": 5, "name": "Laptop Stand", "price": 899, "category": "Electronics", "in_stock": True},
    {"id": 6, "name": "Mechanical Keyboard", "price": 2499, "category": "Electronics", "in_stock": True},
    {"id": 7, "name": "Webcam", "price": 1499, "category": "Electronics", "in_stock": False}
]


# Home endpoint
@app.get("/")
def home():
    return {"message": "Welcome to My E-commerce Store API"}


# 1️- Get all products
# URL: http://127.0.0.1:8000/products
@app.get("/products")
def get_products():
    return {
        "products": products,
        "total": len(products)  # count of products
    }


# 2️- Filter products by category
# URL: /products/category/Electronics
@app.get("/products/category/{category}")
def get_by_category(category: str):

    result = []

    for product in products:
        if product["category"].lower() == category.lower():
            result.append(product)

    if len(result) == 0:
        return {"error": "No products found in this category"}

    return {"products": result}


# 3️- Show only in-stock products
# URL: /products/instock
@app.get("/products/instock")
def instock_products():

    instock = []

    for product in products:
        if product["in_stock"] == True:
            instock.append(product)

    return {
        "in_stock_products": instock,
        "count": len(instock)
    }


# 4️- Store summary information
# URL: /store/summary
@app.get("/store/summary")
def store_summary():

    total_products = len(products)

    instock = 0

    for product in products:
        if product["in_stock"]:
            instock += 1

    out_of_stock = total_products - instock

    # collect unique categories
    categories = []
    for product in products:
        if product["category"] not in categories:
            categories.append(product["category"])

    return {
        "store_name": "My E-commerce Store",
        "total_products": total_products,
        "in_stock": instock,
        "out_of_stock": out_of_stock,
        "categories": categories
    }


# 5️- Search products by name (case-insensitive)
# URL: /products/search/mouse
@app.get("/products/search/{keyword}")
def search_products(keyword: str):

    result = []

    for product in products:
        if keyword.lower() in product["name"].lower():
            result.append(product)

    if len(result) == 0:
        return {"message": "No products matched your search"}

    return {
        "matched_products": result,
        "total_matches": len(result)
    }


# Bonus: Cheapest and most expensive product
# URL: /products/deals
@app.get("/products/deals")
def deals():

    cheapest = min(products, key=lambda p: p["price"])
    expensive = max(products, key=lambda p: p["price"])

    return {
        "best_deal": cheapest,
        "premium_pick": expensive
    }