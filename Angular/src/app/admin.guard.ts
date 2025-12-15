// Guard que protege rutas solo para administradores
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
  ) { }

  // Verifica si el usuario es admin antes de permitir acceso
  canActivate(): boolean {
    if (this.authService.isAuthenticated() && this.authService.checkIsAdmin()) {
      return true;
    }

    // Si no es admin, redirige al login
    this.router.navigate(['/login']);
    return false;
  }
}

