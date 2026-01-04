import {useEffect, useState} from 'react'
import axiosInstance from '../../../axiosInstance.js'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faSpinner } from '@fortawesome/free-solid-svg-icons'
import TrainingStatus from './TrainingStatus'

const Training = () => {
    const [ticker, setTicker] = useState('')
    const [error, setError] = useState()
    const [loading, setLoading] = useState(false)
    const [taskId, setTaskId] = useState(null)
    const [showStatus, setShowStatus] = useState(false)
    const [trainedModels, setTrainedModels] = useState([])
    const [modelsLoading, setModelsLoading] = useState(true)

    useEffect(()=>{
        const fetchProtectedData = async () =>{
            try{
                const response = await axiosInstance.get('/protected-view/');
            }catch(error){
                console.error('Error fetching data:', error)
            }
        }
        
        const fetchTrainedModels = async () => {
            setModelsLoading(true);
            try{
                const response = await axiosInstance.get('/trained-models/');
                setTrainedModels(response.data.models || []);
            }catch(error){
                console.error('Error fetching trained models:', error)
            } finally {
                setModelsLoading(false);
            }
        }
        
        // Check for active training task
        const checkActiveTraining = () => {
            const savedTaskId = localStorage.getItem('activeTrainingTaskId')
            const savedTicker = localStorage.getItem('activeTrainingTicker')
            if (savedTaskId && savedTicker) {
                setTaskId(savedTaskId)
                setTicker(savedTicker)
                setShowStatus(true)
                setLoading(true)
            }
        }
        
        fetchProtectedData();
        fetchTrainedModels();
        checkActiveTraining();
    }, [])

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true)
        setError('')
        try{
            const response = await axiosInstance.post('/train/', {
                ticker: ticker
            });
            console.log(response.data);
            
            if(response.data.task_id){
                setTaskId(response.data.task_id)
                setShowStatus(true)
                // Save to localStorage
                localStorage.setItem('activeTrainingTaskId', response.data.task_id)
                localStorage.setItem('activeTrainingTicker', ticker)
                // Keep loading state true during training
            }
            
            if(response.data.error){
                setError(response.data.error)
            }
        }catch(error){
            console.error('There was an error making the API request', error)
            setError('Failed to start training')
            setLoading(false)
        }
        // Don't set loading to false here - wait for training completion
    }

    const handleTrainingComplete = (result) => {
        console.log('Training completed:', result)
        
        setShowStatus(false)
        setTaskId(null)
        setLoading(false)
        // Clear localStorage
        localStorage.removeItem('activeTrainingTaskId')
        localStorage.removeItem('activeTrainingTicker')
        // Refresh the trained models list from backend
        const fetchTrainedModels = async () => {
            try{
                const response = await axiosInstance.get('/trained-models/');
                setTrainedModels(response.data.models || []);
            }catch(error){
                console.error('Error fetching trained models:', error)
            }
        }
        fetchTrainedModels();
    }

  return (
    <div className='container pt-3 pb-3'>
        <div className="row">
            {/* Left side - Training Form */}
            <div className="col-md-4">
                <div className="card bg-light text-white">
                    <div className="card-header">
                        <h4 className="mb-0 text-dark">Train New Model</h4>
                    </div>
                    <div className="card-body">
                        <form onSubmit={handleSubmit}>
                            <div className="mb-3">
                                <label htmlFor="ticker" className="form-label text-dark">Stock Ticker</label>
                                <input 
                                    type="text" 
                                    id="ticker"
                                    className='form-control' 
                                    placeholder='Enter Stock Ticker (e.g., AAPL)'
                                    onChange={(e) => setTicker(e.target.value)} 
                                    required 
                                    disabled={loading}
                                    value={ticker}
                                />
                                {error && <div className='text-danger mt-2'>{error}</div>}
                            </div>
                            {!loading && (
                                <button type='submit' className='btn btn-info w-100'>
                                    Train Model
                                </button>
                            )}
                        </form>
                        
                        {showStatus && (
                            <div className="mt-4">
                                <TrainingStatus 
                                    taskId={taskId}
                                    ticker={ticker}
                                    onComplete={handleTrainingComplete}
                                />
                            </div>
                        )}
                    </div>
                </div>
            </div>
            
            {/* Right side - Trained Models Table */}
            <div className="col-md-8">
                <div className="card bg-light text-white">
                    <div className="card-header">
                        <h4 className="mb-0 text-dark">Available Trained Models</h4>
                        <small className="text-muted">Models ready for prediction</small>
                    </div>
                    <div className="card-body">
                        {modelsLoading ? (
                            <div className="text-center text-muted py-4">
                                <div className="spinner-border text-info me-2" role="status">
                                    <span className="visually-hidden">Loading...</span>
                                </div>
                                <p>Loading trained models...</p>
                            </div>
                        ) : trainedModels.length > 0 ? (
                            <div className="table-responsive">
                                <table className="table table-light table-striped table-hover table-bordered shadow">
                                    <thead className="table-dark">
                                        <tr>
                                            <th>Ticker</th>
                                            <th>Trained</th>
                                            <th>File Size</th>
                                            <th>Status</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {trainedModels.map((model, index) => (
                                            <tr key={index}>
                                                <td><strong className="text-primary">{model.ticker}</strong></td>
                                                <td>{model.trained_at || 'N/A'}</td>
                                                <td>{(model.file_size / 1024 / 1024).toFixed(2)} MB</td>
                                                <td>
                                                    <span className="badge bg-success">Ready</span>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        ) : (
                            <div className="text-center text-muted py-4">
                                <p>No trained models available yet.</p>
                                <p>Train your first model using the form on the left.</p>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    </div>
  )
}

export default Training