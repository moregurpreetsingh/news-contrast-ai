// Enhanced API service for News Contrast AI
const API_BASE_URL = 'http://127.0.0.1:8000';

class ApiService {
  constructor() {
    this.baseURL = API_BASE_URL;
  }

  // Enhanced analysis with support for both text and URL
  async analyzeContent(options) {
    const { text, url, includeExplanations = true } = options;
    
    if (!text && !url) {
      throw new Error('Either text or URL must be provided');
    }

    try {
      const response = await fetch(`${this.baseURL}/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: text || undefined,
          url: url || undefined,
          include_explanations: includeExplanations
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  }

  // Submit user feedback
  async submitFeedback(feedbackData) {
    try {
      const response = await fetch(`${this.baseURL}/feedback`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(feedbackData),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to submit feedback');
      }

      return await response.json();
    } catch (error) {
      console.error('Feedback Error:', error);
      throw error;
    }
  }

  // Test the pipeline
  async testPipeline() {
    try {
      const response = await fetch(`${this.baseURL}/test-pipeline`, {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error('Pipeline test failed');
      }

      return await response.json();
    } catch (error) {
      console.error('Pipeline test error:', error);
      throw error;
    }
  }

  // Get model status
  async getModelStatus() {
    try {
      const response = await fetch(`${this.baseURL}/model/status`);
      
      if (!response.ok) {
        throw new Error('Failed to get model status');
      }

      return await response.json();
    } catch (error) {
      console.error('Model status error:', error);
      throw error;
    }
  }

  // Get dataset information
  async getDatasetInfo() {
    try {
      const response = await fetch(`${this.baseURL}/datasets/info`);
      
      if (!response.ok) {
        throw new Error('Failed to get dataset info');
      }

      return await response.json();
    } catch (error) {
      console.error('Dataset info error:', error);
      throw error;
    }
  }

  // Retrain model
  async retrainModel() {
    try {
      const response = await fetch(`${this.baseURL}/retrain`, {
        method: 'POST',
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Model retraining failed');
      }

      return await response.json();
    } catch (error) {
      console.error('Retrain error:', error);
      throw error;
    }
  }

  // Health check
  async healthCheck() {
    try {
      const response = await fetch(`${this.baseURL}/`);
      
      if (!response.ok) {
        throw new Error('API health check failed');
      }

      return await response.json();
    } catch (error) {
      console.error('Health check error:', error);
      throw error;
    }
  }

  // Get training data statistics
  async getTrainingDataStats() {
    try {
      const response = await fetch(`${this.baseURL}/training-data/stats`);
      
      if (!response.ok) {
        throw new Error('Failed to get training data stats');
      }

      return await response.json();
    } catch (error) {
      console.error('Training data stats error:', error);
      throw error;
    }
  }
}

// Create singleton instance
const apiService = new ApiService();

export default apiService;
