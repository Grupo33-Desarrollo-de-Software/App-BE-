//servicio para comunicarse con el backend Django
//provee métodos para hacer peticiones HTTP a la API
import { Injectable } from "@angular/core";
import { Observable } from "rxjs";
import { HttpClient } from "@angular/common/http";

import { Album } from "./buscar-album";

//URL base del servidor backend Django
const backendApi = `http://127.0.0.1:8000/api/v1`;

//interfaz: estructura de datos necesarios para registrar un nuevo usuario
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

//interfaz: estructura de la respuesta del servidor al registrar un usuario
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

//interfaz: estructura de datos necesarios para hacer login
export interface LoginRequest {
  username: string;
  password: string;
}

//interfaz: estructura de la respuesta del servidor al hacer login
export interface LoginResponse {
  token: string;
  id: number;
  username: string;
  is_staff: boolean;
  is_superuser: boolean;
}

//registra el servicio en el inyector principal de la aplicación
@Injectable({
  providedIn: "root",
})
export class ServiceAPI {
  //inyecta el servicio HttpClient para hacer peticiones HTTP
  constructor(private http: HttpClient) { }

  //busca álbumes por nombre o artista en la API externa
  //retorna un Observable con un array de álbumes
  searchAlbums(busqueda: string): Observable<Album[]> {
    //codifica el texto de búsqueda para que sea seguro en la URL
    const encodedBusqueda = encodeURIComponent(busqueda);
    //hace una petición GET al endpoint de búsqueda
    return this.http.get<Album[]>(
      `${backendApi}/albums/${encodedBusqueda}`
    );
  }

  //obtiene información detallada de un álbum específico
  //retorna un Observable con los datos completos del álbum
  getInfo(artista: string, album: string): Observable<Album> {
    //codifica artista y álbum para la URL
    const encodedArtista = encodeURIComponent(artista);
    const encodedAlbum = encodeURIComponent(album);
    //hace una petición GET al endpoint de información del álbum
    return this.http.get<Album>(
      `${backendApi}/album/${encodedArtista}/${encodedAlbum}`
    );
  }

  //registra un nuevo usuario en el sistema
  //usa FormData porque puede incluir archivos (foto)
  register(userData: RegisterRequest): Observable<RegisterResponse> {
    const formData = new FormData();

    //agrega los campos requeridos
    formData.append('username', userData.username);
    formData.append('password', userData.password);

    //agrega los campos opcionales solo si existen
    if (userData.email) formData.append('email', userData.email);
    if (userData.first_name) formData.append('first_name', userData.first_name);
    if (userData.last_name) formData.append('last_name', userData.last_name);
    if (userData.bio) formData.append('bio', userData.bio);
    if (userData.foto) formData.append('foto', userData.foto);
    //convierte los booleanos a string para FormData
    if (userData.notifPorEmail !== undefined) formData.append('notifPorEmail', userData.notifPorEmail.toString());
    if (userData.notifRecomendaciones !== undefined) formData.append('notifRecomendaciones', userData.notifRecomendaciones.toString());
    if (userData.notifGenerales !== undefined) formData.append('notifGenerales', userData.notifGenerales.toString());

    if (userData.is_staff !== undefined) formData.append('is_staff', userData.is_staff.toString());
    if (userData.is_superuser !== undefined) formData.append('is_superuser', userData.is_superuser.toString());

    //hace una petición POST al endpoint de registro
    return this.http.post<RegisterResponse>(
      `${backendApi}/usuarios/register`,
      formData
    );
  }

  //hace login con usuario y contraseña
  //retorna un Observable con el token y datos del usuario
  login(credentials: LoginRequest): Observable<LoginResponse> {
    //hace una petición POST al endpoint de login (ruta diferente, no usa /api/v1)
    return this.http.post<LoginResponse>(
      `http://127.0.0.1:8000/api-user-login/`,
      credentials
    );
  }
}

