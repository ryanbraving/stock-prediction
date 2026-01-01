import { useState } from 'react'
import './assets/css/style.css'
import Header from "./assets/componenets/Header.jsx";
import Main from "./assets/componenets/Main.jsx";
import Footer from "./assets/componenets/Footer.jsx";
import { BrowserRouter, Routes, Route } from 'react-router'
import Register from "./assets/componenets/Register.jsx";

function App() {
  return (
    <>

        <BrowserRouter>
             <Header/>
          <Routes>
            <Route path="/" element={<Main/>}/>
              <Route path="/register" element={<Register/>}/>
          </Routes>
            <Footer/>
        </BrowserRouter>

    </>
  )
}

export default App
