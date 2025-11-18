# 🚀 Render Deployment Guide - Urban Fashion AI Agent

## Complete Step-by-Step Guide

---

## Step 1: Sign Up for Render (2 minutes)

1. Go to: **https://render.com**
2. Click **"Get Started"** or **"Sign Up"**
3. Sign up with **GitHub** (easiest option)
4. Authorize Render to access your GitHub

✅ **Done!** You're logged into Render

---

## Step 2: Deploy Backend (5 minutes)

### A. Create Backend Service

1. In Render dashboard, click **"New +"** button (top right)
2. Select **"Web Service"**
3. Click **"Connect a repository"** or find your repo
4. Select: **`sales-bot-for-messanger`**
5. Click **"Connect"**

### B. Configure Backend

Fill in these settings:

**Basic Settings:**
- **Name**: `urban-fashion-backend` (or any name you like)
- **Region**: Choose closest to you (e.g., Singapore, Oregon)
- **Branch**: `main`
- **Root Directory**: `backend`
- **Runtime**: **Python 3**
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn server:app --host 0.0.0.0 --port $PORT`

**Instance Type:**
- Select **"Free"** (scroll down to find it)

### C. Add Environment Variables

Scroll down to **"Environment Variables"** section and add these:

Click **"Add Environment Variable"** for each:

```
MONGO_URL = mongodb+srv://UrbanFashion:urbanfashion%40123@urbanfashion.mirrk83.mongodb.net/?retryWrites=true&w=majority&appName=UrbanFashion

DB_NAME = urban_fashion_db

CORS_ORIGINS = *

FACEBOOK_PAGE_ACCESS_TOKEN = EAA6N1agH8RwBPx7VJVg3IyBTl1ucKokjuuF6OQCcCe27gKKCn8NyXuDmvSMKEubZAZARgZBVhWPr7wCybBSbNsQRJQyTTWyrrE8ZBRseFoRnMWkTWEQxkD9GIUtjZBh5aPX3KhlseQqHeHlpdf60ye2xbaC259FQuBxoHDWIHwBlvDMCIQPLH2rCXyzOA71cilByaxQZDZD

FACEBOOK_VERIFY_TOKEN = nepali_clothing_2025

FACEBOOK_APP_SECRET = 127a816063e01957dcd7a371f46682c1

EMERGENT_LLM_KEY = sk-emergent-6Bb7766873eC7EfE12

IMGBB_API_KEY = (leave empty for now)

ADMIN_PASSWORD = admin123

JWT_SECRET = nepali-fashion-secret-2025

BUSINESS_NAME = Urban Fashion

AGENT_NAME = Aashis

BUSINESS_LOCATION = Gausala area

PORT = 8001
```

### D. Deploy Backend

1. Click **"Create Web Service"** button at the bottom
2. Render will start building and deploying (takes 3-5 minutes)
3. **Wait for it to show "Live"** (green status)

### E. Get Backend URL

1. Once deployed, you'll see your service URL at the top
2. It looks like: `https://urban-fashion-backend.onrender.com`
3. **COPY THIS URL** - you'll need it for frontend!

### F. Test Backend

1. Open: `https://your-backend-url.onrender.com/api/`
2. Should show: `{"message": "Nepal Clothing Sales Agent API", "status": "running"}`
3. ✅ Backend is working!

---

## Step 3: Deploy Frontend (5 minutes)

### A. Create Frontend Service

1. In Render dashboard, click **"New +"** button again
2. Select **"Static Site"**
3. Select the SAME repository: **`sales-bot-for-messanger`**
4. Click **"Connect"**

### B. Configure Frontend

Fill in these settings:

**Basic Settings:**
- **Name**: `urban-fashion-frontend`
- **Branch**: `main`
- **Root Directory**: `frontend`
- **Build Command**: `yarn install && yarn build`
- **Publish Directory**: `build`

### C. Add Environment Variable

Add ONE environment variable:

```
REACT_APP_BACKEND_URL = https://your-backend-url.onrender.com
```

**IMPORTANT:** Replace with your actual backend URL from Step 2E!

Example:
```
REACT_APP_BACKEND_URL = https://urban-fashion-backend.onrender.com
```

### D. Deploy Frontend

1. Click **"Create Static Site"** button
2. Render will build and deploy (takes 3-5 minutes)
3. **Wait for "Live"** status

### E. Get Frontend URL

1. Your frontend URL will be shown at the top
2. It looks like: `https://urban-fashion-frontend.onrender.com`
3. **COPY THIS URL**

### F. Test Frontend

1. Open your frontend URL
2. Should see login page
3. Login with password: `admin123`
4. ✅ Frontend is working!

---

## Step 4: Update CORS (Important!)

