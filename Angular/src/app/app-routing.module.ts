import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { BuscarAlbumComponent } from "./buscar-album/buscar-album.component"
import { RegisterComponent } from "./register/register.component"
import { MonitoringComponent } from "./monitoring/monitoring.component"

const routes: Routes = [
  { path: '', component: BuscarAlbumComponent },
  { path: 'register', component: RegisterComponent },
  { path: 'login', component: BuscarAlbumComponent }, // Placeholder - you can create a login component later
  { path: 'admin/monitoreo', component: MonitoringComponent },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
