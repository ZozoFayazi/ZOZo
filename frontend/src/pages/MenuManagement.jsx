import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getAdminMenuItems } from '../api';
import { toast } from 'sonner';
import { Upload, Image, ArrowLeft } from 'lucide-react';
import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

// Helper function to build full image URL
const getImageUrl = (imageUrl) => {
  if (!imageUrl) return null;
  if (imageUrl.startsWith('http://') || imageUrl.startsWith('https://')) {
    return imageUrl;
  }
  // Convert /uploads/... to /api/uploads/... for Kubernetes Ingress routing
  if (imageUrl.startsWith('/uploads/')) {
    return `${API_URL}/api${imageUrl}`;
  }
  return `${API_URL}${imageUrl}`;
};

function MenuManagement() {
  const navigate = useNavigate();
  const [menuItems, setMenuItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploadingItems, setUploadingItems] = useState({});

  useEffect(() => {
    const token = localStorage.getItem('zozoAuthToken');
    if (!token) {
      navigate('/admin');
      return;
    }
    loadMenuItems();
  }, [navigate]);

  const loadMenuItems = async () => {
    setLoading(true);
    try {
      const data = await getAdminMenuItems();
      setMenuItems(data);
    } catch (error) {
      console.error('Error loading menu items:', error);
      toast.error('Fehler beim Laden der Menü-Items');
    } finally {
      setLoading(false);
    }
  };

  const handleImageUpload = async (itemId, file) => {
    if (!file) return;

    if (!file.type.startsWith('image/')) {
      toast.error('Bitte nur Bilddateien hochladen');
      return;
    }

    if (file.size > 5 * 1024 * 1024) {
      toast.error('Datei zu groß! Maximum 5MB');
      return;
    }

    setUploadingItems(prev => ({ ...prev, [itemId]: true }));

    try {
      const formData = new FormData();
      formData.append('file', file);

      const token = localStorage.getItem('zozoAuthToken');
      const response = await axios.post(
        `${API_URL}/api/admin/menu-items/${itemId}/upload-image`,
        formData,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'multipart/form-data'
          }
        }
      );

      if (response.data.success) {
        toast.success('Bild erfolgreich hochgeladen!');
        setMenuItems(prev => prev.map(item => 
          item.id === itemId 
            ? { ...item, image_url: response.data.image_url }
            : item
        ));
      }
    } catch (error) {
      console.error('Upload error:', error);
      toast.error(error.response?.data?.detail || 'Fehler beim Hochladen');
    } finally {
      setUploadingItems(prev => ({ ...prev, [itemId]: false }));
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4" />
          <p className="text-muted-foreground">Lade Menü...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background py-8">
      <div className="container-custom">
        <div className="flex items-center gap-4 mb-8">
          <button
            onClick={() => navigate('/admin/dashboard')}
            className="btn-secondary flex items-center gap-2"
          >
            <ArrowLeft className="h-4 w-4" />
            Zurück
          </button>
          <div>
            <h1 className="heading-2">Menü-Verwaltung</h1>
            <p className="text-muted-foreground">Produktbilder hochladen und verwalten</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {menuItems.map(item => (
            <div
              key={item.id}
              className="bg-card border border-border rounded-xl p-6 space-y-4"
            >
              <div className="aspect-video rounded-lg overflow-hidden bg-accent flex items-center justify-center">
                {item.image_url ? (
                  <img
                    src={`${API_URL}${item.image_url}`}
                    alt={item.name}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="text-center text-muted-foreground">
                    <Image className="h-12 w-12 mx-auto mb-2 opacity-50" />
                    <p className="text-sm">Kein Bild</p>
                  </div>
                )}
              </div>

              <div>
                <h3 className="font-semibold text-lg">{item.name}</h3>
                {item.description && (
                  <p className="text-sm text-muted-foreground line-clamp-2 mt-1">
                    {item.description}
                  </p>
                )}
                <div className="flex items-center gap-2 mt-2">
                  {item.price_medium && (
                    <span className="text-xs text-primary font-semibold">
                      M: €{item.price_medium.toFixed(2)}
                    </span>
                  )}
                  {item.price_large && (
                    <span className="text-xs text-primary font-semibold">
                      L: €{item.price_large.toFixed(2)}
                    </span>
                  )}
                  {item.price_normal && !item.price_medium && !item.price_large && (
                    <span className="text-xs text-primary font-semibold">
                      €{item.price_normal.toFixed(2)}
                    </span>
                  )}
                </div>
              </div>

              <label
                className={`btn-primary w-full flex items-center justify-center gap-2 cursor-pointer ${
                  uploadingItems[item.id] ? 'opacity-50 cursor-not-allowed' : ''
                }`}
              >
                <input
                  type="file"
                  accept="image/*"
                  className="hidden"
                  onChange={(e) => {
                    const file = e.target.files?.[0];
                    if (file) {
                      handleImageUpload(item.id, file);
                    }
                  }}
                  disabled={uploadingItems[item.id]}
                />
                {uploadingItems[item.id] ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />
                    Uploading...
                  </>
                ) : (
                  <>
                    <Upload className="h-4 w-4" />
                    {item.image_url ? 'Bild ersetzen' : 'Bild hochladen'}
                  </>
                )}
              </label>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default MenuManagement;
