import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';
import { Observable } from 'rxjs';

export interface Rental {
  id: number;
  user_id: number;
  equipment_id: number;
  start_time: string;
  end_time: string | null;
  status: string;
  total_minutes: number | null;
}

@Injectable({
  providedIn: 'root'
})
export class RentalService {
  private apiUrl = environment.rentalApi;

  constructor(private http: HttpClient) {}

  rent(user_id: number, equipment_id: number): Observable<Rental> {
    return this.http.post<Rental>(`${this.apiUrl}/rent`, { user_id, equipment_id });
  }

  return(rental_id: number): Observable<Rental> {
    return this.http.post<Rental>(`${this.apiUrl}/return`, { rental_id });
  }

  getHistory(user_id: number): Observable<Rental[]> {
    return this.http.get<Rental[]>(`${this.apiUrl}/history/${user_id}`);
  }
}
