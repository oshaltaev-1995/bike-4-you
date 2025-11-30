import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { AuthService } from '../../services/auth.service';
import { Router } from '@angular/router';

@Component({
  standalone: true,
  imports: [FormsModule],
  selector: 'app-equipment-add',
  template: `
    <h2>Add Equipment</h2>
    <form (ngSubmit)="submit()">
      <label>Type</label>
      <input [(ngModel)]="form.type" name="type">

      <label>Location</label>
      <input [(ngModel)]="form.location" name="location">

      <label>Rate</label>
      <input type="number" [(ngModel)]="form.hourly_rate" name="hourly">

      <label>Image URL</label>
      <input [(ngModel)]="form.image_url" name="image">

      <button type="submit">Add</button>
    </form>
  `
})
export class EquipmentAddComponent {

  form = {
    type: '',
    status: 'available',
    location: '',
    hourly_rate: 4,
    image_url: ''
  };

  constructor(
    private http: HttpClient,
    private auth: AuthService,
    private router: Router
  ) {}

  submit() {
    this.http.post('http://localhost:8002/equipment/add', this.form, {
      headers: this.auth.getAuthHeaders()
    }).subscribe(() => this.router.navigate(['/admin/equipment']));
  }
}
