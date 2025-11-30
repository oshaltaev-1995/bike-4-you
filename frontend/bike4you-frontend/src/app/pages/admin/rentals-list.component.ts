import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { NgFor } from '@angular/common';
import { AuthService } from '../../services/auth.service';

@Component({
  standalone: true,
  imports: [NgFor],
  selector: 'app-rentals-list',
  template: `
    <h2>All Rentals</h2>
    <table>
      <tr>
        <th>ID</th><th>User</th><th>Equip</th><th>Status</th><th>Price</th>
      </tr>
      <tr *ngFor="let r of rentals">
        <td>{{ r.id }}</td>
        <td>{{ r.user_id }}</td>
        <td>{{ r.equipment_id }}</td>
        <td>{{ r.status }}</td>
        <td>{{ r.total_price }}</td>
      </tr>
    </table>
  `
})
export class RentalsListComponent implements OnInit {
  rentals: any[] = [];

  constructor(private http: HttpClient, private auth: AuthService) {}

  ngOnInit() {
    this.http.get<any[]>('http://localhost:8003/rentals/all', {
      headers: this.auth.getAuthHeaders()
    }).subscribe(res => this.rentals = res);
  }
}
