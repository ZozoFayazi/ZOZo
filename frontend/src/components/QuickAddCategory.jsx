import React, { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogDescription } from './ui/dialog';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { toast } from 'sonner';
import { useAdminAuth } from '../contexts/AdminAuthContext';

export default function QuickAddCategory({ open, onClose, onCategoryCreated }) {
  const { token } = useAdminAuth();
  const [name, setName] = useState('');
  const [loading, setLoading] = useState(false);

  const handleCreate = async () => {
    if (!name.trim()) {
      toast.error('Name ist erforderlich');
      return;
    }

    setLoading(true);
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
      
      // Auto-generate slug
      const slug = name.toLowerCase()
        .replace(/ä/g, 'ae').replace(/ö/g, 'oe').replace(/ü/g, 'ue').replace(/ß/g, 'ss')
        .replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');

      const response = await fetch(`${backendUrl}/api/admin/categories`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ name, slug, active: true })
      });

      if (response.ok) {
        const newCategory = await response.json();
        toast.success('Kategorie erstellt!');
        setName('');
        onCategoryCreated(newCategory);
        onClose();
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Fehler beim Erstellen');
      }
    } catch (error) {
      console.error('Error creating category:', error);
      toast.error('Fehler beim Erstellen der Kategorie');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setName('');
    onClose();
  };

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Schnell Kategorie erstellen</DialogTitle>
          <DialogDescription>
            Neue Kategorie erstellen und direkt auswählen
          </DialogDescription>
        </DialogHeader>

        <div className="py-4">
          <Label htmlFor="quick-category-name">Kategorie-Name *</Label>
          <Input
            id="quick-category-name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="z.B. Burger, Pizza, Salate"
            onKeyDown={(e) => {
              if (e.key === 'Enter' && name.trim()) {
                handleCreate();
              }
            }}
            autoFocus
            data-testid="quick-category-name-input"
          />
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={handleClose} disabled={loading}>
            Abbrechen
          </Button>
          <Button onClick={handleCreate} disabled={loading || !name.trim()} data-testid="quick-create-category-btn">
            {loading ? 'Erstellt...' : 'Erstellen'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
