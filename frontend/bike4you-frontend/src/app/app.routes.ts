import { Routes } from '@angular/router';
import { LoginComponent } from './pages/login/login.component';
import { DashboardComponent } from './pages/dashboard/dashboard.component';
import { RentalsComponent } from './pages/rentals/rentals.component';
import { authGuard } from './guards/auth.guard';
import { adminGuard } from './guards/admin.guard';

export const routes: Routes = [

  // --------------------------
  // PUBLIC
  // --------------------------
  { path: '', component: LoginComponent },

  // --------------------------
  // USER ROUTES
  // --------------------------
  {
    path: 'dashboard',
    component: DashboardComponent,
    canActivate: [authGuard]
  },

  {
    path: 'rentals',
    component: RentalsComponent,
    canActivate: [authGuard]
  },

  // --------------------------
  // ADMIN ROUTES
  // --------------------------
  {
    path: 'admin',
    canActivate: [adminGuard],
    children: [
      {
        path: '',
        loadComponent: () =>
          import('./pages/admin/admin-dashboard.component')
            .then(m => m.AdminDashboardComponent)
      },
      {
        path: 'equipment',
        loadComponent: () =>
          import('./pages/admin/equipment-list.component')
            .then(m => m.EquipmentListComponent)
      },
      {
        path: 'equipment/add',
        loadComponent: () =>
          import('./pages/admin/equipment-add.component')
            .then(m => m.EquipmentAddComponent)
      },
      {
        path: 'equipment/edit/:id',
        loadComponent: () =>
          import('./pages/admin/equipment-edit.component')
            .then(m => m.EquipmentEditComponent)
      },
      {
        path: 'rentals',
        loadComponent: () =>
          import('./pages/admin/rentals-list.component')
            .then(m => m.RentalsListComponent)
      },
    ]
  },

  // --------------------------
  // WILDCARD
  // --------------------------
  { path: '**', redirectTo: '' }
];
