from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

# Initial Product List
products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "Electronics", "in_stock": False},
    {"id": 4, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": True}
]


# Product Model
class Product(BaseModel):
    name: str
    price: int
    category: str
    in_stock: bool


# ------------------------------------------------
# GET ALL PRODUCTS
# ------------------------------------------------
@app.get("/products")
def get_products():
    return {"products": products, "total": len(products)}


# ------------------------------------------------
# ADD PRODUCT (POST)
# ------------------------------------------------
@app.post("/products", status_code=201)
def add_product(product: Product):

    for p in products:
        if p["name"].lower() == product.name.lower():
            raise HTTPException(status_code=400, detail="Product already exists")

    new_id = max(p["id"] for p in products) + 1

    new_product = {
        "id": new_id,
        "name": product.name,
        "price": product.price,
        "category": product.category,
        "in_stock": product.in_stock
    }

    products.append(new_product)

    return {"message": "Product added", "product": new_product}


# ------------------------------------------------
# INVENTORY AUDIT (Q5)
# MUST BE ABOVE /products/{product_id}
# ------------------------------------------------
@app.get("/products/audit")
def audit_products():

    total_products = len(products)

    in_stock_products = [p for p in products if p["in_stock"]]
    out_of_stock_products = [p["name"] for p in products if not p["in_stock"]]

    total_stock_value = sum(p["price"] * 10 for p in in_stock_products)

    most_expensive = max(products, key=lambda x: x["price"])

    return {
        "total_products": total_products,
        "in_stock_count": len(in_stock_products),
        "out_of_stock_names": out_of_stock_products,
        "total_stock_value": total_stock_value,
        "most_expensive": {
            "name": most_expensive["name"],
            "price": most_expensive["price"]
        }
    }


# ------------------------------------------------
# BONUS - CATEGORY DISCOUNT
# MUST BE ABOVE /products/{product_id}
# ------------------------------------------------
@app.put("/products/discount")
def apply_discount(
    category: str,
    discount_percent: int = Query(..., gt=0, lt=100)
):

    updated_products = []

    for p in products:

        if p["category"].lower() == category.lower():

            new_price = int(p["price"] * (1 - discount_percent / 100))

            p["price"] = new_price

            updated_products.append({
                "name": p["name"],
                "new_price": new_price
            })

    if not updated_products:
        return {"message": "No products found in this category"}

    return {
        "updated_count": len(updated_products),
        "products": updated_products
    }


# ------------------------------------------------
# UPDATE PRODUCT (PUT)
# ------------------------------------------------
@app.put("/products/{product_id}")
def update_product(
    product_id: int,
    price: Optional[int] = None,
    in_stock: Optional[bool] = None
):

    for p in products:

        if p["id"] == product_id:

            if price is not None:
                p["price"] = price

            if in_stock is not None:
                p["in_stock"] = in_stock

            return {"message": "Product updated", "product": p}

    raise HTTPException(status_code=404, detail="Product not found")


# ------------------------------------------------
# DELETE PRODUCT (Q3)
# ------------------------------------------------
@app.delete("/products/{product_id}")
def delete_product(product_id: int):

    for p in products:

        if p["id"] == product_id:

            products.remove(p)

            return {"message": f"Product '{p['name']}' deleted"}

    raise HTTPException(status_code=404, detail="Product not found")


# ------------------------------------------------
# GET PRODUCT BY ID
# ------------------------------------------------
@app.get("/products/{product_id}")
def get_product(product_id: int):

    for p in products:

        if p["id"] == product_id:
            return p

    raise HTTPException(status_code=404, detail="Product not found")