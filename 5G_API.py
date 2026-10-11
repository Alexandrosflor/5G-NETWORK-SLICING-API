from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field 
from typing import List, Optional
from enum import Enum


app = FastAPI(title = "5G Network Slicing Controller")

Total_Capacity_Mbps = 1000.0                                                                          # αρχικοποιούμε την συνολική χωρητικότητα στα 1000 Mbps
current_usage = 0.0

Cpu_Cores = 32                                                                                        # αρχικοποιούμε τους συνολικούς πυρήνες της CPU σε 32
current_cores = 0

Total_Memory_GB = 128.0                                                                               # αρχικοποιούμε την συνολική μνήμη σε 128 GB
current_memory = 0.0

class ServiceType(str, Enum):
    embb = "eMBB"
    mmtc = "mMTC"
    urllc = "URLLC"
    
class ComputeResources(BaseModel):                                                                    # περιέχει όλα τα απαιτούμενα τεχνικά χαρακτηριστικά ενός slice
    bandwidth: float = Field(gt=0, description="Εύρος Ζώνης του Slice σε Mbps")
    MaxDevices: int = Field(gt=0, description="Μέγιστος αριθμός συσκευών σε σύνδεση")
    Cpu_Cores: int = Field(gt=0, description="Απαιτούμενοι CPU Πυρήνες")
    memory: float = Field(gt=0, description="Απαιτούμενη Μνήμη σε GB")
    
class QosRequirements(BaseModel):                                                                     # περιέχει όλα τα χαρακτηριστικά QoS
    priority: int = Field(ge=1, le=10, description="Προτεραιότητα Slice από 1 έως 10")
    MaxLatency: float = Field(gt=0, description="Μέγιστη Καθυστέρηση σε ms")
    ErrorRate: float = Field(gt=0, le=1, description="Packet Error Rate (0.0 - 1.0)")


class NetworkSlice(BaseModel):
    id: int 
    name: str
    service_type: ServiceType 
    resources: ComputeResources
    qos: QosRequirements
    
slices_database: List[NetworkSlice] = []

def get_available_resources():                                                                        # μας επιστρέφει τους διαθέσιμους πόρους
    return {
        "available_bandwidth": Total_Capacity_Mbps - current_usage,
        "available_cpu_cores": Cpu_Cores - current_cores,
        "available_memory": Total_Memory_GB - current_memory
    }

def get_recommended_Qos(service_type: ServiceType) -> dict:                                           # μας επιστρέφει κάποιες προτεινόμενες τιμές αναλόγως το Service Type
    recommendations = {
        ServiceType.embb: {
            "Max_Latency": 100.0,
            "Error_Rate": 0.001,
            "priority": 5,
            "note": "Το eMBB απαιτεί υψηλό bandwidth, έχει μέτριο latency και αφορά live streaming και videos."
        },
        ServiceType.urllc: {
            "Max_Latency": 1.0,
            "Error_Rate": 0.00001,
            "priority": 10,
            "note": "Το URLLC έχει αρκετά χαμηλό latency, σχεδόν μηδενικό Error Rate και αφορά αυτόνομα οχήματα."
        },
        ServiceType.mmtc: {
            "Max_Latency": 500.0,
            "Error_Rate": 0.01,
            "priority": 3,
            "note": "Το mMTC έχει πολλές συσκευές, χαμηλές απαιτήσεις σε latency και αφορά IoT sensors"
        }
    }
    return recommendations[service_type]

@app.get("/recommend/{service_type}")                                                                  # μας εμφανίζει τις προτεινόμενες QoS τιμές
def recommend_qos(service_type: ServiceType):
    return get_recommended_Qos(service_type)

@app.post("/slices/")                                                                                            # αφορά τη δημιουργία του slice 
def create_slice(slice_data: NetworkSlice):
    global current_usage, current_cores, current_memory
    
    if any(s.id == slice_data.id for s in slices_database):                                                      # ελέγχει αν υπάρχει το Slice ID
        raise HTTPException(status_code=400, detail="Slice ID already exists.")
    
    available = get_available_resources()
    
    if slice_data.resources.bandwidth > available["available_bandwidth"]:                                           # ελέγχει αν επαρκεί το bandwidth
        raise HTTPException(status_code=400, detail=f"Available: {available['available_bandwidth']} Mbps.")
    
    if slice_data.resources.Cpu_Cores > available["available_cpu_cores"]:                                          # ελέγχει αν επαρκούν οι CPU πυρήνες
        raise HTTPException(status_code=400, detail=f"Available: {available['available_cpu_cores']} cores.")
    
    if slice_data.resources.memory > available["available_memory"]:                                                 # ελέγχει αν επαρκεί η μνήμη
        raise HTTPException(status_code=400, detail=f"Available: {available['available_memory']} GB.")
    
    slices_database.append(slice_data)                                                                              # δεσμεύονται οι πόροι
    current_usage += slice_data.resources.bandwidth
    current_cores += slice_data.resources.Cpu_Cores
    current_memory += slice_data.resources.memory
    
    return {
        "status": "Slice Created Successfully!",
        "data": slice_data,
        "remaining_resources": get_available_resources(),
    }
                                                                                              
@app.get("/slices/{id}", response_model = NetworkSlice)                                                            # αφορά ένα συγκεκριμένο slice
def get_slice(id: int):
    slice_ = next((s for s in slices_database if s.id == id), None)
    if not slice_:
        raise HTTPException(status_code=400, detail="Slice not found.")
    return slice_

    
@app.get("/network/")                                                                                           # αφορά την συνολική κατάσταση του δικτύου 
def get_status():
    return{
        "Total_Capacity": {
            "bandwidth": Total_Capacity_Mbps,
            "cpu_cores": Cpu_Cores,
            "memory": Total_Memory_GB
        },
        "Current_Usage": {
            "bandwidth": current_usage,
            "cpu_cores": current_cores,
            "memory": current_memory   
        },
        "Available": get_available_resources(),
        "Active_Slices": len(slices_database),
        "Active_slices_ids": [s.id for s in slices_database]
    }


@app.delete("/slices/{id}")                                                                              # αφορά την διαγραφή ενός slice 
def delete_slice(id: int):
    global current_usage, current_cores, current_memory
    
    removed_slice = next((s for s in slices_database if s.id == id), None)
    if not removed_slice:
        raise HTTPException(status_code = 400, detail = "Slice not found!")                              # ελέγχει αν υπάρχει το slice
    
    slices_database.remove(removed_slice)
    current_usage -= removed_slice.resources.bandwidth                                                      # αφαιρούνται οι τιμές του διεγραμμένου slice από τις αντίστοιχες μεταβλητές
    current_cores -= removed_slice.resources.Cpu_Cores
    current_memory -= removed_slice.resources.memory
    
    
    return{
        "status": "Slice Deleted Successfully!",
        "removed_id": id,
        "released_resources": {
            "bandwidth": removed_slice.resources.bandwidth,
            "cpu_cores": removed_slice.resources.Cpu_Cores,
            "memory": removed_slice.resources.memory
        },
        "remaining_resources": get_available_resources()
    }

    
