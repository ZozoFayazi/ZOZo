import React, { createContext, useContext, useState, useEffect } from 'react';

const AdminAuthContext = createContext(null);

export const useAdminAuth = () => {
  const context = useContext(AdminAuthContext);
  if (!context) {
    throw new Error('useAdminAuth must be used within AdminAuthProvider');
  }
  return context;
};

export const AdminAuthProvider = ({ children }) => {
  const [admin, setAdmin] = useState(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState(null);

  // Load admin from sessionStorage on mount
  useEffect(() => {
    const storedAdmin = sessionStorage.getItem('admin');
    const storedToken = sessionStorage.getItem('adminToken');
    
    if (storedAdmin && storedToken) {
      try {
        setAdmin(JSON.parse(storedAdmin));
        setToken(storedToken);
      } catch (error) {
        console.error('Failed to parse stored admin data:', error);
        sessionStorage.removeItem('admin');
        sessionStorage.removeItem('adminToken');
      }
    }
    setLoading(false);
  }, []);

  const login = async (email, password) => {
    const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
    const response = await fetch(`${backendUrl}/api/admin/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Login failed');
    }

    const data = await response.json();
    
    // Check if 2FA is required - return early with require_2fa flag
    if (data.require_2fa) {
      return {
        require_2fa: true,
        temp_token: data.temp_token,
        message: data.message
      };
    }
    
    // Normal login - store in state and sessionStorage
    setAdmin(data.admin);
    setToken(data.access_token);
    sessionStorage.setItem('admin', JSON.stringify(data.admin));
    sessionStorage.setItem('adminToken', data.access_token);
    
    return data;
  };

  const logout = () => {
    setAdmin(null);
    setToken(null);
    sessionStorage.removeItem('admin');
    sessionStorage.removeItem('adminToken');
  };

  const hasPermission = (permission) => {
    if (!admin || !admin.permissions) return false;
    return admin.permissions.includes('*') || admin.permissions.includes(permission);
  };

  const canAccessBranch = (branchSlug) => {
    if (!admin) return false;
    // Super admin (empty branch_ids) can access all branches
    if (!admin.branch_ids || admin.branch_ids.length === 0) return true;
    return admin.branch_ids.includes(branchSlug);
  };

  const isSuperAdmin = () => {
    return admin?.role === 'super_admin';
  };

  const mustChangePassword = () => {
    return admin?.must_change_password === true;
  };

  const updateAdminData = (updates) => {
    const updated = { ...admin, ...updates };
    setAdmin(updated);
    sessionStorage.setItem('admin', JSON.stringify(updated));
  };

  const value = {
    admin,
    token,
    loading,
    login,
    logout,
    hasPermission,
    canAccessBranch,
    isSuperAdmin,
    mustChangePassword,
    updateAdminData,
    isAuthenticated: !!admin
  };

  return (
    <AdminAuthContext.Provider value={value}>
      {children}
    </AdminAuthContext.Provider>
  );
};
