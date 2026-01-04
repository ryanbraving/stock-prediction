import {useEffect, useState} from 'react'
import axiosInstance from '../../../axiosInstance.js'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faSpinner } from '@fortawesome/free-solid-svg-icons'

const Training = () => {
    const [ticker, setTicker] = useState('')
    const [error, setError] = useState()
    const [loading, setLoading] = useState(false)

    useEffect(()=>{
        const fetchProtectedData = async () =>{
            try{
                const response = await axiosInstance.get('/protected-view/');
            }catch(error){
                console.error('Error fetching data:', error)
            }
        }
        fetchProtectedData();
    }, [])

    const handleSubmit = async (e) =>{
        e.preventDefault();
        setLoading(true)
        try{
            const response = await axiosInstance.post('/train/', {
                ticker: ticker
            });
            console.log(response.data);
            setError("")
            if(response.data.error){
                setError(response.data.error)
            }
        }catch(error){
            console.error('There was an error making the API request', error)
        }finally{
            setLoading(false);
        }
    }

  return (
    <div className='container'>
        <div className="row">
            <div className="col-md-6 mx-auto">
                <form onSubmit={handleSubmit}>
                    <input type="text" className='form-control' placeholder='Enter Stock Ticker'
                    onChange={(e) => setTicker(e.target.value)} required
                    />
                    <small>{error && <div className='text-danger'>{error}</div>}</small>
                    <button type='submit' className='btn btn-info mt-3' disabled={loading}>
                        {loading ? <span><FontAwesomeIcon icon={faSpinner} spin /> Please wait...</span>: 'Train Model'}
                    </button>
                </form>
            </div>
        </div>
    </div>
  )
}

export default Training