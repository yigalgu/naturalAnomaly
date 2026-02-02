---
description: תוכנית יישום מערכת זיהוי אנומליות אוטומטית
---

# 🎯 מטרה
הוספת מערכת זיהוי אנומליות אוטומטית לפרויקט Natural Anomaly Detection

## 📊 מצב נוכחי
✅ Backend עם FastAPI + YOLO  
✅ זיהוי רכבים (detection only)  
✅ סטטיסטיקות בסיסיות  
✅ צ'אט AI עם Ollama  
✅ שיחה מתמשכת עם זיכרון

## 🚀 4 השלבים

### שלב 1: שדרוג ל-Tracking
**קובץ:** `backend_new/video_processor.py`

**שינויים:**
- להחליף `model()` ב-`model.track()`
- לשמור `track_id` לכל רכב
- לבנות מסלולים (trajectories) - רשימת מיקומים לאורך זמן

**תוצאה:**
```python
trajectories = {
    5: {
        "track_id": 5,
        "class_name": "car",
        "positions": [(100, 200), (105, 205), (110, 210)],
        "timestamps": [0.0, 0.33, 0.66]
    }
}
```

### שלב 2: אלגוריתמים לזיהוי אנומליות
**קובץ חדש:** `backend_new/anomaly_detector.py`

**אנומליות לזיהוי:**

| אנומליה | אלגוריתם | סף |
|---------|-----------|-----|
| 🚗 עצירה חריגה | מרחק תנועה < 20 פיקסלים ב-3+ שניות | 3 שניות |
| 🏃 מהירות חריגה | תנועה > 200 פיקסלים בין פריימים | 200px |
| 📊 שינוי פתאומי | קפיצה של 3x במספר רכבים בסגמנט | 3x |

**פונקציות:**
```python
def detect_stopped_vehicle(trajectory) -> Optional[Anomaly]
def detect_high_speed(trajectory) -> Optional[Anomaly]
def detect_traffic_spike(segments) -> List[Anomaly]
```

### שלב 3: שמירה במסד נתונים
**קובץ:** `backend_new/database.py`

**טבלה חדשה:**
```python
class Anomaly(Base):
    id = Column(Integer, primary_key=True)
    video_filename = Column(String)
    timestamp = Column(Float)
    anomaly_type = Column(String)  # "stopped", "speeding", "spike"
    severity = Column(String)  # "low", "medium", "high"
    description = Column(String)
    track_id = Column(Integer, nullable=True)
    metadata = Column(JSON)
```

### שלב 4: שילוב בצ'אט
**קבצים:** `backend_new/ai_assistant.py`, `backend_new/main.py`

**שינויים:**
- להוסיף אנומליות ל-context של הבוט
- לעדכן את ה-Prompt להתייחס לאנומליות
- להוסיף endpoint: `GET /api/anomalies/{filename}`

**דוגמת context:**
```
Anomalies found: 2
1. Stopped vehicle at 47.0s (severity: medium)
2. High speed at 83.5s (severity: low)
```

## 📁 מבנה קבצים

```
backend_new/
├── video_processor.py      # ✏️ שדרוג ל-tracking
├── anomaly_detector.py     # 🆕 קובץ חדש
├── database.py             # ✏️ הוספת טבלת Anomaly
├── ai_assistant.py         # ✏️ עדכון context
└── main.py                 # ✏️ endpoint חדש
```

## 🎬 תוצאה סופית

שיחה לדוגמה:

```
👤 "יש משהו חריג בסרטון?"
🤖 "כן, מצאתי 2 אנומליות:
    
    1. ⚠️ עצירה חריגה בשנייה 47
       רכב עצר באמצע הנתיב למשך 12 שניות
    
    2. 🏃 מהירות גבוהה בשנייה 1:23
       רכב נע במהירות פי 2 מהממוצע"
```

## 🌿 Git Workflow

```bash
# יצירת branch חדש
git checkout -b feature/anomaly-detection

# עבודה...
git add .
git commit -m "Add anomaly detection system"

# מיזוג חזרה ל-main
git checkout main
git merge feature/anomaly-detection
git push
```
