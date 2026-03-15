from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# ----------------------------
# Product Database
# ----------------------------
products = {
    1: {"name": "Wireless Mouse", "price": 499, "stock": 10},
    2: {"name": "Notebook", "price": 99, "stock": 10},
    3: {"name": "USB Hub", "price": 299, "stock": 0},   # out of stock
    4: {"name": "Pen Set", "price": 49, "stock": 10}
}

# ----------------------------
# In-Memory Storage
# ----------------------------
cart = {}
orders = []
order_counter = 1


# ----------------------------
# Checkout Model
# ----------------------------
class CheckoutRequest(BaseModel):
    customer_name: str
    delivery_address: str


# ----------------------------
# Add to Cart
# ----------------------------
@app.post("/cart/add")
def add_to_cart(product_id: int, quantity: int = 1):

    if product_id not in products:
        raise HTTPException(status_code=404, detail="Product not found")

    product = products[product_id]

    if product["stock"] == 0:
        raise HTTPException(
            status_code=400,
            detail=f"{product['name']} is out of stock"
        )

    if product_id in cart:
        cart[product_id]["quantity"] += quantity
        cart[product_id]["subtotal"] = (
            cart[product_id]["quantity"] * cart[product_id]["unit_price"]
        )

        return {
            "message": "Cart updated",
            "cart_item": cart[product_id]
        }

    cart_item = {
        "product_id": product_id,
        "product_name": product["name"],
        "quantity": quantity,
        "unit_price": product["price"],
        "subtotal": product["price"] * quantity
    }

    cart[product_id] = cart_item

    return {
        "message": "Added to cart",
        "cart_item": cart_item
    }


# ----------------------------
# View Cart
# ----------------------------
@app.get("/cart")
def view_cart():

    if not cart:
        return {"message": "Cart is empty"}

    items = list(cart.values())

    grand_total = sum(item["subtotal"] for item in items)

    return {
        "items": items,
        "item_count": len(items),
        "grand_total": grand_total
    }


# ----------------------------
# Remove Item from Cart
# ----------------------------
@app.delete("/cart/{product_id}")
def remove_from_cart(product_id: int):

    if product_id not in cart:
        raise HTTPException(status_code=404, detail="Item not in cart")

    removed = cart.pop(product_id)

    return {
        "message": f"{removed['product_name']} removed from cart"
    }


# ----------------------------
# Checkout
# ----------------------------
@app.post("/cart/checkout")
def checkout(data: CheckoutRequest):

    global order_counter

    if not cart:
        raise HTTPException(status_code=400, detail="Cart is empty")

    created_orders = []
    grand_total = 0

    for item in cart.values():

        order = {
            "order_id": order_counter,
            "customer_name": data.customer_name,
            "product": item["product_name"],
            "quantity": item["quantity"],
            "subtotal": item["subtotal"],
            "delivery_address": data.delivery_address
        }

        orders.append(order)
        created_orders.append(order)

        grand_total += item["subtotal"]
        order_counter += 1

    cart.clear()

    return {
        "message": "Checkout successful",
        "orders_placed": len(created_orders),
        "grand_total": grand_total
    }


# ----------------------------
# View Orders
# ----------------------------
@app.get("/orders")
def get_orders():

    return {
        "orders": orders,
        "total_orders": len(orders)
    }