Now that you have the frontend URL, update backend CORS:

1. Go to your **backend service** in Render
2. Click **"Environment"** tab (left sidebar)
3. Find `CORS_ORIGINS` variable
4. Click **"Edit"**
5. Change from `*` to your frontend URL:
   ```
   https://urban-fashion-frontend.onrender.com
   ```
6. Click **"Save Changes"**
7. Backend will automatically redeploy

---

## Step 5: Connect Facebook Webhook (5 minutes)

### A. Go to Facebook Developers

1. Open: **https://developers.facebook.com/apps**
2. Select your "Urban Fashion Bot" app

### B. Setup Webhook

1. Click **"Messenger"** in left sidebar
2. Click **"Settings"**
3. Scroll to **"Webhooks"** section
4. Click **"Add Callback URL"**

### C. Enter Webhook Details

- **Callback URL**: `https://your-backend-url.onrender.com/api/webhook`
  (Use your actual backend URL from Step 2E)
  
  Example: `https://urban-fashion-backend.onrender.com/api/webhook`

- **Verify Token**: `nepali_clothing_2025`

5. Click **"Verify and Save"**
6. ✅ Should show green checkmark!

### D. Subscribe to Page

1. Under "Webhooks" section
2. Click **"Add or Remove Pages"**
3. Select your "Urban Fashion" page
4. Click **"Subscribe"**
5. Check these events:
   - ✅ **messages**
   - ✅ **messaging_postbacks**
6. Click **"Done"**

---

## Step 6: Test Your Bot! 🎉

### A. Test on Facebook Messenger

1. Go to your **Facebook Page**
2. Click **"Send Message"**
3. Type: **"Hello"**
4. Bot should respond:
   ```
   Namaste! Hajur kasto hununcha? 😊
   Ma Aashis ho, Urban Fashion bata.
   ```

### B. Test Full Conversation

- Ask about products
- Try to place an order
- Bot should respond naturally in high-respect Nepali-English

---

## Step 7: Add Your Products (5 minutes)

### A. Login to Admin Dashboard

1. Open: `https://your-frontend-url.onrender.com`
2. Password: `admin123`

### B. Add Product

1. Click **"Products"** in navigation
2. Click **"Add Product"** button
3. Fill in:
   - **Name**: Your product name
   - **Price**: 999
   - **Regular Price**: 1499
   - **Description**: Product details
   - **Colors**: Blue, Black, Navy (comma-separated)
   - **Sizes**: 28, 30, 32, 34, 36 (comma-separated)
   - **Stock**: 50
   - **Upload images**
   - Check **"Product Active"**
4. Click **"Add Product"**

### C. Test Bot with Product

- Message your Facebook page again
- Ask about the product
- Bot should now know about it!

---

## ✅ Deployment Complete!

### Your Live URLs:
- **Backend API**: https://your-backend-url.onrender.com
- **Frontend Dashboard**: https://your-frontend-url.onrender.com
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

Update these in Render backend environment variables:

1. **Change Admin Password:**
   - Edit `ADMIN_PASSWORD` to a strong password

2. **Change JWT Secret:**
   - Edit `JWT_SECRET` to a random secret key

3. **Update CORS:**
   - Already done in Step 4!

---

## 🆘 Troubleshooting

### Backend deployment failed?
- Check logs: Click service → "Logs" tab
- Verify MongoDB connection string is correct
- Check all environment variables are set

### Frontend can't connect to backend?
- Verify `REACT_APP_BACKEND_URL` matches backend URL exactly
- Check CORS_ORIGINS in backend includes frontend URL
- Clear browser cache

### Bot not responding on Facebook?
- Check webhook shows green checkmark in Facebook
- Verify `FACEBOOK_PAGE_ACCESS_TOKEN` is correct
- Check backend logs for errors
- Test webhook manually: `https://your-backend-url/api/webhook?hub.mode=subscribe&hub.verify_token=nepali_clothing_2025&hub.challenge=test`

### Render free tier limitations:
- Services spin down after 15 minutes of inactivity
- First request after spin-down takes 30-60 seconds
- Upgrade to paid tier ($7/month) for always-on service

---

## 📊 Monitor Your Deployment

**Check Logs:**
- Render Dashboard → Click service → "Logs" tab

**Check Status:**
- Backend health: `https://your-backend-url/api/`
- Should return: `{"message": "Nepal Clothing Sales Agent API", "status": "running"}`

---

## 🎉 You're Live!

Your AI sales agent is now running 24/7 on Render, ready to handle customers on Facebook Messenger!

**Next Steps:**
1. Add your real products
2. Test full order flow
3. Share your Facebook page
4. Start selling! 🚀

---

**Need help? Check the logs or refer back to this guide!**
