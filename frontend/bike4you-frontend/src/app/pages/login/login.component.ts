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
  name = '';
  email = '';
  mode: 'login' | 'register' = 'login';
  error: string | null = null;

  constructor(
    private authService: AuthService,
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

  // -------------------------------
  //      UNIVERSAL ERROR PARSER
  // -------------------------------
  private extractError(err: any): string {
    // Backend usually returns: { detail: "message" }
    const detail = err?.error?.detail;

    if (!detail) return 'Unknown error';

    // If it's already string
    if (typeof detail === 'string') return detail;

    // If backend returned an object: { message: "...", code: ... }
    if (typeof detail === 'object') {
      try {
        return Object.values(detail).join(', ');
      } catch {
        return JSON.stringify(detail);
      }
    }

    return 'Unknown error';
  }

  // --------------------------------
  //            LOGIN
  // --------------------------------
  onLogin() {
    this.error = null;
    this.authService.login(this.email).subscribe({
      next: () => {
        this.router.navigate(['/dashboard']);
      },
      error: (err) => {
        this.error = this.extractError(err);
      }
    });
  }

  // --------------------------------
  //          REGISTER
  // --------------------------------
  onRegister() {
    this.error = null;
    this.authService.register(this.name, this.email).subscribe({
      next: () => {
        this.router.navigate(['/dashboard']);
      },
      error: (err) => {
        this.error = this.extractError(err);
      }
    });
  }
}
