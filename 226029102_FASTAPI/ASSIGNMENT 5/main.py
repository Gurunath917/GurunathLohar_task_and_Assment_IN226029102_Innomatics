from fastapi import FastAPI, Query, HTTPException
from typing import List, Optional
from pydantic import BaseModel
import math

app = FastAPI()

# -----------------------------
#  Sample Data (In-Memory DB)
# -----------------------------

products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics"},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery"},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "Electronics"},
    {"id": 4, "name": "Pen Set", "price": 49, "category": "Stationery"},
]

orders = []
order_counter = 1


# -----------------------------
#  Models
# -----------------------------

class Order(BaseModel):
    customer_name: str
    product_id: int


# -----------------------------
#  Create Order
# -----------------------------

@app.post("/orders")
def create_order(order: Order):
    global order_counter

    new_order = {
        "order_id": order_counter,
        "customer_name": order.customer_name,
        "product_id": order.product_id
    }

    orders.append(new_order)
    order_counter += 1

    return {"message": "Order placed successfully", "order": new_order}


# -----------------------------
#  SEARCH PRODUCTS
# -----------------------------

@app.get("/products/search")
def search_products(keyword: str = Query(...)):
    result = [p for p in products if keyword.lower() in p["name"].lower()]

    if not result:
        return {"message": f"No products found for: {keyword}"}

    return {
        "keyword": keyword,
        "total_found": len(result),
        "products": result
    }


# -----------------------------
# ↕ SORT PRODUCTS
# -----------------------------

@app.get("/products/sort")
def sort_products(
    sort_by: str = Query("price"),
    order: str = Query("asc")
):
    #  Validate sort_by
    if sort_by not in ["price", "name"]:
        raise HTTPException(
            status_code=400,
            detail="sort_by must be 'price' or 'name'"
        )

    #  Validate order (NEW IMPROVEMENT)
    if order not in ["asc", "desc"]:
        raise HTTPException(
            status_code=400,
            detail="order must be 'asc' or 'desc'"
        )

    # Sorting logic
    reverse = (order == "desc")

    sorted_products = sorted(
        products,
        key=lambda x: x[sort_by],
        reverse=reverse
    )

    return {
        "sort_by": sort_by,
        "order": order,
        "products": sorted_products
    }

# -----------------------------
#  PAGINATION
# -----------------------------

@app.get("/products/page")
def paginate_products(
    page: int = Query(1, ge=1),
    limit: int = Query(2, ge=1)
):
    total = len(products)
    total_pages = math.ceil(total / limit)

    start = (page - 1) * limit
    end = start + limit

    return {
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
        "products": products[start:end]
    }


# -----------------------------
#  SEARCH ORDERS
# -----------------------------

@app.get("/orders/search")
def search_orders(customer_name: str = Query(...)):
    result = [
        o for o in orders
        if customer_name.lower() in o["customer_name"].lower()
    ]

    if not result:
        return {"message": f"No orders found for: {customer_name}"}

    return {
        "customer_name": customer_name,
        "total_found": len(result),
        "orders": result
    }


# -----------------------------
#  SORT BY CATEGORY + PRICE
# -----------------------------

@app.get("/products/sort-by-category")
def sort_by_category():
    sorted_products = sorted(
        products,
        key=lambda x: (x["category"], x["price"])
    )

    return {
        "message": "Sorted by category then price",
        "products": sorted_products
    }


# -----------------------------
# COMBINED ENDPOINT
# -----------------------------

@app.get("/products/browse")
def browse_products(
    keyword: Optional[str] = None,
    sort_by: str = "price",
    order: str = "asc",
    page: int = 1,
    limit: int = 4
):
    data = products

    # 🔍 Step 1: Filter
    if keyword:
        data = [p for p in data if keyword.lower() in p["name"].lower()]

    # ↕ Step 2: Sort
    if sort_by not in ["price", "name"]:
        raise HTTPException(status_code=400, detail="sort_by must be 'price' or 'name'")

    reverse = True if order == "desc" else False
    data = sorted(data, key=lambda x: x[sort_by], reverse=reverse)

    # 📄 Step 3: Pagination
    total = len(data)
    total_pages = math.ceil(total / limit) if total else 1

    start = (page - 1) * limit
    end = start + limit

    return {
        "keyword": keyword,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "limit": limit,
        "total_found": total,
        "total_pages": total_pages,
        "products": data[start:end]
    }


# -----------------------------
#  BONUS: PAGINATE ORDERS
# -----------------------------

@app.get("/orders/page")
def paginate_orders(
    page: int = Query(1, ge=1),
    limit: int = Query(3, ge=1)
):
    total = len(orders)
    total_pages = math.ceil(total / limit) if total else 1

    start = (page - 1) * limit
    end = start + limit

    return {
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
        "orders": orders[start:end]
    }


# -----------------------------
#  GET PRODUCT BY ID (Keep Last)
# -----------------------------

@app.get("/products/{product_id}")
def get_product(product_id: int):
    for p in products:
        if p["id"] == product_id:
            return p

    raise HTTPException(status_code=404, detail="Product not found")