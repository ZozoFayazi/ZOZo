import React, { useState, useEffect, useMemo } from 'react';
import { useAdminAuth } from '../contexts/AdminAuthContext';
import AdminLayout from '../components/AdminLayout';
import ProductDialog from '../components/ProductDialog';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Switch } from '../components/ui/switch';
import { Label } from '../components/ui/label';
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
import { Plus, Edit, Trash2, Search, Package, FolderPlus, GripVertical, Save } from 'lucide-react';

// DnD Kit imports
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
} from '@dnd-kit/core';
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  useSortable,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';

// Helper function to build full image URL
const getImageUrl = (imageUrl) => {
  if (!imageUrl) return null;
  if (imageUrl.startsWith('http://') || imageUrl.startsWith('https://')) {
    return imageUrl;
  }
  const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
  // Convert /uploads/... to /api/uploads/... for Kubernetes Ingress routing
  if (imageUrl.startsWith('/uploads/')) {
    return `${backendUrl}/api${imageUrl}`;
  }
  return `${backendUrl}${imageUrl}`;
};

// Sortable Table Row Component
function SortableTableRow({ product, categories, permissions, onEdit, onToggleActive, onToggleStock, onDelete }) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: product.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
    backgroundColor: isDragging ? 'hsl(var(--accent))' : undefined,
  };

  // Find category name by ID - check multiple possible matches
  const getCategoryName = (categoryId) => {
    if (!categoryId) return '-';
    // Try to find category by id, slug, or partial match
    const category = categories.find(c => 
      c.id === categoryId || 
      c.slug === categoryId ||
      c.id?.toString() === categoryId?.toString() ||
      // For ObjectId stored as string - check if the categoryId contains the category's ObjectId
      categoryId.includes && c.id && categoryId.includes(c.id.slice(-12))
    );
    return category?.name || categoryId || '-';
  };

  return (
    <TableRow ref={setNodeRef} style={style} data-testid={`product-row-${product.id}`}>
      {permissions.can_reorder && (
        <TableCell className="w-10">
          <button
            {...attributes}
            {...listeners}
            className="cursor-grab active:cursor-grabbing p-1 rounded hover:bg-accent"
            data-testid={`product-drag-${product.id}`}
          >
            <GripVertical className="h-5 w-5 text-muted-foreground" />
          </button>
        </TableCell>
      )}
      <TableCell>
        {product.image_url ? (
          <img
            src={getImageUrl(product.image_url)}
            alt={product.name}
            className="h-12 w-12 object-cover rounded"
          />
        ) : (
          <div className="h-12 w-12 bg-muted rounded flex items-center justify-center">
            <Package className="h-6 w-6 text-muted-foreground" />
          </div>
        )}
      </TableCell>
      <TableCell className="font-medium">
        {product.name}
      </TableCell>
      <TableCell className="text-muted-foreground">
        {getCategoryName(product.category_id)}
      </TableCell>
      <TableCell>
        {product.price_normal 
          ? `${product.price_normal.toFixed(2)}€` 
          : product.price_medium 
            ? `${product.price_medium.toFixed(2)}€` 
            : '-'}
      </TableCell>
      <TableCell>
        <div className="flex items-center gap-2">
          <Switch
            checked={product.active ?? true}
            onCheckedChange={() => onToggleActive(product.id, product.active ?? true)}
            data-testid={`product-active-${product.id}`}
          />
          <Badge variant={product.active ?? true ? "default" : "secondary"}>
            {product.active ?? true ? 'Aktiv' : 'Inaktiv'}
          </Badge>
        </div>
      </TableCell>
      <TableCell>
        <div className="flex items-center gap-2">
          <Switch
            checked={product.in_stock ?? true}
            onCheckedChange={() => onToggleStock(product.id, product.in_stock ?? true)}
            data-testid={`product-stock-${product.id}`}
          />
          <Badge 
            variant={product.in_stock ?? true ? "default" : "destructive"}
            className={product.in_stock ?? true ? "bg-[hsl(var(--success))]" : ""}
          >
            {product.in_stock ?? true ? 'Verfügbar' : 'Ausverkauft'}
          </Badge>
        </div>
      </TableCell>
      {permissions.can_edit && (
        <TableCell>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => onEdit(product)}
              data-testid={`product-edit-${product.id}`}
            >
              <Edit className="h-4 w-4" />
            </Button>
            <Button
              variant="outline"
              size="sm"
              className="text-destructive hover:bg-destructive hover:text-destructive-foreground"
              onClick={() => onDelete(product.id, product.name)}
              data-testid={`product-delete-${product.id}`}
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        </TableCell>
      )}
    </TableRow>
  );
}

