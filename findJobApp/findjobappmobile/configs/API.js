import axios from "axios";
const BASE_URL = 'http://192.168.1.107:8000/';
export const endpoints = {
  // ==== AUTH ====
  'login': '/o/token/',
  'register-employer': '/users/register-employer/',
  'register-candidate': '/users/register-candidate/',
  'current_user': '/users/current-user/',
  'send-email': '/users/send-email/',

  // ==== JOB ====
  'jobs': '/jobs/',
  'job-details': (jobId) => `/jobs/${jobId}/`,
  'job-map': (jobId) => `/jobs/${jobId}/map-data/`,
  'job-employer': (jobId) => `/jobs/${jobId}/employer/`,
  'job-search': (query) => `/jobs/?q=${query}`,

  // ==== EMPLOYER ====
  'employers': '/employers/',
  'current-employer': '/employers/current-employer/',
  'employer-details': (id) => `/employers/${id}/`,
  'employer-map': (id) => `/employers/${id}/map-data/`,

  // ==== CANDIDATE ====
  'candidates': '/candidate/',
  'current-candidate': '/candidate/current-candidate/',
  'candidate-details': (id) => `/candidate/${id}/`, 

  // ==== APPLY ====
  'apply': '/apply/',
  'apply-details': (id) => `/apply/${id}/`,
  'apply-job': (jobId) => `/apply/job/${jobId}/`,
  'apply-approve': (id) => `/apply/${id}/approve/`,
  'apply-reject': (id) => `/apply/${id}/reject/`,

  // ==== CATEGORY ====
  'categories': '/categories/',
  'category-details': (id) => `/categories/${id}/`, 

  // ==== NOTIFICATION ====
  'notifications': '/notifications/',
  'notification-details': (id) => `/notifications/${id}/`,

  // ==== VERIFICATION ====
  'verifications': '/verifications/',
  'verification-details': (id) => `/verifications/${id}/`, 

  // === Follow ===
  'follow': '/follow/',
  'unfollow': '/follow/unfollow/',
  'check-following': '/follow/',
  // ==== STATS ====
  'stats': '/stats/summary/',
};

export const authApis = (token) => {
  return axios.create({
    'baseURL': BASE_URL,
    'headers': {
      'Authorization': `Bearer ${token}`
    }
  });
};


export default axios.create({
  baseURL: BASE_URL
});
