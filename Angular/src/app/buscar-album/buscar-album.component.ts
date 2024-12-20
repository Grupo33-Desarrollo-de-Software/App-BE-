import { Component, OnInit } from "@angular/core";
import { ServiceAPI } from "../service-api.service";
import type { Album } from "../buscar-album.ts";

@Component({
  selector: "app-buscar-album",
  standalone: false,

  templateUrl: "./buscar-album.component.html",
  styleUrl: "./buscar-album.component.css",
})
export class BuscarAlbumComponent {
  busqueda = "";
  albums: Album[] = [];

  constructor(private serviceAPI: ServiceAPI) {}

  buscar(busqueda: string) {
    if (busqueda != "") {
      this.serviceAPI.searchAlbums(busqueda).subscribe((data) => {
        this.albums = data;
        console.log(this.albums);
      });
    }
  }
}
