from fastapi import FastAPI, status, Body, HTTPException, Depends, Path, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
import json
import pytz
from datetime import datetime, timedelta, time
from hashlib import sha256
from werkzeug.security import safe_str_cmp
import jwt
import os
import sqlite3
import math
import time as tme
from fastapi.staticfiles import StaticFiles


# UNCOMMENT ON MAC/LINUX
# from recommendations.rec import *


JWT_SECRET = "secret"


class SqlManager:

    def __init__(self):

        self.tmz = pytz.timezone("US/Pacific")

        self.dtb = "db.sqlite3"

    def connect(self):

        return sqlite3.connect(self.dtb)

    def timestamp(self):

        return int(self.tmz.localize(datetime.now(), is_dst=True).timestamp())

    def run(self, query):

        con = self.connect()
        cur = con.cursor()
        try:
            cur.execute(query)
        except:
            print("# Query Failure:", query, flush=True)
        con.commit()
        cur.close()
        con.close()

    def get(self, query):

        con = self.connect()
        cur = con.cursor()
        # try:
        cur.execute(query)
        res = cur.fetchall()
        col = [e[0] for e in cur.description]
        res = [{k: v for k, v in zip(col, e)} for e in res]
        # except:
        # print('# Query Failure:', query, flush=True)
        # res = []
        cur.close()
        con.close()

        return res

    def get_unique(self, query):

        con = self.connect()
        cur = con.cursor()
        try:
            cur.execute(query)
            res = cur.fetchone()
            if not res is None:
                col = [e[0] for e in cur.description]
                res = {k: v for k, v in zip(col, res)}
        except:
            print("# Query Failure:", query, flush=True)
            res = None
        cur.close()
        con.close()

        return res

    def add(self, table, item):
        
        val = ", ".join([r"'{}'".format(item.get(k)) for k in sorted(item.keys())])
        itm = ", ".join(sorted(item.keys()))
        self.run("INSERT INTO {} ({}) VALUES ({})".format(table, itm, val))

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/store", StaticFiles(directory="./store"), name="store")

sql = SqlManager()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth")

@app.get("/status",)
def health():
    return {"status": "online"}


def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    try:
        payload = jwt.decode(
            token, JWT_SECRET, algorithms=["HS256"]
        )
        
        qry = "SELECT * FROM users_customuser WHERE id='{}'"
        user = sql.get_unique(qry.format(payload["identity"]))

        if user is None:
            raise credentials_exception

    except Exception as e:
        print("Error: ")
        print(e)
        raise credentials_exception

    return user

@app.post("/register")
def register(email: str = Body(..., embed=True), password: str = Body(...,embed=True), first_name: str = Body(...,embed=True), last_name: str = Body(...,embed=True), phone_number: str = Body(...,embed=True)):
    qry = "SELECT * FROM users_customuser WHERE email='{}'"
    usr = sql.get_unique(qry.format(email))
    if not usr is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email already registered",
            headers={"WWW-Authenticate": "Bearer"},
        )
    else:
        obj = dict()
        obj['email'] = email
        obj['username'] = email
        obj['role'] = "CUSTOMER"
        obj['password'] = sha256(password.encode("utf-8")).hexdigest()
        obj['first_name'] = first_name
        obj['last_name'] = last_name
        obj['phoneNumber'] = phone_number
        sql.add('users_customuser', obj)
        qry = "SELECT * FROM users_customuser WHERE email='{}'"
        usr = sql.get_unique(qry.format(email))

        data = {"identity": usr.get("id"), "role": usr.get("role"), "exp": datetime.utcnow() + timedelta(86400)}
        return  {"access_token": jwt.encode(data, JWT_SECRET, algorithm="HS256")}

@app.post("/auth")
def login(email: str = Body(..., embed=True), password: str = Body(..., embed=True)):
    qry = "SELECT * FROM users_customuser WHERE email='{}'"
    usr = sql.get_unique(qry.format(email))
    print(usr)
    if not usr is None:
        pwd = sha256(password.encode("utf-8")).hexdigest()
        if not safe_str_cmp(pwd, usr.get("password")):
            usr = None

    if not usr:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    data = {"identity": usr.get("id"), "role": usr.get("role"), "exp": datetime.utcnow() + timedelta(86400)}
    return  {"access_token": jwt.encode(data, JWT_SECRET, algorithm="HS256")}

