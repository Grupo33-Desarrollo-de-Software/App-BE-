//componente principal de la aplicación (raíz)
//se carga al iniciar y contiene la estructura base de la app
import { Component, OnInit } from "@angular/core";
import { AuthService } from "./auth.service";
import { Router } from "@angular/router";

@Component({
  selector: "app-root", //selector HTML para usar este componente
  templateUrl: "./app.component.html", //template HTML del componente
  standalone: false, //no es un componente standalone (pertenece a un módulo)
  styleUrl: "./app.component.css", //estilos CSS del componente
})
export class AppComponent implements OnInit {
  title = "Angular"; //título de la aplicación

  //inyecta los servicios necesarios en el constructor
  constructor(
    public authService: AuthService, //servicio de autenticación (público para usar en el template)
    private router: Router //servicio de navegación entre rutas
  ) { }

  //se ejecuta cuando el componente se inicializa
  //verifica si hay un usuario autenticado guardado en el navegador
  ngOnInit(): void {
    this.authService.checkAuthStatus();
  }

  //cierra la sesión del usuario actual
  //elimina el token y redirige al login
  logout(): void {
    this.authService.logout();
  }

  //navega a una ruta específica de la aplicación
  navigateTo(path: string): void {
    this.router.navigate([path]);
  }
}