export default function ProductManagement() {
  const { token, hasPermission } = useAdminAuth();
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [productDialogOpen, setProductDialogOpen] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [categoryDialogOpen, setCategoryDialogOpen] = useState(false);
  const [categoryName, setCategoryName] = useState('');
  const [hasOrderChanges, setHasOrderChanges] = useState(false);
  const [savingOrder, setSavingOrder] = useState(false);
  const [permissions, setPermissions] = useState({
    can_create: false,
    can_edit: false,
    can_delete: false,
    can_toggle_status: true,
    is_master: false
  });
  
  const canManageProducts = hasPermission('manage_products');
  
  // DnD Kit sensors
  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8,
      },
    }),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );
  
  useEffect(() => {
    if (token) {
      fetchPermissions();
      fetchProducts();
      fetchCategories();
    }
  }, [token]);
  
  const fetchPermissions = async () => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
      const response = await fetch(`${backendUrl}/api/admin/products/permissions`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.status === 401) {
        // Session expired - redirect to login
        toast.error('Session abgelaufen. Bitte melden Sie sich erneut an.');
        localStorage.removeItem('adminToken');
        window.location.href = '/admin/login';
        return;
      }
      
      if (!response.ok) {
        throw new Error('Failed to fetch permissions');
      }
      
      const data = await response.json();
      setPermissions(data);
    } catch (error) {
      console.error('Fetch permissions error:', error);
      // Keep defaults - don't crash the UI
    }
  };
  
  const fetchProducts = async () => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
      const response = await fetch(`${backendUrl}/api/admin/products`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.status === 401) {
        // Session expired - redirect to login
        toast.error('Session abgelaufen. Bitte melden Sie sich erneut an.');
        localStorage.removeItem('adminToken');
        window.location.href = '/admin/login';
        return;
      }
      
      if (!response.ok) {
        throw new Error('Failed to fetch products');
      }
      
      const data = await response.json();
      // Sort by sort_order if available, otherwise by name
      const sortedProducts = (data.products || []).sort((a, b) => {
        if (a.sort_order !== undefined && b.sort_order !== undefined) {
          return a.sort_order - b.sort_order;
        }
        return (a.name || '').localeCompare(b.name || '');
      });
      setProducts(sortedProducts);
    } catch (error) {
      console.error('Fetch products error:', error);
      toast.error('Fehler beim Laden der Produkte');
    } finally {
      setLoading(false);
    }
  };
  
  const fetchCategories = async () => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
      const response = await fetch(`${backendUrl}/api/categories`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (!response.ok) {
        throw new Error('Failed to fetch categories');
      }
      
      const data = await response.json();
      // Create simple category objects from the data
      const cats = data.categories || [];
      setCategories(cats.map(cat => ({
        id: cat.id || cat._id,
        slug: cat.slug,
        name: cat.name
      })));
    } catch (error) {
      console.error('Fetch categories error:', error);
      // Use fallback categories if fetch fails
      setCategories([
        { id: 'burgers', name: 'Burgers' },
        { id: 'sides', name: 'Beilagen' },
        { id: 'drinks', name: 'Getränke' },
        { id: 'desserts', name: 'Desserts' }
      ]);
    }
  };
  
  const handleCreateProduct = () => {
    setSelectedProduct(null);
    setProductDialogOpen(true);
  };
  
  const handleEditProduct = (product) => {
    setSelectedProduct(product);
    setProductDialogOpen(true);
  };
  
  const handleProductSuccess = (updatedProduct) => {
    if (selectedProduct) {
      // Update existing
      setProducts(prev => prev.map(p => 
        p.id === updatedProduct.id ? updatedProduct : p
      ));
    } else {
      // Add new
      setProducts(prev => [updatedProduct, ...prev]);
    }
  };
  
  const handleCreateCategory = async () => {
    if (!categoryName.trim()) {
      toast.error('Bitte Kategorienamen eingeben');
      return;
    }
    
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
      const response = await fetch(`${backendUrl}/api/admin/categories`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          name: categoryName,
          slug: categoryName.toLowerCase().replace(/\s+/g, '-')
        })
      });
      
      if (!response.ok) {
        throw new Error('Fehler beim Erstellen');
      }
      
      const newCategory = await response.json();
      setCategories(prev => [...prev, {
        id: newCategory.id || newCategory.slug,
        slug: newCategory.slug,
        name: newCategory.name
      }]);
      
      toast.success('Kategorie erstellt');
      setCategoryDialogOpen(false);
      setCategoryName('');
    } catch (error) {
      console.error('Create category error:', error);
      toast.error(error.message || 'Fehler beim Erstellen');
    }
  };
  
  const handleToggleActive = async (productId, currentStatus) => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
      const response = await fetch(
        `${backendUrl}/api/admin/products/${productId}/toggle`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({
            is_active: !currentStatus
          })
        }
      );
      
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Fehler beim Ändern des Status');
      }
      
      // Update local state
      setProducts(prev => prev.map(p => 
        p.id === productId ? { ...p, is_active: !currentStatus, active: !currentStatus } : p
      ));
      
      toast.success(`Produkt ${!currentStatus ? 'aktiviert' : 'deaktiviert'}`);
      
      // Reload to get fresh data with overrides
      fetchProducts();
    } catch (error) {
      console.error('Toggle active error:', error);
      toast.error(error.message || 'Fehler beim Ändern des Status');
    }
  };
  
  const handleToggleStock = async (productId, currentStatus) => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
      const response = await fetch(
        `${backendUrl}/api/admin/products/${productId}/toggle`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({
            in_stock: !currentStatus
          })
        }
      );
      
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Fehler beim Ändern des Lagerstatus');
      }
      
      // Update local state
      setProducts(prev => prev.map(p => 
        p.id === productId ? { ...p, in_stock: !currentStatus } : p
      ));
      
      toast.success(`Produkt ${!currentStatus ? 'verfügbar' : 'ausverkauft'}`);
      
      // Reload to get fresh data with overrides
      fetchProducts();
    } catch (error) {
      console.error('Toggle stock error:', error);
      toast.error(error.message || 'Fehler beim Ändern des Lagerstatus');
    }
  };
  
  const handleDelete = async (productId, productName) => {
    if (!window.confirm(`Möchten Sie "${productName}" wirklich löschen?`)) {
      return;
    }
    
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
      const response = await fetch(`${backendUrl}/api/admin/products/${productId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Fehler beim Löschen');
      }
      
      // Remove from local state
      setProducts(prev => prev.filter(p => p.id !== productId));
      
      toast.success('Produkt gelöscht');
    } catch (error) {
      console.error('Delete error:', error);
      toast.error(error.message || 'Fehler beim Löschen');
    }
  };
  
  // Drag and Drop Handler
  const handleDragEnd = (event) => {
    const { active, over } = event;
    
    if (active.id !== over?.id) {
      setProducts((items) => {
        const oldIndex = items.findIndex((item) => item.id === active.id);
        const newIndex = items.findIndex((item) => item.id === over.id);
        
        const newItems = arrayMove(items, oldIndex, newIndex);
        setHasOrderChanges(true);
        return newItems;
      });
    }
  };
  
  // Save new order to backend
  const handleSaveOrder = async () => {
    setSavingOrder(true);
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
      
      // Create order data with new sort_order values
      const orderData = products.map((product, index) => ({
        id: product.id,
        sort_order: index
      }));
      
      const response = await fetch(`${backendUrl}/api/admin/products/reorder`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(orderData)
      });
      
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Fehler beim Speichern');
      }
      
      setHasOrderChanges(false);
      toast.success('Reihenfolge gespeichert');
    } catch (error) {
      console.error('Save order error:', error);
      toast.error(error.message || 'Fehler beim Speichern der Reihenfolge');
    } finally {
      setSavingOrder(false);
    }
  };
  
  // Filter products based on search term
  const filteredProducts = useMemo(() => {
    return products.filter(product =>
      product.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      product.description?.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [products, searchTerm]);
  
  // Get product IDs for sortable context
  const productIds = useMemo(() => filteredProducts.map(p => p.id), [filteredProducts]);
  
  if (loading) {
    return (
      <AdminLayout>
        <div className="p-6">
          <p className="text-muted-foreground">Lädt Produkte...</p>
        </div>
      </AdminLayout>
    );
  }
  
  return (
    <AdminLayout>
      <div className="p-6">
        <div className="max-w-7xl mx-auto space-y-6">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-foreground" data-testid="products-page-title">
                Produktverwaltung
              </h1>
              <p className="text-muted-foreground mt-1">
                {permissions.is_master
                  ? 'Master-Menü: Verwalten Sie Ihr komplettes Produktsortiment - Drag & Drop zum Sortieren' 
                  : `${permissions.location_slug?.toUpperCase() || 'Standort'}-Verwaltung: Produktstatus anpassen (Verfügbarkeit)`}
              </p>
              {!permissions.is_master && (
                <p className="text-sm text-orange-600 mt-1">
                  ℹ️ Produkte können nur vom Master-Standort ({permissions.master_location?.toUpperCase()}) bearbeitet werden. 
                  Sie können hier nur Verfügbarkeit steuern.
                </p>
              )}
            </div>
            <div className="flex gap-2">
              {permissions.can_reorder && hasOrderChanges && (
                <Button 
                  onClick={handleSaveOrder} 
                  disabled={savingOrder}
                  variant="default"
                  className="bg-green-600 hover:bg-green-700"
                  data-testid="save-order-button"
                >
                  <Save className="h-4 w-4 mr-2" />
                  {savingOrder ? 'Speichert...' : 'Reihenfolge speichern'}
                </Button>
              )}
              {permissions.can_create && (
                <>
                  <Button onClick={handleCreateProduct} data-testid="products-add-button">
                    <Plus className="h-4 w-4 mr-2" />
                    Neues Produkt
                  </Button>
                  <Button variant="outline" onClick={() => setCategoryDialogOpen(true)} data-testid="categories-add-button">
                    <FolderPlus className="h-4 w-4 mr-2" />
                    Kategorie
                  </Button>
                </>
              )}
            </div>
          </div>
          
          {/* Search */}
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-2">
                <Search className="h-5 w-5 text-muted-foreground" />
                <Input
                  placeholder="Produkte suchen..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="max-w-md"
                  data-testid="products-search"
                />
              </div>
            </CardContent>
          </Card>
          
          {/* Products Table */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>Produkte ({filteredProducts.length})</span>
                {canManageProducts && (
                  <span className="text-sm font-normal text-muted-foreground">
                    <GripVertical className="h-4 w-4 inline mr-1" />
                    Ziehen Sie Produkte zum Sortieren
                  </span>
                )}
              </CardTitle>
            </CardHeader>
            <CardContent>
              {filteredProducts.length === 0 ? (
                <div className="text-center py-12">
                  <Package className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-foreground mb-2">
                    Keine Produkte gefunden
                  </h3>
                  <p className="text-muted-foreground">
                    {searchTerm ? 'Versuchen Sie einen anderen Suchbegriff' : 'Legen Sie Ihr erstes Produkt an'}
                  </p>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <DndContext
                    sensors={sensors}
                    collisionDetection={closestCenter}
                    onDragEnd={handleDragEnd}
                  >
                    <Table>
                      <TableHeader>
                        <TableRow>
                          {permissions.can_reorder && <TableHead className="w-10"></TableHead>}
                          <TableHead>Bild</TableHead>
                          <TableHead>Name</TableHead>
                          <TableHead>Kategorie</TableHead>
                          <TableHead>Preis</TableHead>
                          <TableHead>Aktiv</TableHead>
                          <TableHead>Lagerbestand</TableHead>
                          {permissions.can_edit && <TableHead>Aktionen</TableHead>}
                        </TableRow>
                      </TableHeader>
                      <SortableContext items={productIds} strategy={verticalListSortingStrategy}>
                        <TableBody>
                          {filteredProducts.map((product) => (
                            <SortableTableRow
                              key={product.id}
                              product={product}
                              categories={categories}
                              permissions={permissions}
                              onEdit={handleEditProduct}
                              onToggleActive={handleToggleActive}
                              onToggleStock={handleToggleStock}
                              onDelete={handleDelete}
                            />
                          ))}
                        </TableBody>
                      </SortableContext>
                    </Table>
                  </DndContext>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Product Dialog */}
      <ProductDialog
        open={productDialogOpen}
        onClose={() => setProductDialogOpen(false)}
        product={selectedProduct}
        categories={categories}
        onSuccess={handleProductSuccess}
      />

      {/* Category Dialog */}
      <Dialog open={categoryDialogOpen} onOpenChange={setCategoryDialogOpen}>
        <DialogContent data-testid="category-dialog">
          <DialogHeader>
            <DialogTitle>Neue Kategorie</DialogTitle>
            <DialogDescription>
              Erstellen Sie eine neue Produktkategorie
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="category-name">Kategoriename</Label>
              <Input
                id="category-name"
                value={categoryName}
                onChange={(e) => setCategoryName(e.target.value)}
                placeholder="z.B. Specials"
                data-testid="category-name-input"
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setCategoryDialogOpen(false)}>
              Abbrechen
            </Button>
            <Button onClick={handleCreateCategory} data-testid="category-save">
              Erstellen
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </AdminLayout>
  );
}
