import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';

import { RentalService, Rental } from '../../services/rental.service';
import { InventoryService, Equipment } from '../../services/inventory.service';
import { AuthService, User } from '../../services/auth.service';

import { NavbarComponent } from '../../components/navbar/navbar.component';
import { forkJoin } from 'rxjs';

@Component({
  selector: 'app-rentals',
  standalone: true,
  imports: [CommonModule, NavbarComponent],
  templateUrl: './rentals.component.html',
  styleUrls: ['./rentals.component.scss']
})
export class RentalsComponent implements OnInit {

  user: User | null = null;

  activeRentals: Rental[] = [];
  historyRentals: Rental[] = [];

  equipmentCache: { [id: number]: Equipment } = {};

  tab: 'active' | 'history' = 'active';

  loading = false;
  error: string | null = null;

  constructor(
    private rentals: RentalService,
    private inventory: InventoryService,
    private auth: AuthService
  ) {}

  ngOnInit() {
    this.user = this.auth.getUser();
    if (this.user) {
      this.loadActive();
      this.loadHistory();
    }
  }

  preloadEquipmentFor(rentals: Rental[]) {
    const calls = rentals.map(r =>
      this.inventory.getById(r.equipment_id)
    );

    if (calls.length === 0) return;

    forkJoin(calls).subscribe(items => {
      items.forEach(eq => {
        this.equipmentCache[eq.id] = eq;
      });
    });
  }

  loadActive() {
    if (!this.user) return;
    this.loading = true;
    this.error = null;

    this.rentals.getActive(this.user.id).subscribe({
      next: (data) => {
        this.activeRentals = data;
        this.preloadEquipmentFor(data);
        this.loading = false;
      },
      error: (err) => {
        this.error = err.error?.detail || 'Failed to load active rentals';
        this.loading = false;
      }
    });
  }

  loadHistory() {
    if (!this.user) return;

    this.rentals.getHistory(this.user.id).subscribe({
      next: (data) => {
        this.historyRentals = data;
        this.preloadEquipmentFor(data);
      },
      error: (err) => {
        this.error = err.error?.detail || 'Failed to load rental history';
      }
    });
  }

  setTab(t: 'active' | 'history') {
    this.tab = t;
  }

  getEquipment(rental: Rental): Equipment | null {
    return this.equipmentCache[rental.equipment_id] ?? null;
  }

  returnRental(id: number) {
    if (!this.user) return;

    this.loading = true;
    this.error = null;

    this.rentals.returnRental(id).subscribe({
      next: (rental: Rental) => {

        this.inventory.updateStatus(rental.equipment_id, 'available').subscribe({
          next: () => {
            this.loadActive();
            this.loadHistory();
            this.loading = false;
          },
          error: () => {
            this.loadActive();
            this.loadHistory();
            this.loading = false;
          }
        });
      },
      error: (err) => {
        this.error = err.error?.detail || 'Failed to return rental';
        this.loading = false;
      }
    });
  }
}
