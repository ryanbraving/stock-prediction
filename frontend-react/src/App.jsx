import { useState } from 'react'
import './assets/css/style.css'
import Header from './assets/componenets/Header.jsx'
import Main from './assets/componenets/Main.jsx'
import Footer from './assets/componenets/Footer.jsx'
import Register from './assets/componenets/Register.jsx'
import Login from './assets/componenets/Login.jsx'
import Dashboard from './assets/componenets/dashboard/Dashboard.jsx'
import { BrowserRouter, Routes, Route } from 'react-router'
import AuthProvider from './AuthProvider.jsx'
import PrivateRoute from "./PrivateRoute.jsx";
import PublicRoute from "./PublicRoute.jsx";

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Header />
        <Routes>
          <Route path="/" element={<Main />} />
          <Route path='/register' element={<PublicRoute><Register /></PublicRoute>} />
          <Route path='/login' element={<PublicRoute><Login /></PublicRoute>} />
          <Route path='/dashboard' element={<PrivateRoute><Dashboard /></PrivateRoute>} />
        </Routes>
        <Footer />
      </BrowserRouter>
    </AuthProvider>
  )
}

export default App
