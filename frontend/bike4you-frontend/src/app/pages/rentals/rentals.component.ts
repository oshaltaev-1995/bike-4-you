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

  // -----------------------
  // Equipment preload
  // -----------------------
  preloadEquipmentFor(rentals: Rental[]) {
    const calls = rentals.map(r => this.inventory.getById(r.equipment_id));
    if (calls.length === 0) return;

    forkJoin(calls).subscribe(items => {
      items.forEach(eq => this.equipmentCache[eq.id] = eq);
    });
  }

  // -----------------------
  // Load active rentals
  // -----------------------
  loadActive() {
    if (!this.user) return;

    this.loading = true;
    this.error = null;

    this.rentals.getActive(this.user.id).subscribe({
      next: (data) => {
        this.activeRentals = data.filter(r => r.status === 'active');
        this.preloadEquipmentFor(this.activeRentals);
        this.loading = false;
      },
      error: (err) => {
        this.error = this.formatError(err) || 'Failed to load active rentals';
        this.loading = false;
      }
    });
  }

  // -----------------------
  // Load rental history
  // -----------------------
  loadHistory() {
    if (!this.user) return;

    this.rentals.getHistory(this.user.id).subscribe({
      next: (data) => {
        this.historyRentals = data.filter(r => r.status !== 'active');
        this.preloadEquipmentFor(this.historyRentals);
      },
      error: (err) => {
        this.error = this.formatError(err) || 'Failed to load rental history';
      }
    });
  }

  // -----------------------
  // Helpers
  // -----------------------
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
        this.error = this.formatError(err) || 'Failed to return rental';
        this.loading = false;
      }
    });
  }

  // -----------------------
  // Pretty error formatting
  // -----------------------
  private formatError(err: any): string {
    if (!err) return 'Unknown error';

    if (typeof err === 'string') return err;

    if (err.error) {
      if (typeof err.error === 'string') return err.error;

      if (err.error.detail) {
        if (typeof err.error.detail === 'string') return err.error.detail;

        if (Array.isArray(err.error.detail)) {
          return err.error.detail
            .map((d: any) => d.msg || JSON.stringify(d))
            .join('; ');
        }
      }
    }

    if (err.message) return err.message;

    try {
      return JSON.stringify(err);
    } catch {
      return 'Unknown error';
    }
  }
}
