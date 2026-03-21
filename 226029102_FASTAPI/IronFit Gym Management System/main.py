from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional
import math

app = FastAPI(title="IronFit Gym Management System")

# ---------------- DATA ----------------
plans = [
    {
        "id": 1,
        "name": "Basic",
        "duration_months": 1,
        "price": 1200,
        "includes_classes": False,
        "includes_trainer": False
    },
    {
        "id": 2,
        "name": "Standard",
        "duration_months": 3,
        "price": 3200,
        "includes_classes": True,
        "includes_trainer": False
    },
    {
        "id": 3,
        "name": "Premium",
        "duration_months": 6,
        "price": 6000,
        "includes_classes": True,
        "includes_trainer": True
    },
    {
        "id": 4,
        "name": "Elite",
        "duration_months": 12,
        "price": 11000,
        "includes_classes": True,
        "includes_trainer": True
    },
    {
        "id": 5,
        "name": "Student",
        "duration_months": 1,
        "price": 900,
        "includes_classes": False,
        "includes_trainer": False
    },
    {
        "id": 6,
        "name": "Corporate",
        "duration_months": 6,
        "price": 5500,
        "includes_classes": True,
        "includes_trainer": False
    },
    {
        "id": 7,
        "name": "Weight Loss Special",
        "duration_months": 3,
        "price": 4000,
        "includes_classes": True,
        "includes_trainer": True
    },
    {
        "id": 8,
        "name": "Personal Training",
        "duration_months": 1,
        "price": 3000,
        "includes_classes": False,
        "includes_trainer": True
    }
]

memberships = []
membership_counter = 1

class_bookings = []
class_counter = 1


# ---------------- MODELS ----------------
class EnrollRequest(BaseModel):
    member_name: str = Field(..., min_length=2)
    plan_id: int = Field(..., gt=0)
    phone: str = Field(..., min_length=10)
    start_month: str = Field(..., min_length=3)
    payment_mode: str = "cash"
    referral_code: Optional[str] = ""


class NewPlan(BaseModel):
    name: str = Field(..., min_length=2)
    duration_months: int = Field(..., gt=0)
    price: int = Field(..., gt=0)
    includes_classes: bool = False
    includes_trainer: bool = False


class ClassBookingRequest(BaseModel):
    member_name: str
    class_name: str
    class_date: str


# ---------------- HELPERS ----------------
def find_plan(plan_id: int):
    return next((p for p in plans if p["id"] == plan_id), None)


def filter_plans_logic(max_price, max_duration, includes_classes, includes_trainer):
    data = plans
    if max_price is not None:
        data = [p for p in data if p["price"] <= max_price]
    if max_duration is not None:
        data = [p for p in data if p["duration_months"] <= max_duration]
    if includes_classes is not None:
        data = [p for p in data if p["includes_classes"] == includes_classes]
    if includes_trainer is not None:
        data = [p for p in data if p["includes_trainer"] == includes_trainer]
    return data


def calculate_membership_fee(base_price, duration, payment_mode, referral_code=""):
    discount_pct = 0

    if duration >= 12:
        discount_pct = 20
    elif duration >= 6:
        discount_pct = 10

    discount_amount = (base_price * discount_pct) / 100
    after_discount = base_price - discount_amount

    referral_discount_amt = 0
    if referral_code:
        referral_discount_amt = (after_discount * 5) / 100

    final_fee = after_discount - referral_discount_amt

    processing_fee = 200 if payment_mode.lower() == "emi" else 0
    total = final_fee + processing_fee

    return {
        "base_price": base_price,
        "duration_discount": f"{discount_pct}%",
        "referral_discount": "5%" if referral_code else "0%",
        "processing_fee": processing_fee,
        "total_fee": total,
        "monthly_equivalent": total / duration
    }


# ---------------- ROUTES ----------------

# Q1
@app.get("/")
def home():
    return {"message": "Welcome to IronFit Gym"}


