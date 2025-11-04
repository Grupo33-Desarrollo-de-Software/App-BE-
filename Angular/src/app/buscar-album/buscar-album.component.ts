import { ChangeDetectionStrategy, Component, signal, inject } from '@angular/core';
import { HttpClientModule } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { ServiceAPI } from '../service-api.service';
import { Album } from '../buscar-album';

// --- Interfaces para definir la estructura de nuestros datos ---
interface AlbumSimple {
  titulo: string;
  artista: string;
  foto: string;
}

interface AlbumDetallado {
  titulo: string;
  artista: string;
  foto: string;
  fechaLanzamiento: string;
  reproducciones: string; // Usamos string para formato con comas
  oyentes: string; // Usamos string para formato con comas
  info: string;
  cantidadCanciones: number;
}

@Component({
  selector: 'app-buscar-album',
  standalone: true,
  imports: [CommonModule],
  // Usamos 'standalone: true' y 'imports' si necesitamos módulos
  // pero para este ejemplo simple con @if/@for, no son estrictamente necesarios
  // si CommonModule se provee de forma global.
  // Para evitar `ngModel` y `FormsModule`, manejamos el input con `(input)`.
  // Para evitar `*ngIf` y `*ngFor`, usamos `@if` y `@for`.
  template: `
    <!-- Fondo principal y layout general con gradiente verde y círculos -->
    <div class="min-h-screen text-white font-sans gradient-bg relative overflow-hidden">
      <!-- Círculos decorativos de fondo -->
      <div class="absolute inset-0 overflow-hidden pointer-events-none">
        <div class="circle circle-1"></div>
        <div class="circle circle-2"></div>
        <div class="circle circle-3"></div>
        <div class="circle circle-4"></div>
        <div class="circle circle-5"></div>
        <div class="circle circle-6"></div>
      </div>
      <!-- Header con logo Notify -->
      <header class="w-full py-6 px-6 border-b-2 border-white/20 bg-black/30 backdrop-blur-md relative z-10">
        <div class="container mx-auto flex justify-center items-center">
          <h1 class="text-6xl md:text-7xl font-black text-white tracking-wider drop-shadow-2xl">
            NOTIFY
          </h1>
        </div>
      </header>
      
      <div class="container mx-auto max-w-5xl p-6 md:p-12 relative z-10">
        
        <!-- Título principal -->
        <h2 class="text-4xl md:text-5xl font-extrabold mb-8 text-center text-green-400">
          Búsqueda de Álbumes
        </h2>

        <!-- Formulario de Búsqueda -->
        <form class="flex w-full max-w-2xl mx-auto mb-12 shadow-lg" (submit)="$event.preventDefault()">
          <input 
            type="text" 
            id="album" 
            name="album"
            placeholder="Buscar por artista o álbum..."
            class="flex-grow p-4 rounded-l-lg bg-gray-800 text-white placeholder-gray-400 border-2 border-transparent focus:border-green-500 focus:ring-green-500 focus:outline-none transition-colors"
            [value]="busqueda()"
            (input)="buscar($event)">
          <button 
            type="submit"
            class="p-4 bg-green-600 hover:bg-green-700 rounded-r-lg font-semibold transition-colors">
            Buscar
          </button>
        </form>

        <!-- Vista de Detalle del Álbum -->
        @if (cargandoDetalle()) {
          <div class="text-center py-12">
            <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-green-400"></div>
            <p class="mt-4 text-gray-300">Cargando información del álbum...</p>
          </div>
        } @else if (albumSeleccionado()) {
          <div class="w-full max-w-4xl mx-auto bg-gray-900/90 border-2 border-green-500 rounded-2xl shadow-2xl p-6 md:p-8 animate-fade-in backdrop-blur-sm">
            <div class="flex flex-col md:flex-row gap-8">
              
              <!-- Portada del Álbum -->
              <div class="w-full md:w-1/3 flex-shrink-0">
                <img 
                  [src]="albumSeleccionado()!.foto" 
                  alt="Portada de {{ albumSeleccionado()!.titulo }}"
                  class="w-full h-auto rounded-lg object-cover aspect-square shadow-lg border-2 border-green-500">
              </div>
              
              <!-- Información del Álbum -->
              <div class="flex-1 min-w-0">
                <h1 class="text-3xl md:text-4xl font-extrabold mb-2 break-words text-green-400">{{ albumSeleccionado()!.titulo }}</h1>
                <p class="text-xl md:text-2xl font-light text-green-300 mb-6 break-words">{{ albumSeleccionado()!.artista }}</p>
                
                <!-- Estadísticas -->
                <div class="grid grid-cols-2 gap-4 mb-6 text-gray-300">
                  <div class="border border-gray-700 rounded-lg p-3 bg-black/30">
                    <span class="block text-xs font-medium text-gray-400 mb-1">Lanzamiento</span>
                    <span class="text-base font-semibold break-words">{{ albumSeleccionado()!.fechaLanzamiento }}</span>
                  </div>
                  <div class="border border-gray-700 rounded-lg p-3 bg-black/30">
                    <span class="block text-xs font-medium text-gray-400 mb-1">Canciones</span>
                    <span class="text-base font-semibold">{{ albumSeleccionado()!.cantidadCanciones }}</span>
                  </div>
                  <div class="border border-gray-700 rounded-lg p-3 bg-black/30">
                    <span class="block text-xs font-medium text-gray-400 mb-1">Reproducciones</span>
                    <span class="text-base font-semibold break-words">{{ albumSeleccionado()!.reproducciones }}</span>
                  </div>
                  <div class="border border-gray-700 rounded-lg p-3 bg-black/30">
                    <span class="block text-xs font-medium text-gray-400 mb-1">Oyentes</span>
                    <span class="text-base font-semibold break-words">{{ albumSeleccionado()!.oyentes }}</span>
                  </div>
                </div>

                <!-- Descripción -->
                <div class="border border-gray-700 rounded-lg p-4 bg-black/30 mb-8">
                  <h3 class="text-sm font-medium text-gray-400 mb-2">Descripción</h3>
                  <p class="text-gray-300 leading-relaxed break-words whitespace-pre-wrap max-h-60 overflow-y-auto">{{ albumSeleccionado()!.info }}</p>
                </div>

                <!-- Botón para Volver -->
                <button 
                  (click)="limpiarSeleccion()"
                  class="w-full md:w-auto mt-4 px-6 py-3 bg-gray-600 hover:bg-gray-700 rounded-lg font-semibold transition-colors">
                  &larr; Volver a la búsqueda
                </button>
              </div>
            </div>
          </div>
        } @else {
          <!-- Loading State -->
          @if (cargando()) {
            <div class="text-center py-12">
              <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-green-400"></div>
              <p class="mt-4 text-gray-300">Buscando álbumes...</p>
            </div>
          }

          <!-- Error State -->
          @if (error() && !cargando()) {
            <div class="bg-red-900/50 border-2 border-red-700 rounded-lg p-4 text-center">
              <p class="text-red-300 break-words">{{ error() }}</p>
              <button 
                (click)="error.set('')"
                class="mt-2 px-4 py-2 bg-red-700 hover:bg-red-600 rounded-lg text-sm transition-colors">
                Cerrar
              </button>
            </div>
          }

          <!-- Vista de Lista de Álbumes (Resultados) -->
          @if (!cargando() && !error()) {
            @if (albumsFiltrados().length > 0) {
              <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
                @for (album of albumsFiltrados(); track album.titulo) {
                  <div
                    class="bg-gray-900/90 border-2 border-green-500 rounded-lg overflow-hidden shadow-lg transition-all duration-300 hover:shadow-green-500/50 hover:scale-105 cursor-pointer animate-fade-in backdrop-blur-sm"
                    (click)="getInfo(album.artista, album.titulo)">

                    <img [src]="album.foto" alt="Portada de {{ album.titulo }}" class="w-full h-48 object-cover">

                    <div class="p-4">
                      <p class="text-lg font-bold truncate text-green-400">{{ album.titulo }}</p>
                      <p class="text-sm text-gray-400 truncate">{{ album.artista }}</p>

                      <button
                        class="mt-4 w-full bg-green-600 hover:bg-green-700 p-2 rounded-lg text-sm font-medium transition-colors">
                        Más información
                      </button>
                    </div>
                  </div>
                }
              </div>
            } @else {
              @if (busqueda().length > 0 && !cargando()) {
                <p class="text-center text-gray-300 col-span-full">No se encontraron álbumes para "{{busqueda()}}".</p>
              } @else if (!cargando()) {
                <p class="text-center text-gray-300 col-span-full">Comienza a buscar para ver resultados.</p>
              }
            }
          }
        }
      </div>
    </div>
  `,
  // Añadimos estilos para las animaciones y fondo con gradiente y círculos
  styles: [`
    @keyframes fade-in {
      from { opacity: 0; transform: translateY(10px); }
      to { opacity: 1; transform: translateY(0); }
    }
    .animate-fade-in {
      animation: fade-in 0.3s ease-out forwards;
    }
    .gradient-bg {
      background: linear-gradient(135deg, #1DB954 0%, #1ed760 25%, #1DB954 50%, #0d8043 75%, #0a5d2e 100%);
      background-size: 400% 400%;
      animation: gradient-shift 15s ease infinite;
    }
    @keyframes gradient-shift {
      0% { background-position: 0% 50%; }
      50% { background-position: 100% 50%; }
      100% { background-position: 0% 50%; }
    }
    .circle {
      position: absolute;
      border-radius: 50%;
      background: rgba(255, 255, 255, 0.1);
      filter: blur(40px);
      opacity: 0.6;
      animation: float 20s ease-in-out infinite;
    }
    .circle-1 {
      width: 500px;
      height: 500px;
      top: -100px;
      left: -100px;
      animation-delay: 0s;
    }
    .circle-2 {
      width: 600px;
      height: 600px;
      top: 20%;
      right: -150px;
      animation-delay: 3s;
    }
    .circle-3 {
      width: 400px;
      height: 400px;
      bottom: 10%;
      left: 10%;
      animation-delay: 6s;
    }
    .circle-4 {
      width: 700px;
      height: 700px;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      animation-delay: 9s;
    }
    .circle-5 {
      width: 350px;
      height: 350px;
      bottom: -50px;
      right: 20%;
      animation-delay: 12s;
    }
    .circle-6 {
      width: 450px;
      height: 450px;
      top: 70%;
      right: -80px;
      animation-delay: 15s;
    }
    @keyframes float {
      0%, 100% {
        transform: translate(0, 0) scale(1);
      }
      25% {
        transform: translate(30px, -30px) scale(1.1);
      }
      50% {
        transform: translate(-20px, 20px) scale(0.9);
      }
      75% {
        transform: translate(20px, 30px) scale(1.05);
      }
    }
  `],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class BuscarAlbumComponent {
  // --- Inyección de dependencias ---
  private apiService = inject(ServiceAPI);

  // --- Estado de la aplicación usando Signals ---

  // Término de búsqueda actual
  busqueda = signal('');

  // Álbumes filtrados que se muestran en la lista
  albumsFiltrados = signal<AlbumSimple[]>([]);

  // El álbum seleccionado para ver en detalle
  albumSeleccionado = signal<AlbumDetallado | null>(null);

  // Estados de carga y error
  cargando = signal(false);
  cargandoDetalle = signal(false);
  error = signal('');

  // --- Métodos del Componente ---

  /**
   * Se llama cada vez que el usuario escribe en el input.
   * Realiza la búsqueda en el API de Django.
   */
  buscar(event: Event) {
    const valor = (event.target as HTMLInputElement).value.trim();
    this.busqueda.set(valor);

    if (valor === '') {
      this.albumsFiltrados.set([]);
      this.error.set('');
      return;
    }

    // Realizar búsqueda en el API
    this.cargando.set(true);
    this.error.set('');

    this.apiService.searchAlbums(valor).subscribe({
      next: (albums: Album[]) => {
        // Convertir los álbumes del API al formato AlbumSimple
        const albumsSimples: AlbumSimple[] = albums.map(album => ({
          titulo: album.titulo,
          artista: album.artista,
          foto: album.foto
        }));
        this.albumsFiltrados.set(albumsSimples);
        this.cargando.set(false);
      },
      error: (err) => {
        console.error('Error al buscar álbumes:', err);
        this.error.set('Error al buscar álbumes. Por favor, intenta de nuevo.');
        this.cargando.set(false);
        this.albumsFiltrados.set([]);
      }
    });
  }

  /**
   * Obtiene la información detallada de un álbum desde el API de Django.
   */
  getInfo(artista: string, titulo: string) {
    this.cargandoDetalle.set(true);
    this.error.set('');

    this.apiService.getInfo(artista, titulo).subscribe({
      next: (album: Album) => {
        // Convertir el álbum del API al formato AlbumDetallado
        const detalle: AlbumDetallado = {
          titulo: album.titulo,
          artista: album.artista,
          foto: album.foto,
          fechaLanzamiento: this.formatearFecha(album.fechaLanzamiento),
          reproducciones: this.formatearNumero(album.reproducciones),
          oyentes: this.formatearNumero(album.oyentes),
          info: album.info || 'No hay descripción disponible.',
          cantidadCanciones: album.cantidadCanciones || 0
        };
        this.albumSeleccionado.set(detalle);
        this.cargandoDetalle.set(false);
      },
      error: (err) => {
        console.error('Error al obtener información del álbum:', err);
        this.error.set('Error al obtener información del álbum. Por favor, intenta de nuevo.');
        this.cargandoDetalle.set(false);
      }
    });
  }

  /**
   * Limpia el álbum seleccionado para volver a la lista.
   */
  limpiarSeleccion() {
    this.albumSeleccionado.set(null);
    this.error.set('');
  }

  /**
   * Formatea un número agregando comas como separadores de miles.
   */
  private formatearNumero(numero: number | string): string {
    if (typeof numero === 'string') {
      numero = parseInt(numero, 10);
    }
    if (isNaN(numero)) {
      return '0';
    }
    return numero.toLocaleString('es-ES');
  }

  /**
   * Formatea la fecha de lanzamiento.
   */
  private formatearFecha(fecha: string | null | undefined): string {
    if (!fecha) {
      return 'Fecha no disponible';
    }
    // La fecha viene en formato "01 Jan 2024" desde la API
    // Intentamos parsearla y formatearla
    try {
      const fechaObj = new Date(fecha);
      if (isNaN(fechaObj.getTime())) {
        return fecha; // Si no se puede parsear, devolver la fecha original
      }
      return fechaObj.toLocaleDateString('es-ES', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      });
    } catch {
      return fecha;
    }
  }
}
