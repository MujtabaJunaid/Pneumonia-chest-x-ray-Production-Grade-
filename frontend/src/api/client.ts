/**
 * Axios API Ú©Ù„Ø§Ø¦Ù†Ù¹
 * API Client for Backend Communication
 */

import axios, { AxiosInstance, AxiosError } from 'axios';

// FastAPI Ø¨ÛŒÚ© Ø§ÛŒÙ†Úˆ Ú©Ø§ URL
const API_BASE_URL = 'http://localhost:8000';

// API Ø¬ÙˆØ§Ø¨ Ú©ÛŒ Ø´Ú©Ù„
export interface PredictionResponse {
  class_index: number;           // 0: Normal, 1: Pneumonia
  confidence_score: number;       // 0-100
  inference_time_ms: number;     // Milliseconds
  status_message: string;         // Urdu status
  patient_id: number;
  prediction_id: number;
}

// Ø®Ø±Ø§Ø¨ÛŒ Ú©ÛŒ Ø´Ú©Ù„
export interface ApiError {
  message: string;
  status_code?: number;
  details?: string;
}

// Axios Ù…Ø«Ø§Ù„ Ø¨Ù†Ø§Ø¦ÛŒÚº
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 Ø³ÛŒÚ©Ù†Úˆ
  headers: {
    'Content-Type': 'application/json',
  },
});

