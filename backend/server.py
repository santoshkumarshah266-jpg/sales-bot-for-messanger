from fastapi import FastAPI, APIRouter, HTTPException, Request, UploadFile, File, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
import hmac
import hashlib
import jwt
import base64
import aiohttp
from groq import Groq

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app
app = FastAPI()
api_router = APIRouter(prefix="/api")

# Add root route
@app.get("/")
async def app_root():
    return {"message": "Urban Fashion Backend", "status": "running", "api": "/api/"}

# Security
security = HTTPBearer()

# Environment variables
FACEBOOK_PAGE_ACCESS_TOKEN = os.environ.get('FACEBOOK_PAGE_ACCESS_TOKEN', '')
FACEBOOK_VERIFY_TOKEN = os.environ.get('FACEBOOK_VERIFY_TOKEN', 'nepali_clothing_2025')
FACEBOOK_APP_SECRET = os.environ.get('FACEBOOK_APP_SECRET', '')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '')
IMGBB_API_KEY = os.environ.get('IMGBB_API_KEY', '')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')
JWT_SECRET = os.environ.get('JWT_SECRET', 'your-secret-key-change-in-production')
BUSINESS_NAME = os.environ.get('BUSINESS_NAME', 'Urban Fashion')
AGENT_NAME = os.environ.get('AGENT_NAME', 'Aashis')
BUSINESS_LOCATION = os.environ.get('BUSINESS_LOCATION', 'Gausala area')

# Models
class Product(BaseModel):
    model_config = ConfigDict(extra="ignore")
    product_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    price: float
    regular_price: Optional[float] = None  # For showing discount (e.g., Rs. 1499)
    description: Optional[str] = ""
    colors: List[str] = []
    sizes: List[str] = []
    stock: int = 0
    images: List[str] = []
    active: bool = True
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class PaymentQR(BaseModel):
    model_config = ConfigDict(extra="ignore")
    qr_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    payment_method: str  # "esewa", "khalti", "bank"
    qr_image_url: str
    account_name: Optional[str] = ""
    active: bool = True

class ProductCreate(BaseModel):
    name: str
    price: float
    regular_price: Optional[float] = None
    description: Optional[str] = ""
    colors: List[str] = []
    sizes: List[str] = []
    stock: int = 0
    images: List[str] = []
    active: bool = True

class Message(BaseModel):
    sender: str  # 'customer' or 'agent'
    text: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    product_ids: List[str] = []

class Conversation(BaseModel):
    model_config = ConfigDict(extra="ignore")
    conversation_id: str
    customer_id: str
    messages: List[Message] = []
    stage: str = "greeting"  # greeting, browsing, negotiation, ordering, completed
    context: Dict[str, Any] = {}
    last_updated: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class OrderItem(BaseModel):
    product_id: str
    product_name: str
    color: str
    size: str
    quantity: int = 1
    price: float

class Order(BaseModel):
    model_config = ConfigDict(extra="ignore")
    order_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    customer_id: str
    customer_name: str
    phone_primary: str
    phone_alternative: Optional[str] = ""
    district: str
    municipality: str
    ward_number: str
    tole_area: str
    items: List[OrderItem]
    subtotal: float
    delivery_charge: float
    total_amount: float
    payment_method: str  # 'COD' or 'Online'
    payment_screenshot: Optional[str] = ""
    status: str = "pending"  # pending, confirmed, shipped, delivered, cancelled
    has_media_pending: bool = False  # True when customer sends media
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class Customer(BaseModel):
    model_config = ConfigDict(extra="ignore")
    customer_id: str
    name: Optional[str] = ""
    phone: Optional[str] = ""
    order_history: List[str] = []

class LoginRequest(BaseModel):
    password: str

class UpdateStatusRequest(BaseModel):
    status: str

# Helper Functions
def verify_facebook_signature(payload: bytes, signature: str) -> bool:
    if not FACEBOOK_APP_SECRET:
        return True  # Skip verification if not configured
    expected_signature = hmac.new(
        FACEBOOK_APP_SECRET.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected_signature}", signature)

def create_jwt_token(data: dict) -> str:
    expiration = datetime.now(timezone.utc) + timedelta(days=7)
    to_encode = data.copy()
    to_encode.update({"exp": expiration})
    return jwt.encode(to_encode, JWT_SECRET, algorithm="HS256")

