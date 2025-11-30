import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';

@Component({
  standalone: true,
  selector: 'app-admin-dashboard',
  imports: [RouterLink],
  template: `
    <h2>Admin Panel</h2>
    <ul>
      <li><a routerLink="/admin/equipment">Manage Equipment</a></li>
      <li><a routerLink="/admin/rentals">All Rentals</a></li>
    </ul>
  `
})
export class AdminDashboardComponent {}
