import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';
import { Observable } from 'rxjs';

export interface Equipment {
  id: number;
  type: string;
  status: string;
  location: string;
  created_at: string; // ISO-строка времени от бэкенда
}

@Injectable({
  providedIn: 'root'
})
export class InventoryService {
  private apiUrl = environment.inventoryApi;

  constructor(private http: HttpClient) {}

  getAll(): Observable<Equipment[]> {
    return this.http.get<Equipment[]>(`${this.apiUrl}/equipment`);
  }

  updateStatus(id: number, status: string): Observable<Equipment> {
    return this.http.post<Equipment>(`${this.apiUrl}/equipment/update`, { id, status });
  }
}
