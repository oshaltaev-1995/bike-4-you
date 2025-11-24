import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface Rental {
  id: number;
  user_id: number;
  equipment_id: number;
  start_time: string;
  end_time?: string | null;
  status: string;
  total_minutes?: number | null;
  total_price?: number | null;
  penalty_eur: number;
}

@Injectable({
  providedIn: 'root'
})
export class RentalService {

  private API_URL = environment.rentalApi;

  constructor(private http: HttpClient) {}

  getActive(userId: number): Observable<Rental[]> {
    return this.http.get<Rental[]>(`${this.API_URL}/rentals/active?user_id=${userId}`);
  }

  getHistory(userId: number): Observable<Rental[]> {
    return this.http.get<Rental[]>(`${this.API_URL}/rentals/history?user_id=${userId}`);
  }

  startRental(userId: number, equipmentId: number): Observable<Rental> {
    return this.http.post<Rental>(`${this.API_URL}/rentals/start`, {
      user_id: userId,
      equipment_id: equipmentId
    });
  }

  returnRental(id: number): Observable<Rental> {
    return this.http.post<Rental>(`${this.API_URL}/rentals/return/${id}`, {});
  }
}
