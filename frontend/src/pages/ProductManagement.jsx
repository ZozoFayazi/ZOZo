import React, { useState, useEffect } from 'react';
import { useAdminAuth } from '../contexts/AdminAuthContext';
import AdminLayout from '../components/AdminLayout';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Switch } from '../components/ui/switch';
import { Label } from '../components/ui/label';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '../components/ui/table';
import { toast } from 'sonner';
import { Plus, Edit, Trash2, Upload, Search, Package } from 'lucide-react';

export default function ProductManagement() {
  const { token, hasPermission } = useAdminAuth();
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  
  const canManageProducts = hasPermission('manage_products');
  
  useEffect(() => {
    if (token) {
      fetchProducts();
    }
  }, [token]);
  
  const fetchProducts = async () => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
      const response = await fetch(`${backendUrl}/api/admin/products`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (!response.ok) {
        throw new Error('Failed to fetch products');
      }
      
      const data = await response.json();
      setProducts(data.products);
    } catch (error) {
      console.error('Fetch products error:', error);
      toast.error('Fehler beim Laden der Produkte');
    } finally {
      setLoading(false);
    }
  };
  
  const handleToggleActive = async (productId, currentStatus) => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
      const response = await fetch(
        `${backendUrl}/api/admin/products/${productId}/toggle-active?is_active=${!currentStatus}`,
        {
          method: 'PATCH',
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );
      
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Fehler beim Ändern des Status');
      }
      
      const updatedProduct = await response.json();
      
      // Update local state
      setProducts(prev => prev.map(p => 
        p.id === productId ? { ...p, active: updatedProduct.active } : p
      ));
      
      toast.success(`Produkt ${!currentStatus ? 'aktiviert' : 'deaktiviert'}`);
    } catch (error) {
      console.error('Toggle active error:', error);
      toast.error(error.message || 'Fehler beim Ändern des Status');
    }
  };
  
  const handleToggleStock = async (productId, currentStatus) => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
      const response = await fetch(
        `${backendUrl}/api/admin/products/${productId}/toggle-stock?in_stock=${!currentStatus}`,
        {
          method: 'PATCH',
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );
      
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Fehler beim Ändern des Lagerstatus');
      }
      
      const updatedProduct = await response.json();
      
      // Update local state
      setProducts(prev => prev.map(p => 
        p.id === productId ? { ...p, in_stock: updatedProduct.in_stock } : p
      ));
      
      toast.success(`Produkt ${!currentStatus ? 'verfügbar' : 'ausverkauft'}`);
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
  
  const filteredProducts = products.filter(product =>
    product.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    product.description?.toLowerCase().includes(searchTerm.toLowerCase())
  );
  
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
                {canManageProducts 
                  ? 'Verwalten Sie Ihr komplettes Produktsortiment' 
                  : 'Produkte aktivieren/deaktivieren'}
              </p>
            </div>
            {canManageProducts && (
              <Button data-testid="products-add-button">
                <Plus className="h-4 w-4 mr-2" />
                Neues Produkt
              </Button>
            )}
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
              <CardTitle>
                Produkte ({filteredProducts.length})
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
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Bild</TableHead>
                        <TableHead>Name</TableHead>
                        <TableHead>Kategorie</TableHead>
                        <TableHead>Preis</TableHead>
                        <TableHead>Aktiv</TableHead>
                        <TableHead>Lagerbestand</TableHead>
                        {canManageProducts && <TableHead>Aktionen</TableHead>}
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {filteredProducts.map((product) => (
                        <TableRow key={product.id} data-testid={`product-row-${product.id}`}>
                          <TableCell>
                            {product.image_url ? (
                              <img
                                src={product.image_url}
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
                            {product.category_id}
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
                                onCheckedChange={() => handleToggleActive(product.id, product.active ?? true)}
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
                                onCheckedChange={() => handleToggleStock(product.id, product.in_stock ?? true)}
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
                          {canManageProducts && (
                            <TableCell>
                              <div className="flex items-center gap-2">
                                <Button
                                  variant="outline"
                                  size="sm"
                                  data-testid={`product-edit-${product.id}`}
                                >
                                  <Edit className="h-4 w-4" />
                                </Button>
                                <Button
                                  variant="outline"
                                  size="sm"
                                  className="text-destructive hover:bg-destructive hover:text-destructive-foreground"
                                  onClick={() => handleDelete(product.id, product.name)}
                                  data-testid={`product-delete-${product.id}`}
                                >
                                  <Trash2 className="h-4 w-4" />
                                </Button>
                              </div>
                            </TableCell>
                          )}
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </AdminLayout>
  );
}
