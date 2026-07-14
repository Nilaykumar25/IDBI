/**
 * Authentication context provider.
 * Manages auth state throughout the app using Firebase Auth.
 */
import { createContext, useContext, useEffect, useState } from 'react'
import {
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  signOut as firebaseSignOut,
  onAuthStateChanged,
  GoogleAuthProvider,
  signInWithPopup
} from 'firebase/auth'
import { doc, setDoc, serverTimestamp } from 'firebase/firestore'
import { auth, db } from '../lib/firebase'

const AuthContext = createContext({})

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}

// Helper function to map Firebase error codes to user-friendly messages
const getFirebaseErrorMessage = (errorCode) => {
  switch (errorCode) {
    case 'auth/wrong-password':
    case 'auth/user-not-found':
    case 'auth/invalid-credential':
      return 'Invalid email or password'
    case 'auth/email-already-in-use':
      return 'This email is already registered. Please sign in instead.'
    case 'auth/weak-password':
      return 'Password should be at least 6 characters'
    case 'auth/invalid-email':
      return 'Invalid email address'
    case 'auth/user-disabled':
      return 'This account has been disabled'
    case 'auth/too-many-requests':
      return 'Too many failed attempts. Please try again later.'
    case 'auth/network-request-failed':
      return 'Network error. Please check your connection.'
    case 'auth/popup-closed-by-user':
      return 'Sign-in popup was closed'
    case 'auth/unauthorized-domain':
      return 'This domain is not authorized. Please contact support or try email/password sign-in.'
    case 'auth/operation-not-allowed':
      return 'Google Sign-In is not enabled. Please contact support.'
    default:
      return 'An error occurred. Please try again.'
  }
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (firebaseUser) => {
      setUser(firebaseUser)
      setLoading(false)
    })

    return () => unsubscribe()
  }, [])

  const signUp = async (email, password) => {
    try {
      // Create user account with Firebase Auth
      const userCredential = await createUserWithEmailAndPassword(auth, email, password)
      const user = userCredential.user

      // Create user profile document in Firestore
      await setDoc(doc(db, 'users', user.uid), {
        email: user.email,
        createdAt: serverTimestamp(),
        // Add any additional fields from your signup form here
        // e.g., name, role, etc.
      })

      return userCredential
    } catch (error) {
      // Throw user-friendly error message
      const friendlyMessage = getFirebaseErrorMessage(error.code)
      const customError = new Error(friendlyMessage)
      customError.code = error.code
      throw customError
    }
  }

  const signIn = async (email, password) => {
    try {
      const userCredential = await signInWithEmailAndPassword(auth, email, password)
      return userCredential
    } catch (error) {
      // Throw user-friendly error message
      const friendlyMessage = getFirebaseErrorMessage(error.code)
      const customError = new Error(friendlyMessage)
      customError.code = error.code
      throw customError
    }
  }

  const signInWithGoogle = async () => {
    try {
      const provider = new GoogleAuthProvider()
      const result = await signInWithPopup(auth, provider)
      const user = result.user

      // Create or update user profile in Firestore
      await setDoc(
        doc(db, 'users', user.uid),
        {
          email: user.email,
          displayName: user.displayName,
          photoURL: user.photoURL,
          createdAt: serverTimestamp(),
          lastSignIn: serverTimestamp()
        },
        { merge: true }
      )

      return result
    } catch (error) {
      const friendlyMessage = getFirebaseErrorMessage(error.code)
      const customError = new Error(friendlyMessage)
      customError.code = error.code
      throw customError
    }
  }

  const signOut = async () => {
    try {
      await firebaseSignOut(auth)
      // Clear any cached data
      sessionStorage.clear()
      localStorage.removeItem('currentMSME')
    } catch (error) {
      const friendlyMessage = getFirebaseErrorMessage(error.code)
      throw new Error(friendlyMessage)
    }
  }

  const value = {
    user,
    loading,
    signUp,
    signIn,
    signInWithGoogle,
    signOut,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
