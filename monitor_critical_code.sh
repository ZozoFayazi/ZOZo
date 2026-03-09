#!/bin/bash
# 🔍 CONTINUOUS MONITORING
# Kann als Cronjob eingerichtet werden für kontinuierliche Überwachung

LOGFILE="/app/logs/critical_validation_$(date +%Y%m%d).log"
mkdir -p /app/logs

echo "================================================================" >> $LOGFILE
echo "Validation Check: $(date)" >> $LOGFILE
echo "================================================================" >> $LOGFILE

# Validation ausführen
python /app/validate_critical_code.py >> $LOGFILE 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Status: OK" >> $LOGFILE
else
    echo "❌ Status: FAILED" >> $LOGFILE
    echo "" >> $LOGFILE
    
    # ALERT senden (optional)
    echo "🚨 CRITICAL CODE VALIDATION FAILED!" >> $LOGFILE
    echo "Siehe Details oben." >> $LOGFILE
    
    # Optional: E-Mail-Alert senden
    # mail -s "ZOZO CRITICAL CODE ALERT" admin@zozo-burger.de < $LOGFILE
fi

echo "" >> $LOGFILE

# Logs älter als 30 Tage löschen
find /app/logs -name "critical_validation_*.log" -mtime +30 -delete
