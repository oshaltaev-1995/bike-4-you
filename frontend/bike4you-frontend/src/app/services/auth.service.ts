import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface User {
  id: number;
  name: string;
  email: string;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = environment.authApi;
  private storageKey = 'user';
  private currentUser: User | null = null;

  constructor(private http: HttpClient) {
    const raw = localStorage.getItem(this.storageKey);
    if (raw) {
      try {
        this.currentUser = JSON.parse(raw);
      } catch {
        this.currentUser = null;
        localStorage.removeItem(this.storageKey);
      }
    }
  }

  login(email: string): Observable<User> {
    return this.http.post<User>(`${this.apiUrl}/auth/login`, { email });
  }

  register(name: string, email: string): Observable<User> {
    return this.http.post<User>(`${this.apiUrl}/auth/register`, { name, email });
  }

  saveUser(user: User) {
    this.currentUser = user;
    localStorage.setItem(this.storageKey, JSON.stringify(user));
  }

  getUser(): User | null {
    return this.currentUser;
  }

  logout() {
    this.currentUser = null;
    localStorage.removeItem(this.storageKey);
  }
}
