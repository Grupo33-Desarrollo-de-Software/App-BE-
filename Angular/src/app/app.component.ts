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
  ) {}

  ngOnInit(): void {
    // Verificar estado de autenticación al inicializar
    this.authService.checkAuthStatus();
  }

  logout(): void {
    this.authService.logout();
  }

  navigateTo(path: string): void {
    this.router.navigate([path]);
  }
}