# Q5 (above dynamic route)
@app.get("/plans/summary")
def plans_summary():
    cheapest = min(plans, key=lambda x: x["price"])
    expensive = max(plans, key=lambda x: x["price"])

    return {
        "total_plans": len(plans),
        "include_classes": len([p for p in plans if p["includes_classes"]]),
        "include_trainer": len([p for p in plans if p["includes_trainer"]]),
        "cheapest": {"name": cheapest["name"], "price": cheapest["price"]},
        "most_expensive": {"name": expensive["name"], "price": expensive["price"]}
    }


# Q2
@app.get("/plans")
def get_plans():
    prices = [p["price"] for p in plans]
    return {
        "plans": plans,
        "total": len(plans),
        "min_price": min(prices),
        "max_price": max(prices)
    }


# Q10
@app.get("/plans/filter")
def filter_plans(
    max_price: Optional[int] = None,
    max_duration: Optional[int] = None,
    includes_classes: Optional[bool] = None,
    includes_trainer: Optional[bool] = None
):
    return filter_plans_logic(max_price, max_duration, includes_classes, includes_trainer)


# Q16
@app.get("/plans/search")
def search_plans(keyword: str):
    k = keyword.lower()
    results = [
        p for p in plans
        if k in p["name"].lower()
        or (k == "classes" and p["includes_classes"])
        or (k == "trainer" and p["includes_trainer"])
    ]
    return {"matches": results, "total_found": len(results)}


# Q17
@app.get("/plans/sort")
def sort_plans(sort_by: str = "price", order: str = "asc"):
    if sort_by not in ["price", "name", "duration_months"]:
        raise HTTPException(400, "Invalid sort field")

    reverse = True if order == "desc" else False
    return sorted(plans, key=lambda x: x[sort_by], reverse=reverse)


# Q18
@app.get("/plans/page")
def paginate_plans(page: int = 1, limit: int = 2):
    start = (page - 1) * limit
    total_pages = math.ceil(len(plans) / limit)

    return {
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
        "data": plans[start:start+limit]
    }


# Q20
@app.get("/plans/browse")
def browse_plans(
    keyword: Optional[str] = None,
    includes_classes: Optional[bool] = None,
    includes_trainer: Optional[bool] = None,
    sort_by: str = "price",
    order: str = "asc",
    page: int = 1,
    limit: int = 5
):
    data = plans

    if keyword:
        k = keyword.lower()
        data = [
            p for p in data
            if k in p["name"].lower()
            or (k == "classes" and p["includes_classes"])
            or (k == "trainer" and p["includes_trainer"])
        ]

    if includes_classes is not None:
        data = [p for p in data if p["includes_classes"] == includes_classes]

    if includes_trainer is not None:
        data = [p for p in data if p["includes_trainer"] == includes_trainer]

    reverse = True if order == "desc" else False
    data = sorted(data, key=lambda x: x.get(sort_by, 0), reverse=reverse)

    total_pages = math.ceil(len(data) / limit)
    start = (page - 1) * limit

    return {
        "metadata": {
            "total": len(data),
            "page": page,
            "limit": limit,
            "total_pages": total_pages
        },
        "results": data[start:start+limit]
    }


# Q3
@app.get("/plans/{plan_id}")
def get_plan(plan_id: int):
    plan = find_plan(plan_id)
    if not plan:
        raise HTTPException(404, "Plan not found")
    return plan


# Q11
@app.post("/plans", status_code=201)
def create_plan(plan: NewPlan):
    if any(p["name"].lower() == plan.name.lower() for p in plans):
        raise HTTPException(400, "Duplicate plan")

    new_id = max(p["id"] for p in plans) + 1
    new_plan = {"id": new_id, **plan.dict()}
    plans.append(new_plan)
    return new_plan


