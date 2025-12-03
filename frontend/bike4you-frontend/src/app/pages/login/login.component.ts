import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [FormsModule, CommonModule],
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss']
})
export class LoginComponent {

  mode: 'login' | 'register' = 'login';

  name = '';
  email = '';
  password = '';

  error: string | null = null;

  constructor(
    private auth: AuthService,
    private router: Router
  ) {}

  switchToLogin() {
    this.mode = 'login';
    this.error = null;
  }

  switchToRegister() {
    this.mode = 'register';
    this.error = null;
  }

  isEmailValid(): boolean {
    return this.email.endsWith('@kamk.fi');
  }

  extractError(err: any): string {
    const detail = err?.error?.detail;

    if (!detail) return "Unknown error";
    if (typeof detail === 'string') return detail;

    try {
      return JSON.stringify(detail);
    } catch {
      return 'Unknown error';
    }
  }

  // ---------------- LOGIN ----------------
  onLogin() {
    this.error = null;

    this.auth.login(this.email, this.password).subscribe({
      next: () => {
        this.router.navigate(['/dashboard']);
      },
      error: (err) => {
        this.error = this.extractError(err);
      }
    });
  }

  // ---------------- REGISTER ----------------
  onRegister() {
    this.error = null;

    this.auth.register(this.name, this.email, this.password).subscribe({
      next: () => {
        this.router.navigate(['/dashboard']);
      },
      error: (err) => {
        this.error = this.extractError(err);
      }
    });
  }
}
