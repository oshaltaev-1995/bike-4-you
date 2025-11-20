import { Component, OnInit } from '@angular/core';
import { RentalService, Rental } from '../../services/rental.service';
import { AuthService, User } from '../../services/auth.service';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-rentals',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './rentals.component.html'
})
export class RentalsComponent implements OnInit {
  rentals: Rental[] = [];
  user: User | null = null;

  constructor(
    private rentalService: RentalService,
    private auth: AuthService
  ) {}

  ngOnInit() {
    this.user = this.auth.getUser();
    if (this.user) {
      this.rentalService.getHistory(this.user.id).subscribe(data => this.rentals = data);
    }
  }

  returnRental(id: number) {
    this.rentalService.return(id).subscribe(() => {
      alert('Returned!');
      if (this.user) {
        this.rentalService.getHistory(this.user.id).subscribe(data => this.rentals = data);
      }
    });
  }
}
