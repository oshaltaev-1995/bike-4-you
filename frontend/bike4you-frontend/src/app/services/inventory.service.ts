import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { environment } from '../../environments/environment';
import { Observable } from 'rxjs';

export interface Equipment {
  id: number;
  type: string;
  status: string;
  location: string;
  created_at: string;
  hourly_rate: number;
  image_url?: string | null;
}

@Injectable({
  providedIn: 'root'
})
export class InventoryService {
  private apiUrl = environment.inventoryApi;

  constructor(private http: HttpClient) {}

  getAll(filters?: { status?: string; type?: string }): Observable<Equipment[]> {
    let params = new HttpParams();

    if (filters?.status && filters.status !== 'all') {
      params = params.set('status', filters.status);
    }

    if (filters?.type && filters.type !== 'all') {
      params = params.set('type', filters.type);
    }

    return this.http.get<Equipment[]>(`${this.apiUrl}/equipment`, { params });
  }

  getById(id: number): Observable<Equipment> {
    return this.http.get<Equipment>(`${this.apiUrl}/equipment/${id}`);
  }

  add(data: { type: string; status: string; location: string; image_url?: string }): Observable<Equipment> {
    return this.http.post<Equipment>(`${this.apiUrl}/equipment/add`, data);
  }

  updateStatus(id: number, status: string): Observable<Equipment> {
    return this.http.post<Equipment>(`${this.apiUrl}/equipment/update`, { id, status });
  }
}
