# 🚀 Railway Deployment Guide - Urban Fashion AI Agent

## Prerequisites Checklist ✅

You have:
- ✅ MongoDB Connection String
- ✅ Facebook Page Access Token
- ✅ Facebook App Secret

---

## Step 1: Push Code to GitHub

1. **Create GitHub Repository:**
   - Go to: https://github.com/new
   - Repository name: `urban-fashion-ai-agent`
   - Make it **Private** (recommended)
   - Click "Create repository"

2. **Push your code:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit - Urban Fashion AI Agent"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/urban-fashion-ai-agent.git
   git push -u origin main
   ```

---

## Step 2: Deploy Backend to Railway

1. **Go to Railway:**
   - Open: https://railway.app
   - Click "Login" → Sign in with GitHub
   - Authorize Railway

2. **Create New Project:**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Select your `urban-fashion-ai-agent` repository
   - Click "Deploy Now"

3. **Configure Backend Service:**
   - Railway will detect your project
   - Click on the service that gets created
   - Click "Settings" tab
   - Change "Root Directory" to: `backend`
   - Click "Variables" tab
   - Click "Raw Editor"
   - Paste this (with YOUR actual values):

```
MONGO_URL=mongodb+srv://UrbanFashion:YOUR_PASSWORD@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
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

   - Click "Update Variables"
   - Backend will redeploy automatically (takes 2-3 minutes)

4. **Generate Backend Domain:**
   - Click "Settings" tab
   - Scroll to "Networking"
   - Click "Generate Domain"
   - Copy the URL (like: `https://urban-fashion-backend.up.railway.app`)
   - **SAVE THIS URL** - you'll need it!

5. **Test Backend:**
   - Open: `https://your-backend-url.up.railway.app/api/`
   - Should show: `{"message": "Nepal Clothing Sales Agent API", "status": "running"}`
   - ✅ If you see this, backend is working!

---

## Step 3: Deploy Frontend to Railway

1. **Add Frontend Service:**
   - In your Railway project dashboard
   - Click "+ New"
   - Select "GitHub Repo"
   - Select the same repository
   - Click "Deploy"

2. **Configure Frontend Service:**
   - Click on the new service
   - Click "Settings" tab
   - Change "Root Directory" to: `frontend`
   - Click "Variables" tab
   - Add these variables:

```
REACT_APP_BACKEND_URL=https://your-backend-url.up.railway.app
PORT=3000
```

   (Replace with your actual backend URL from Step 2)

   - Click "Add"
   - Frontend will redeploy (takes 3-5 minutes)

3. **Generate Frontend Domain:**
   - Click "Settings" tab
   - Scroll to "Networking"
   - Click "Generate Domain"
   - Copy the URL (like: `https://urban-fashion-frontend.up.railway.app`)
   - **SAVE THIS URL**

4. **Test Frontend:**
   - Open your frontend URL
   - Should see login page
   - Login with password: `admin123`
   - ✅ If you can login, frontend is working!

---

## Step 4: Connect Facebook Webhook

Now connect your bot to Facebook Messenger:

1. **Go to Facebook Developers:**
   - https://developers.facebook.com/apps
   - Select your "Urban Fashion Bot" app

2. **Configure Webhook:**
   - Click "Messenger" in left sidebar
   - Scroll to "Webhooks" section
   - Click "Add Callback URL"
   - **Callback URL**: `https://your-backend-url.up.railway.app/api/webhook`
   - **Verify Token**: `nepali_clothing_2025`
   - Click "Verify and Save"
   - ✅ Should show green checkmark!

3. **Subscribe to Page Events:**
   - Under "Webhooks" section
   - Click "Add or Remove Pages"
   - Select your "Urban Fashion" page
   - Click "Subscribe"
   - Check these fields:
     - ✅ messages
     - ✅ messaging_postbacks
   - Click "Done"

---

## Step 5: Test Your Bot! 🎉

1. **Go to your Facebook Page**
2. **Click "Send Message"**
3. **Type**: "Hello"
4. **Bot should respond**:
   ```
   Namaste! Hajur kasto hununcha? 😊
   Ma Aashis ho, Urban Fashion bata.
   ```

5. **Test conversation:**
   - Ask about products
   - Try to place an order
   - Bot should respond naturally in Nepali-English

---

## Step 6: Add Your Products

1. **Login to Admin Dashboard:**
   - Open: `https://your-frontend-url.up.railway.app`
   - Password: `admin123`

2. **Add Product:**
   - Click "Products"
   - Click "Add Product"
   - Fill in details:
     - Name: Your product name
     - Price: 999
     - Regular Price: 1499
     - Colors: Blue, Black (comma-separated)
     - Sizes: 28, 30, 32, 34, 36
     - Stock: 50
     - Upload images
   - Click "Add Product"

3. **Test Bot Again:**
   - Message your page
   - Bot should now know about your product!

---

## 🎉 CONGRATULATIONS!

Your Urban Fashion AI Agent is LIVE on Railway!

### Your URLs:
- **Admin Dashboard**: https://your-frontend-url.up.railway.app
- **Backend API**: https://your-backend-url.up.railway.app
- **Facebook Page**: Your Urban Fashion page

### What's Working:
✅ AI Agent Aashis responding in Nepali-English
✅ Facebook Messenger integration
✅ Order collection system
✅ Admin dashboard
✅ Product management
✅ Analytics

---

## 🔐 Security (IMPORTANT!)

Before going fully live, update these in Railway backend variables:

```
ADMIN_PASSWORD=your_strong_password_here
JWT_SECRET=your_random_secret_key_here
CORS_ORIGINS=https://your-frontend-url.up.railway.app
```

---

## 🆘 Troubleshooting

### Bot not responding?
- Check webhook is verified (green checkmark in Facebook)
- Check backend logs in Railway (click service → "Deployments" → "View Logs")
- Verify FACEBOOK_PAGE_ACCESS_TOKEN is correct

### Backend deployment failed?
- Check MongoDB connection string is correct
- Verify all environment variables are set
- Check logs for specific errors

### Frontend can't connect to backend?
- Verify REACT_APP_BACKEND_URL is correct
- Check CORS_ORIGINS in backend includes frontend URL

---

## 📞 Need Help?

Check Railway logs:
1. Click on service (backend or frontend)
2. Click "Deployments" tab
3. Click latest deployment
4. Click "View Logs"

---

**Your AI sales agent is ready to sell! 🚀**
