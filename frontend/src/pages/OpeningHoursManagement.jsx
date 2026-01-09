import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { toast } from 'sonner';
import { 
  Clock, 
  Calendar, 
  Plus, 
  Trash2, 
  Save,
  AlertCircle,
  CheckCircle
} from 'lucide-react';

const DAYS_OF_WEEK = [
  { key: 'monday', label: 'Montag' },
  { key: 'tuesday', label: 'Dienstag' },
  { key: 'wednesday', label: 'Mittwoch' },
  { key: 'thursday', label: 'Donnerstag' },
  { key: 'friday', label: 'Freitag' },
  { key: 'saturday', label: 'Samstag' },
  { key: 'sunday', label: 'Sonntag' }
];

const OpeningHoursManagement = () => {
  const [locations, setLocations] = useState([]);
  const [selectedLocation, setSelectedLocation] = useState(null);
  const [weeklySchedule, setWeeklySchedule] = useState([]);
  const [specialDays, setSpecialDays] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  
  // Special day form
  const [newSpecialDay, setNewSpecialDay] = useState({
    date: '',
    is_open: true,
    time_slots: [{ start: '11:00', end: '22:00' }],
    note: ''
  });

  const backendUrl = process.env.REACT_APP_BACKEND_URL;
  const token = localStorage.getItem('token');

  // Load locations
  useEffect(() => {
    fetchLocations();
  }, []);

  // Load opening hours when location selected
  useEffect(() => {
    if (selectedLocation) {
      fetchOpeningHours();
    }
  }, [selectedLocation]);

  const fetchLocations = async () => {
    try {
      const response = await fetch(`${backendUrl}/api/locations`);
      const data = await response.json();
      setLocations(data);
      if (data.length > 0) {
        setSelectedLocation(data[0].slug);
      }
    } catch (error) {
      console.error('Fetch locations error:', error);
      toast.error('Fehler beim Laden der Standorte');
    }
  };

  const fetchOpeningHours = async () => {
    if (!selectedLocation) return;
    
    try {
      setLoading(true);
      const response = await fetch(`${backendUrl}/api/locations/${selectedLocation}/opening-hours`);
      const data = await response.json();
      
      // Initialize weekly schedule
      let schedule = data.weekly_schedule || [];
      
      // Ensure all days exist
      if (schedule.length === 0) {
        schedule = DAYS_OF_WEEK.map(day => ({
          day: day.key,
          is_open: true,
          time_slots: [{ start: '11:00', end: '22:00' }]
        }));
      }
      
      setWeeklySchedule(schedule);
      setSpecialDays(data.special_days || []);
    } catch (error) {
      console.error('Fetch opening hours error:', error);
      toast.error('Fehler beim Laden der Öffnungszeiten');
    } finally {
      setLoading(false);
    }
  };

  const updateDayStatus = (dayKey, isOpen) => {
    setWeeklySchedule(prev => prev.map(day => 
      day.day === dayKey ? { ...day, is_open: isOpen } : day
    ));
  };

  const updateTimeSlot = (dayKey, slotIndex, field, value) => {
    setWeeklySchedule(prev => prev.map(day => {
      if (day.day !== dayKey) return day;
      
      const newSlots = [...day.time_slots];
      newSlots[slotIndex] = { ...newSlots[slotIndex], [field]: value };
      return { ...day, time_slots: newSlots };
    }));
  };

  const addTimeSlot = (dayKey) => {
    setWeeklySchedule(prev => prev.map(day => {
      if (day.day !== dayKey) return day;
      
      return {
        ...day,
        time_slots: [...day.time_slots, { start: '17:00', end: '22:00' }]
      };
    }));
  };

  const removeTimeSlot = (dayKey, slotIndex) => {
    setWeeklySchedule(prev => prev.map(day => {
      if (day.day !== dayKey) return day;
      
      const newSlots = day.time_slots.filter((_, idx) => idx !== slotIndex);
      return { ...day, time_slots: newSlots.length > 0 ? newSlots : [{ start: '11:00', end: '22:00' }] };
    }));
  };

  const saveWeeklySchedule = async () => {
    if (!selectedLocation) return;
    
    try {
      setSaving(true);
      const response = await fetch(
        `${backendUrl}/api/admin/locations/${selectedLocation}/opening-hours`,
        {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({ weekly_schedule: weeklySchedule })
        }
      );

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Fehler beim Speichern');
      }

      toast.success('Öffnungszeiten gespeichert');
      fetchOpeningHours();
    } catch (error) {
      console.error('Save error:', error);
      toast.error(error.message);
    } finally {
      setSaving(false);
    }
  };

  const addSpecialDay = async () => {
    if (!newSpecialDay.date) {
      toast.error('Bitte Datum auswählen');
      return;
    }

    try {
      const response = await fetch(
        `${backendUrl}/api/admin/locations/${selectedLocation}/special-days`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify(newSpecialDay)
        }
      );

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Fehler');
      }

      toast.success('Sondertag hinzugefügt');
      setNewSpecialDay({
        date: '',
        is_open: true,
        time_slots: [{ start: '11:00', end: '22:00' }],
        note: ''
      });
      fetchOpeningHours();
    } catch (error) {
      console.error('Add special day error:', error);
      toast.error(error.message);
    }
  };

  const deleteSpecialDay = async (dateStr) => {
    if (!window.confirm(`Sondertag ${dateStr} wirklich löschen?`)) return;

    try {
      const response = await fetch(
        `${backendUrl}/api/admin/locations/${selectedLocation}/special-days/${dateStr}`,
        {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      if (!response.ok) throw new Error('Fehler beim Löschen');

      toast.success('Sondertag gelöscht');
      fetchOpeningHours();
    } catch (error) {
      console.error('Delete special day error:', error);
      toast.error(error.message);
    }
  };

  if (loading) {
    return <div className="p-6">Lädt...</div>;
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">Öffnungszeiten</h1>
        <p className="text-gray-600 mt-1">Verwalten Sie Wochenplan und Sondertage</p>
      </div>

      {/* Location Selector */}
      <Card>
        <CardContent className="pt-6">
          <Label>Standort</Label>
          <select
            value={selectedLocation || ''}
            onChange={(e) => setSelectedLocation(e.target.value)}
            className="w-full mt-2 px-3 py-2 border rounded-lg"
          >
            {locations.map(loc => (
              <option key={loc.slug} value={loc.slug}>{loc.name}</option>
            ))}
          </select>
        </CardContent>
      </Card>

      {/* Tabs */}
      <Tabs defaultValue="weekly" className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="weekly">
            <Clock className="w-4 h-4 mr-2" />
            Wochenplan
          </TabsTrigger>
          <TabsTrigger value="special">
            <Calendar className="w-4 h-4 mr-2" />
            Sondertage
          </TabsTrigger>
        </TabsList>

        {/* Weekly Schedule Tab */}
        <TabsContent value="weekly">
          <Card>
            <CardHeader>
              <CardTitle>Standard-Wochenplan</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {DAYS_OF_WEEK.map(({ key, label }) => {
                const dayData = weeklySchedule.find(d => d.day === key) || {
                  day: key,
                  is_open: true,
                  time_slots: [{ start: '11:00', end: '22:00' }]
                };

                return (
                  <div key={key} className="p-4 border rounded-lg space-y-3">
                    {/* Day Header */}
                    <div className="flex items-center justify-between">
                      <h3 className="font-semibold">{label}</h3>
                      <div className="flex items-center gap-2">
                        <Switch
                          checked={dayData.is_open}
                          onCheckedChange={(checked) => updateDayStatus(key, checked)}
                        />
                        <span className="text-sm">
                          {dayData.is_open ? 'Geöffnet' : 'Geschlossen'}
                        </span>
                      </div>
                    </div>

                    {/* Time Slots */}
                    {dayData.is_open && (
                      <div className="space-y-2">
                        {dayData.time_slots.map((slot, idx) => (
                          <div key={idx} className="flex items-center gap-2">
                            <Input
                              type="time"
                              value={slot.start}
                              onChange={(e) => updateTimeSlot(key, idx, 'start', e.target.value)}
                              className="w-32"
                            />
                            <span>bis</span>
                            <Input
                              type="time"
                              value={slot.end}
                              onChange={(e) => updateTimeSlot(key, idx, 'end', e.target.value)}
                              className="w-32"
                            />
                            {dayData.time_slots.length > 1 && (
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => removeTimeSlot(key, idx)}
                              >
                                <Trash2 className="w-4 h-4" />
                              </Button>
                            )}
                          </div>
                        ))}
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => addTimeSlot(key)}
                          className="mt-2"
                        >
                          <Plus className="w-4 h-4 mr-2" />
                          Zeitfenster hinzufügen
                        </Button>
                      </div>
                    )}
                  </div>
                );
              })}

              <Button
                onClick={saveWeeklySchedule}
                disabled={saving}
                className="w-full"
                size="lg"
              >
                {saving ? 'Speichert...' : (
                  <>
                    <Save className="w-4 h-4 mr-2" />
                    Wochenplan speichern
                  </>
                )}
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Special Days Tab */}
        <TabsContent value="special">
          <Card>
            <CardHeader>
              <CardTitle>Sondertag hinzufügen</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Date Picker */}
              <div>
                <Label>Datum</Label>
                <Input
                  type="date"
                  value={newSpecialDay.date}
                  onChange={(e) => setNewSpecialDay(prev => ({ ...prev, date: e.target.value }))}
                  className="mt-2"
                  min={new Date().toISOString().split('T')[0]}
                />
              </div>

              {/* Open/Closed Toggle */}
              <div className="flex items-center justify-between">
                <Label>Status</Label>
                <div className="flex items-center gap-2">
                  <Switch
                    checked={newSpecialDay.is_open}
                    onCheckedChange={(checked) => setNewSpecialDay(prev => ({ ...prev, is_open: checked }))}
                  />
                  <span className="text-sm">
                    {newSpecialDay.is_open ? 'Geöffnet' : 'Geschlossen'}
                  </span>
                </div>
              </div>

              {/* Time Slots (if open) */}
              {newSpecialDay.is_open && (
                <div>
                  <Label>Öffnungszeiten</Label>
                  <div className="space-y-2 mt-2">
                    {newSpecialDay.time_slots.map((slot, idx) => (
                      <div key={idx} className="flex items-center gap-2">
                        <Input
                          type="time"
                          value={slot.start}
                          onChange={(e) => {
                            const newSlots = [...newSpecialDay.time_slots];
                            newSlots[idx].start = e.target.value;
                            setNewSpecialDay(prev => ({ ...prev, time_slots: newSlots }));
                          }}
                          className="w-32"
                        />
                        <span>bis</span>
                        <Input
                          type="time"
                          value={slot.end}
                          onChange={(e) => {
                            const newSlots = [...newSpecialDay.time_slots];
                            newSlots[idx].end = e.target.value;
                            setNewSpecialDay(prev => ({ ...prev, time_slots: newSlots }));
                          }}
                          className="w-32"
                        />
                        {newSpecialDay.time_slots.length > 1 && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => {
                              const newSlots = newSpecialDay.time_slots.filter((_, i) => i !== idx);
                              setNewSpecialDay(prev => ({ ...prev, time_slots: newSlots }));
                            }}
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        )}
                      </div>
                    ))}
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        setNewSpecialDay(prev => ({
                          ...prev,
                          time_slots: [...prev.time_slots, { start: '17:00', end: '22:00' }]
                        }));
                      }}
                    >
                      <Plus className="w-4 h-4 mr-2" />
                      Zeitfenster hinzufügen
                    </Button>
                  </div>
                </div>
              )}

              {/* Note */}
              <div>
                <Label>Notiz (optional)</Label>
                <Input
                  value={newSpecialDay.note}
                  onChange={(e) => setNewSpecialDay(prev => ({ ...prev, note: e.target.value }))}
                  placeholder="z.B. Weihnachten, Feiertag, Betriebsfeier"
                  className="mt-2"
                />
              </div>

              <Button onClick={addSpecialDay} className="w-full">
                <Plus className="w-4 h-4 mr-2" />
                Sondertag hinzufügen
              </Button>
            </CardContent>
          </Card>

          {/* Special Days List */}
          <Card className="mt-4">
            <CardHeader>
              <CardTitle>Gespeicherte Sondertage</CardTitle>
            </CardHeader>
            <CardContent>
              {specialDays.length === 0 ? (
                <p className="text-center text-gray-500 py-8">Keine Sondertage definiert</p>
              ) : (
                <div className="space-y-3">
                  {specialDays
                    .sort((a, b) => a.date.localeCompare(b.date))
                    .map(day => (
                      <div
                        key={day.date}
                        className="flex items-center justify-between p-4 border rounded-lg"
                      >
                        <div className="flex-1">
                          <div className="flex items-center gap-3">
                            <Calendar className="w-4 h-4 text-gray-500" />
                            <span className="font-semibold">
                              {new Date(day.date + 'T12:00:00').toLocaleDateString('de-DE', {
                                weekday: 'short',
                                year: 'numeric',
                                month: 'long',
                                day: 'numeric'
                              })}
                            </span>
                            {day.note && (
                              <span className="text-sm text-gray-600">({day.note})</span>
                            )}
                          </div>
                          
                          {day.is_open ? (
                            <div className="mt-2 flex items-center gap-2 text-sm">
                              <CheckCircle className="w-4 h-4 text-green-500" />
                              <span>
                                {day.time_slots.map(slot => `${slot.start}–${slot.end}`).join(', ')}
                              </span>
                            </div>
                          ) : (
                            <div className="mt-2 flex items-center gap-2 text-sm text-red-600">
                              <AlertCircle className="w-4 h-4" />
                              <span>Geschlossen</span>
                            </div>
                          )}
                        </div>

                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => deleteSpecialDay(day.date)}
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default OpeningHoursManagement;
