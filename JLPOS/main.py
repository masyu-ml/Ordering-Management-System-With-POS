from fastapi import FastAPI
from routers import menu, inventory, order, auth, kitchen, expenses, admin, staff, analytics, reports

app = FastAPI()

app.include_router(menu.router)
app.include_router(inventory.router)
app.include_router(order.router)
app.include_router(auth.router)
app.include_router(kitchen.router)
app.include_router(expenses.router)
app.include_router(admin.router)
app.include_router(staff.router)
app.include_router(analytics.router)
app.include_router(reports.router)
@app.get("/")
def headquarters():
    return {"message": "JLPOS is Online!"}
    return {"message": "JLPOS is Online!"}