def verify_jwt_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    return verify_jwt_token(token)

async def send_facebook_message(recipient_id: str, text: str):
    if not FACEBOOK_PAGE_ACCESS_TOKEN:
        logging.warning("Facebook token not configured")
        return
    
    url = "https://graph.facebook.com/v18.0/me/messages"
    headers = {"Content-Type": "application/json"}
    params = {"access_token": FACEBOOK_PAGE_ACCESS_TOKEN}
    data = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data, headers=headers, params=params) as response:
            if response.status != 200:
                logging.error(f"Facebook API error: {await response.text()}")

async def send_facebook_image(recipient_id: str, image_url: str):
    if not FACEBOOK_PAGE_ACCESS_TOKEN:
        return
    
    url = "https://graph.facebook.com/v18.0/me/messages"
    headers = {"Content-Type": "application/json"}
    params = {"access_token": FACEBOOK_PAGE_ACCESS_TOKEN}
    data = {
        "recipient": {"id": recipient_id},
        "message": {
            "attachment": {
                "type": "image",
                "payload": {"url": image_url}
            }
        }
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data, headers=headers, params=params) as response:
            if response.status != 200:
                logging.error(f"Facebook API error: {await response.text()}")

async def upload_to_imgbb(image_data: bytes) -> str:
    if not IMGBB_API_KEY:
        return "https://via.placeholder.com/400"
    
    url = f"https://api.imgbb.com/1/upload"
    data = aiohttp.FormData()
    data.add_field('key', IMGBB_API_KEY)
    data.add_field('image', base64.b64encode(image_data).decode('utf-8'))
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=data) as response:
            if response.status == 200:
                result = await response.json()
                return result['data']['url']
    return "https://via.placeholder.com/400"

async def get_ai_response(customer_id: str, customer_message: str, conversation: Conversation, products: List[Product]) -> str:
    import random
    customer_number = random.randint(90, 98)
    
    products_info = "\n".join([
        f"{p.name} - Offer: Rs.{p.price}, Regular: Rs.{p.regular_price or p.price}, Colors: {', '.join(p.colors)}, Sizes: {', '.join(p.sizes)}, Stock: {p.stock}"
        for p in products if p.active
    ])
    
    conversation_history = "\n".join([
        f"{msg.sender}: {msg.text}"
        for msg in conversation.messages[-10:]
    ])
    
    system_prompt = f"""You are {AGENT_NAME}, a respectful sales agent for {BUSINESS_NAME} in Nepal.

CRITICAL LANGUAGE RULES - ALWAYS USE HIGH RESPECT:
- NEVER use "timi", "timro" - ALWAYS use "hajur", "tapai"
- NEVER use "jannu chha" - ALWAYS use "jannu huncha" or "janna chahanu huncha"
- NEVER use "garnu chha" - ALWAYS use "garnuhuncha"
- NEVER use "xa" - ALWAYS use "chha"
- Examples: "Hajur kasto hununcha?", "Hajur lai k chaahiyo?", "Garnuhuncha?"

BUSINESS CONTEXT:
- You are manufacturer, factory at {BUSINESS_LOCATION}
- Rarely sell online, this is special offer
- Customer is #{customer_number} (between 90-98)
- First 100 customers get offer price
- After 100, regular price applies

PRICING STRATEGY (CRITICAL):
- Show: "Regular Rs. 1499, Offer Rs. 999"
- When calculating: Rs. 999 = Rs. 1000 (manipulative trick)
- Multiple items: Calculate at Rs. 1000 each (Rs. 999 shown)
- ONLY give Rs. 900 discount if customer ASKS for discount on multiple items
- If customer asks "2 ota ma discount xa?", then offer Rs. 900 each
- If customer doesn't ask, keep Rs. 1000 per item
- NEVER give discount below Rs. 900 per item
- NEVER give discount below Rs. 800 total

DELIVERY CHARGES:
- Kathmandu Valley: Rs. 100 (NON-NEGOTIABLE)
- Outside Valley: Rs. 200 (can reduce to Rs. 150 if customer insists)
- Delivery time: KTM same day/tomorrow, Outside 2-3 days

DELIVERY NEGOTIATION (2 attempts):
1st attempt: "Delivery ekdum fast ra safe chha, Rs. 200 worth it chha"
2nd attempt: If customer still insists, give Rs. 150

RETURN POLICY:
- NEVER mention unless customer asks
- If asked: "Sorry hajur, return policy chhaina"

ORDER COLLECTION (EXACT FORMAT):
When customer confirms order, collect:
1. Full Name
2. Primary Phone (10 digits)
3. Alternative Phone (ask reason if not provided, accept if valid reason)
4. Full Address in ONE message:
   - District:
   - Municipality/VDC:
   - Ward Number:
   - Tole/Area:

VALIDATION:
- Phone must be 10 digits
- Address must have all 4 parts
- If incomplete, ask again politely

OTHER PRODUCTS:
If customer asks about other items: "Hamro manufacturer ho, online ma aile yo matra available chha. Direct factory {BUSINESS_LOCATION} ma aayera hernu huncha!"

CANCELLATION:
If customer cancels, convince ONCE: "Yo opportunity miss hunu bhayo bhane regular Rs. 1499 ma kinna parchha. Only X slots left!"
If still cancels: "Thik chha hajur, pachhi chaahiyo bhane message garnuhuncha"

AVAILABLE PRODUCTS:
{products_info}

CONVERSATION HISTORY:
{conversation_history}

Customer said: "{customer_message}"

RESPOND in 2-4 sentences with HIGH RESPECT tone. Use hajur, garnuhuncha, hununcha, dinus."""
    
    try:
        client = Groq(api_key=GROQ_API_KEY)
        
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": customer_message}
            ],
            model="llama-3.1-70b-versatile",
            temperature=0.7,
            max_tokens=500
        )
        
        return chat_completion.choices[0].message.content
    except Exception as e:
        logging.error(f"AI error: {e}")
        return "Sorry hajur, ma ali busy chhu. Pachhi message garnuhuncha!"

