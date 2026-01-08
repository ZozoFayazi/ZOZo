import React, { useState, useEffect } from 'react';
import { useAdminAuth } from '../contexts/AdminAuthContext';
import AdminLayout from '../components/AdminLayout';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '../components/ui/dialog';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../components/ui/table';
import { toast } from 'sonner';
import { Plus, Edit, Trash2, GripVertical } from 'lucide-react';
import { DndContext, closestCenter, KeyboardSensor, PointerSensor, useSensor, useSensors } from '@dnd-kit/core';
import { arrayMove, SortableContext, sortableKeyboardCoordinates, useSortable, verticalListSortingStrategy } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';

function SortableCategoryRow({ category, onEdit, onDelete }) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({ id: category.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  };

  return (
    <TableRow ref={setNodeRef} style={style}>
      <TableCell className="w-10">
        <button {...attributes} {...listeners} className="cursor-move p-2 hover:bg-accent rounded">
          <GripVertical className="h-4 w-4 text-muted-foreground" />
        </button>
      </TableCell>
      <TableCell className="font-medium">{category.name}</TableCell>
      <TableCell className="text-muted-foreground">{category.slug}</TableCell>
      <TableCell className="text-center">{category.order || 0}</TableCell>
      <TableCell className="text-right">
        <div className="flex gap-2 justify-end">
          <Button variant="outline" size="sm" onClick={() => onEdit(category)}>
            <Edit className="h-4 w-4" />
          </Button>
          <Button variant="outline" size="sm" onClick={() => onDelete(category.id)}>
            <Trash2 className="h-4 w-4 text-destructive" />
          </Button>
        </div>
      </TableCell>
    </TableRow>
  );
}

export default function CategoryManagement() {
  const { token } = useAdminAuth();
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingCategory, setEditingCategory] = useState(null);
  const [formData, setFormData] = useState({ name: '', slug: '' });
  const [saving, setSaving] = useState(false);

  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates })
  );

  useEffect(() => {
    fetchCategories();
  }, []);

  const fetchCategories = async () => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
      const response = await fetch(`${backendUrl}/api/categories`);
      const data = await response.json();
      setCategories(data.categories || []);
    } catch (error) {
      console.error('Error fetching categories:', error);
      toast.error('Fehler beim Laden der Kategorien');
    } finally {
      setLoading(false);
    }
  };

  const handleDragEnd = async (event) => {
    const { active, over } = event;

    if (active.id !== over.id) {
      const oldIndex = categories.findIndex(c => c.id === active.id);
      const newIndex = categories.findIndex(c => c.id === over.id);

      const newOrder = arrayMove(categories, oldIndex, newIndex);
      setCategories(newOrder);

      // Update order in backend
      try {
        const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
        const updates = newOrder.map((cat, index) => ({
          id: cat.id,
          order: index
        }));

        await fetch(`${backendUrl}/api/admin/categories/reorder`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({ categories: updates })
        });

        toast.success('Reihenfolge gespeichert');
      } catch (error) {
        console.error('Error saving order:', error);
        toast.error('Fehler beim Speichern der Reihenfolge');
        fetchCategories(); // Reload on error
      }
    }
  };

  const handleCreate = () => {
    setEditingCategory(null);
    setFormData({ name: '', slug: '' });
    setDialogOpen(true);
  };

  const handleEdit = (category) => {
    setEditingCategory(category);
    setFormData({ name: category.name, slug: category.slug });
    setDialogOpen(true);
  };

  const handleSave = async () => {
    if (!formData.name.trim()) {
      toast.error('Name ist erforderlich');
      return;
    }

    setSaving(true);
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
      const url = editingCategory
        ? `${backendUrl}/api/admin/categories/${editingCategory.id}`
        : `${backendUrl}/api/admin/categories`;

      const method = editingCategory ? 'PATCH' : 'POST';

      // Auto-generate slug if not provided
      const slug = formData.slug || formData.name.toLowerCase()
        .replace(/ä/g, 'ae').replace(/ö/g, 'oe').replace(/ü/g, 'ue').replace(/ß/g, 'ss')
        .replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');

      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ ...formData, slug })
      });

      if (response.ok) {
        toast.success(editingCategory ? 'Kategorie aktualisiert' : 'Kategorie erstellt');
        setDialogOpen(false);
        fetchCategories();
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Fehler beim Speichern');
      }
    } catch (error) {
      console.error('Error saving category:', error);
      toast.error('Fehler beim Speichern');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (categoryId) => {
    if (!window.confirm('Kategorie wirklich löschen? Produkte in dieser Kategorie bleiben erhalten.')) {
      return;
    }

    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
      const response = await fetch(`${backendUrl}/api/admin/categories/${categoryId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        toast.success('Kategorie gelöscht');
        fetchCategories();
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Fehler beim Löschen');
      }
    } catch (error) {
      console.error('Error deleting category:', error);
      toast.error('Fehler beim Löschen');
    }
  };

  if (loading) {
    return (
      <AdminLayout>
        <div className="flex items-center justify-center h-64">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      </AdminLayout>
    );
  }

  return (
    <AdminLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Kategorien</h1>
            <p className="text-muted-foreground mt-2">Kategorien für Speisekarte verwalten</p>
          </div>
          <Button onClick={handleCreate} data-testid="create-category-btn">
            <Plus className="h-4 w-4 mr-2" />
            Neue Kategorie
          </Button>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Alle Kategorien ({categories.length})</CardTitle>
          </CardHeader>
          <CardContent>
            {categories.length === 0 ? (
              <div className="text-center py-12 text-muted-foreground">
                <p>Keine Kategorien vorhanden</p>
                <Button onClick={handleCreate} variant="outline" className="mt-4">
                  <Plus className="h-4 w-4 mr-2" />
                  Erste Kategorie erstellen
                </Button>
              </div>
            ) : (
              <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="w-10"></TableHead>
                      <TableHead>Name</TableHead>
                      <TableHead>Slug</TableHead>
                      <TableHead className="text-center">Reihenfolge</TableHead>
                      <TableHead className="text-right">Aktionen</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    <SortableContext items={categories.map(c => c.id)} strategy={verticalListSortingStrategy}>
                      {categories.map((category) => (
                        <SortableCategoryRow
                          key={category.id}
                          category={category}
                          onEdit={handleEdit}
                          onDelete={handleDelete}
                        />
                      ))}
                    </SortableContext>
                  </TableBody>
                </Table>
              </DndContext>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Create/Edit Dialog */}
      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{editingCategory ? 'Kategorie bearbeiten' : 'Neue Kategorie'}</DialogTitle>
            <DialogDescription>
              {editingCategory ? 'Kategorie-Informationen aktualisieren' : 'Neue Kategorie für Speisekarte erstellen'}
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            <div>
              <Label htmlFor="name">Name *</Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="z.B. Burger, Pizza, Pasta"
                data-testid="category-name-input"
              />
            </div>

            <div>
              <Label htmlFor="slug">Slug (optional)</Label>
              <Input
                id="slug"
                value={formData.slug}
                onChange={(e) => setFormData({ ...formData, slug: e.target.value })}
                placeholder="Auto-generiert wenn leer"
                data-testid="category-slug-input"
              />
              <p className="text-xs text-muted-foreground mt-1">
                Wird automatisch aus dem Namen generiert wenn leer gelassen
              </p>
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setDialogOpen(false)} disabled={saving}>
              Abbrechen
            </Button>
            <Button onClick={handleSave} disabled={saving} data-testid="save-category-btn">
              {saving ? 'Speichert...' : editingCategory ? 'Aktualisieren' : 'Erstellen'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </AdminLayout>
  );
}
