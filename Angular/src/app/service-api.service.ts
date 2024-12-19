import { Injectable } from '@angular/core';
import { Observable } from "rxjs";
import { HttpClient } from "@angular/common/http";

import { Album } from "./buscar-album";


@Injectable({
  providedIn: 'root'
})
export class ServiceAPI {

  constructor(private http: HttpClient) { }

  getServiceAPI(): Observable<Album> {
    return this.http.get('http://127.0.0.1:8000/api/v1/questions/') as Observable<Album>;
  }
}