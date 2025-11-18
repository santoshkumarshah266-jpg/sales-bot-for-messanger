# 🚀 Railway Deployment - Both Backend & Frontend

## Quick Setup Guide

### Step 1: Deploy to Railway

1. **Go to Railway:**
   - Open: https://railway.app
   - Click "Login" → Sign in with **GitHub**
   - Authorize Railway

2. **Create New Project:**
   - Click **"New Project"**
   - Select **"Deploy from GitHub repo"**
   - Find: `sales-bot-for-messanger`
   - Click **"Deploy Now"**

Railway will automatically detect your project and may create one service. We need TWO services (backend + frontend).

---

### Step 2: Configure Backend Service

**A. Rename the service (optional):**
- Click on the service
- Click "Settings" tab
- Change name to: `backend`

**B. Set Root Directory:**
- In "Settings" tab
- Find "Root Directory"
- Set to: `backend`
- Click outside to save

**C. Add Environment Variables:**
- Click **"Variables"** tab
- Click **"+ New Variable"** or **"Raw Editor"**
- Paste ALL these variables:

```
MONGO_URL=mongodb+srv://UrbanFashion:urbanfashion%40123@urbanfashion.mirrk83.mongodb.net/?retryWrites=true&w=majority&appName=UrbanFashion
DB_NAME=urban_fashion_db
CORS_ORIGINS=*
FACEBOOK_PAGE_ACCESS_TOKEN=EAA6N1agH8RwBPx7VJVg3IyBTl1ucKokjuuF6OQCcCe27gKKCn8NyXuDmvSMKEubZAZARgZBVhWPr7wCybBSbNsQRJQyTTWyrrE8ZBRseFoRnMWkTWEQxkD9GIUtjZBh5aPX3KhlseQqHeHlpdf60ye2xbaC259FQuBxoHDWIHwBlvDMCIQPLH2rCXyzOA71cilByaxQZDZD
FACEBOOK_VERIFY_TOKEN=nepali_clothing_2025
FACEBOOK_APP_SECRET=127a816063e01957dcd7a371f46682c1
EMERGENT_LLM_KEY=sk-emergent-6Bb7766873eC7EfE12
IMGBB_API_KEY=
ADMIN_PASSWORD=admin123
JWT_SECRET=nepali-fashion-secret-2025
BUSINESS_NAME=Urban Fashion
AGENT_NAME=Aashis
BUSINESS_LOCATION=Gausala area
PORT=8001
```

- Click **"Add"** or **"Update Variables"**
- Wait for redeploy (2-3 minutes)

**D. Generate Public URL:**
- Click **"Settings"** tab
- Scroll to **"Networking"** section
- Click **"Generate Domain"**
- **COPY THIS URL** → Example: `https://sales-bot-backend.up.railway.app`
- **SAVE IT** - you'll need it for frontend!

**E. Test Backend:**
- Open: `https://your-backend-url/api/`
- Should show: `{"message": "Nepal Clothing Sales Agent API", "status": "running"}`
- ✅ Backend is working!

---

### Step 3: Add Frontend Service

**A. Add New Service:**
- Go back to your Railway project dashboard (click project name at top)
- Click **"+ New"** button
- Select **"GitHub Repo"**
- Select the SAME repository: `sales-bot-for-messanger`
- Click **"Add"** or **"Deploy"**

**B. Configure Frontend:**
- Click on the new service
- Click **"Settings"** tab
- Change name to: `frontend` (optional)
- Set "Root Directory" to: `frontend`

**C. Add Frontend Variables:**
- Click **"Variables"** tab
- Add these TWO variables:

```
REACT_APP_BACKEND_URL=https://your-backend-url-from-step-2
PORT=3000
```

**IMPORTANT:** Replace `https://your-backend-url-from-step-2` with the actual backend URL you copied in Step 2D!

Example:
```
REACT_APP_BACKEND_URL=https://sales-bot-backend.up.railway.app
PORT=3000
```

- Click **"Add"**
- Wait for deployment (3-5 minutes)

**D. Generate Frontend URL:**
- Click **"Settings"** tab
- Scroll to **"Networking"**
- Click **"Generate Domain"**
- **COPY THIS URL** → Example: `https://sales-bot-frontend.up.railway.app`

**E. Test Frontend:**
- Open your frontend URL
- Should see login page with "Urban Fashion"
- Login with password: `admin123`
- ✅ Frontend is working!

---

### Step 4: Update CORS (Important!)

Now that you have the frontend URL, update backend CORS:

**A. Go to Backend Service:**
- Click on backend service in Railway
- Click **"Variables"** tab
- Find `CORS_ORIGINS`
- Change from `*` to your frontend URL:

```
CORS_ORIGINS=https://your-frontend-url.up.railway.app
```

