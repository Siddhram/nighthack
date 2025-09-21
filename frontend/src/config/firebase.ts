import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';

const firebaseConfig = {
  apiKey: "AIzaSyDLtmBm4_PdqImWTaAyPLdXab00ONx1szU",
  authDomain: "resume-c4a5e.firebaseapp.com",
  projectId: "resume-c4a5e",
  storageBucket: "resume-c4a5e.firebasestorage.app",
  messagingSenderId: "101747391380",
  appId: "1:101747391380:web:5eddd4ea189965421a6d81"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize Firebase Authentication and get a reference to the service
export const auth = getAuth(app);
export default app;
