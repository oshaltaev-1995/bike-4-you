import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { environment } from '../../environments/environment';
import { Observable, tap } from 'rxjs';

export interface User {
  id: number;
  name: string;
  email: string;
  role: string;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {

  private apiUrl = environment.authApi;

  private userKey = 'user';
  private tokenKey = 'access_token';

  private currentUser: User | null = null;

  constructor(private http: HttpClient) {
    const u = localStorage.getItem(this.userKey);
    const t = localStorage.getItem(this.tokenKey);

    if (u && t) {
      try {
        this.currentUser = JSON.parse(u);
      } catch {
        this.currentUser = null;
      }
    }
  }

  // -------------------------------------
  //                LOGIN
  // -------------------------------------
  login(email: string, password: string): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/auth/login`, { email, password })
      .pipe(
        tap(res => {
          localStorage.setItem(this.tokenKey, res.access_token);
          localStorage.setItem(this.userKey, JSON.stringify(res.user));
          this.currentUser = res.user;
        })
      );
  }

  // -------------------------------------
  //               REGISTER
  // -------------------------------------
  register(name: string, email: string, password: string): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/auth/register`, {
      name, email, password
    })
      .pipe(
        tap(res => {
          localStorage.setItem(this.tokenKey, res.access_token);
          localStorage.setItem(this.userKey, JSON.stringify(res.user));
          this.currentUser = res.user;
        })
      );
  }

  // -------------------------------------
  //     TOKEN + AUTH HEADERS
  // -------------------------------------
  getToken(): string {
    return localStorage.getItem(this.tokenKey) ?? '';
  }

  getAuthHeaders(): HttpHeaders {
    return new HttpHeaders({
      Authorization: `Bearer ${this.getToken()}`
    });
  }

  // -------------------------------------
  //              USER
  // -------------------------------------
  getUser(): User | null {
    return this.currentUser;
  }

  isAdmin(): boolean {
    return this.currentUser?.role === 'admin';
  }

  // -------------------------------------
  //              LOGOUT
  // -------------------------------------
  logout() {
    this.currentUser = null;
    localStorage.removeItem(this.userKey);
    localStorage.removeItem(this.tokenKey);
  }
}