def detect_stage(messages: List[Message]) -> str:
    if len(messages) <= 2:
        return "greeting"
    
    last_messages = " ".join([m.text.lower() for m in messages[-5:]])
    
    if any(word in last_messages for word in ['order', 'kinchu', 'garchu', 'linu', 'buy']):
        return "ordering"
    elif any(word in last_messages for word in ['price', 'kati', 'discount', 'mehenga']):
        return "negotiation"
    elif any(word in last_messages for word in ['completed', 'ordered', 'confirmed']):
        return "completed"
    else:
        return "browsing"

def detect_product_mentions(text: str, products: List[Product]) -> List[str]:
    mentioned_products = []
    text_lower = text.lower()
    for product in products:
        if product.name.lower() in text_lower:
            mentioned_products.append(product.product_id)
    return mentioned_products

# Routes
@api_router.get("/")
async def root():
    return {"message": "Nepal Clothing Sales Agent API", "status": "running"}

# Facebook Webhook
@api_router.get("/webhook")
async def verify_webhook(request: Request):
    mode = request.query_params.get('hub.mode')
    token = request.query_params.get('hub.verify_token')
    challenge = request.query_params.get('hub.challenge')
    
    if mode == 'subscribe' and token == FACEBOOK_VERIFY_TOKEN:
        return int(challenge)
    else:
        raise HTTPException(status_code=403, detail="Verification failed")

