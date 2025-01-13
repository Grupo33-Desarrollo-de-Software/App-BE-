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
  album: Album = {} as Album;

  constructor(private serviceAPI: ServiceAPI) {}

  buscar(busqueda: string) {
    if (busqueda != "") {
      this.serviceAPI.searchAlbums(busqueda).subscribe((data) => {
        this.album = {} as Album;
        this.albums = data;
      });
    }
  }

  getInfo(artista: string, album: string) {
    console.log(album, artista);
    this.serviceAPI.getInfo(artista, album).subscribe((data) => {
      this.album = data;
      console.log(this.album);
    });
  }

  hayAlbumSeleccionado() {
    return Object.keys(this.album).length !== 0;
  }
}
