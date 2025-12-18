//servicio para manejar la autenticación de usuarios
//gestiona el estado de autenticación, tokens y datos del usuario
import { Injectable, signal } from '@angular/core';
import { Router } from '@angular/router';

//interfaz: estructura de datos de un usuario autenticado
export interface User {
  id: number;
  username: string;
  is_staff: boolean;
  is_superuser: boolean;
}

@Injectable({
  providedIn: 'root' //disponible en toda la aplicación
})
export class AuthService {
  //claves para guardar datos en localStorage del navegador
  private readonly TOKEN_KEY = 'auth_token'; //clave para el token de autenticación
  private readonly USER_KEY = 'user_data'; //clave para los datos del usuario

  //estados reactivos de autenticación usando signals (Angular 16+)
  isAuthenticated = signal<boolean>(false); //indica si el usuario está autenticado
  currentUser = signal<User | null>(null); //usuario actual autenticado
  isAdmin = signal<boolean>(false); //indica si el usuario es administrador

  constructor(private router: Router) {
    //al crear el servicio, verifica si hay un usuario guardado en el navegador
    this.checkAuthStatus();
  }

  //verifica si el usuario está autenticado leyendo datos del localStorage
  checkAuthStatus(): void {
    const token = localStorage.getItem(this.TOKEN_KEY);
    const userData = localStorage.getItem(this.USER_KEY);

    //si hay token y datos de usuario, intenta restaurar la sesión
    if (token && userData) {
      try {
        const user: User = JSON.parse(userData);
        //actualiza los estados reactivos
        this.isAuthenticated.set(true);
        this.currentUser.set(user);
        this.isAdmin.set(user.is_staff || user.is_superuser);
      } catch (e) {
        //si hay error al parsear, cierra sesión (datos corruptos)
        this.logout();
      }
    } else {
      //si no hay datos, el usuario no está autenticado
      this.isAuthenticated.set(false);
      this.currentUser.set(null);
      this.isAdmin.set(false);
    }
  }

  //guarda los datos del usuario después de un login exitoso
  setUser(token: string, user: User): void {
    //guarda en localStorage para persistir entre recargas
    localStorage.setItem(this.TOKEN_KEY, token);
    localStorage.setItem(this.USER_KEY, JSON.stringify(user));
    //actualiza los estados reactivos
    this.isAuthenticated.set(true);
    this.currentUser.set(user);
    this.isAdmin.set(user.is_staff || user.is_superuser);
  }

  //obtiene el token de autenticación guardado
  getToken(): string | null {
    return localStorage.getItem(this.TOKEN_KEY);
  }

  //obtiene el usuario actual autenticado
  getUser(): User | null {
    return this.currentUser();
  }

  //verifica si el usuario actual es administrador
  checkIsAdmin(): boolean {
    return this.isAdmin();
  }

  //cierra sesión: elimina todos los datos y redirige al login
  logout(): void {
    //elimina todos los datos del localStorage
    localStorage.removeItem(this.TOKEN_KEY);
    localStorage.removeItem(this.USER_KEY);
    localStorage.removeItem('user_id');
    localStorage.removeItem('username');
    //actualiza los estados reactivos
    this.isAuthenticated.set(false);
    this.currentUser.set(null);
    this.isAdmin.set(false);
    //redirige al usuario a la página de login
    this.router.navigate(['/login']);
  }
}