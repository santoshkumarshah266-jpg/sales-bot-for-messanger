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
from emergentintegrations.llm.chat import LlmChat, UserMessage

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app
app = FastAPI()
api_router = APIRouter(prefix="/api")

# Security
security = HTTPBearer()

# Environment variables
FACEBOOK_PAGE_ACCESS_TOKEN = os.environ.get('FACEBOOK_PAGE_ACCESS_TOKEN', '')
FACEBOOK_VERIFY_TOKEN = os.environ.get('FACEBOOK_VERIFY_TOKEN', 'nepali_clothing_2025')
FACEBOOK_APP_SECRET = os.environ.get('FACEBOOK_APP_SECRET', '')
GROQ_API_KEY = os.environ.get('EMERGENT_LLM_KEY', '')
IMGBB_API_KEY = os.environ.get('IMGBB_API_KEY', '')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')
JWT_SECRET = os.environ.get('JWT_SECRET', 'your-secret-key-change-in-production')
BUSINESS_NAME = os.environ.get('BUSINESS_NAME', 'Nepal Fashion Store')
AGENT_NAME = os.environ.get('AGENT_NAME', 'Maya')

# Models
class Product(BaseModel):
    model_config = ConfigDict(extra="ignore")
    product_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    price: float
    description: Optional[str] = ""
    colors: List[str] = []
    sizes: List[str] = []
    stock: int = 0
    images: List[str] = []
    active: bool = True
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class ProductCreate(BaseModel):
    name: str
    price: float
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
    color: Optional[str] = ""
    size: Optional[str] = ""
    quantity: int = 1
    price: float

class Order(BaseModel):
    model_config = ConfigDict(extra="ignore")
    order_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    customer_id: str
    customer_name: str
    phone: str
    address: str
    items: List[OrderItem]
    total_amount: float
    payment_method: str  # 'COD' or 'Online'
    payment_screenshot: Optional[str] = ""
    status: str = "pending"  # pending, confirmed, shipped, delivered, cancelled
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
    products_info = "\n".join([
        f"{p.name} - Rs.{p.price}, Colors: {', '.join(p.colors) if p.colors else 'N/A'}, Stock: {p.stock}"
        for p in products if p.active
    ])
    
    conversation_history = "\n".join([
        f"{msg.sender}: {msg.text}"
        for msg in conversation.messages[-10:]
    ])
    
    system_prompt = f"""You are {AGENT_NAME}, a sales agent for {BUSINESS_NAME} in Nepal.

LANGUAGE: Romanized Nepali + English mix (NO Devanagari)
Examples: "Namaste! Kasto chha?", "Yo design ta viral bhaisakyo!", "Rs. {products[0].price if products else 1500} ma ekdum worth it chha!"

PERSONALITY: Friendly, warm, professional salesperson

SALES PSYCHOLOGY:
- Rapport: "Tapai kaha bata ho?"
- Social Proof: "5 jana le aaja order garyo!"
- Scarcity: "Only 3 left!"
- Urgency: "Aaja order = bholi delivery!"
- Empathy: "Ma bujhchu budget important chha"
- Value: Explain quality, durability

CONVERSATION STAGE: {conversation.stage}
- greeting: Welcome warmly
- browsing: Understand needs, recommend products
- negotiation: Handle objections, justify price
- ordering: Collect name, phone, address
- completed: Thank customer

AVAILABLE PRODUCTS:
{products_info}

CONVERSATION HISTORY:
{conversation_history}

Customer just said: "{customer_message}"

Respond in 2-4 sentences in Nepali-English mix. If mentioning products, I'll auto-send images. Keep natural, friendly, guide toward sale."""
    
    try:
        chat = LlmChat(
            api_key=GROQ_API_KEY,
            session_id=customer_id,
            system_message=system_prompt
        ).with_model("openai", "gpt-4o-mini")
        
        user_message = UserMessage(text=customer_message)
        response = await chat.send_message(user_message)
        return response
    except Exception as e:
        logging.error(f"AI error: {e}")
        return "Sorry, ma ali busy chhu. Pachhi message garnus!"

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
                    message_text = messaging_event['message'].get('text', '')
                    
                    if not message_text:
                        continue
                    
                    # Get or create conversation
                    conversation_doc = await db.conversations.find_one({"customer_id": sender_id})
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
        "recent_orders": all_orders[:10]
    }

# Include router
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()