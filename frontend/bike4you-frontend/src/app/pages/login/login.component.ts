import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { AuthService, User } from '../../services/auth.service';

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

  onLogin() {
    this.error = null;
    this.authService.login(this.email).subscribe({
      next: (user: User) => {
        this.authService.saveUser(user);
        this.router.navigate(['/dashboard']);
      },
      error: (err) => {
        this.error = err.error?.detail || 'Login failed';
      }
    });
  }

  onRegister() {
    this.error = null;
    this.authService.register(this.name, this.email).subscribe({
      next: (user: User) => {
        this.authService.saveUser(user);
        this.router.navigate(['/dashboard']);
      },
      error: (err) => {
        this.error = err.error?.detail || 'Registration failed';
      }
    });
  }
}