// ÛØ± Ø¯Ø±Ø®ÙˆØ§Ø³Øª Ø³Û’ Ù¾ÛÙ„Û’ interceptor
apiClient.interceptors.request.use(
  (config) => {
    console.log(`ðŸ”„ API Ø¯Ø±Ø®ÙˆØ§Ø³Øª: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('âŒ Ø¯Ø±Ø®ÙˆØ§Ø³Øª Ù…ÛŒÚº Ø®Ø±Ø§Ø¨ÛŒ:', error);
    return Promise.reject(error);
  }
);

// ÛØ± Ø¬ÙˆØ§Ø¨ Ú©Û’ Ø¨Ø¹Ø¯ interceptor
apiClient.interceptors.response.use(
  (response) => {
    console.log(`âœ… Ø¬ÙˆØ§Ø¨ Ù…ÙˆØµÙˆÙ„: ${response.status}`, response.data);
    return response;
  },
  (error: AxiosError) => {
    console.error('âŒ Ø¬ÙˆØ§Ø¨ Ù…ÛŒÚº Ø®Ø±Ø§Ø¨ÛŒ:', error.response?.status, error.message);
    return Promise.reject(error);
  }
);

/**
 * ØµØ­Øª Ú©ÛŒ Ø¬Ø§Ù†Ú† - Ø¨ÛŒÚ© Ø§ÛŒÙ†Úˆ Ø³Û’ Ø±Ø§Ø¨Ø·Û Ú©ÛŒ ØªØµØ¯ÛŒÙ‚
 */
export const checkHealth = async (): Promise<boolean> => {
  try {
    console.log('ðŸ” ØµØ­Øª Ú©ÛŒ Ø¬Ø§Ù†Ú† Ú©ÛŒ Ø¬Ø§ Ø±ÛÛŒ ÛÛ’...');
    const response = await apiClient.get('/health');
    console.log('âœ“ ØµØ­Øª Ú©ÛŒ Ø¬Ø§Ù†Ú†: Ø¨ÛŒÚ© Ø§ÛŒÙ†Úˆ Ø¯Ø³ØªÛŒØ§Ø¨ ÛÛ’');
    return response.status === 200;
  } catch (error) {
    console.error('âŒ Ø¨ÛŒÚ© Ø§ÛŒÙ†Úˆ Ø³Û’ Ø±Ø§Ø¨Ø·Û Ù…ÛŒÚº Ù†Ø§Ú©Ø§Ù…ÛŒ:', error);
    return false;
  }
};

/**
 * X-Ray Ú©Û’ Ù„ÛŒÛ’ ØªÙ†Ø¨ÛØ§Øª Ù„ÛŒÚº
 * Upload X-Ray and Get Predictions
 *
 * @param patientId - Ù…Ø±ÛŒØ¶ Ú©ÛŒ ID
 * @param file - X-Ray ÙØ§Ø¦Ù„ (PNG, JPG, DICOM)
 * @returns Prediction Ù†ØªØ§Ø¦Ø¬
 */
export const uploadPrediction = async (
  patientId: number,
  file: File
): Promise<PredictionResponse> => {
  try {
    console.log(`ðŸ“¤ Ù¾ÛŒØ´Ù†Ú¯ÙˆØ¦ÛŒ Ø§Ù¾ Ù„ÙˆÚˆ Ú©ÛŒ Ø¬Ø§ Ø±ÛÛŒ ÛÛ’: Ù…Ø±ÛŒØ¶ ID=${patientId}, ÙØ§Ø¦Ù„=${file.name}`);

    // FormData Ø¨Ù†Ø§Ø¦ÛŒÚº (multipart/form-data Ú©Û’ Ù„ÛŒÛ’)
    const formData = new FormData();
    formData.append('file', file);

    const response = await apiClient.post<PredictionResponse>(
      `/api/v1/predictions/predict-with-patient?patient_id=${patientId}`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );

    console.log('âœ… Ù¾ÛŒØ´Ù†Ú¯ÙˆØ¦ÛŒ Ú©Ø§Ù…ÛŒØ§Ø¨:', response.data);
    return response.data;
  } catch (error: unknown) {
    const axiosError = error as AxiosError;
    const errorMessage =
      axiosError.response?.data instanceof Object &&
      'detail' in (axiosError.response?.data as Record<string, unknown>)
        ? (axiosError.response?.data as Record<string, unknown>).detail
        : axiosError.message;

    console.error('âŒ Ù¾ÛŒØ´Ù†Ú¯ÙˆØ¦ÛŒ Ù…ÛŒÚº Ø®Ø±Ø§Ø¨ÛŒ:', errorMessage);
    throw {
      message: 'Ù¾ÛŒØ´Ù†Ú¯ÙˆØ¦ÛŒ Ù†Ø§Ú©Ø§Ù… ÛÙˆ Ú¯Ø¦ÛŒ',
      status_code: axiosError.response?.status,
      details: String(errorMessage),
    } as ApiError;
  }
};

/**
 * Ù…Ø±ÛŒØ¶ Ù…Ø¹Ù„ÙˆÙ…Ø§Øª Ø­Ø§ØµÙ„ Ú©Ø±ÛŒÚº
 */
export const getPatient = async (patientId: number) => {
  try {
    const response = await apiClient.get(`/api/v1/patients/${patientId}`);
    console.log(`âœ… Ù…Ø±ÛŒØ¶ Ù…Ø¹Ù„ÙˆÙ…Ø§Øª Ø­Ø§ØµÙ„: ID=${patientId}`);
    return response.data;
  } catch (error: unknown) {
    const axiosError = error as AxiosError;
    console.error(`âŒ Ù…Ø±ÛŒØ¶ Ù…Ø¹Ù„ÙˆÙ…Ø§Øª Ø­Ø§ØµÙ„ Ù…ÛŒÚº Ø®Ø±Ø§Ø¨ÛŒ: ${axiosError.message}`);
    throw {
      message: 'Ù…Ø±ÛŒØ¶ Ù…Ø¹Ù„ÙˆÙ…Ø§Øª Ø­Ø§ØµÙ„ Ù†ÛÛŒÚº ÛÙˆ Ø³Ú©ÛŒ',
      status_code: axiosError.response?.status,
      details: String(axiosError.message),
    } as ApiError;
  }
};

/**
 * Ù†ÛŒØ§ Ù…Ø±ÛŒØ¶ Ø¨Ù†Ø§Ø¦ÛŒÚº
 */
export const createPatient = async (patientData: {
  name: string;
  age: number;
  gender: string;
  contact_info?: string;
}) => {
  try {
    const response = await apiClient.post('/api/v1/patients/', patientData);
    console.log('âœ… Ù†ÛŒØ§ Ù…Ø±ÛŒØ¶ Ø¨Ù†Ø§ÛŒØ§ Ú¯ÛŒØ§:', response.data);
    return response.data;
  } catch (error: unknown) {
    const axiosError = error as AxiosError;
    console.error('âŒ Ù…Ø±ÛŒØ¶ Ø¨Ù†Ø§Ù†Û’ Ù…ÛŒÚº Ø®Ø±Ø§Ø¨ÛŒ:', axiosError.message);
    throw {
      message: 'Ù…Ø±ÛŒØ¶ Ø¨Ù†Ø§Ù†Û’ Ù…ÛŒÚº Ù†Ø§Ú©Ø§Ù…',
      status_code: axiosError.response?.status,
      details: String(axiosError.message),
    } as ApiError;
  }
};

export default apiClient;
