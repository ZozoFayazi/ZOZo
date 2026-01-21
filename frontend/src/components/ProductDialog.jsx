import React, { useState, useEffect } from 'react';
import { useAdminAuth } from '../contexts/AdminAuthContext';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogFooter } from './ui/dialog';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Switch } from './ui/switch';
import { toast } from 'sonner';
import { Loader2, Upload, X, FolderPlus } from 'lucide-react';
import QuickAddCategory from './QuickAddCategory';

export default function ProductDialog({ open, onClose, product, categories, onSuccess }) {
  const { token } = useAdminAuth();
  const isEdit = !!product;
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [quickAddOpen, setQuickAddOpen] = useState(false);
  const [localCategories, setLocalCategories] = useState(categories || []);
  
  const [formData, setFormData] = useState({
    name: '',
    category_id: '',
    description: '',
    price_normal: '',
    price_medium: '',
    price_large: '',
    image_url: '',
    size_label_medium: 'Medium (125g)',
    size_label_large: 'Large (180g)',
    can_upgrade_to_menu: false,
    menu_requires_side: true,
    menu_requires_drink: true,
    menu_upgrade_price_medium: '',
    menu_upgrade_price_large: '',
    show_as_checkout_upsell: false,
    upsell_priority: 5,
    upsell_text: ''
  });
  
  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState('');
  
  // Update local categories when prop changes
  useEffect(() => {
    setLocalCategories(categories || []);
  }, [categories]);
  
  useEffect(() => {
    if (product) {
      setFormData({
        name: product.name || '',
        category_id: product.category_id || '',
        description: product.description || '',
        price_normal: product.price_normal || '',
        price_medium: product.price_medium || '',
        price_large: product.price_large || '',
        image_url: product.image_url || '',
        size_label_medium: product.size_labels?.medium || 'Medium (125g)',
        size_label_large: product.size_labels?.large || 'Large (180g)',
        can_upgrade_to_menu: product.can_upgrade_to_menu || false,
        menu_requires_side: product.menu_requires_side !== false, // default true
        menu_requires_drink: product.menu_requires_drink !== false, // default true
        menu_upgrade_price_medium: product.menu_upgrade_price_medium || '',
        menu_upgrade_price_large: product.menu_upgrade_price_large || '',
        show_as_checkout_upsell: product.show_as_checkout_upsell || false,
        upsell_priority: product.upsell_priority || 5,
        upsell_text: product.upsell_text || ''
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
        image_url: '',
        size_label_medium: 'Medium (125g)',
        size_label_large: 'Large (180g)',
        can_upgrade_to_menu: false,
        menu_requires_side: true,
        menu_requires_drink: true,
        menu_upgrade_price_medium: '',
        menu_upgrade_price_large: '',
        show_as_checkout_upsell: false,
        upsell_priority: 5,
        upsell_text: ''
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
        price_large: formData.price_large ? parseFloat(formData.price_large) : null,
        size_labels: {
          medium: formData.size_label_medium || 'Medium (125g)',
          large: formData.size_label_large || 'Large (180g)'
        },
        can_upgrade_to_menu: formData.can_upgrade_to_menu || false,
        menu_requires_side: formData.menu_requires_side,
        menu_requires_drink: formData.menu_requires_drink,
        menu_upgrade_price_medium: formData.menu_upgrade_price_medium ? parseFloat(formData.menu_upgrade_price_medium) : null,
        menu_upgrade_price_large: formData.menu_upgrade_price_large ? parseFloat(formData.menu_upgrade_price_large) : null,
        show_as_checkout_upsell: formData.show_as_checkout_upsell || false,
        upsell_priority: formData.upsell_priority || 5,
        upsell_text: formData.upsell_text || null
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
  
  const handleCategoryCreated = (newCategory) => {
    // Add new category to local list and select it
    setLocalCategories(prev => [...prev, newCategory]);
    setFormData(prev => ({ ...prev, category_id: newCategory.id }));
    toast.success('Kategorie erstellt und ausgewählt!');
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
            <div className="flex items-center justify-between">
              <Label htmlFor="category">Kategorie *</Label>
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() => setQuickAddOpen(true)}
                data-testid="quick-add-category-btn"
              >
                <FolderPlus className="h-4 w-4 mr-2" />
                Neue Kategorie
              </Button>
            </div>
            <Select
              value={formData.category_id}
              onValueChange={(value) => setFormData(prev => ({ ...prev, category_id: value }))}
            >
              <SelectTrigger data-testid="product-category">
                <SelectValue placeholder="Kategorie wählen" />
              </SelectTrigger>
              <SelectContent>
                {localCategories.map(cat => (
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
            const singleSizeKeywords = [
              'crunchy chicken',
              'crunchy chickenburger',
              'double crunchy',
              'veggie burger',
              'veggie',
              '250',
              'twohundred fifty',
              'two hundred fifty',
              '360',
              'three hundred sixty',
              'crunchy chicken bacon'
            ];
            
            const isSingleSizeBurger = singleSizeKeywords.some(keyword => 
              productName.includes(keyword)
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
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="price_medium">Medium Preis (€)</Label>
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
                      <Label htmlFor="price_large">Large Preis (€)</Label>
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
                  
                  {/* Size Label Customization */}
                  <div className="border-t pt-4">
                    <p className="text-sm font-medium mb-3">Größennamen anpassen (optional)</p>
                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="size_label_medium" className="text-xs text-muted-foreground">
                          Medium Label
                        </Label>
                        <Input
                          id="size_label_medium"
                          value={formData.size_label_medium}
                          onChange={(e) => setFormData(prev => ({ ...prev, size_label_medium: e.target.value }))}
                          placeholder="Medium (125g)"
                          className="text-sm"
                          data-testid="size-label-medium"
                        />
                        <p className="text-xs text-muted-foreground">z.B. "Medium (125g)" oder "Klein"</p>
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="size_label_large" className="text-xs text-muted-foreground">
                          Large Label
                        </Label>
                        <Input
                          id="size_label_large"
                          value={formData.size_label_large}
                          onChange={(e) => setFormData(prev => ({ ...prev, size_label_large: e.target.value }))}
                          placeholder="Large (180g)"
                          className="text-sm"
                          data-testid="size-label-large"
                        />
                        <p className="text-xs text-muted-foreground">z.B. "Large (180g)" oder "Groß"</p>
                      </div>
                    </div>
                  </div>
                  
                  {/* Menu Configuration */}
                  <div className="border-t pt-4 space-y-4">
                    <div className="flex items-center justify-between">
                      <div className="space-y-0.5">
                        <Label htmlFor="can_upgrade_to_menu" className="text-sm font-medium">
                          Als Menü verfügbar
                        </Label>
                        <p className="text-xs text-muted-foreground">
                          Kunde kann Beilage + Getränk hinzufügen
                        </p>
                      </div>
                      <Switch
                        id="can_upgrade_to_menu"
                        checked={formData.can_upgrade_to_menu}
                        onCheckedChange={(checked) => setFormData(prev => ({ ...prev, can_upgrade_to_menu: checked }))}
                        data-testid="menu-toggle"
                      />
                    </div>
                    
                    {formData.can_upgrade_to_menu && (
                      <div className="space-y-4 pl-4 border-l-2 border-primary/20">
                        {/* Menu Requirements */}
                        <div className="space-y-3">
                          <p className="text-sm font-medium">Menü-Komponenten</p>
                          
                          <div className="flex items-center justify-between">
                            <Label htmlFor="menu_requires_side" className="text-sm font-normal cursor-pointer">
                              Beilage erforderlich
                            </Label>
                            <Switch
                              id="menu_requires_side"
                              checked={formData.menu_requires_side}
                              onCheckedChange={(checked) => setFormData(prev => ({ ...prev, menu_requires_side: checked }))}
                              data-testid="menu-requires-side"
                            />
                          </div>
                          
                          <div className="flex items-center justify-between">
                            <Label htmlFor="menu_requires_drink" className="text-sm font-normal cursor-pointer">
                              Getränk erforderlich
                            </Label>
                            <Switch
                              id="menu_requires_drink"
                              checked={formData.menu_requires_drink}
                              onCheckedChange={(checked) => setFormData(prev => ({ ...prev, menu_requires_drink: checked }))}
                              data-testid="menu-requires-drink"
                            />
                          </div>
                        </div>
                        
                        {/* Menu Prices */}
                        <div className="space-y-3">
                          <p className="text-sm font-medium">Menü-Preise</p>
                          <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                              <Label htmlFor="menu_upgrade_price_medium" className="text-xs">
                                Medium Menü (€)
                              </Label>
                              <Input
                                id="menu_upgrade_price_medium"
                                type="number"
                                step="0.01"
                                value={formData.menu_upgrade_price_medium}
                                onChange={(e) => setFormData(prev => ({ ...prev, menu_upgrade_price_medium: e.target.value }))}
                                placeholder="13.89"
                                className="text-sm"
                                data-testid="menu-price-medium"
                              />
                              <p className="text-xs text-muted-foreground">
                                Basis: €{formData.price_medium || '0.00'}
                              </p>
                            </div>
                            <div className="space-y-2">
                              <Label htmlFor="menu_upgrade_price_large" className="text-xs">
                                Large Menü (€)
                              </Label>
                              <Input
                                id="menu_upgrade_price_large"
                                type="number"
                                step="0.01"
                                value={formData.menu_upgrade_price_large}
                                onChange={(e) => setFormData(prev => ({ ...prev, menu_upgrade_price_large: e.target.value }))}
                                placeholder="17.09"
                                className="text-sm"
                                data-testid="menu-price-large"
                              />
                              <p className="text-xs text-muted-foreground">
                                Basis: €{formData.price_large || '0.00'}
                              </p>
                            </div>
                          </div>
                        </div>
                      </div>
                    )}
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
            
            // Getränke: 0,5L und 1L (Cola, Fanta, Sprite, etc.)
            if (categorySlug.includes('getränke') || categorySlug.includes('getraenke') || 
                categoryName.includes('getränke') || categoryName.includes('drink')) {
              return (
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="price_medium">0,5L (€)</Label>
                    <Input
                      id="price_medium"
                      type="number"
                      step="0.01"
                      value={formData.price_medium}
                      onChange={(e) => setFormData(prev => ({ ...prev, price_medium: e.target.value }))}
                      placeholder="2.99"
                      data-testid="product-price-medium"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="price_large">1L (€)</Label>
                    <Input
                      id="price_large"
                      type="number"
                      step="0.01"
                      value={formData.price_large}
                      onChange={(e) => setFormData(prev => ({ ...prev, price_large: e.target.value }))}
                      placeholder="3.89"
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
        
        {/* Checkout Upselling Configuration */}
        <div className="border-t pt-4 space-y-4">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label htmlFor="show_as_checkout_upsell" className="text-sm font-medium">
                🛒 Als Checkout-Upsell anzeigen
              </Label>
              <p className="text-xs text-muted-foreground">
                Wird im Warenkorb als Empfehlung angezeigt ("Vergiss nicht...")
              </p>
            </div>
            <Switch
              id="show_as_checkout_upsell"
              checked={formData.show_as_checkout_upsell}
              onCheckedChange={(checked) => setFormData(prev => ({ ...prev, show_as_checkout_upsell: checked }))}
              data-testid="upsell-toggle"
            />
          </div>
          
          {formData.show_as_checkout_upsell && (
            <div className="space-y-4 pl-4 border-l-2 border-primary/20">
              {/* Upsell Priority */}
              <div className="space-y-2">
                <Label htmlFor="upsell_priority" className="text-sm">
                  Priorität: {formData.upsell_priority}/10
                </Label>
                <p className="text-xs text-muted-foreground mb-2">
                  Höhere Priorität = weiter oben angezeigt
                </p>
                <input
                  type="range"
                  id="upsell_priority"
                  min="1"
                  max="10"
                  value={formData.upsell_priority}
                  onChange={(e) => setFormData(prev => ({ ...prev, upsell_priority: parseInt(e.target.value) }))}
                  className="w-full"
                  data-testid="upsell-priority"
                />
                <div className="flex justify-between text-xs text-muted-foreground">
                  <span>Niedrig</span>
                  <span>Hoch</span>
                </div>
              </div>
              
              {/* Upsell Text */}
              <div className="space-y-2">
                <Label htmlFor="upsell_text" className="text-sm">
                  Upsell-Text (optional)
                </Label>
                <Input
                  id="upsell_text"
                  value={formData.upsell_text}
                  onChange={(e) => setFormData(prev => ({ ...prev, upsell_text: e.target.value }))}
                  placeholder="z.B. 'Noch durstig? 🥤' oder 'Perfekt dazu!'"
                  className="text-sm"
                  data-testid="upsell-text"
                />
                <p className="text-xs text-muted-foreground">
                  Wird über dem Produkt im Warenkorb angezeigt
                </p>
              </div>
            </div>
          )}
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
      
      {/* Quick Add Category Dialog */}
      <QuickAddCategory
        open={quickAddOpen}
        onClose={() => setQuickAddOpen(false)}
        onCategoryCreated={handleCategoryCreated}
      />
    </Dialog>
  );
}
