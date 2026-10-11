# 5G Network Slicing Controller API

Ένα REST API για τη διαχείριση Network Slices σε δίκτυα 5G, αναπτυγμένο με **FastAPI** και **Python**.

Το σύστημα προσομοιώνει έναν Network Slice Controller που διαχειρίζεται εικονικούς πόρους (bandwidth, CPU, memory) και υποστηρίζει τους τρεις βασικούς τύπους υπηρεσιών 5G: **eMBB**, **mMTC** και **URLLC**.

---

## Τεχνολογίες

- **Python 3.10+**
- **FastAPI** — REST API framework
- **Uvicorn** — ASGI server
- **Pydantic** — Validation δεδομένων
- **Swagger UI** — Αυτόματη τεκμηρίωση (διαθέσιμη στο `/docs`)

---

## Διαθέσιμοι Πόροι (Προσομοίωση)

| Πόρος | Συνολική Χωρητικότητα |
|---|---|
| Bandwidth | 1000 Mbps |
| CPU Cores | 32 |
| Memory | 128 GB |

---

## Εγκατάσταση

**1. Κλωνοποίηση του repository**
```bash
git clone https://github.com/<username>/5G-Network-Slicing-API.git
cd 5G-Network-Slicing-API
```

**2. Εγκατάσταση dependencies**
```bash
pip install -r requirements.txt
```

**3. Εκκίνηση του server**
```bash
python -m uvicorn 5G_API:app --reload
```

**4. Άνοιγμα Swagger UI**

Μεταβείτε στο: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## Endpoints

| Μέθοδος | URL | Περιγραφή |
|---|---|---|
| `POST` | `/slices/` | Δημιουργία νέου Network Slice |
| `GET` | `/slices/{id}` | Ανάκτηση συγκεκριμένου Slice |
| `DELETE` | `/slices/{id}` | Διαγραφή Slice & αποδέσμευση πόρων |
| `GET` | `/network/` | Κατάσταση δικτύου & διαθέσιμοι πόροι |
| `GET` | `/recommend/{service_type}` | Προτεινόμενες τιμές QoS ανά τύπο υπηρεσίας |

---

## Παράδειγμα Χρήσης

**Δημιουργία ενός eMBB Slice:**
```json
POST /slices/
{
  "id": 1,
  "name": "VideoStreamingSlice",
  "service_type": "eMBB",
  "resources": {
    "bandwidth": 200,
    "MaxDevices": 500,
    "Cpu_Cores": 4,
    "memory": 16
  },
  "qos": {
    "priority": 5,
    "MaxLatency": 100,
    "ErrorRate": 0.001
  }
}
```

**Απάντηση:**
```json
{
  "status": "Slice Created Successfully!",
  "data": { ... },
  "remaining_resources": {
    "available_bandwidth": 800.0,
    "available_cpu_cores": 28,
    "available_memory": 112.0
  }
}
```

---

## Τύποι Υπηρεσιών 5G

| Τύπος | Περιγραφή | Max Latency | Error Rate |
|---|---|---|---|
| `eMBB` | Enhanced Mobile Broadband (streaming, video) | 100 ms | 0.001 |
| `mMTC` | Massive Machine-Type Communications (IoT) | 500 ms | 0.01 |
| `URLLC` | Ultra-Reliable Low-Latency (αυτόνομα οχήματα) | 1 ms | 0.00001 |

---

## Admission Control

Κατά τη δημιουργία ενός slice, το σύστημα ελέγχει:
1. **Μοναδικότητα ID** — δεν επιτρέπονται ίδια IDs
2. **Επάρκεια Bandwidth** — σύγκριση με διαθέσιμη χωρητικότητα
3. **Επάρκεια CPU Cores** — έλεγχος διαθέσιμων πυρήνων
4. **Επάρκεια Memory** — έλεγχος διαθέσιμης μνήμης

Αν αποτύχει οποιοσδήποτε έλεγχος → `HTTP 400 Bad Request`

---
