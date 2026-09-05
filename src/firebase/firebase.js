import { initializeApp } from 'firebase/app'
import { getFirestore } from 'firebase/firestore'
import { getStorage } from 'firebase/storage'

const firebaseConfig = {
    apiKey: 'AIzaSyCm8Cd6qZ-y1Zl4wGu846q32egFQG5cvj4',
    authDomain: 'pilotwatch-2e15e.firebaseapp.com',
    projectId: 'pilotwatch-2e15e',
    storageBucket: 'pilotwatch-2e15e.firebasestorage.app',
    messagingSenderId: '230762883757',
    appId: '1:230762883757:web:ab1324a4df648178b8b424',
    measurementId: 'G-EDNKT85LDS',
}

const app = initializeApp(firebaseConfig)

export const db = getFirestore(app)
export const storage = getStorage(app)

export default app