import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Save, Download, Upload, AlertCircle } from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';
import { Input } from '../components/ui/input';

const API_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

function POSItemMapping() {
  const navigate = useNavigate();
  const [categories, setCategories] = useState([]);
  const [products, setProducts] = useState([]);
  const [modifierGroups, setModifierGroups] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('zozoAuthToken');
      
      const [categoriesRes, modifierGroupsRes] = await Promise.all([
        axios.get(`${API_URL}/api/categories`),
        axios.get(`${API_URL}/api/modifier-groups`)
      ]);
      
      setCategories(categoriesRes.data.categories || []);
      setModifierGroups(modifierGroupsRes.data || []);
      
      // Load all products from all categories
      const allProducts = [];
      for (const category of categoriesRes.data.categories || []) {
        try {
          const productsRes = await axios.get(
            `${API_URL}/api/admin/products/by-category/${category.id}`,
            { headers: { Authorization: `Bearer ${token}` } }
          );
          allProducts.push(...(productsRes.data || []));
        } catch (error) {
          console.error(`Error loading products for category ${category.name}:`, error);
        }
      }
      
      setProducts(allProducts);
    } catch (error) {
      console.error('Error loading data:', error);
      toast.error('Fehler beim Laden der Daten');
    } finally {
      setLoading(false);
    }
  };

  const updateProductPOSID = (productId, posItemId) => {
    setProducts(products.map(p => 
      (p.id || p._id) === productId 
        ? { ...p, pos_item_id: posItemId }
        : p
    ));
  };

  const updateModifierOptionPOSID = (groupId, optionIndex, posItemId) => {
    setModifierGroups(modifierGroups.map(group => {
      if ((group.id || group._id) === groupId) {
        const newOptions = [...(group.options || [])];
        if (newOptions[optionIndex]) {
          newOptions[optionIndex] = {
            ...newOptions[optionIndex],
            pos_item_id: posItemId
          };
        }
        return { ...group, options: newOptions };
      }
      return group;
    }));
  };

  const saveAllMappings = async () => {
    setSaving(true);
    let successCount = 0;
    let errorCount = 0;

    try {
      const token = localStorage.getItem('zozoAuthToken');

      // Save products
      for (const product of products) {
        if (!product.pos_item_id) continue; // Skip if no POS ID set

        try {
          await axios.patch(
            `${API_URL}/api/admin/products/${product.id || product._id}`,
            { pos_item_id: product.pos_item_id },
            { headers: { Authorization: `Bearer ${token}` } }
          );
          successCount++;
        } catch (error) {
          console.error(`Error saving product ${product.name}:`, error);
          errorCount++;
        }
      }

      // Save modifier groups
      for (const group of modifierGroups) {
        try {
          await axios.patch(
            `${API_URL}/api/admin/modifier-groups/${group.id || group._id}`,
            { options: group.options },
            { headers: { Authorization: `Bearer ${token}` } }
          );
          successCount++;
        } catch (error) {
          console.error(`Error saving modifier group ${group.name}:`, error);
          errorCount++;
        }
      }

      if (errorCount === 0) {
        toast.success(`Alle Mappings gespeichert! (${successCount} Items)`);
      } else {
        toast.warning(`${successCount} gespeichert, ${errorCount} Fehler`);
      }
    } catch (error) {
      console.error('Error saving mappings:', error);
      toast.error('Fehler beim Speichern');
    } finally {
      setSaving(false);
    }
  };

  const exportMappings = () => {
    const data = {
      products: products.map(p => ({
        id: p.id || p._id,
        name: p.name,
        pos_item_id: p.pos_item_id || ''
      })),
      modifier_groups: modifierGroups.map(g => ({
        id: g.id || g._id,
        name: g.name,
        options: (g.options || []).map(opt => ({
          name: opt.name,
          pos_item_id: opt.pos_item_id || ''
        }))
      }))
    };

    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `pos-mappings-${new Date().toISOString().split('T')[0]}.json`;
    a.click();

    toast.success('Mappings exportiert');
  };

  const filteredProducts = products.filter(p =>
    p.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Lade Produkte...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <div className="bg-card border-b border-border">
        <div className="container-custom py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={() => navigate('/admin/dashboard')}
                className="p-2 hover:bg-secondary rounded-lg transition-colors"
              >
                <ArrowLeft className="h-5 w-5" />
              </button>
              <div>
                <h1 className="text-2xl font-serif font-semibold">🏷️ POS-Artikel Mapping</h1>
                <p className="text-sm text-muted-foreground">
                  Verknüpfe Produkte mit ExpertOrder Kassensystem-Artikeln
                </p>
              </div>
            </div>

            <div className="flex gap-2">
              <button
                onClick={exportMappings}
                className="btn-secondary flex items-center gap-2"
              >
                <Download className="h-4 w-4" />
                Export
              </button>
              <button
                onClick={saveAllMappings}
                disabled={saving}
                className="btn-primary flex items-center gap-2 disabled:opacity-50"
              >
                <Save className="h-4 w-4" />
                {saving ? 'Speichere...' : 'Alle speichern'}
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="container-custom py-8">
        {/* Info Banner */}
        <div className="bg-orange-500/10 border border-orange-500/20 rounded-lg p-4 mb-6 flex gap-3">
          <AlertCircle className="h-5 w-5 text-orange-600 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="font-semibold text-orange-600 mb-1">Wichtig: POS-Item-IDs konfigurieren</h3>
            <p className="text-sm text-muted-foreground">
              Trage für jedes Produkt die exakte Artikel-ID aus dem ExpertOrder Kassensystem ein.
              Nur so können Bestellungen automatisch mit dem Kassensystem gemappt werden.
            </p>
          </div>
        </div>

        {/* Search */}
        <div className="mb-6">
          <Input
            type="text"
            placeholder="Produkt suchen..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="max-w-md"
          />
        </div>

        {/* Products Table */}
        <div className="bg-card border border-border rounded-xl overflow-hidden mb-8">
          <div className="p-4 border-b border-border bg-muted/50">
            <h2 className="font-semibold">Produkte ({filteredProducts.length})</h2>
          </div>
          
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-muted/30 border-b border-border">
                <tr>
                  <th className="px-4 py-3 text-left text-sm font-semibold">Produkt</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold">Kategorie</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold w-96">ExpertOrder Artikel-ID</th>
                  <th className="px-4 py-3 text-center text-sm font-semibold">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {filteredProducts.map((product) => {
                  const category = categories.find(c => c.id === product.category_id);
                  const hasPOSID = Boolean(product.pos_item_id);

                  return (
                    <tr key={product.id || product._id} className="hover:bg-muted/30">
                      <td className="px-4 py-3">
                        <div className="font-medium">{product.name}</div>
                        <div className="text-xs text-muted-foreground">
                          {product.price_medium && `Medium: €${product.price_medium}`}
                          {product.price_large && ` | Large: €${product.price_large}`}
                        </div>
                      </td>
                      <td className="px-4 py-3 text-sm text-muted-foreground">
                        {category?.name || 'N/A'}
                      </td>
                      <td className="px-4 py-3">
                        <input
                          type="text"
                          value={product.pos_item_id || ''}
                          onChange={(e) => updateProductPOSID(product.id || product._id, e.target.value)}
                          placeholder="z.B. BURGER_HAMBURGER_001"
                          className="w-full px-3 py-1.5 bg-background border border-border rounded text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                        />
                      </td>
                      <td className="px-4 py-3 text-center">
                        {hasPOSID ? (
                          <span className="px-2 py-1 bg-green-500/10 text-green-600 text-xs rounded-full font-medium">
                            ✓ Gemappt
                          </span>
                        ) : (
                          <span className="px-2 py-1 bg-red-500/10 text-red-600 text-xs rounded-full font-medium">
                            ⚠ Fehlt
                          </span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Modifier Groups */}
        <div className="space-y-6">
          <h2 className="text-lg font-semibold">Menü-Komponenten & Modifier Groups</h2>

          {modifierGroups.filter(g => g.name).map((group) => (
            <div key={group.id || group._id} className="bg-card border border-border rounded-xl overflow-hidden">
              <div className="p-4 border-b border-border bg-muted/50">
                <h3 className="font-semibold">{group.name}</h3>
                <p className="text-xs text-muted-foreground">Group ID: {group.id || 'N/A'}</p>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-muted/20">
                    <tr>
                      <th className="px-4 py-2 text-left text-sm font-medium">Option</th>
                      <th className="px-4 py-2 text-left text-sm font-medium w-96">ExpertOrder Artikel-ID</th>
                      <th className="px-4 py-2 text-center text-sm font-medium">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border">
                    {(group.options || []).map((option, idx) => {
                      const hasPOSID = Boolean(option.pos_item_id);

                      return (
                        <tr key={idx} className="hover:bg-muted/20">
                          <td className="px-4 py-2 text-sm">
                            {option.name}
                            {option.price > 0 && (
                              <span className="ml-2 text-xs text-muted-foreground">
                                (+€{option.price.toFixed(2)})
                              </span>
                            )}
                          </td>
                          <td className="px-4 py-2">
                            <input
                              type="text"
                              value={option.pos_item_id || ''}
                              onChange={(e) => updateModifierOptionPOSID(
                                group.id || group._id,
                                idx,
                                e.target.value
                              )}
                              placeholder="z.B. SIDES_FRIES_NORMAL"
                              className="w-full px-3 py-1.5 bg-background border border-border rounded text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                            />
                          </td>
                          <td className="px-4 py-2 text-center">
                            {hasPOSID ? (
                              <span className="px-2 py-1 bg-green-500/10 text-green-600 text-xs rounded-full">
                                ✓
                              </span>
                            ) : (
                              <span className="px-2 py-1 bg-red-500/10 text-red-600 text-xs rounded-full">
                                ⚠
                              </span>
                            )}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          ))}
        </div>

        {/* Stats */}
        <div className="mt-8 bg-muted/30 rounded-lg p-6">
          <h3 className="font-semibold mb-4">📊 Mapping-Status</h3>
          <div className="grid md:grid-cols-3 gap-4 text-sm">
            <div>
              <span className="text-muted-foreground">Produkte:</span>
              <span className="ml-2 font-semibold">
                {products.filter(p => p.pos_item_id).length} / {products.length} gemappt
              </span>
            </div>
            <div>
              <span className="text-muted-foreground">Modifier-Optionen:</span>
              <span className="ml-2 font-semibold">
                {modifierGroups.reduce((acc, g) => 
                  acc + (g.options || []).filter(o => o.pos_item_id).length, 0
                )} / {modifierGroups.reduce((acc, g) => acc + (g.options || []).length, 0)} gemappt
              </span>
            </div>
            <div>
              <span className="text-muted-foreground">Fortschritt:</span>
              <span className="ml-2 font-semibold text-primary">
                {Math.round(
                  (products.filter(p => p.pos_item_id).length / products.length) * 100
                )}%
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default POSItemMapping;
