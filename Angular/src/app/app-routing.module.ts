// Configuración de las rutas de la aplicación
import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { BuscarAlbumComponent } from "./buscar-album/buscar-album.component"
import { LoginComponent } from "./login/login.component"
import { MonitoringComponent } from "./monitoring/monitoring.component"
import { AdminGuard } from "./admin.guard"

// Define todas las rutas disponibles
const routes: Routes = [
  { path: '', component: BuscarAlbumComponent },
  { path: 'login', component: LoginComponent },
  { path: 'admin/monitoreo', component: MonitoringComponent, canActivate: [AdminGuard] },
  { path: '**', redirectTo: '' } // Ruta por defecto
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
