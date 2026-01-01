import {useEffect} from 'react'
import axiosInstance from '../../../axiosInstance.js'


const Dashboard = () => {

    useEffect(()=>{
        const fetchProtectedData = async () =>{
            try{
                const response = await axiosInstance.get('/protected-view/');
                console.log('Seccess: ', response.data)

            }catch(error){
                console.error('Error fetching data:', error)
            }
        }
        fetchProtectedData();
    }, [])

  return (
      <div className='text-light container'>Dashboard</div>
  )
}

export default Dashboard