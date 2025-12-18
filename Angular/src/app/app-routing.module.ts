//configuración de las rutas de la aplicación
//define qué componente se muestra en cada URL
import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { BuscarAlbumComponent } from "./buscar-album/buscar-album.component"
import { LoginComponent } from "./login/login.component"
import { MonitoringComponent } from "./monitoring/monitoring.component"
import { AdminGuard } from "./admin.guard"

//define todas las rutas disponibles en la aplicación
const routes: Routes = [
  { path: '', component: BuscarAlbumComponent }, //ruta raíz: muestra el buscador de álbumes
  { path: 'login', component: LoginComponent }, //ruta de login
  //ruta de monitoreo: solo accesible para administradores (protegida por AdminGuard)
  { path: 'admin/monitoreo', component: MonitoringComponent, canActivate: [AdminGuard] },
  { path: '**', redirectTo: '' } //cualquier ruta no definida redirige a la raíz
];

@NgModule({
  //configura el módulo de rutas con las rutas definidas
  imports: [RouterModule.forRoot(routes)],
  //exporta RouterModule para que otros módulos puedan usar las directivas de routing
  exports: [RouterModule]
})
export class AppRoutingModule { }