# Q12
@app.put("/plans/{plan_id}")
def update_plan(plan_id: int, price: Optional[int] = None,
                includes_classes: Optional[bool] = None,
                includes_trainer: Optional[bool] = None):

    plan = find_plan(plan_id)
    if not plan:
        raise HTTPException(404, "Plan not found")

    if price is not None:
        plan["price"] = price
    if includes_classes is not None:
        plan["includes_classes"] = includes_classes
    if includes_trainer is not None:
        plan["includes_trainer"] = includes_trainer

    return plan


# Q13
@app.delete("/plans/{plan_id}")
def delete_plan(plan_id: int):
    plan = find_plan(plan_id)
    if not plan:
        raise HTTPException(404, "Plan not found")

    if any(m["plan_name"] == plan["name"] and m["status"] == "active" for m in memberships):
        raise HTTPException(400, "Cannot delete active plan")

    plans.remove(plan)
    return {"message": "Deleted successfully"}


# Q8
@app.post("/memberships")
def enroll(req: EnrollRequest):
    global membership_counter

    plan = find_plan(req.plan_id)
    if not plan:
        raise HTTPException(404, "Plan not found")

    fee = calculate_membership_fee(
        plan["price"], plan["duration_months"], req.payment_mode, req.referral_code
    )

    new_member = {
        "membership_id": membership_counter,
        "member_name": req.member_name,
        "plan_name": plan["name"],
        "duration": plan["duration_months"],
        "monthly_equivalent_cost": fee["monthly_equivalent"],
        "total_fee": fee["total_fee"],
        "breakdown": fee,
        "status": "active"
    }

    memberships.append(new_member)
    membership_counter += 1
    return new_member


# Q4
@app.get("/memberships")
def get_memberships():
    return {"memberships": memberships, "total": len(memberships)}


# Q19
@app.get("/memberships/search")
def search_memberships(member_name: str):
    results = [m for m in memberships if member_name.lower() in m["member_name"].lower()]
    return {"results": results, "total_found": len(results)}


@app.get("/memberships/sort")
def sort_memberships(sort_by: str = "total_fee"):
    if sort_by not in ["total_fee", "duration"]:
        raise HTTPException(400, "Invalid sort field")
    return sorted(memberships, key=lambda x: x.get(sort_by, 0))


@app.get("/memberships/page")
def paginate_memberships(page: int = 1, limit: int = 5):
    start = (page - 1) * limit
    total_pages = math.ceil(len(memberships) / limit)

    return {
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
        "data": memberships[start:start+limit]
    }


# Q15
@app.put("/memberships/{membership_id}/freeze")
def freeze(membership_id: int):
    member = next((m for m in memberships if m["membership_id"] == membership_id), None)
    if not member:
        raise HTTPException(404, "Not found")
    member["status"] = "frozen"
    return member


@app.put("/memberships/{membership_id}/reactivate")
def reactivate(membership_id: int):
    member = next((m for m in memberships if m["membership_id"] == membership_id), None)
    if not member:
        raise HTTPException(404, "Not found")
    member["status"] = "active"
    return member


# Q14
@app.post("/classes/book")
def book(req: ClassBookingRequest):
    global class_counter

    member = next((m for m in memberships if m["member_name"] == req.member_name and m["status"] == "active"), None)
    if not member:
        raise HTTPException(400, "Inactive member")

    plan = next((p for p in plans if p["name"] == member["plan_name"]), None)
    if not plan or not plan["includes_classes"]:
        raise HTTPException(403, "No class access")

    booking = {"booking_id": class_counter, **req.dict()}
    class_bookings.append(booking)
    class_counter += 1

    return booking


@app.get("/classes/bookings")
def get_bookings():
    return class_bookings


@app.delete("/classes/cancel/{booking_id}")
def cancel_booking(booking_id: int):
    booking = next((b for b in class_bookings if b["booking_id"] == booking_id), None)
    if not booking:
        raise HTTPException(404, "Not found")

    class_bookings.remove(booking)
    return {"message": "Cancelled"}