Example:
```
CORS_ORIGINS=https://sales-bot-frontend.up.railway.app
```

- Backend will redeploy automatically

---

### Step 5: Connect Facebook Webhook

**A. Go to Facebook Developers:**
- Open: https://developers.facebook.com/apps
- Select your "Urban Fashion Bot" app

**B. Setup Webhook:**
- Click **"Messenger"** in left sidebar
- Click **"Settings"**
- Scroll to **"Webhooks"** section
- Click **"Add Callback URL"**

**C. Enter Details:**
- **Callback URL**: `https://your-backend-url.up.railway.app/api/webhook`
  (Use your actual backend URL from Step 2D)
- **Verify Token**: `nepali_clothing_2025`
- Click **"Verify and Save"**
- ✅ Should show green checkmark!

**D. Subscribe to Page:**
- Under "Webhooks" section
- Click **"Add or Remove Pages"**
- Select your "Urban Fashion" page
- Click **"Subscribe"**
- Check these events:
  - ✅ **messages**
  - ✅ **messaging_postbacks**
- Click **"Done"**

---

### Step 6: Test Your Bot! 🎉

**A. Test on Facebook:**
1. Go to your Facebook Page
2. Click **"Send Message"**
3. Type: **"Hello"**
4. Bot should respond:
   ```
   Namaste! Hajur kasto hununcha? 😊
   Ma Aashis ho, Urban Fashion bata.
   ```

**B. Test Conversation:**
- Ask: "Product ko baare ma jannu huncha?"
- Bot should respond naturally in Nepali-English
- Try placing an order

---

### Step 7: Add Your Products

**A. Login to Admin:**
- Open: `https://your-frontend-url.up.railway.app`
- Password: `admin123`

**B. Add Product:**
- Click **"Products"** in navigation
- Click **"Add Product"** button
- Fill in:
  - **Name**: Your product name (e.g., "Premium Jeans")
  - **Price**: 999
  - **Regular Price**: 1499
  - **Description**: Product details
  - **Colors**: Blue, Black, Navy (comma-separated)
  - **Sizes**: 28, 30, 32, 34, 36 (comma-separated)
  - **Stock**: 50
  - **Upload images** (drag & drop or click)
  - Check **"Product Active"**
- Click **"Add Product"**

**C. Test Bot Again:**
- Message your Facebook page
- Bot should now know about your product!
- Ask about the product
- Try to order

---

## ✅ Deployment Complete!

### Your Live URLs:
- **Backend API**: https://your-backend-url.up.railway.app
- **Frontend Dashboard**: https://your-frontend-url.up.railway.app
- **Facebook Page**: Your Urban Fashion page

### What's Working:
✅ AI Agent Aashis responding in high-respect Nepali-English
✅ Facebook Messenger integration
✅ Order collection with delivery charges (Rs. 150)
✅ Admin dashboard with analytics
✅ Product management with images
✅ Payment QR system
✅ Media notification system

---

## 🔐 Security (Before Going Live)

Update these in Railway backend variables:

1. **Change Admin Password:**
   - `ADMIN_PASSWORD=your_strong_password_123`

2. **Change JWT Secret:**
   - `JWT_SECRET=your_random_secret_key_xyz789`

3. **Update CORS:**
   - `CORS_ORIGINS=https://your-frontend-url.up.railway.app`

---

## 🆘 Troubleshooting

### Backend deployment failed?
- Check logs: Click backend service → "Deployments" → "View Logs"
- Verify MongoDB connection string is correct
- Check all environment variables are set

### Frontend can't connect to backend?
- Verify `REACT_APP_BACKEND_URL` matches backend URL exactly
- Check CORS_ORIGINS in backend includes frontend URL
- Clear browser cache and try again

### Bot not responding on Facebook?
- Check webhook shows green checkmark in Facebook
- Verify `FACEBOOK_PAGE_ACCESS_TOKEN` is correct
- Check backend logs for errors
- Test webhook: `https://your-backend-url/api/webhook?hub.mode=subscribe&hub.verify_token=nepali_clothing_2025&hub.challenge=test`

### Images not uploading?
- Get free ImgBB API key: https://imgbb.com
- Add to backend variables: `IMGBB_API_KEY=your_key`

---

## 📊 Monitor Your Deployment

**Check Logs:**
- Railway Dashboard → Click service → "Deployments" → "View Logs"

**Check Status:**
- Backend health: `https://your-backend-url/api/`
- Should return: `{"message": "Nepal Clothing Sales Agent API", "status": "running"}`

---

## 🎉 You're Live!

Your AI sales agent is now running 24/7 on Railway, ready to handle customers on Facebook Messenger!

**Next Steps:**
1. Add your real products
2. Test full order flow
3. Share your Facebook page
4. Start selling! 🚀

---

**Need help? Check the logs or ask for assistance!**