@app.get("/me/det")
def get_user(current_user = Depends(get_current_user)):
    return {
        "role": current_user.get("role"), 
        "email": current_user.get("email"), 
        "name": f"{current_user.get('first_name')} {current_user.get('last_name')}" 
    }

@app.get("/me/hasOngoing")
def ongoing(current_user = Depends(get_current_user)):
    qry = f"SELECT * from users_order WHERE user_id={current_user.get('id')} AND is_complete=0";
    return {"hasOngoing": len(sql.get(qry)) > 0}

@app.get("/getStores")
def stores(current_user = Depends(get_current_user)):
    qry = f"SELECT store_id as id, name, latitude as lat, longitude as lng, description as desc, logo as image, contactNumber, start, end FROM users_store";

    stores = sql.get(qry)
    for store in stores:
        store["start"] = datetime.strptime(store["start"], '%H:%M:%S').strftime("%I:%M %p")
        store["end"] = datetime.strptime(store["end"], '%H:%M:%S').strftime("%I:%M %p")
    return stores


@app.get("/getStoreItems")
def stores( 
    store_id: int, 
    category: str,
    skip: int,
    resPerPage: int = Query(8),
    current_user = Depends(get_current_user)
):
    cartItems = sql.get(f"SELECT b.item_id, b.quantity FROM users_cart as a INNER JOIN users_cartitems as b ON a.cart_id=b.cart_id WHERE a.store_id={store_id} AND a.user_id={current_user.get('id')}")
    storeItems = sql.get(f"SELECT item_id as id, name, price, logo as image, description FROM users_storeitem WHERE store_id={store_id} AND category='{category}'")
    for item in storeItems:
        quant = 0
        for c_item in cartItems:
            if c_item["item_id"] == item["id"]:
                quant = c_item["quantity"]
        item["quantity"] = quant
    
    return {"pageCount": math.ceil(len(storeItems) / resPerPage), "items": storeItems[skip: skip+resPerPage]}

@app.get("/getStoreCategories")
def storeCategories(store_id: int, current_user = Depends(get_current_user)):
    qry = f"SELECT DISTINCT category FROM users_storeitem WHERE store_id={store_id}"

    return [category["category"] for category in sql.get(qry)]

@app.get("/getRecommendedItems")
def recItems(store_id: int, current_user = Depends(get_current_user)):
    qry = f"""SELECT user_id, item_id, SUM(quantity) as purchase_count 
                FROM users_order as a INNER JOIN users_orderitems as b 
                ON a.order_id=b.order_id 
                WHERE store_id={store_id}
                GROUP BY user_id, item_id;"""
    
    data= pd.DataFrame(sql.get(qry))
    user_column='user_id'
    item_column='item_id' 
    freq_column='purchase_count'
    k = 4
    user_id = current_user.get("id")

    recommendations = get_best_k_items(data, user_column=user_column, item_column=item_column, freq_column=freq_column, k=k, user_id=user_id)
    recommendations=[int(r) for r in recommendations]
    return {"recommendations": recommendations}

@app.get("/getRecommendedStores")
def recItems(current_user = Depends(get_current_user)):
    qry = f"""SELECT user_id, store_id, COUNT(*) as order_count from users_order GROUP BY user_id, store_id;"""
    
    data= pd.DataFrame(sql.get(qry))
    user_column='user_id'
    merchant_column='store_id' 
    freq_column='order_count'
    k = 4
    user_id = current_user.get("id")

    recommendations = get_best_k_merchants(data, user_column=user_column, merchant_column=merchant_column, freq_column=freq_column, k=k, user_id=user_id)
    recommendations=[int(r) for r in recommendations]
    return {"recommendations": recommendations}