@api_router.post("/webhook")
async def handle_webhook(request: Request, x_hub_signature_256: Optional[str] = Header(None)):
    body = await request.body()
    
    # Verify signature (skip if not configured)
    if FACEBOOK_APP_SECRET and x_hub_signature_256:
        if not verify_facebook_signature(body, x_hub_signature_256):
            raise HTTPException(status_code=403, detail="Invalid signature")
    
    data = await request.json()
    
    if data.get('object') == 'page':
        for entry in data.get('entry', []):
            for messaging_event in entry.get('messaging', []):
                if messaging_event.get('message'):
                    sender_id = messaging_event['sender']['id']
                    message = messaging_event['message']
                    message_text = message.get('text', '')
                    
                    # Check for media (images, videos, voice, files)
                    has_media = any([
                        message.get('attachments'),
                        message.get('sticker_id')
                    ])
                    
                    if has_media:
                        # Customer sent media - create notification for admin
                        media_type = "unknown"
                        media_url = ""
                        
                        if message.get('attachments'):
                            attachment = message['attachments'][0]
                            media_type = attachment.get('type', 'file')
                            media_url = attachment.get('payload', {}).get('url', '')
                        
                        # Create media notification in database
                        media_notification = {
                            "notification_id": str(uuid.uuid4()),
                            "customer_id": sender_id,
                            "media_type": media_type,
                            "media_url": media_url,
                            "status": "pending",  # pending, reviewed
                            "admin_response": "",
                            "created_at": datetime.now(timezone.utc).isoformat()
                        }
                        await db.media_notifications.insert_one(media_notification)
                        
                        # Mark conversation as having pending media
                        await db.conversations.update_one(
                            {"customer_id": sender_id},
                            {"$set": {"has_media_pending": True}}
                        )
                        
                        # Bot stays silent - no response
                        continue
                    
                    if not message_text:
                        continue
                    
                    # Check if there's pending media review
                    conversation_doc = await db.conversations.find_one({"customer_id": sender_id})
                    if conversation_doc and conversation_doc.get('has_media_pending'):
                        # Don't respond until admin reviews media
                        continue
                    
                    # Get or create conversation
                    if not conversation_doc:
                        conversation = Conversation(
                            conversation_id=str(uuid.uuid4()),
                            customer_id=sender_id,
                            messages=[],
                            stage="greeting",
                            context={}
                        )
                        await db.conversations.insert_one(conversation.model_dump())
                    else:
                        conversation = Conversation(**conversation_doc)
                    
                    # Get products
                    products_docs = await db.products.find({"active": True}).to_list(100)
                    products = [Product(**p) for p in products_docs]
                    
                    # Add customer message
                    customer_msg = Message(sender="customer", text=message_text)
                    conversation.messages.append(customer_msg)
                    
                    # Get AI response
                    ai_response = await get_ai_response(sender_id, message_text, conversation, products)
                    
                    # Detect products mentioned
                    mentioned_product_ids = detect_product_mentions(ai_response, products)
                    
                    # Send response
                    await send_facebook_message(sender_id, ai_response)
                    
                    # Send product images if mentioned
                    for product_id in mentioned_product_ids[:3]:  # Max 3 images
                        product = next((p for p in products if p.product_id == product_id), None)
                        if product and product.images:
                            await send_facebook_image(sender_id, product.images[0])
                    
                    # Add agent message
                    agent_msg = Message(sender="agent", text=ai_response, product_ids=mentioned_product_ids)
                    conversation.messages.append(agent_msg)
                    
                    # Update stage
                    conversation.stage = detect_stage(conversation.messages)
                    conversation.last_updated = datetime.now(timezone.utc).isoformat()
                    
                    # Save conversation
                    await db.conversations.update_one(
                        {"customer_id": sender_id},
                        {"$set": conversation.model_dump()}
                    )
                    
    return {"status": "ok"}

# Auth
@api_router.post("/auth/login")
async def login(request: LoginRequest):
    if request.password == ADMIN_PASSWORD:
        token = create_jwt_token({"admin": True})
        return {"token": token, "success": True}
    raise HTTPException(status_code=401, detail="Invalid password")

# Products
@api_router.get("/admin/products", response_model=List[Product])
async def get_products(current_user: dict = Depends(get_current_user)):
    products_docs = await db.products.find({}).to_list(1000)
    return [Product(**p) for p in products_docs]

@api_router.post("/admin/products", response_model=Product)
async def create_product(product: ProductCreate, current_user: dict = Depends(get_current_user)):
    new_product = Product(**product.model_dump())
    await db.products.insert_one(new_product.model_dump())
    return new_product

