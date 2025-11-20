import { bootstrapApplication } from '@angular/platform-browser';
import { provideHttpClient, withInterceptorsFromDi } from '@angular/common/http';
import { provideRouter } from '@angular/router';
import { AuthService } from './app/services/auth.service';
import { InventoryService } from './app/services/inventory.service';
import { RentalService } from './app/services/rental.service';

import { AppComponent } from './app/app.component';
import { routes } from './app/app.routes';

bootstrapApplication(AppComponent, {
  providers: [
    provideHttpClient(withInterceptorsFromDi()),
    provideRouter(routes),
    AuthService,
    InventoryService,
    RentalService
  ]
})
.catch(err => console.error(err));
