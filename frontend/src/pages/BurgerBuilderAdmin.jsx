import React, { useState, useEffect } from 'react';
import { useAdminAuth } from '../contexts/AdminAuthContext';
import AdminLayout from '../components/AdminLayout';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../components/ui/select';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '../components/ui/dialog';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '../components/ui/table';
import { toast } from 'sonner';
import { Plus, Edit, Trash2, Upload, X, Image as ImageIcon } from 'lucide-react';

const CATEGORIES = [
  { value: 'buns', label: 'Brötchen' },
  { value: 'proteins', label: 'Protein / Patty' },
  { value: 'cheese', label: 'Käse' },
  { value: 'veggies_standard', label: 'Gemüse Standard' },
  { value: 'veggies_premium', label: 'Gemüse Premium' },
  { value: 'extras', label: 'Crunch / Extras' },
  { value: 'avocado', label: 'Avocado' },
  { value: 'sauces', label: 'Saucen' }
];

const LAYER_GROUPS = [
  { value: 'bun_bottom', label: 'Bun Bottom', order: 10 },
  { value: 'sauce_bottom', label: 'Sauce Bottom', order: 20 },
  { value: 'salad', label: 'Salat', order: 30 },
  { value: 'tomato', label: 'Tomate', order: 40 },
  { value: 'patty', label: 'Patty', order: 50 },
  { value: 'cheese', label: 'Käse', order: 60 },
  { value: 'onion', label: 'Zwiebeln', order: 70 },
  { value: 'pickle', label: 'Gurken', order: 80 },
  { value: 'extras', label: 'Extras', order: 85 },
  { value: 'sauce_top', label: 'Sauce Top', order: 90 },
  { value: 'bun_top', label: 'Bun Top', order: 100 }
];

