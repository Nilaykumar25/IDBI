/**
 * Firebase Configuration and Initialization
 * 
 * This file initializes Firebase Authentication and Firestore
 * using environment variables for security.
 */
import { initializeApp } from 'firebase/app'
import { getAuth, setPersistence, browserLocalPersistence } from 'firebase/auth'
import { getFirestore } from 'firebase/firestore'

// Firebase configuration from environment variables
const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID
}

// Validate that all required config values are present
const requiredConfigKeys = [
  'VITE_FIREBASE_API_KEY',
  'VITE_FIREBASE_AUTH_DOMAIN',
  'VITE_FIREBASE_PROJECT_ID',
  'VITE_FIREBASE_STORAGE_BUCKET',
  'VITE_FIREBASE_MESSAGING_SENDER_ID',
  'VITE_FIREBASE_APP_ID'
]

const missingKeys = requiredConfigKeys.filter(
  key => !import.meta.env[key]
)

if (missingKeys.length > 0) {
  console.error('Missing Firebase configuration:', missingKeys)
  throw new Error(
    `Missing required Firebase environment variables: ${missingKeys.join(', ')}. ` +
    'Please check your .env file.'
  )
}

// Initialize Firebase
const app = initializeApp(firebaseConfig)

// Initialize Firebase Authentication and set persistence
const auth = getAuth(app)
setPersistence(auth, browserLocalPersistence).catch((error) => {
  console.error('Error setting auth persistence:', error)
})

// Initialize Firestore
const db = getFirestore(app)

export { auth, db }
