import React, { createContext, useContext, useEffect, useState } from 'react';
import { 
  User, 
  signInWithEmailAndPassword, 
  createUserWithEmailAndPassword,
  signOut,
  onAuthStateChanged,
  GoogleAuthProvider,
  signInWithPopup,
  updateProfile
} from 'firebase/auth';
import { auth } from '../config/firebase';

export type UserRole = 'admin' | 'user';

export interface UserProfile {
  uid: string;
  email: string;
  role: UserRole;
  displayName?: string;
}

interface AuthContextType {
  currentUser: User | null;
  userProfile: UserProfile | null;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string, role?: UserRole) => Promise<void>;
  logout: () => Promise<void>;
  signInWithGoogle: () => Promise<void>;
  loading: boolean;
  isAdmin: boolean;
}

const AuthContext = createContext<AuthContextType>({} as AuthContextType);

export const useAuth = () => {
  return useContext(AuthContext);
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);

  // Define admin emails (you can expand this or move to a database)
  const adminEmails = ['admin@resume-system.com', 'sachin@admin.com'];

  const signup = async (email: string, password: string, role: UserRole = 'user') => {
    const userCredential = await createUserWithEmailAndPassword(auth, email, password);
    
    // Use the selected role during signup, or fall back to email-based detection for existing admin emails
    const userRole = role === 'admin' ? 'admin' : (adminEmails.includes(email) ? 'admin' : 'user');
    
    // Update user profile with role info
    await updateProfile(userCredential.user, {
      displayName: userRole
    });

    // Create user profile
    const profile: UserProfile = {
      uid: userCredential.user.uid,
      email: email,
      role: userRole,
      displayName: userCredential.user.displayName || undefined
    };
    
    setUserProfile(profile);
  };

  const login = async (email: string, password: string) => {
    await signInWithEmailAndPassword(auth, email, password);
  };

  const logout = async () => {
    setUserProfile(null);
    await signOut(auth);
  };

  const signInWithGoogle = async () => {
    const provider = new GoogleAuthProvider();
    const userCredential = await signInWithPopup(auth, provider);
    
    // Determine role based on email
    const userRole = adminEmails.includes(userCredential.user.email || '') ? 'admin' : 'user';
    
    // Update user profile with role
    await updateProfile(userCredential.user, {
      displayName: userRole
    });

    // Create user profile
    const profile: UserProfile = {
      uid: userCredential.user.uid,
      email: userCredential.user.email || '',
      role: userRole,
      displayName: userCredential.user.displayName || undefined
    };
    
    setUserProfile(profile);
  };

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      setCurrentUser(user);
      
      if (user) {
        // Determine user role based on email or displayName
        const adminEmails = ['admin@resume-system.com', 'sachin@admin.com'];
        const userRole = adminEmails.includes(user.email || '') || user.displayName === 'admin' ? 'admin' : 'user';
        
        const profile: UserProfile = {
          uid: user.uid,
          email: user.email || '',
          role: userRole,
          displayName: user.displayName || undefined
        };
        
        setUserProfile(profile);
      } else {
        setUserProfile(null);
      }
      
      setLoading(false);
    });

    return unsubscribe;
  }, []);

  const value = {
    currentUser,
    userProfile,
    login,
    signup,
    logout,
    signInWithGoogle,
    loading,
    isAdmin: userProfile?.role === 'admin'
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
};
