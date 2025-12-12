import { Injectable, signal } from '@angular/core';
import { Router } from '@angular/router';

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
  private readonly TOKEN_KEY = 'auth_token';
  private readonly USER_KEY = 'user_data';
  
  // Signals para el estado de autenticación
  isAuthenticated = signal<boolean>(false);
  currentUser = signal<User | null>(null);
  isAdmin = signal<boolean>(false);

  constructor(private router: Router) {
    // Verificar si hay un usuario guardado al inicializar
    this.checkAuthStatus();
  }

  /**
   * Verifica el estado de autenticación desde localStorage
   */
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
        // Si hay error al parsear, limpiar datos
        this.logout();
      }
    } else {
      this.isAuthenticated.set(false);
      this.currentUser.set(null);
      this.isAdmin.set(false);
    }
  }

  /**
   * Guarda los datos del usuario después del login
   */
  setUser(token: string, user: User): void {
    localStorage.setItem(this.TOKEN_KEY, token);
    localStorage.setItem(this.USER_KEY, JSON.stringify(user));
    this.isAuthenticated.set(true);
    this.currentUser.set(user);
    this.isAdmin.set(user.is_staff || user.is_superuser);
  }

  /**
   * Obtiene el token de autenticación
   */
  getToken(): string | null {
    return localStorage.getItem(this.TOKEN_KEY);
  }

  /**
   * Obtiene el usuario actual
   */
  getUser(): User | null {
    return this.currentUser();
  }

  /**
   * Verifica si el usuario es admin
   */
  checkIsAdmin(): boolean {
    return this.isAdmin();
  }

  /**
   * Cierra sesión y limpia los datos
   */
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

