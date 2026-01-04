import React, { useState, useEffect } from 'react';
import axiosInstance from '../../../axiosInstance';

const TrainingStatus = ({ taskId, ticker, onComplete }) => {
  const [status, setStatus] = useState('pending');
  const [progress, setProgress] = useState(0);
  const [message, setMessage] = useState('Initializing...');
  const [currentEpoch, setCurrentEpoch] = useState(0);
  const [totalEpochs, setTotalEpochs] = useState(0);
  const [elapsedTime, setElapsedTime] = useState(null);
  const [startTime] = useState(Date.now());
  const [modelSummary, setModelSummary] = useState(null);
  const [showSummaryModal, setShowSummaryModal] = useState(false);

  useEffect(() => {
    if (!taskId) return;

    const checkStatus = async () => {
      try {
        const response = await axiosInstance.get(`/task-status/${taskId}/`);
        const data = response.data;
        
        setStatus(data.status);
        
        if (data.status === 'in_progress' || data.status === 'pending') {
          if (data.progress !== undefined) {
            setProgress(data.progress);
          }
          if (data.message) {
            setMessage(data.message);
          }
          if (data.current_epoch) {
            setCurrentEpoch(data.current_epoch);
          }
          if (data.total_epochs) {
            setTotalEpochs(data.total_epochs);
          }
        } else if (data.status === 'completed') {
          setProgress(100);
          const elapsed = data.result?.elapsed_time_formatted || 
                         `${((Date.now() - startTime) / 1000).toFixed(2)}s`;
          setElapsedTime(elapsed);
          setMessage(`Training completed successfully in ${elapsed}`);
          if (data.result?.model_summary) {
            setModelSummary(data.result.model_summary);
            setShowSummaryModal(true);
          }
          if (onComplete) onComplete(data.result);
          return 'completed'; // Signal to stop polling
        } else if (data.status === 'failed') {
          setMessage(`Training failed: ${data.error}`);
          if (onComplete) onComplete({ error: data.error });
          return 'failed'; // Signal to stop polling
        }
      } catch (error) {
        console.error('Error checking task status:', error);
        setMessage('Error checking training status');
        if (onComplete) onComplete({ error: 'Connection error' });
        return 'error'; // Signal to stop polling
      }
    };

    // Check immediately
    checkStatus();
    
    // Then check every 2 seconds, but stop if completed/failed
    const interval = setInterval(async () => {
      const result = await checkStatus();
      if (result === 'completed' || result === 'failed' || result === 'error') {
        clearInterval(interval);
      }
    }, 2000);
    
    return () => clearInterval(interval);
  }, [taskId, startTime, onComplete]);

  const getStatusColor = () => {
    switch (status) {
      case 'completed': return 'text-green-600';
      case 'failed': return 'text-red-600';
      case 'in_progress': return 'text-blue-600';
      default: return 'text-gray-600';
    }
  };

  const getProgressBarColor = () => {
    switch (status) {
      case 'completed': return 'bg-green-500';
      case 'failed': return 'bg-red-500';
      default: return 'bg-blue-500';
    }
  };

  return (
    <div className="card bg-dark text-white border-info">
      <div className="card-header bg-info">
        <h6 className="mb-0">🤖 Training ML Model for {ticker}</h6>
      </div>
      <div className="card-body">
        {/* Task ID */}
        {/*<div className="mb-3">*/}
        {/*  <small className="text-white">Task ID:</small>*/}
        {/*  <div className="font-monospace bg-secondary p-2 rounded mt-1">*/}
        {/*    <small>{taskId}</small>*/}
        {/*  </div>*/}
        {/*</div>*/}
        

        
        {/* Main Progress Bar */}
        <div className="mb-4">
          <div className="d-flex justify-content-between mb-2">
            <span className="fw-bold">Overall Progress</span>
            {/*<span className="badge bg-info">{progress}%</span>*/}
          </div>
          <div className="progress" style={{height: '20px'}}>
            <div 
              className={`progress-bar progress-bar-striped ${
                status === 'in_progress' ? 'progress-bar-animated bg-info' :
                status === 'completed' ? 'bg-success' :
                status === 'failed' ? 'bg-danger' : 'bg-secondary'
              }`}
              style={{ width: `${progress}%`, transition: 'width 0.5s ease' }}
            >
              {progress}%
            </div>
          </div>
        </div>
        
        {/*/!* Epoch Progress *!/*/}
        {/*/!* Removed epoch progress section *!/*/}
        
        {/*/!* Status Message *!/*/}
        {/*<div className="alert alert-info mb-3">*/}
        {/*  <i className="fas fa-info-circle me-2"></i>*/}
        {/*  {message}*/}
        {/*</div>*/}
        
        {/* Completion Time */}
        {elapsedTime && (
          <div className="alert alert-success">
            <i className="fas fa-check-circle me-2"></i>
            <strong>Completed in:</strong> {elapsedTime}
          </div>
        )}
        
        {/* Loading Animation */}
        {(status === 'pending' || status === 'in_progress') && (
          <div className="text-center mt-3">
            <div className="spinner-border text-info me-2" role="status">
              <span className="visually-hidden">Loading...</span>
            </div>
            <span className="text-info ">Neural Network Training...</span>
            <div className="mt-2">
              <button 
                className="btn btn-sm btn-outline-warning"
                onClick={() => {
                  if (onComplete) onComplete({ cancelled: true });
                }}
              >
                Stop Monitoring
              </button>
            </div>
          </div>
        )}
        
      </div>
      
      {/* Model Summary Modal */}
      {showSummaryModal && (
        <div className="position-fixed top-0 start-0 w-100 h-100" style={{backgroundColor: 'rgba(0,0,0,0.8)', zIndex: 9999}}>
          <div className="d-flex justify-content-center align-items-center h-100">
            <div className="bg-dark text-white border border-info rounded p-4" style={{maxWidth: '90%', maxHeight: '90%', overflow: 'auto'}}>
              <div className="d-flex justify-content-between align-items-center mb-3">
                <h5 className="text-info mb-0">🧠 Model Architecture Summary</h5>
                <button 
                  type="button" 
                  className="btn btn-sm btn-outline-light"
                  onClick={() => setShowSummaryModal(false)}
                >
                  ✕
                </button>
              </div>
              
              <div className="row">
                <div className="col-md-8">
                  <h6 className="text-info mb-3">Model Architecture</h6>
                  <pre className="bg-secondary text-white p-3 rounded" style={{fontSize: '11px', overflow: 'auto', whiteSpace: 'pre', maxHeight: '400px'}}>
                    {modelSummary?.raw_summary}
                  </pre>
                </div>
                <div className="col-md-4">
                  <h6 className="text-info mb-3">Model Statistics</h6>
                  <div className="bg-secondary p-3 rounded">
                    <div className="mb-2">
                      <strong>Total Parameters:</strong><br/>
                      <span className="text-warning">{modelSummary?.total_params?.toLocaleString()}</span>
                    </div>
                    <div className="mb-2">
                      <strong>Trainable Parameters:</strong><br/>
                      <span className="text-success">{modelSummary?.trainable_params?.toLocaleString()}</span>
                    </div>
                    <div className="mb-2">
                      <strong>Model Size:</strong><br/>
                      <span className="text-info">{((modelSummary?.total_params || 0) * 4 / 1024 / 1024).toFixed(2)} MB</span>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="text-center mt-3">
                <button 
                  type="button" 
                  className="btn btn-info"
                  onClick={() => setShowSummaryModal(false)}
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TrainingStatus;