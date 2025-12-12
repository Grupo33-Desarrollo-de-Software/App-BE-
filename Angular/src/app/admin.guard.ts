import { Injectable } from '@angular/core';
import { CanActivate, Router } from '@angular/router';
import { AuthService } from './auth.service';

@Injectable({
  providedIn: 'root'
})
export class AdminGuard implements CanActivate {
  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  canActivate(): boolean {
    if (this.authService.isAuthenticated() && this.authService.checkIsAdmin()) {
      return true;
    }
    
    // Si no es admin, redirigir al login
    this.router.navigate(['/login']);
    return false;
  }
}