@app.get("/storeAvailability")
def availability(store_id: int, current_user=Depends(get_current_user)):
    times = sql.get(f"SELECT start, end, slotFreqMinutes, slotCapacity FROM users_store WHERE store_id={store_id}")[0]
    orderSlots = sql.get(f"SELECT pickup_slot, COUNT(*) as cap FROM users_order WHERE pickup_slot>{int(tme.time())} AND store_id={store_id} GROUP BY pickup_slot")
    orderSlots = {item["pickup_slot"]: item["cap"] for item in orderSlots}
    start, end = datetime.strptime(times["start"], '%H:%M:%S'), datetime.strptime(times["end"], '%H:%M:%S')

    avl = []
    curr_time = datetime.today()
    curr_day = datetime(year=curr_time.year, month=curr_time.month, day=curr_time.day)
    for i in range(5):
        startDateTime = curr_day + timedelta(days=i, hours=start.hour, minutes=start.minute)
        endDateTime = curr_day + timedelta(days=i, hours=end.hour, minutes=end.minute)
        avl.append([])

        while startDateTime < endDateTime:
            unixTime = tme.mktime(startDateTime.timetuple())
            if unixTime > (tme.time()+15*60) and (unixTime not in orderSlots or orderSlots[unixTime] < times["slotCapacity"]):
                avl[i].append({"text": startDateTime.strftime("%I:%M %p"),"value": startDateTime.strftime("%B %d, %Y - %H:%M")})
            startDateTime += timedelta(minutes=times["slotFreqMinutes"])

    
    return avl

@app.put("/modifyCart")
def modifyCart(store_id: int, itemId: int=Body(..., embed=True), quant: int=Body(..., embed=True), current_user=Depends(get_current_user)):
    cart = sql.get(f"SELECT cart_id from users_cart WHERE store_id={store_id} AND user_id={current_user.get('id')}")
    if len(cart):
        cart = cart[0]
        sql.run(f"UPDATE users_cart SET last_modified={int(tme.time())} WHERE cart_id={cart.get('cart_id')}")
    else:
        sql.add("users_cart", {"store_id": store_id, "user_id": current_user.get("id"), "last_modified": int(tme.time())})
        cart = sql.get(f"SELECT cart_id from users_cart WHERE store_id={store_id} AND user_id={current_user.get('id')}")[0]
    
    cartId = cart.get("cart_id")

    if quant == 0:
        sql.run(f"DELETE FROM users_cartitems WHERE cart_id={cartId} AND item_id={itemId}")
    elif quant == 1:
        sql.add("users_cartitems", {"cart_id": cartId, "item_id": itemId, "quantity": 1})
    else:
        sql.run(f"UPDATE users_cartitems SET quantity={quant} WHERE cart_id={cartId} AND item_id={itemId}")

@app.get("/myLatestCart")
def userCart(current_user=Depends(get_current_user)):
    cart = sql.get(f"SELECT cart_id, store_id from users_cart WHERE user_id={current_user.get('id')} ORDER BY last_modified DESC")
    if not len(cart):
        return []
    else:
        store_id = cart[0]["store_id"]
        cart = cart[0]["cart_id"]
        storeItems = sql.get(f"SELECT a.item_id as id, b.name, b.price, b.logo as image, a.quantity FROM users_cartitems as a INNER JOIN users_storeitem as b ON a.item_id=b.item_id WHERE a.cart_id={cart}")
        return {"store_id": store_id, "items": storeItems}


@app.post("/submitOrder")
def submitOrder(current_user=Depends(get_current_user), time: str = Body(..., embed=True)):
    cart = sql.get(f"SELECT cart_id, store_id from users_cart WHERE user_id={current_user.get('id')} ORDER BY last_modified DESC")
    if not len(cart):
        raise HTTPException(
            status_code=400
        )
    else:
        store_id = cart[0]["store_id"]
        user_id = current_user.get('id')
        timeUnix = tme.mktime(datetime.strptime(time, "%B %d, %Y - %H:%M").timetuple())
        sql.add("users_order", {"store_id": store_id, "user_id": user_id, "pickup_slot": timeUnix, "is_complete": 0})

@app.get("/myLatestOrder")
def getOrder(current_user=Depends(get_current_user)):
    order = sql.get(f"SELECT parking_number, pickup_slot, store_id FROM users_order WHERE user_id={current_user.get('id')} AND is_complete=0")[0]
    order["pickup_slot"] = datetime.fromtimestamp(order["pickup_slot"]).strftime("%B %d, %Y - %H:%M")
    order.update(sql.get(f"SELECT name as store_name, latitude as lat, longitude as lng from users_store WHERE store_id={order['store_id']}")[0])
    
    return order

    

