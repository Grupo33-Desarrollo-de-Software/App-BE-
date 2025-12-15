// Componente principal de la aplicación
import { Component, OnInit } from "@angular/core";
import { AuthService } from "./auth.service";
import { Router } from "@angular/router";

@Component({
  selector: "app-root",
  templateUrl: "./app.component.html",
  standalone: false,
  styleUrl: "./app.component.css",
})
export class AppComponent implements OnInit {
  title = "Angular";

  constructor(
    public authService: AuthService,
    private router: Router
  ) { }

  // Al iniciar, verifica si hay un usuario autenticado
  ngOnInit(): void {
    this.authService.checkAuthStatus();
  }

  // Cierra la sesión del usuario
  logout(): void {
    this.authService.logout();
  }

  // Navega a una ruta específica
  navigateTo(path: string): void {
    this.router.navigate([path]);
  }
}
