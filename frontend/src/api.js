import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('zozoAuthToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const getLocations = async (includeStatus = false) => {
  const params = includeStatus ? { include_status: true } : {};
  const response = await api.get('/api/locations', { params });
  return response.data;
};

export const getMenu = async (locationId) => {
  const response = await api.get(`/api/menu?location_id=${locationId}`);
  return response.data;
};

export const createOrder = async (orderData) => {
  const response = await api.post('/api/orders', orderData);
  return response.data;
};

export const login = async (email, password) => {
  const response = await api.post('/api/auth/login', { email, password });
  return response.data;
};

export const getAdminOrders = async (params = {}) => {
  const response = await api.get('/api/admin/orders', { params });
  return response.data;
};

export const updateOrderStatus = async (orderId, status) => {
  const response = await api.patch(`/api/admin/orders/${orderId}/status`, { status });
  return response.data;
};

export const getDashboardStats = async (locationId) => {
  const params = locationId ? { location_id: locationId } : {};
  const response = await api.get('/api/admin/stats', { params });
  return response.data;
};

export const getAdminMenuItems = async () => {
  const response = await api.get('/api/admin/menu-items');
  return response.data;
};

export const updateMenuItem = async (itemId, data) => {
  const response = await api.patch(`/api/admin/menu-items/${itemId}`, data);
  return response.data;
};

// Deals
export const getActiveDeals = async (locationId) => {
  const params = locationId ? { location_id: locationId } : {};
  const response = await api.get('/api/deals', { params });
  return response.data;
};

export const getAdminDeals = async () => {
  const response = await api.get('/api/admin/deals');
  return response.data;
};

export const createDeal = async (dealData) => {
  const response = await api.post('/api/admin/deals', dealData);
  return response.data;
};

export const updateDeal = async (dealId, data) => {
  const response = await api.patch(`/api/admin/deals/${dealId}`, data);
  return response.data;
};

export const deleteDeal = async (dealId) => {
  const response = await api.delete(`/api/admin/deals/${dealId}`);
  return response.data;
};

// Order History
export const getOrderHistory = async (email, phone) => {
  const params = {};
  if (email) params.customer_email = email;
  if (phone) params.customer_phone = phone;
  const response = await api.get('/api/orders/history', { params });
  return response.data;
};

export default api;
