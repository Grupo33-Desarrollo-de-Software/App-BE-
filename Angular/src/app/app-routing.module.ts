import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { BuscarAlbumComponent } from "./buscar-album/buscar-album.component"

const routes: Routes = [
  { path: '', component: BuscarAlbumComponent },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
