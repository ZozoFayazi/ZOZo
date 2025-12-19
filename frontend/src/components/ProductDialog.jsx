import React, { useState, useEffect } from 'react';
import { useAdminAuth } from '../contexts/AdminAuthContext';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogFooter } from './ui/dialog';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { toast } from 'sonner';
import { Loader2, Upload, X } from 'lucide-react';

export default function ProductDialog({ open, onClose, product, categories, onSuccess }) {
  const { token } = useAdminAuth();
  const isEdit = !!product;
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  
  const [formData, setFormData] = useState({
    name: '',
    category_id: '',
    description: '',
    price_normal: '',
    price_medium: '',
    price_large: '',
    image_url: ''
  });
  
  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState('');
  
  useEffect(() => {
    if (product) {
      setFormData({
        name: product.name || '',
        category_id: product.category_id || '',
        description: product.description || '',
        price_normal: product.price_normal || '',
        price_medium: product.price_medium || '',
        price_large: product.price_large || '',
        image_url: product.image_url || ''
      });
      setImagePreview(product.image_url || '');
    } else {
      // Reset for create
      setFormData({
        name: '',
        category_id: '',
        description: '',
        price_normal: '',
        price_medium: '',
        price_large: '',
        image_url: ''
      });
      setImagePreview('');
    }
    setImageFile(null);
  }, [product, open]);
  
  const handleImageSelect = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    
    // Validate file type
    if (!file.type.startsWith('image/')) {
      toast.error('Bitte nur Bilddateien auswählen');
      return;
    }
    
    // Validate file size (5MB)
    if (file.size > 5 * 1024 * 1024) {
      toast.error('Bild zu groß! Maximum 5MB');
      return;
    }
    
    setImageFile(file);
    
    // Create preview
    const reader = new FileReader();
    reader.onloadend = () => {
      setImagePreview(reader.result);
    };
    reader.readAsDataURL(file);
  };
  
  const uploadImage = async (productId) => {
    if (!imageFile) return null;
    
    setUploading(true);
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
      const formData = new FormData();
      formData.append('file', imageFile);
      
      const response = await fetch(`${backendUrl}/api/admin/products/${productId}/upload-image`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });
      
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Upload fehlgeschlagen');
      }
      
      const result = await response.json();
      return result.image_url;
    } catch (error) {
      console.error('Image upload error:', error);
      toast.error(error.message || 'Bildupload fehlgeschlagen');
      return null;
    } finally {
      setUploading(false);
    }
  };
  
  const handleSubmit = async () => {
    // Validation
    if (!formData.name || !formData.category_id) {
      toast.error('Bitte Name und Kategorie ausfüllen');
      return;
    }
    
    if (!formData.price_normal && !formData.price_medium) {
      toast.error('Bitte mindestens einen Preis angeben');
      return;
    }
    
    setLoading(true);
    
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
      
      // Prepare payload
      const payload = {
        name: formData.name,
        category_id: formData.category_id,
        description: formData.description || null,
        price_normal: formData.price_normal ? parseFloat(formData.price_normal) : null,
        price_medium: formData.price_medium ? parseFloat(formData.price_medium) : null,
        price_large: formData.price_large ? parseFloat(formData.price_large) : null
      };
      
      const url = isEdit 
        ? `${backendUrl}/api/admin/products/${product.id}`
        : `${backendUrl}/api/admin/products`;
      
      const method = isEdit ? 'PUT' : 'POST';
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(payload)
      });
      
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Fehler beim Speichern');
      }
      
      const result = await response.json();
      
      // Upload image if selected
      if (imageFile) {
        const imageUrl = await uploadImage(result.id);
        if (imageUrl) {
          result.image_url = imageUrl;
        }
      }
      
      toast.success(isEdit ? 'Produkt aktualisiert' : 'Produkt erstellt');
      onSuccess(result);
      onClose();
    } catch (error) {
      console.error('Save product error:', error);
      toast.error(error.message || 'Fehler beim Speichern');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto" data-testid="product-dialog">
        <DialogHeader>
          <DialogTitle>
            {isEdit ? 'Produkt bearbeiten' : 'Neues Produkt erstellen'}
          </DialogTitle>
          <DialogDescription>
            {isEdit ? 'Ändern Sie die Produktdetails' : 'Erstellen Sie ein neues Produkt'}
          </DialogDescription>
        </DialogHeader>
        
        <div className="space-y-4">
          {/* Image Upload */}
          <div className="space-y-2">
            <Label>Produktbild</Label>
            {imagePreview ? (
              <div className="space-y-3">
                <div className="relative">
                  <img
                    src={imagePreview}
                    alt="Preview"
                    className="w-full h-48 object-cover rounded-lg"
                  />
                  <Button
                    type="button"
                    variant="destructive"
                    size="sm"
                    className="absolute top-2 right-2"
                    onClick={() => {
                      setImagePreview('');
                      setImageFile(null);
                      setFormData(prev => ({ ...prev, image_url: '' }));
                    }}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
                {/* Option to change image */}
                <div className="flex items-center gap-2">
                  <Input
                    type="file"
                    accept="image/*"
                    onChange={handleImageSelect}
                    className="text-sm"
                    data-testid="product-image-change"
                  />
                  <span className="text-xs text-muted-foreground">Neues Bild wählen</span>
                </div>
              </div>
            ) : (
              <div className="border-2 border-dashed rounded-lg p-8 text-center">
                <Upload className="h-12 w-12 text-muted-foreground mx-auto mb-2" />
                <p className="text-sm text-muted-foreground mb-2">
                  Bild hochladen (max. 5MB)
                </p>
                <Input
                  type="file"
                  accept="image/*"
                  onChange={handleImageSelect}
                  className="max-w-xs mx-auto"
                  data-testid="product-image-input"
                />
              </div>
            )}
          </div>
          
          {/* Name */}
          <div className="space-y-2">
            <Label htmlFor="name">Name *</Label>
            <Input
              id="name"
              value={formData.name}
              onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
              placeholder="z.B. Cheeseburger"
              data-testid="product-name"
            />
          </div>
          
          {/* Category */}
          <div className="space-y-2">
            <Label htmlFor="category">Kategorie *</Label>
            <Select
              value={formData.category_id}
              onValueChange={(value) => setFormData(prev => ({ ...prev, category_id: value }))}
            >
              <SelectTrigger data-testid="product-category">
                <SelectValue placeholder="Kategorie wählen" />
              </SelectTrigger>
              <SelectContent>
                {categories.map(cat => (
                  <SelectItem key={cat.id} value={cat.id}>
                    {cat.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          
          {/* Description */}
          <div className="space-y-2">
            <Label htmlFor="description">Beschreibung</Label>
            <Textarea
              id="description"
              value={formData.description}
              onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
              placeholder="Produktbeschreibung..."
              rows={3}
              data-testid="product-description"
            />
          </div>
          
          {/* Prices - dynamically show based on category and product name */}
          {(() => {
            // Get selected category
            const selectedCategory = categories.find(c => c.id === formData.category_id);
            const categorySlug = (selectedCategory?.slug || selectedCategory?.name || '').toLowerCase();
            const categoryName = (selectedCategory?.name || '').toLowerCase();
            const productName = (formData.name || '').toLowerCase();
            
            // Burger with SINGLE SIZE (no medium/large):
            // Crunchy Chicken, Veggie, 250, 360 Burger
            const singleSizeBurgers = [
              'crunchy chicken burger',
              'crunchy chicken bacon burger', 
              'double crunchy chicken burger',
              'veggie burger',
              '250 burger',
              'twohundred fifty burger',
              '360 burger',
              'three hundred sixty burger'
            ];
            
            const isSingleSizeBurger = singleSizeBurgers.some(b => 
              productName.includes(b) || 
              productName.replace(/\s+/g, '').includes(b.replace(/\s+/g, ''))
            );
            
            // Check for single size burger first
            if ((categorySlug.includes('burger') || categoryName.includes('burger')) && isSingleSizeBurger) {
              return (
                <div className="space-y-2">
                  <Label htmlFor="price_normal">Preis (€) *</Label>
                  <Input
                    id="price_normal"
                    type="number"
                    step="0.01"
                    value={formData.price_normal}
                    onChange={(e) => setFormData(prev => ({ ...prev, price_normal: e.target.value }))}
                    placeholder="8.99"
                    className="max-w-xs"
                    data-testid="product-price-normal"
                  />
                  <p className="text-xs text-muted-foreground">Dieser Burger hat nur eine Größe</p>
                </div>
              );
            }
            
            // Regular Burger: Medium (125g) und Large (180g)
            if (categorySlug.includes('burger') || categoryName.includes('burger')) {
              return (
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="price_medium">Medium (125g) €</Label>
                    <Input
                      id="price_medium"
                      type="number"
                      step="0.01"
                      value={formData.price_medium}
                      onChange={(e) => setFormData(prev => ({ ...prev, price_medium: e.target.value }))}
                      placeholder="7.99"
                      data-testid="product-price-medium"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="price_large">Large (180g) €</Label>
                    <Input
                      id="price_large"
                      type="number"
                      step="0.01"
                      value={formData.price_large}
                      onChange={(e) => setFormData(prev => ({ ...prev, price_large: e.target.value }))}
                      placeholder="9.99"
                      data-testid="product-price-large"
                    />
                  </div>
                </div>
              );
            }
            
            // Pizza: Medium (25cm) und Large (30cm)
            if (categorySlug.includes('pizza') || categoryName.includes('pizza')) {
              return (
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="price_medium">Medium (25cm) €</Label>
                    <Input
                      id="price_medium"
                      type="number"
                      step="0.01"
                      value={formData.price_medium}
                      onChange={(e) => setFormData(prev => ({ ...prev, price_medium: e.target.value }))}
                      placeholder="9.99"
                      data-testid="product-price-medium"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="price_large">Large (30cm) €</Label>
                    <Input
                      id="price_large"
                      type="number"
                      step="0.01"
                      value={formData.price_large}
                      onChange={(e) => setFormData(prev => ({ ...prev, price_large: e.target.value }))}
                      placeholder="12.99"
                      data-testid="product-price-large"
                    />
                  </div>
                </div>
              );
            }
            
            // All other categories: Single price (Salate, Getränke, Pasta, Wraps, etc.)
            return (
              <div className="space-y-2">
                <Label htmlFor="price_normal">Preis (€) *</Label>
                <Input
                  id="price_normal"
                  type="number"
                  step="0.01"
                  value={formData.price_normal}
                  onChange={(e) => setFormData(prev => ({ ...prev, price_normal: e.target.value }))}
                  placeholder="10.79"
                  className="max-w-xs"
                  data-testid="product-price-normal"
                />
              </div>
            );
          })()}
        </div>
        
        <DialogFooter>
          <Button variant="outline" onClick={onClose} disabled={loading || uploading}>
            Abbrechen
          </Button>
          <Button 
            onClick={handleSubmit} 
            disabled={loading || uploading}
            data-testid="product-save"
          >
            {(loading || uploading) && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            {uploading ? 'Bild wird hochgeladen...' : isEdit ? 'Speichern' : 'Erstellen'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
