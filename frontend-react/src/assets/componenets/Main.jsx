import React from 'react'
import Header from './Header'
import Footer from './Footer'
import Button from './Button'

const Main = () => {
  return (
    <>

    <div className="container">
        <div className='p-5 text-center bg-light-dark rounded'>
            <h1 className='text-light'>Stock Prediction App</h1>
            <p className="lead text-light">This is a stock prediction app built with Django, designed to forecast future prices using machine learning. It leverages an LSTM model implemented via Keras and analyzes key technical indicators like the 100-day and 200-day moving averages, which are widely used in trading and investment decisions.</p>
            <Button text="Explore Now" class="btn-info" url="/dashboard" />
        </div>
    </div>


    </>
  )
}

export default Main