export default function BurgerBuilderAdmin() {
  const { token } = useAdminAuth();
  const [ingredients, setIngredients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingIngredient, setEditingIngredient] = useState(null);
  const [uploadingImage, setUploadingImage] = useState(false);
  
  const [formData, setFormData] = useState({
    category: 'buns',
    name: '',
    price: '',
    layer_order: '',
    layer_group: 'bun_bottom',
    position: 'center',
    sort_order: '0'
  });
  
  const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
  
  useEffect(() => {
    if (token) {
      fetchIngredients();
    }
  }, [token]);
  
  const fetchIngredients = async () => {
    try {
      const response = await fetch(`${backendUrl}/api/burger-builder/ingredients`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (!response.ok) throw new Error('Failed to fetch');
      
      const data = await response.json();
      setIngredients(data.ingredients || []);
    } catch (error) {
      console.error('Fetch ingredients error:', error);
      toast.error('Fehler beim Laden der Zutaten');
    } finally {
      setLoading(false);
    }
  };
  
  const handleSubmit = async () => {
    if (!formData.name || !formData.price) {
      toast.error('Bitte Name und Preis ausfüllen');
      return;
    }
    
    const url = editingIngredient
      ? `${backendUrl}/api/burger-builder/admin/ingredients/${editingIngredient.id}`
      : `${backendUrl}/api/burger-builder/admin/ingredients`;
    
    const method = editingIngredient ? 'PUT' : 'POST';
    
    try {
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          ...formData,
          price: parseFloat(formData.price),
          layer_order: parseInt(formData.layer_order) || 50,
          sort_order: parseInt(formData.sort_order) || 0
        })
      });
      
      if (!response.ok) throw new Error('Save failed');
      
      toast.success(editingIngredient ? 'Zutat aktualisiert' : 'Zutat erstellt');
      setDialogOpen(false);
      fetchIngredients();
    } catch (error) {
      console.error('Save error:', error);
      toast.error('Fehler beim Speichern');
    }
  };
  
  const handleImageUpload = async (ingredientId, file) => {
    if (!file) return;
    
    setUploadingImage(true);
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      const response = await fetch(
        `${backendUrl}/api/burger-builder/admin/ingredients/${ingredientId}/upload-image`,
        {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${token}` },
          body: formData
        }
      );
      
      if (!response.ok) throw new Error('Upload failed');
      
      const result = await response.json();
      toast.success('Bild hochgeladen');
      fetchIngredients();
    } catch (error) {
      console.error('Upload error:', error);
      toast.error('Fehler beim Hochladen');
    } finally {
      setUploadingImage(false);
    }
  };
  
  const handleDeleteImage = async (ingredientId) => {
    try {
      const response = await fetch(
        `${backendUrl}/api/burger-builder/admin/ingredients/${ingredientId}/image`,
        {
          method: 'DELETE',
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );
      
      if (!response.ok) throw new Error('Delete failed');
      
      toast.success('Bild entfernt');
      fetchIngredients();
    } catch (error) {
      console.error('Delete image error:', error);
      toast.error('Fehler beim Löschen');
    }
  };
  
  const handleEdit = (ingredient) => {
    setEditingIngredient(ingredient);
    setFormData({
      category: ingredient.category,
      name: ingredient.name,
      price: ingredient.price.toString(),
      layer_order: ingredient.layer_order.toString(),
      layer_group: ingredient.layer_group,
      position: ingredient.position || 'center',
      sort_order: ingredient.sort_order?.toString() || '0'
    });
    setDialogOpen(true);
  };
  
  const handleDelete = async (ingredientId) => {
    if (!confirm('Zutat wirklich löschen?')) return;
    
    try {
      const response = await fetch(
        `${backendUrl}/api/burger-builder/admin/ingredients/${ingredientId}`,
        {
          method: 'DELETE',
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );
      
      if (!response.ok) throw new Error('Delete failed');
      
      toast.success('Zutat gelöscht');
      fetchIngredients();
    } catch (error) {
      console.error('Delete error:', error);
      toast.error('Fehler beim Löschen');
    }
  };
  
  return (
    <AdminLayout>
      <div className="space-y-6" data-testid="burger-builder-admin">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Burger Builder Zutaten</h1>
            <p className="text-muted-foreground mt-1">
              Verwalte Zutaten mit Bildern für den Burger Builder
            </p>
          </div>
          <Button onClick={() => {
            setEditingIngredient(null);
            setFormData({
              category: 'buns',
              name: '',
              price: '',
              layer_order: '',
              layer_group: 'bun_bottom',
              position: 'center',
              sort_order: '0'
            });
            setDialogOpen(true);
          }}>
            <Plus className="w-4 h-4 mr-2" />
            Neue Zutat
          </Button>
        </div>
        
        {loading ? (
          <div className="text-center py-12">Lädt...</div>
        ) : (
          <Card>
            <CardContent className="p-0">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Bild</TableHead>
                    <TableHead>Name</TableHead>
                    <TableHead>Kategorie</TableHead>
                    <TableHead>Preis</TableHead>
                    <TableHead>Layer Order</TableHead>
                    <TableHead>Layer Group</TableHead>
                    <TableHead>Aktionen</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {ingredients.map(ingredient => (
                    <TableRow key={ingredient.id}>
                      <TableCell>
                        {ingredient.image_url ? (
                          <div className="relative group">
                            <img
                              src={ingredient.image_url}
                              alt={ingredient.name}
                              className="w-16 h-16 object-contain bg-accent rounded"
                            />
                            <button
                              onClick={() => handleDeleteImage(ingredient.id)}
                              className="absolute top-0 right-0 w-6 h-6 bg-destructive rounded-full opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center"
                            >
                              <X className="w-4 h-4 text-white" />
                            </button>
                          </div>
                        ) : (
                          <label className="cursor-pointer">
                            <div className="w-16 h-16 border-2 border-dashed border-border rounded flex items-center justify-center hover:border-primary transition-colors">
                              <Upload className="w-6 h-6 text-muted-foreground" />
                            </div>
                            <input
                              type="file"
                              accept="image/png,image/jpeg,image/webp"
                              className="hidden"
                              onChange={(e) => {
                                if (e.target.files?.[0]) {
                                  handleImageUpload(ingredient.id, e.target.files[0]);
                                }
                              }}
                            />
                          </label>
                        )}
                      </TableCell>
                      <TableCell className="font-medium">{ingredient.name}</TableCell>
                      <TableCell>
                        {CATEGORIES.find(c => c.value === ingredient.category)?.label || ingredient.category}
                      </TableCell>
                      <TableCell>€{ingredient.price.toFixed(2)}</TableCell>
                      <TableCell>{ingredient.layer_order}</TableCell>
                      <TableCell>{ingredient.layer_group}</TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleEdit(ingredient)}
                          >
                            <Edit className="w-4 h-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleDelete(ingredient.id)}
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        )}
      </div>
      
      {/* Edit/Create Dialog */}
      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {editingIngredient ? 'Zutat bearbeiten' : 'Neue Zutat erstellen'}
            </DialogTitle>
            <DialogDescription>
              Zutat für Burger Builder konfigurieren
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4">
            <div>
              <Label>Kategorie</Label>
              <Select
                value={formData.category}
                onValueChange={(value) => setFormData({ ...formData, category: value })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {CATEGORIES.map(cat => (
                    <SelectItem key={cat.value} value={cat.value}>
                      {cat.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            <div>
              <Label>Name</Label>
              <Input
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="z.B. Brioche Bun"
              />
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Preis (€)</Label>
                <Input
                  type="number"
                  step="0.10"
                  value={formData.price}
                  onChange={(e) => setFormData({ ...formData, price: e.target.value })}
                  placeholder="1.50"
                />
              </div>
              
              <div>
                <Label>Sort Order</Label>
                <Input
                  type="number"
                  value={formData.sort_order}
                  onChange={(e) => setFormData({ ...formData, sort_order: e.target.value })}
                  placeholder="0"
                />
              </div>
            </div>
            
            <div>
              <Label>Layer Group</Label>
              <Select
                value={formData.layer_group}
                onValueChange={(value) => {
                  const group = LAYER_GROUPS.find(g => g.value === value);
                  setFormData({ 
                    ...formData, 
                    layer_group: value,
                    layer_order: group?.order.toString() || formData.layer_order
                  });
                }}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {LAYER_GROUPS.map(group => (
                    <SelectItem key={group.value} value={group.value}>
                      {group.label} (Order: {group.order})
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            <div>
              <Label>Layer Order (10-100)</Label>
              <Input
                type="number"
                value={formData.layer_order}
                onChange={(e) => setFormData({ ...formData, layer_order: e.target.value })}
                placeholder="50"
              />
              <p className="text-xs text-muted-foreground mt-1">
                10 = unten (Bottom Bun), 100 = oben (Top Bun)
              </p>
            </div>
            
            <div>
              <Label>Position</Label>
              <Select
                value={formData.position}
                onValueChange={(value) => setFormData({ ...formData, position: value })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="center">Center (80%)</SelectItem>
                  <SelectItem value="full">Full (100%)</SelectItem>
                  <SelectItem value="drizzle">Drizzle (Sauce)</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          
          <DialogFooter>
            <Button variant="outline" onClick={() => setDialogOpen(false)}>
              Abbrechen
            </Button>
            <Button onClick={handleSubmit}>
              Speichern
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </AdminLayout>
  );
}
