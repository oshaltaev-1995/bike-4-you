import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from '../services/auth.service';

export const authGuard: CanActivateFn = (route, state) => {
  const auth = inject(AuthService);
  const router = inject(Router);

  const user = auth.getUser();
  if (user) {
    return true;
  }

  router.navigate(['/'], { queryParams: { returnUrl: state.url } });
  return false;
};
