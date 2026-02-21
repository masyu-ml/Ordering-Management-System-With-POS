from fastapi import FastAPI
from routers import menu, inventory, order

app = FastAPI()

app.include_router(menu.router)
app.include_router(inventory.router)
app.include_router(order.router)

@app.get("/")
def headquarters():
    return {"message": "JLPOS is Online!"}