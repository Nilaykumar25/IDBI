# Firebase Authentication Setup Guide

This document explains how to complete the Firebase Authentication integration for the IDBI MSME Financial Health Score application.

## ✅ What's Already Done

1. **Firebase SDK Integration**
   - Created `src/lib/firebase.js` with Firebase initialization
   - Environment variable-based configuration (no hardcoded secrets)
   
2. **AuthContext Updated**
   - Replaced Supabase Auth with Firebase Auth
   - Added user-friendly error message mapping
   - Implemented Firestore user profile creation on signup
   - Added Google Sign-In support (ready to use)

3. **Protected Routes**
   - `ProtectedRoute` component already exists
   - Dashboard and protected pages are wrapped with authentication checks
   - Automatic redirect to `/login` for unauthenticated users

4. **UI Components**
   - Sign In and Sign Up forms unchanged (as requested)
   - Error display using existing error message pattern
   - Loading states preserved

## 🔧 Setup Steps Required

### 1. Install Firebase Package

```bash
cd c:\Desktop\IDBI\frontend
npm install firebase
```

### 2. Configure Environment Variables

Create or update `c:\Desktop\IDBI\frontend\.env` with your Firebase project credentials:

```env
# Firebase Configuration (from Firebase Console)
VITE_FIREBASE_API_KEY=your-actual-api-key-here
VITE_FIREBASE_AUTH_DOMAIN=idbi-msme.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=idbi-msme
VITE_FIREBASE_STORAGE_BUCKET=idbi-msme.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=your-sender-id
VITE_FIREBASE_APP_ID=your-app-id

# Backend API Configuration
VITE_API_URL=http://localhost:5000/api
```

**Where to find these values:**
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your "IDBI" project
3. Click the gear icon ⚙️ → Project settings
4. Scroll down to "Your apps" section
5. Click on the web app or add one if needed
6. Copy the config values to your `.env` file

### 3. Enable Authentication Providers (Already Done ✅)

According to your prompt, these are already enabled in Firebase Console:
- ✅ Email/Password authentication
- ✅ Google Sign-In
- ✅ `idbi-msme.vercel.app` added as authorized domain

### 4. Set Up Firestore Database

1. In Firebase Console, go to **Firestore Database**
2. Click "Create database"
3. Choose **Start in production mode** (or test mode for development)
4. Select a region (closest to your users)
5. The database will be created with a `users` collection automatically when first user signs up

**Firestore Security Rules (Recommended):**
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users can only read/write their own profile
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
  }
}
```

### 5. Update Firestore Indexes (If Needed)

No indexes required for basic user profiles. If you add queries later, Firestore will prompt you to create indexes automatically.

## 🎯 How It Works

### Sign Up Flow
1. User fills form on `/signup` page
2. `signUp(email, password)` → Firebase creates account
3. User profile created in Firestore: `users/{uid}`
   ```javascript
   {
     email: "user@example.com",
     createdAt: timestamp
   }
   ```
4. User automatically signed in
5. Redirected to `/dashboard`

### Sign In Flow
1. User fills form on `/login` page
2. `signIn(email, password)` → Firebase authenticates
3. Session persisted in browser (localStorage)
4. Redirected to `/dashboard`

### Error Handling
Firebase errors are mapped to user-friendly messages:
- `auth/wrong-password` → "Invalid email or password"
- `auth/email-already-in-use` → "This email is already registered. Please sign in instead."
- `auth/weak-password` → "Password should be at least 6 characters"
- And more...

### Session Persistence
- Uses `browserLocalPersistence` (default)
- User stays logged in across page reloads
- `onAuthStateChanged` listener tracks auth state
- Protected routes automatically redirect unauthenticated users

## 🔐 Security Notes

1. **Environment Variables**: Never commit `.env` file to Git (already in `.gitignore`)
2. **Firebase API Key**: Safe to use in frontend (restricted by domain in Firebase Console)
3. **Firestore Rules**: Set up proper security rules in production
4. **HTTPS**: Always use HTTPS in production (Vercel handles this automatically)

## 🚀 Testing

### Local Development
```bash
cd c:\Desktop\IDBI\frontend
npm run dev
```

### Test Sign Up
1. Go to `http://localhost:3010/signup`
2. Enter email and password
3. Click "Sign up"
4. Should redirect to dashboard
5. Check Firestore Console to see user profile created

