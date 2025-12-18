//guard (protector de rutas) que protege rutas solo para administradores
//se ejecuta antes de cargar una ruta protegida
import { Injectable } from '@angular/core';
import { CanActivate, Router } from '@angular/router';
import { AuthService } from './auth.service';

@Injectable({
  providedIn: 'root'
})
export class AdminGuard implements CanActivate {
  constructor(
    private authService: AuthService, //servicio de autenticación
    private router: Router //servicio de navegación
  ) { }

  //método que Angular llama antes de activar una ruta protegida
  //retorna true si permite el acceso, false si lo bloquea
  canActivate(): boolean {
    //verifica que el usuario esté autenticado Y sea administrador
    if (this.authService.isAuthenticated() && this.authService.checkIsAdmin()) {
      return true; //permite el acceso
    }

    //si no es admin o no está autenticado, redirige al login
    this.router.navigate(['/login']);
    return false; //bloquea el acceso
  }
}

