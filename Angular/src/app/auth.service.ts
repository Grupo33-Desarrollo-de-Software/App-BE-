// Servicio para manejar la autenticación de usuarios
import { Injectable, signal } from '@angular/core';
import { Router } from '@angular/router';

// Define la estructura de un usuario
export interface User {
  id: number;
  username: string;
  is_staff: boolean;
  is_superuser: boolean;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  // Claves para guardar datos en el navegador
  private readonly TOKEN_KEY = 'auth_token';
  private readonly USER_KEY = 'user_data';

  // Estados de autenticación
  isAuthenticated = signal<boolean>(false);
  currentUser = signal<User | null>(null);
  isAdmin = signal<boolean>(false);

  constructor(private router: Router) {
    // Al iniciar, verifica si hay un usuario guardado
    this.checkAuthStatus();
  }

  // Verifica si el usuario está autenticado
  checkAuthStatus(): void {
    const token = localStorage.getItem(this.TOKEN_KEY);
    const userData = localStorage.getItem(this.USER_KEY);

    if (token && userData) {
      try {
        const user: User = JSON.parse(userData);
        this.isAuthenticated.set(true);
        this.currentUser.set(user);
        this.isAdmin.set(user.is_staff || user.is_superuser);
      } catch (e) {
        this.logout();
      }
    } else {
      this.isAuthenticated.set(false);
      this.currentUser.set(null);
      this.isAdmin.set(false);
    }
  }

  // Guarda los datos del usuario al hacer login
  setUser(token: string, user: User): void {
    localStorage.setItem(this.TOKEN_KEY, token);
    localStorage.setItem(this.USER_KEY, JSON.stringify(user));
    this.isAuthenticated.set(true);
    this.currentUser.set(user);
    this.isAdmin.set(user.is_staff || user.is_superuser);
  }

  // Obtiene el token guardado
  getToken(): string | null {
    return localStorage.getItem(this.TOKEN_KEY);
  }

  // Obtiene el usuario actual
  getUser(): User | null {
    return this.currentUser();
  }

  // Verifica si el usuario es administrador
  checkIsAdmin(): boolean {
    return this.isAdmin();
  }

  // Cierra sesión y borra todos los datos
  logout(): void {
    localStorage.removeItem(this.TOKEN_KEY);
    localStorage.removeItem(this.USER_KEY);
    localStorage.removeItem('user_id');
    localStorage.removeItem('username');
    this.isAuthenticated.set(false);
    this.currentUser.set(null);
    this.isAdmin.set(false);
    this.router.navigate(['/login']);
  }
}