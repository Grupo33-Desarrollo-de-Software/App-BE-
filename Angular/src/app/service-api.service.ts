import { Injectable } from "@angular/core";
import { Observable } from "rxjs";
import { HttpClient } from "@angular/common/http";

import { Album } from "./buscar-album";

const backendApi = `http://127.0.0.1:8000/api/v1`;

@Injectable({
  providedIn: "root",
})
export class ServiceAPI {
  constructor(private http: HttpClient) {}

  searchAlbums(busqueda: string): Observable<Album[]> {
    return this.http.get(
      backendApi + `/albums/${busqueda}`,
    ) as Observable<Album[]>;
  }

  getInfo(artista: string, album: string): Observable<Album> {
    return this.http.get(
      backendApi + `/album/${artista}/${album}`,
    ) as Observable<Album>;
  }
}

 