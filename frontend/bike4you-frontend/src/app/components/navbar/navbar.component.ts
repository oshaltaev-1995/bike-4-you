import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterLink, RouterLinkActive } from '@angular/router';

import { AuthService, User } from '../../services/auth.service';

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [CommonModule, RouterLink, RouterLinkActive],
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.scss']
})
export class NavbarComponent {

  @Input() loading: boolean = false;

  user: User | null = null;

  constructor(
    public auth: AuthService,
    private router: Router
  ) {}

  ngOnInit() {
    this.user = this.auth.getUser();
  }

  logout() {
    this.auth.logout();
    this.router.navigate(['/']);
  }

  refresh() {
    window.dispatchEvent(new CustomEvent('dashboard-refresh'));
  }
}
