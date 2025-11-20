import { Component, OnInit } from '@angular/core';
import { InventoryService, Equipment } from '../../services/inventory.service';
import { RentalService } from '../../services/rental.service';
import { AuthService, User } from '../../services/auth.service';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './dashboard.component.html'
})
export class DashboardComponent implements OnInit {
  equipment: Equipment[] = [];
  user: User | null = null;

  constructor(
    private inventory: InventoryService,
    private rental: RentalService,
    private auth: AuthService
  ) {}

  ngOnInit() {
    this.user = this.auth.getUser();
    this.inventory.getAll().subscribe(data => this.equipment = data);
  }

  rentItem(id: number) {
    if (!this.user) {
      alert('No user logged in');
      return;
    }
    this.rental.rent(this.user.id, id).subscribe(() => {
      alert('Successfully rented!');
      this.inventory.getAll().subscribe(data => this.equipment = data);
    });
  }
}
