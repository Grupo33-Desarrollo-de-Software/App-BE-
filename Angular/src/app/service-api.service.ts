// Servicio para comunicarse con el backend
import { Injectable } from "@angular/core";
import { Observable } from "rxjs";
import { HttpClient } from "@angular/common/http";

import { Album } from "./buscar-album";

// URL del servidor backend
const backendApi = `http://127.0.0.1:8000/api/v1`;

// Datos necesarios para registrar un usuario
export interface RegisterRequest {
  username: string;
  password: string;
  email?: string;
  first_name?: string;
  last_name?: string;
  bio?: string;
  foto?: File;
  notifPorEmail?: boolean;
  notifRecomendaciones?: boolean;
  notifGenerales?: boolean;
  is_staff?: boolean;
  is_superuser?: boolean;
}

// Respuesta del servidor al registrar un usuario
export interface RegisterResponse {
  token: string;
  id: number;
  username: string;
  email?: string;
  first_name?: string;
  last_name?: string;
  is_staff?: boolean;
  is_superuser?: boolean;
  message: string;
}

// Datos necesarios para hacer login
export interface LoginRequest {
  username: string;
  password: string;
}

// Respuesta del servidor al hacer login
export interface LoginResponse {
  token: string;
  id: number;
  username: string;
  is_staff: boolean;
  is_superuser: boolean;
}

@Injectable({
  providedIn: "root",
})
export class ServiceAPI {
  constructor(private http: HttpClient) { }

  // Busca álbumes por nombre o artista
  searchAlbums(busqueda: string): Observable<Album[]> {
    const encodedBusqueda = encodeURIComponent(busqueda);
    return this.http.get<Album[]>(
      `${backendApi}/albums/${encodedBusqueda}`
    );
  }

  // Obtiene información detallada de un álbum
  getInfo(artista: string, album: string): Observable<Album> {
    const encodedArtista = encodeURIComponent(artista);
    const encodedAlbum = encodeURIComponent(album);
    return this.http.get<Album>(
      `${backendApi}/album/${encodedArtista}/${encodedAlbum}`
    );
  }

  // Registra un nuevo usuario
  register(userData: RegisterRequest): Observable<RegisterResponse> {
    const formData = new FormData();

    formData.append('username', userData.username);
    formData.append('password', userData.password);

    if (userData.email) formData.append('email', userData.email);
    if (userData.first_name) formData.append('first_name', userData.first_name);
    if (userData.last_name) formData.append('last_name', userData.last_name);
    if (userData.bio) formData.append('bio', userData.bio);
    if (userData.foto) formData.append('foto', userData.foto);
    if (userData.notifPorEmail !== undefined) formData.append('notifPorEmail', userData.notifPorEmail.toString());
    if (userData.notifRecomendaciones !== undefined) formData.append('notifRecomendaciones', userData.notifRecomendaciones.toString());
    if (userData.notifGenerales !== undefined) formData.append('notifGenerales', userData.notifGenerales.toString());

    if (userData.is_staff !== undefined) formData.append('is_staff', userData.is_staff.toString());
    if (userData.is_superuser !== undefined) formData.append('is_superuser', userData.is_superuser.toString());

    return this.http.post<RegisterResponse>(
      `${backendApi}/usuarios/register`,
      formData
    );
  }

  // Hace login con usuario y contraseña
  login(credentials: LoginRequest): Observable<LoginResponse> {
    return this.http.post<LoginResponse>(
      `http://127.0.0.1:8000/api-user-login/`,
      credentials
    );
  }
}

