from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.background import BackgroundTasks
from redis_om import get_redis_connection, HashModel
from starlette.requests import Request
import requests, time

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000'],
    allow_methods=["*"],
    allow_headers=['*']
)

redis = get_redis_connection(
    host="0.0.0.0",
    port=6379,
    decode_responses=True
)
class Order(HashModel):
    product_id: str
    price: float
    fee: float
    total: float
    quantity: int
    status: str #pending, complete, refunded

    class Meta:
        database = redis


@app.get("/orders/{pk}")
async def get(pk: str):
    return Order.get(pk)

@app.post('/orders')
async def create(request: Request, background_tasks:BackgroundTasks): #id, quantity
    body = await request.json()
    # print(body["id"])

    req = requests.get(f'http://localhost:8000/products/{body["id"]}')

    product = req.json()
    print(product)
    order = Order(
        product_id = body["id"],
        price = product["price"],
        fee = 0.2 * product['price'],
        total =  product['price'],
        quantity = body['quantity'],
        status = 'pending'

    )

    order.save()
    background_tasks.add_task(order_completed, order)
    return order


def order_completed(order: Order):
    print("processing")
    time.sleep(10)
    order.status = 'completed'
    order.save()
    redis.xadd('order_completed', order.dict(), '*')

