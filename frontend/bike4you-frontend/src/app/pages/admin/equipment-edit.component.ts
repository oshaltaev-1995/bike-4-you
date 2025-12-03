import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, RouterLink, Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../../services/auth.service';

@Component({
  standalone: true,
  styleUrls: ['./admin.scss'],
  selector: 'app-equipment-edit',
  imports: [FormsModule, RouterLink],
  template: `
    <h2>Edit Equipment</h2>
    <form (ngSubmit)="submit()">

      <label>Status</label>
      <input [(ngModel)]="form.status" name="status">

      <label>Location</label>
      <input [(ngModel)]="form.location" name="location">

      <label>Rate</label>
      <input type="number" [(ngModel)]="form.hourly_rate" name="rate">

      <label>Image</label>
      <input [(ngModel)]="form.image_url" name="image">

      <button type="submit">Save</button>
    </form>
  `
})
export class EquipmentEditComponent implements OnInit {
  id!: number;
  form: any = {};

  constructor(
    private route: ActivatedRoute,
    private http: HttpClient,
    private auth: AuthService,
    private router: Router
  ) {}

  ngOnInit() {
    this.id = Number(this.route.snapshot.paramMap.get('id'));
    this.http.get(`http://localhost:8002/equipment/${this.id}`, {
      headers: this.auth.getAuthHeaders()
    }).subscribe(res => this.form = res);
  }

  submit() {
    this.http.post('http://localhost:8002/equipment/update', this.form, {
      headers: this.auth.getAuthHeaders()
    }).subscribe(() => this.router.navigate(['/admin/equipment']));
  }
}