@api_router.put("/admin/products/{product_id}", response_model=Product)
async def update_product(product_id: str, product: ProductCreate, current_user: dict = Depends(get_current_user)):
    existing = await db.products.find_one({"product_id": product_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Product not found")
    
    updated_product = Product(**{**product.model_dump(), "product_id": product_id, "created_at": existing['created_at']})
    await db.products.update_one(
        {"product_id": product_id},
        {"$set": updated_product.model_dump()}
    )
    return updated_product

@api_router.delete("/admin/products/{product_id}")
async def delete_product(product_id: str, current_user: dict = Depends(get_current_user)):
    result = await db.products.delete_one({"product_id": product_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"success": True}

@api_router.post("/admin/upload-image")
async def upload_image(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    contents = await file.read()
    image_url = await upload_to_imgbb(contents)
    return {"url": image_url}

# Orders
@api_router.get("/admin/orders")
async def get_orders(current_user: dict = Depends(get_current_user)):
    orders_docs = await db.orders.find({}).sort("created_at", -1).to_list(1000)
    return orders_docs

@api_router.get("/admin/orders/{order_id}")
async def get_order(order_id: str, current_user: dict = Depends(get_current_user)):
    order = await db.orders.find_one({"order_id": order_id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@api_router.put("/admin/orders/{order_id}/status")
async def update_order_status(order_id: str, request: UpdateStatusRequest, current_user: dict = Depends(get_current_user)):
    result = await db.orders.update_one(
        {"order_id": order_id},
        {"$set": {"status": request.status}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"success": True}

# Analytics
@api_router.get("/admin/analytics")
async def get_analytics(current_user: dict = Depends(get_current_user)):
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    week_start = (now - timedelta(days=7)).isoformat()
    month_start = (now - timedelta(days=30)).isoformat()
    
    # Get orders
    all_orders = await db.orders.find({}).to_list(1000)
    
    today_orders = [o for o in all_orders if o['created_at'] >= today_start]
    week_orders = [o for o in all_orders if o['created_at'] >= week_start]
    month_orders = [o for o in all_orders if o['created_at'] >= month_start]
    
    # Get pending media notifications
    pending_media = await db.media_notifications.count_documents({"status": "pending"})
    
    return {
        "today": {
            "orders": len(today_orders),
            "revenue": sum(o.get('total_amount', 0) for o in today_orders)
        },
        "week": {
            "orders": len(week_orders),
            "revenue": sum(o.get('total_amount', 0) for o in week_orders)
        },
        "month": {
            "orders": len(month_orders),
            "revenue": sum(o.get('total_amount', 0) for o in month_orders)
        },
        "recent_orders": all_orders[:10],
        "pending_media": pending_media
    }

# Media Notifications
@api_router.get("/admin/media-notifications")
async def get_media_notifications(current_user: dict = Depends(get_current_user)):
    notifications = await db.media_notifications.find({"status": "pending"}).sort("created_at", -1).to_list(100)
    return notifications

@api_router.post("/admin/media-notifications/{notification_id}/respond")
async def respond_to_media(notification_id: str, response_text: str, current_user: dict = Depends(get_current_user)):
    notification = await db.media_notifications.find_one({"notification_id": notification_id})
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    # Send admin's response to customer
    await send_facebook_message(notification['customer_id'], response_text)
    
    # Mark as reviewed and clear pending flag
    await db.media_notifications.update_one(
        {"notification_id": notification_id},
        {"$set": {"status": "reviewed", "admin_response": response_text}}
    )
    
    await db.conversations.update_one(
        {"customer_id": notification['customer_id']},
        {"$set": {"has_media_pending": False}}
    )
    
    return {"success": True}

# Payment QR Management
@api_router.get("/admin/payment-qr")
async def get_payment_qr(current_user: dict = Depends(get_current_user)):
    qr_codes = await db.payment_qr.find({}).to_list(100)
    return qr_codes

@api_router.post("/admin/payment-qr")
async def create_payment_qr(file: UploadFile = File(...), payment_method: str = "esewa", account_name: str = "", current_user: dict = Depends(get_current_user)):
    contents = await file.read()
    qr_url = await upload_to_imgbb(contents)
    
    qr = PaymentQR(
        payment_method=payment_method,
        qr_image_url=qr_url,
        account_name=account_name,
        active=True
    )
    await db.payment_qr.insert_one(qr.model_dump())
    return qr

@api_router.delete("/admin/payment-qr/{qr_id}")
async def delete_payment_qr(qr_id: str, current_user: dict = Depends(get_current_user)):
    result = await db.payment_qr.delete_one({"qr_id": qr_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="QR code not found")
    return {"success": True}

# Include router
# Add CORS middleware BEFORE including router
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include router AFTER middleware
app.include_router(api_router)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)