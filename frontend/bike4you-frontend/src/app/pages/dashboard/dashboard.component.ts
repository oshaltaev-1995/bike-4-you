import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { InventoryService, Equipment } from '../../services/inventory.service';
import { RentalService } from '../../services/rental.service';
import { AuthService, User } from '../../services/auth.service';

// Import Navbar
import { NavbarComponent } from '../../components/navbar/navbar.component';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, FormsModule, NavbarComponent],
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent implements OnInit {

  user: User | null = null;
  equipment: Equipment[] = [];

  loading = false;
  error: string | null = null;

  statusFilter: 'all' | 'available' | 'rented' = 'all';
  typeFilter: 'all' | 'bike' | 'scooter' | 'ski' = 'all';

  constructor(
    private inventoryService: InventoryService,
    private rentalService: RentalService,
    private authService: AuthService
  ) {}

  ngOnInit(): void {
    this.user = this.authService.getUser();
    this.loadEquipment();

    // ← Ловим refresh событие из Navbar
    window.addEventListener('dashboard-refresh', () => {
      this.onRefresh();
    });
  }

  // =============================
  // LOAD EQUIPMENT WITH FILTERS
  // =============================
  loadEquipment(): void {
    this.loading = true;
    this.error = null;

    this.inventoryService
      .getAll({
        status: this.statusFilter,
        type: this.typeFilter === 'all' ? undefined : this.typeFilter
      })
      .subscribe({
        next: (items) => {
          this.equipment = items;
          this.loading = false;
        },
        error: (err) => {
          this.error = err.error?.detail || 'Failed to load equipment';
          this.loading = false;
        }
      });
  }

  onRefresh(): void {
    this.loadEquipment();
  }

  onChangeFilters(): void {
    this.loadEquipment();
  }

  // =============================
  // RENT LOGIC
  // =============================
  onRent(item: Equipment): void {
    if (!this.user) {
      this.error = 'User not logged in';
      return;
    }

    this.loading = true;

    // 1) создаём аренду
    this.rentalService.startRental(this.user.id, item.id).subscribe({
      next: () => {
        // 2) обновляем equipment → rented
        this.inventoryService.updateStatus(item.id, 'rented').subscribe({
          next: (updatedItem) => {
            // 3) локально заменяем статус
            this.equipment = this.equipment.map(e =>
              e.id === updatedItem.id ? updatedItem : e
            );
            this.loading = false;
          },
          error: () => {
            this.error = 'Rental started, but status update failed';
            this.loading = false;
          }
        });
      },
      error: (err) => {
        this.error = err.error?.detail || 'Failed to start rental';
        this.loading = false;
      }
    });
  }
}
