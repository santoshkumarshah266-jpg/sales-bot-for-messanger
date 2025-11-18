# Urban Fashion - AI Sales Agent for Facebook Messenger

A complete AI-powered Facebook Messenger sales agent for clothing businesses in Nepal. Built with FastAPI, React, MongoDB, and Emergent LLM.

## Features

### AI-Powered Sales Agent
- Natural conversational AI using Groq API (llama model via Emergent LLM)
- Romanized Nepali + English mixed responses
- Sales psychology techniques (rapport, scarcity, urgency, social proof)
- Smart product recommendations
- Context-aware conversations

### Admin Dashboard
- Real-time analytics (today/week/month orders & revenue)
- Product management with image upload
- Order tracking and status updates
- Beautiful modern UI with purple gradient design

### Facebook Messenger Integration
- Webhook handling for incoming messages
- Image sending capabilities
- Multiple customer conversation management
- Order collection flow (name → phone → address → payment)

### Product Management
- Add/Edit/Delete products
- Multiple images per product
- Color and size variants
- Stock tracking
- Active/Inactive status

### Order Management
- Order status tracking
- Payment method tracking (COD/Online)
- Customer information management
- Order filtering and search

## Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: React + Tailwind CSS + Shadcn UI
- **Database**: MongoDB
- **AI**: Emergent LLM (via emergentintegrations library)
- **Image Hosting**: ImgBB API
- **Deployment**: Emergent Platform (Railway.app compatible)

## Prerequisites

1. Facebook Page & App
2. Groq API Key (FREE) OR use Emergent LLM Key (provided)
3. ImgBB API Key (FREE) - optional for image uploads
4. MongoDB instance

## Installation

### 1. Install Dependencies

**Backend:**
```bash
cd /app/backend
pip install -r requirements.txt
```

**Frontend:**
```bash
cd /app/frontend
yarn install
```

### 2. Environment Configuration

The `.env` file is already configured with default values in `/app/backend/.env`:

```env
# Database
MONGO_URL="mongodb://localhost:27017"
DB_NAME="nepal_clothing_db"
CORS_ORIGINS="*"

# Facebook Messenger Configuration
FACEBOOK_PAGE_ACCESS_TOKEN=       # Add your token
FACEBOOK_VERIFY_TOKEN=nepali_clothing_2025
FACEBOOK_APP_SECRET=              # Add your secret

# AI Configuration
EMERGENT_LLM_KEY=sk-emergent-6Bb7766873eC7EfE12  # Pre-configured

# Image Upload (Optional)
IMGBB_API_KEY=                    # Add your key

# Admin
ADMIN_PASSWORD=admin123           # Change in production
JWT_SECRET=nepali-fashion-secret-2025

# Business Configuration
BUSINESS_NAME=Urban Fashion
AGENT_NAME=Aashis
BUSINESS_LOCATION=Gausala area
```

### 3. Get Required API Keys