### Test Sign In
1. Go to `http://localhost:3010/login`
2. Enter same credentials
3. Click "Sign in"
4. Should redirect to dashboard

### Test Protected Routes
1. Open `http://localhost:3010/dashboard` in incognito
2. Should automatically redirect to `/login`
3. After signing in, should access dashboard

## 🆕 Optional: Add Google Sign-In Button

The `signInWithGoogle()` function is already implemented in AuthContext. To add a Google sign-in button:

**In Login.jsx or Signup.jsx, add after the form:**
```jsx
<div style={{ margin: '1rem 0', textAlign: 'center', color: '#6b7280' }}>
  or
</div>
<button 
  type="button" 
  onClick={handleGoogleSignIn}
  className="btn btn-google"
  disabled={loading}
>
  <img src="/google-icon.svg" alt="Google" style={{ width: 20, marginRight: 8 }} />
  Continue with Google
</button>
```

**Add handler:**
```javascript
const handleGoogleSignIn = async () => {
  setError('')
  setLoading(true)
  try {
    await signInWithGoogle()
    navigate('/dashboard')
  } catch (err) {
    setError(err.message || 'Failed to sign in with Google')
  } finally {
    setLoading(false)
  }
}
```

**Add CSS (in Auth.css):**
```css
.btn-google {
  background: white;
  border: 1px solid #d1d5db;
  color: #374151;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-google:hover {
  background: #f9fafb;
  border-color: #9ca3af;
}
```

## 📊 Firestore User Profile Structure

```javascript
// Collection: users
// Document ID: Firebase Auth UID
{
  email: "user@example.com",
  createdAt: Firestore timestamp,
  // Optional fields (add to signup form if needed):
  displayName: "John Doe",
  photoURL: "https://...",
  role: "credit_officer", // or "admin", "viewer"
  organization: "IDBI Bank",
  lastSignIn: Firestore timestamp
}
```

## 🐛 Troubleshooting

### "Missing Firebase configuration" error
- Check all `VITE_FIREBASE_*` variables are in `.env`
- Restart dev server after adding env variables

### "Firebase: Error (auth/network-request-failed)"
- Check internet connection
- Verify Firebase project is active in Console

### "Firebase: Error (auth/unauthorized-domain)"
- Add `localhost:3010` to authorized domains in Firebase Console
- Go to Authentication → Settings → Authorized domains

### User profile not created in Firestore
- Check Firestore security rules allow writes
- Verify database exists in Firebase Console

## ✨ Features Implemented

- ✅ Email/Password authentication
- ✅ User-friendly error messages
- ✅ Session persistence across page reloads
- ✅ Protected routes with auto-redirect
- ✅ Firestore user profile creation
- ✅ Google Sign-In support (ready to wire to UI)
- ✅ Loading states
- ✅ Clean error handling
- ✅ No UI changes (drop-in functional layer)

## 📝 Migration from Supabase

The integration replaces Supabase Auth with Firebase Auth. The API is similar, so existing components (Login, Signup) work without changes. Key differences:

| Feature | Supabase | Firebase |
|---------|----------|----------|
| Session object | `session` | Removed (use `user` directly) |
| User object | `session.user` | `user` |
| Error handling | Supabase errors | Firebase errors (mapped to friendly messages) |
| User profiles | Supabase Auth tables | Firestore `users` collection |

## 🔄 Next Steps

1. **Install Firebase**: Run `npm install firebase`
2. **Add Environment Variables**: Create `.env` with Firebase config
3. **Test Authentication**: Try signup and signin
4. **Deploy**: Push to Vercel (env vars configured there too)
5. **Optional**: Add Google Sign-In button to UI

---

**Need Help?**
- [Firebase Auth Documentation](https://firebase.google.com/docs/auth/web/start)
- [Firestore Documentation](https://firebase.google.com/docs/firestore)
- [Firebase Console](https://console.firebase.google.com/)
