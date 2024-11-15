import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { album } from './album.model';

@Injectable({
  providedIn: 'root'
})
export class albumService {
  private apiUrl = 'http://localhost:8000/api';

  constructor(private http: HttpClient) { }

  getalbums(): Observable<album[]> {
    return this.http.get<album[]>(this.apiUrl);
  }

  addalbum(album: album): Observable<album> {
    return this.http.post<album>(this.apiUrl, album);
  }
}