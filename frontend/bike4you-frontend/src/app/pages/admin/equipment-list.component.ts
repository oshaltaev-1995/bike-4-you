import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { RouterLink } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { NgFor } from '@angular/common';

@Component({
  standalone: true,
  selector: 'app-equipment-list',
  imports: [RouterLink, NgFor],
  template: `
    <h2>Equipment List</h2>

    <a routerLink="/admin/equipment/add">+ Add New</a>

    <table>
      <tr>
        <th>ID</th><th>Type</th><th>Status</th><th>Rate</th><th>Actions</th>
      </tr>
      <tr *ngFor="let item of items">
        <td>{{ item.id }}</td>
        <td>{{ item.type }}</td>
        <td>{{ item.status }}</td>
        <td>{{ item.hourly_rate }}</td>
        <td>
          <a [routerLink]="['/admin/equipment/edit', item.id]">Edit</a>
        </td>
      </tr>
    </table>
  `
})
export class EquipmentListComponent implements OnInit {
  items: any[] = [];

  constructor(private http: HttpClient, private auth: AuthService) {}

  ngOnInit() {
    this.http.get<any[]>('http://localhost:8002/equipment', {
      headers: this.auth.getAuthHeaders()
    }).subscribe(res => this.items = res);
  }
}
