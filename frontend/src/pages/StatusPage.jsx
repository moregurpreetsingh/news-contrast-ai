import { useState, useEffect } from 'react';
import Header from '../components/Header';
import apiService from '../services/api';
import { ToastContainer, useToasts } from '../components/Toast';

export default function StatusPage() {
  const [modelStatus, setModelStatus] = useState(null);
  const [datasetInfo, setDatasetInfo] = useState(null);
  const [trainingDataStats, setTrainingDataStats] = useState(null);
  const [systemHealth, setSystemHealth] = useState(null);
  const [loading, setLoading] = useState(true);
  const [retraining, setRetraining] = useState(false);
  const [testingPipeline, setTestingPipeline] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [retrainResult, setRetrainResult] = useState(null);
  
  const { toasts, removeToast, showSuccess, showError, showWarning, showInfo } = useToasts();

  useEffect(() => {
    loadSystemInfo();
  }, []);

  const loadSystemInfo = async () => {
    setLoading(true);
    try {
      const [modelData, datasetData, trainingData, healthData] = await Promise.allSettled([
        apiService.getModelStatus(),
        apiService.getDatasetInfo(),
        apiService.getTrainingDataStats(),
        apiService.healthCheck()
      ]);

      if (modelData.status === 'fulfilled') {
        setModelStatus(modelData.value);
      }
      if (datasetData.status === 'fulfilled') {
        setDatasetInfo(datasetData.value);
      }
      if (trainingData.status === 'fulfilled') {
        setTrainingDataStats(trainingData.value);
      }
      if (healthData.status === 'fulfilled') {
        setSystemHealth(healthData.value);
      }
    } catch (error) {
      console.error('Failed to load system info:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRetrain = async () => {
    setRetraining(true);
    setRetrainResult(null);
    showInfo('Starting model retraining... This may take several minutes.');
    
    try {
      const result = await apiService.retrainModel();
      setRetrainResult({ success: true, data: result });
      showSuccess(
        `Model retrained successfully! Accuracy: ${(result.training_metrics?.eval_accuracy * 100 || 0).toFixed(1)}%`,
        6000
      );
      // Reload model status after successful retraining
      setTimeout(loadSystemInfo, 2000);
    } catch (error) {
      setRetrainResult({ success: false, error: error.message });
      showError(`Model retraining failed: ${error.message}`, 6000);
    } finally {
      setRetraining(false);
    }
  };

  const testPipeline = async () => {
    setTestingPipeline(true);
    showInfo('Testing pipeline functionality...');
    
    try {
      const result = await apiService.testPipeline();
      if (result.pipeline_status === 'operational') {
        showSuccess('Pipeline test completed successfully! All components are working.');
      } else {
        showWarning(`Pipeline test completed with status: ${result.pipeline_status}`);
      }
    } catch (error) {
      showError(`Pipeline test failed: ${error.message}`, 6000);
    } finally {
      setTestingPipeline(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    showInfo('Refreshing system status...');
    
    try {
      await loadSystemInfo();
      showSuccess('System status refreshed successfully!');
    } catch (error) {
      showError('Failed to refresh system status');
    } finally {
      setRefreshing(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-background text-foreground px-4">
        <Header />
        <div className="flex items-center gap-2 mt-8">
          <div className="w-6 h-6 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
          <span className="text-lg">Loading system status...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background text-foreground px-4 py-8">
      <Header />
      
      <div className="max-w-6xl mx-auto mt-8">
        <h1 className="text-3xl font-bold mb-8 text-center">System Status & Administration</h1>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* System Health */}
          {systemHealth && (
            <div className="py-20 px-4 bg-card rounded-lg shadow-md p-6">
              <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
                🏥 System Health
              </h2>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="font-medium">API Status:</span>
                  <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm">
                    {systemHealth.status || 'operational'}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="font-medium">Version:</span>
                  <span className="text-white">{systemHealth.version}</span>
                </div>
                {systemHealth.features && (
                  <div>
                    <span className="font-medium">Features:</span>
                    <ul className="mt-2 space-y-1">
                      {systemHealth.features.map((feature, index) => (
                        <li key={index} className="text-sm text-white-600 flex items-center gap-2">
                          <span className="text-green-500">✓</span>
                          {feature}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Model Status */}
          {modelStatus && (
            <div className="py-20 px-4 bg-card rounded-lg shadow-md p-6">
              <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
                🤖 Model Status
              </h2>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="font-medium">Model Available:</span>
                  <span className={`px-3 py-1 rounded-full text-sm ${
                    modelStatus.model_available 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-red-100 text-red-800'
                  }`}>
                    {modelStatus.model_available ? 'Yes' : 'No'}
                  </span>
                </div>
                
                {modelStatus.model_info && (
                  <>
                    <div className="flex items-center justify-between">
                      <span className="font-medium">Model Type:</span>
                      <span className="text-white-700">{modelStatus.model_info.model_name}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="font-medium">Training Samples:</span>
                      <span className="text-white">{modelStatus.model_info.train_samples}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="font-medium">Last Trained:</span>
                      <span className="text-white">
                        {new Date(modelStatus.model_info.trained_at).toLocaleDateString()}
                      </span>
                    </div>
                    {/* {modelStatus.model_info.final_metrics && (
                      <div className="mt-4">
                        <span className="font-medium">Performance Metrics:</span>
                        <div className="mt-2 grid grid-cols-2 gap-2 text-sm">
                          <div className="bg-gray-50 p-2 rounded">
                            <span className="font-medium">Accuracy:</span>
                            <span className="ml-2">{(modelStatus.model_info.final_metrics.eval_accuracy * 100).toFixed(1)}%</span>
                          </div>
                          <div className="bg-gray-50 p-2 rounded">
                            <span className="font-medium">F1 Score:</span>
                            <span className="ml-2">{(modelStatus.model_info.final_metrics.eval_f1 * 100).toFixed(1)}%</span>
                          </div>
                        </div>
                      </div>
                    )} */}
                  </>
                )}
                
                {modelStatus.message && !modelStatus.model_info && (
                  <div className="text-white-600 text-sm">{modelStatus.message}</div>
                )}
              </div>
            </div>
          )}

          {/* Live Training Data Statistics */}
          {trainingDataStats && (
            <div className="py-20 px-4 bg-card rounded-lg shadow-md p-6">
              <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
                🔥 Live Analysis Data
                <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full ml-2">
                  Updates with Analyze clicks
                </span>
              </h2>
              <div className="space-y-4">
                {trainingDataStats.status === 'success' ? (
                  <>
                    <div className="flex items-center justify-between">
                      <span className="font-medium">Total Analysis Results:</span>
                      <span className="text-blue-600 font-bold text-lg">{trainingDataStats.total_entries}</span>
                    </div>
                    
                    <div className="border-t pt-3">
                      <div className="font-medium mb-2">Analysis Distribution</div>
                      <div className="grid grid-cols-3 gap-2 text-sm">
                        <div className="bg-blue-50 p-3 rounded text-center">
                          <div className="font-bold text-blue-800 text-lg">{trainingDataStats.total_entries}</div>
                          <div className="text-gray-600">Total</div>
                        </div>
                        <div className="bg-green-50 p-3 rounded text-center">
                          <div className="font-bold text-green-800 text-lg">{trainingDataStats.label_distribution.REAL}</div>
                          <div className="text-gray-600">Real News</div>
                        </div>
                        <div className="bg-red-50 p-3 rounded text-center">
                          <div className="font-bold text-red-800 text-lg">{trainingDataStats.label_distribution.FAKE}</div>
                          <div className="text-gray-600">Fake News</div>
                        </div>
                      </div>
                    </div>

                    {trainingDataStats.recent_entries && trainingDataStats.recent_entries.length > 0 && (
                      <div className="border-t pt-3">
                        <div className="font-medium mb-2">Recent Analysis</div>
                        <style>
                          {`
                            .custom-scrollbar::-webkit-scrollbar {
                              width: 6px;
                            }
                            .custom-scrollbar::-webkit-scrollbar-thumb {
                              background-color: rgba(156, 163, 175, 0.5); /* gray-400 */
                              border-radius: 3px;
                            }
                            .custom-scrollbar::-webkit-scrollbar-thumb:hover {
                              background-color: rgba(107, 114, 128, 0.7); /* gray-500 */
                            }
                          `}
                        </style>

                        <div className="space-y-3 max-h-48 overflow-y-auto pr-2 custom-scrollbar">
                          {trainingDataStats.recent_entries.slice(-5).reverse().map((entry, index) => (
                            <div
                              key={index}
                              className="text-xs bg-white p-3 rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow"
                            >
                              <div className="flex items-center justify-between mb-2">
                                <span className="font-medium text-gray-700">
                                  {new Date(entry.timestamp).toLocaleString()}
                                </span>
                                <span
                                  className={`px-2 py-0.5 rounded-full text-xs font-semibold ${
                                    entry.label === "REAL"
                                      ? "bg-green-100 text-green-700"
                                      : "bg-red-100 text-red-700"
                                  }`}
                                >
                                  {entry.label}
                                </span>
                              </div>
                              <div className="text-gray-600 text-xs line-clamp-2">
                                {entry.text_preview}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {trainingDataStats.last_modified && (
                      <div className="border-t pt-2 text-xs text-gray-500">
                        Last updated: {new Date(trainingDataStats.last_modified).toLocaleString()}
                      </div>
                    )}
                  </>
                ) : (
                  <div className="text-center py-4">
                    <div className="text-gray-500 mb-2">No analysis data available yet</div>
                    <div className="text-xs text-gray-400">
                      Use the Analyze button on the main page to generate training data
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Actions */}
          <div className="py-20 px-4 bg-card rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              ⚡ Actions
            </h2>
            <div className="space-y-3">
              <button
                onClick={testPipeline}
                disabled={testingPipeline}
                className="w-full px-4 py-2 bg-blue-100 text-blue-800 rounded-lg hover:bg-blue-200 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {testingPipeline ? (
                  <span className="flex items-center justify-center gap-2">
                    <div className="w-4 h-4 border-2 border-blue-800 border-t-transparent rounded-full animate-spin"></div>
                    Testing Pipeline...
                  </span>
                ) : (
                  '🧪 Test Pipeline'
                )}
              </button>
              
              <button
                onClick={handleRetrain}
                disabled={retraining}
                className="w-full px-4 py-2 bg-purple-100 text-purple-800 rounded-lg hover:bg-purple-200 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {retraining ? (
                  <span className="flex items-center justify-center gap-2">
                    <div className="w-4 h-4 border-2 border-purple-800 border-t-transparent rounded-full animate-spin"></div>
                    Retraining Model...
                  </span>
                ) : (
                  '🔄 Retrain Model'
                )}
              </button>
              
              <button
                onClick={handleRefresh}
                disabled={refreshing}
                className="w-full px-4 py-2 bg-gray-100 text-gray-800 rounded-lg hover:bg-gray-200 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {refreshing ? (
                  <span className="flex items-center justify-center gap-2">
                    <div className="w-4 h-4 border-2 border-gray-800 border-t-transparent rounded-full animate-spin"></div>
                    Refreshing...
                  </span>
                ) : (
                  '🔄 Refresh Status'
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
      
      {/* Toast Container */}
      <ToastContainer toasts={toasts} removeToast={removeToast} />
    </div>
  );
}