#### Facebook Page Access Token (Required for Messenger)
1. Go to [Facebook Developers](https://developers.facebook.com)
2. Create a new app → Choose "Business" type
3. Add "Messenger" product
4. Go to Messenger Settings → Access Tokens
5. Generate token for your page
6. Copy and paste into `FACEBOOK_PAGE_ACCESS_TOKEN`

#### Facebook App Secret (Required for webhook verification)
1. In Facebook Developers Console
2. Settings → Basic
3. Copy App Secret
4. Paste into `FACEBOOK_APP_SECRET`

#### ImgBB API Key (Optional - for image uploads)
1. Go to [imgbb.com](https://imgbb.com)
2. Sign up for free account
3. Go to API → Get API Key
4. Copy and paste into `IMGBB_API_KEY`

**Note**: If you don't provide ImgBB key, placeholder images will be used.

### 4. Setup Facebook Webhook

1. Start your application (see Running section below)
2. Get your public URL (on Emergent, it's auto-provided)
3. In Facebook App → Messenger → Webhooks:
   - Callback URL: `https://your-domain.com/api/webhook`
   - Verify Token: `nepali_clothing_2025`
   - Subscribe to: `messages`, `messaging_postbacks`

## Running the Application

The application is already running on Emergent platform with supervisor:

```bash
# Restart backend
sudo supervisorctl restart backend

# Restart frontend
sudo supervisorctl restart frontend

# Check status
sudo supervisorctl status
```

## Admin Panel Usage

### Login
- URL: `http://localhost:3000` or your deployed URL
- Default Password: `admin123`

### Dashboard
- View today/week/month statistics
- See recent orders
- Quick actions to products and orders

### Products Management
1. Click "Products" in navigation
2. Click "Add Product" button
3. Fill in product details:
   - Name, price, description
   - Colors (comma-separated: Red, Blue, Green)
   - Sizes (comma-separated: S, M, L, XL)
   - Stock quantity
   - Upload images (drag & drop or click)
4. Click "Add Product"

### Orders Management
1. Click "Orders" in navigation
2. View all orders with status
3. Search by name, phone, or order ID
4. Filter by status
5. Update order status (Confirm → Ship → Deliver)

## AI Sales Agent Features

### Conversation Stages
1. **Greeting**: Welcome and establish rapport
2. **Browsing**: Understand needs and recommend products
3. **Negotiation**: Handle objections and justify pricing
4. **Ordering**: Collect customer details
5. **Completed**: Thank customer

### Example Nepali-English Responses
- "Namaste! Kasto chha? Tapailai k type ko dress chaahiyo?"
- "Yo design ta viral bhaisakyo! Only 3 pieces left chha"
- "Rs. 1500 ma ekdum worth it chha. Quality ekdum ramro!"
- "5 jana le aaja order garyo yo design!"

### Smart Features
- Auto-detects product mentions and sends images
- Tracks conversation context per customer
- Handles multiple customers simultaneously
- Stock management with urgency messaging
- Order collection with validation

## Testing

### Test the Admin Panel
1. Login with password: `admin123`
2. Add a sample product
3. Check dashboard analytics
4. Test order filtering

### Test Facebook Messenger Bot
1. Send "Hello" to your Facebook page
2. Bot should respond in Nepali-English mix
3. Ask about products
4. Try to place an order

### Test with curl
```bash
# Test backend health
curl http://localhost:8001/api/

# Test webhook verification (as Facebook would)
curl "http://localhost:8001/api/webhook?hub.mode=subscribe&hub.verify_token=nepali_clothing_2025&hub.challenge=12345"
```

## Deployment

### On Emergent Platform (Current)
Already configured! Just ensure environment variables are set.

### On Railway.app
1. Push code to GitHub
2. Connect repository to Railway
3. Add environment variables in Railway dashboard
4. Deploy

## API Endpoints

### Public
- `GET /api/webhook` - Facebook webhook verification
- `POST /api/webhook` - Handle incoming messages
- `POST /api/auth/login` - Admin login

### Admin (Requires JWT Token)
- `GET /api/admin/products` - List products
- `POST /api/admin/products` - Create product
- `PUT /api/admin/products/{id}` - Update product
- `DELETE /api/admin/products/{id}` - Delete product
- `POST /api/admin/upload-image` - Upload image
- `GET /api/admin/orders` - List orders
- `GET /api/admin/orders/{id}` - Get order details
- `PUT /api/admin/orders/{id}/status` - Update order status
- `GET /api/admin/analytics` - Get dashboard analytics

## Database Schema

### Products Collection
```javascript
{
  product_id: String,
  name: String,
  price: Number,
  description: String,
  colors: [String],
  sizes: [String],
  stock: Number,
  images: [String],
  active: Boolean,
  created_at: String
}
```

### Conversations Collection
```javascript
{
  conversation_id: String,
  customer_id: String,
  messages: [{
    sender: String,  // 'customer' or 'agent'
    text: String,
    timestamp: String,
    product_ids: [String]
  }],
  stage: String,  // greeting, browsing, negotiation, ordering, completed
  context: Object,
  last_updated: String
}
```

### Orders Collection
```javascript
{
  order_id: String,
  customer_id: String,
  customer_name: String,
  phone: String,
  address: String,
  items: [{
    product_id: String,
    product_name: String,
    color: String,
    size: String,
    quantity: Number,
    price: Number
  }],
  total_amount: Number,
  payment_method: String,  // 'COD' or 'Online'
  payment_screenshot: String,
  status: String,  // pending, confirmed, shipped, delivered, cancelled
  created_at: String
}
```

## Troubleshooting

### Bot not responding on Facebook
- Check `FACEBOOK_PAGE_ACCESS_TOKEN` is correct
- Verify webhook is subscribed to page
- Check backend logs: `tail -f /var/log/supervisor/backend.err.log`
- Ensure webhook URL is publicly accessible

### Images not uploading
- Check `IMGBB_API_KEY` is set (or leave empty for placeholders)
- Verify image file size < 10MB
- Check file format (PNG, JPG supported)

### Admin panel not loading
- Check frontend is running: `sudo supervisorctl status frontend`
- Verify `REACT_APP_BACKEND_URL` in `/app/frontend/.env`
- Check browser console for errors

### AI responses not working
- Verify `EMERGENT_LLM_KEY` is set correctly
- Check backend logs for API errors
- Ensure internet connectivity for API calls

### Database connection issues
- Verify `MONGO_URL` is correct
- Check MongoDB is running: `sudo systemctl status mongod`
- Test connection: `mongosh mongodb://localhost:27017`

## Production Checklist

- [ ] Change `ADMIN_PASSWORD` from default
- [ ] Update `JWT_SECRET` to secure random string
- [ ] Set proper `CORS_ORIGINS` (remove `*`)
- [ ] Configure Facebook webhook with HTTPS
- [ ] Add ImgBB API key for image uploads
- [ ] Set up proper Facebook App review
- [ ] Configure rate limiting
- [ ] Set up monitoring and logging
- [ ] Regular database backups

## Features Roadmap

- [ ] Payment gateway integration (Khalti, eSewa)
- [ ] SMS notifications
- [ ] Order tracking
- [ ] Customer feedback system
- [ ] Analytics dashboard
- [ ] Multi-language support
- [ ] Inventory alerts
- [ ] Discount codes

## Support

For issues or questions:
- Check logs: `/var/log/supervisor/`
- Review backend errors: `tail -f /var/log/supervisor/backend.err.log`
- Review frontend errors: `tail -f /var/log/supervisor/frontend.err.log`

## License

MIT License - Feel free to use for your business!

## Credits

Built with:
- FastAPI
- React
- MongoDB
- Emergent LLM (via emergentintegrations)
- Shadcn UI Components
- Tailwind CSS

---

**Made with ❤️ for Urban fashion Fashion Businesses**
