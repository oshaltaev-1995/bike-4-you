import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';
import { Observable } from 'rxjs';

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

  constructor(private http: HttpClient) {}

  register(name: string, email: string): Observable<User> {
    return this.http.post<User>(`${this.apiUrl}/auth/register`, { name, email });
  }

  login(email: string): Observable<User> {
    return this.http.post<User>(`${this.apiUrl}/auth/login`, { email });
  }

  saveUser(user: User) {
    localStorage.setItem('bike4you_user', JSON.stringify(user));
  }

  getUser(): User | null {
    const data = localStorage.getItem('bike4you_user');
    return data ? JSON.parse(data) : null;
  }

  logout() {
    localStorage.removeItem('bike4you_user');
  }
}
