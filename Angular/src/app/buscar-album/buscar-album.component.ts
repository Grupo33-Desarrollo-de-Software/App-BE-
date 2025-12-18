//componente para buscar y mostrar álbumes
//permite buscar álbumes por nombre o artista y ver detalles
import { ChangeDetectionStrategy, Component, signal, inject } from '@angular/core';
import { HttpClientModule } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { ServiceAPI } from '../service-api.service';
import { Album } from '../buscar-album';

//interfaz: estructura simplificada de un álbum para mostrar en la lista de resultados
interface AlbumSimple {
  titulo: string;
  artista: string;
  foto: string;
}

//interfaz: estructura detallada de un álbum para la vista de detalles
interface AlbumDetallado {
  titulo: string;
  artista: string;
  foto: string;
  fechaLanzamiento: string;
  reproducciones: string; // Formato con comas
  oyentes: string; // Formato con comas
  info: string;
  cantidadCanciones: number;
}

@Component({
  selector: 'app-buscar-album',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="min-h-screen bg-black text-white p-6">
      <div class="max-w-7xl mx-auto">
        <div class="flex justify-center mb-8">
          <img src="assets/logo.png" alt="Notify Logo" class="h-12 w-auto object-contain max-w-[150px]">
        </div>
        <div class="mb-8">
          <h1 class="text-4xl font-bold mb-2 text-white">Búsqueda de Álbumes</h1>
          <p class="text-gray-400">Encuentra tus álbumes favoritos</p>
        </div>

        <div class="mb-6">
          <form class="flex w-full max-w-2xl mx-auto" (submit)="$event.preventDefault()">
            <input 
              type="text" 
              id="album" 
              name="album"
              placeholder="Buscar por artista o álbum..."
              class="flex-grow p-4 rounded-l-lg bg-gray-800 text-white placeholder-gray-400 border border-gray-700 focus:border-green-500 focus:ring-green-500 focus:outline-none transition-colors"
              [value]="busqueda()"
              (input)="buscar($event)">
            <button 
              type="submit"
              class="p-4 bg-[#1DB954] hover:bg-[#1ed760] rounded-r-lg font-semibold transition-colors text-black">
              Buscar
            </button>
          </form>
        </div>

        @if (cargandoDetalle()) {
          <div class="text-center py-12">
            <div class="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-green-500"></div>
            <p class="mt-4 text-gray-400">Cargando información del álbum...</p>
          </div>
        } @else if (albumSeleccionado()) {
          <div class="bg-gray-900 rounded-lg p-6 md:p-8 border border-gray-800">
            <div class="flex flex-col md:flex-row gap-8">
              
              <div class="w-full md:w-1/3 flex-shrink-0">
                <img 
                  [src]="albumSeleccionado()!.foto" 
                  alt="Portada de {{ albumSeleccionado()!.titulo }}"
                  class="w-full h-auto rounded-lg object-cover aspect-square shadow-lg border border-gray-800">
              </div>
              
              <div class="flex-1 min-w-0">
                <h1 class="text-3xl md:text-4xl font-bold mb-2 break-words text-white">{{ albumSeleccionado()!.titulo }}</h1>
                <p class="text-xl md:text-2xl font-light text-gray-300 mb-6 break-words">{{ albumSeleccionado()!.artista }}</p>
                
                <div class="grid grid-cols-2 gap-4 mb-6">
                  <div class="bg-gray-800 rounded-lg p-4 border border-gray-700">
                    <span class="block text-xs font-medium text-gray-400 mb-1">Lanzamiento</span>
                    <span class="text-base font-semibold text-white break-words">{{ albumSeleccionado()!.fechaLanzamiento }}</span>
                  </div>
                  <div class="bg-gray-800 rounded-lg p-4 border border-gray-700">
                    <span class="block text-xs font-medium text-gray-400 mb-1">Canciones</span>
                    <span class="text-base font-semibold text-white">{{ albumSeleccionado()!.cantidadCanciones }}</span>
                  </div>
                  <div class="bg-gray-800 rounded-lg p-4 border border-gray-700">
                    <span class="block text-xs font-medium text-gray-400 mb-1">Reproducciones</span>
                    <span class="text-base font-semibold text-white break-words">{{ albumSeleccionado()!.reproducciones }}</span>
                  </div>
                  <div class="bg-gray-800 rounded-lg p-4 border border-gray-700">
                    <span class="block text-xs font-medium text-gray-400 mb-1">Oyentes</span>
                    <span class="text-base font-semibold text-white break-words">{{ albumSeleccionado()!.oyentes }}</span>
                  </div>
                </div>

                <div class="bg-gray-800 rounded-lg p-4 border border-gray-700 mb-8">
                  <h3 class="text-sm font-medium text-gray-400 mb-2">Descripción</h3>
                  <p class="text-gray-300 leading-relaxed break-words whitespace-pre-wrap max-h-60 overflow-y-auto">{{ albumSeleccionado()!.info }}</p>
                </div>

                <button 
                  (click)="limpiarSeleccion()"
                  class="w-full md:w-auto mt-4 px-6 py-3 bg-gray-800 hover:bg-gray-700 rounded-lg font-semibold transition-colors text-white border border-gray-700">
                  &larr; Volver a la búsqueda
                </button>
              </div>
            </div>
          </div>
        } @else {
          @if (cargando()) {
            <div class="text-center py-12">
              <div class="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-green-500"></div>
              <p class="mt-4 text-gray-400">Buscando álbumes...</p>
            </div>
          }

          @if (error() && !cargando()) {
            <div class="mb-6 p-4 bg-red-500/20 border border-red-500 rounded-lg text-red-200">
              <p class="break-words mb-2">{{ error() }}</p>
              <button 
                (click)="error.set('')"
                class="px-4 py-2 bg-red-700 hover:bg-red-600 rounded-lg text-sm transition-colors">
                Cerrar
              </button>
            </div>
          }

          @if (!cargando() && !error()) {
            @if (albumsFiltrados().length > 0) {
              <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
                @for (album of albumsFiltrados(); track album.titulo) {
                  <div
                    class="bg-gray-900 rounded-lg overflow-hidden border border-gray-800 shadow-lg transition-all duration-300 hover:border-[#1DB954] hover:shadow-[#1DB954]/20 cursor-pointer"
                    (click)="getInfo(album.artista, album.titulo)">

                    <img [src]="album.foto" alt="Portada de {{ album.titulo }}" class="w-full h-48 object-cover">

                    <div class="p-4">
                      <p class="text-lg font-bold truncate text-white mb-1">{{ album.titulo }}</p>
                      <p class="text-sm text-gray-400 truncate mb-4">{{ album.artista }}</p>

                      <button
                        class="w-full bg-[#1DB954] hover:bg-[#1ed760] p-2 rounded-lg text-sm font-medium transition-colors text-black font-semibold">
                        Más información
                      </button>
                    </div>
                  </div>
                }
              </div>
            } @else {
              @if (busqueda().length > 0 && !cargando()) {
                <div class="bg-gray-900 rounded-lg p-8 border border-gray-800 text-center">
                  <p class="text-gray-400 text-lg">No se encontraron álbumes para "{{busqueda()}}".</p>
                </div>
              } @else if (!cargando()) {
                <div class="bg-gray-900 rounded-lg p-8 border border-gray-800 text-center">
                  <p class="text-gray-400 text-lg">Comienza a buscar para ver resultados.</p>
                </div>
              }
            }
          }
        }
      </div>
    </div>
  `,
  styles: [`
    @keyframes spin {
      to {
        transform: rotate(360deg);
      }
    }
    .animate-spin {
      animation: spin 1s linear infinite;
    }
  `],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class BuscarAlbumComponent {
  //inyecta el servicio de API usando inject() (alternativa a constructor)
  private apiService = inject(ServiceAPI);

  //estados reactivos usando signals
  busqueda = signal(''); //texto actual de búsqueda en el input
  albumsFiltrados = signal<AlbumSimple[]>([]); //lista de álbumes encontrados en la búsqueda
  albumSeleccionado = signal<AlbumDetallado | null>(null); //álbum seleccionado para ver detalles
  cargando = signal(false); //indica si está cargando la búsqueda
  cargandoDetalle = signal(false); //indica si está cargando los detalles de un álbum
  error = signal(''); //mensaje de error a mostrar

  //busca álbumes según el texto ingresado en el input
  //se ejecuta cada vez que el usuario escribe en el campo de búsqueda
  buscar(event: Event) {
    //obtiene el valor del input y elimina espacios al inicio y final
    const valor = (event.target as HTMLInputElement).value.trim();
    this.busqueda.set(valor);

    //si el campo está vacío, limpia los resultados
    if (valor === '') {
      this.albumsFiltrados.set([]);
      this.error.set('');
      return;
    }

    //activa el estado de carga y limpia errores anteriores
    this.cargando.set(true);
    this.error.set('');

    //hace la petición al backend para buscar álbumes
    this.apiService.searchAlbums(valor).subscribe({
      //si la búsqueda es exitosa
      next: (albums: Album[]) => {
        //convierte los álbumes completos a formato simple para la lista
        const albumsSimples: AlbumSimple[] = albums.map(album => ({
          titulo: album.titulo,
          artista: album.artista,
          foto: album.foto
        }));
        //actualiza la lista de álbumes y desactiva el estado de carga
        this.albumsFiltrados.set(albumsSimples);
        this.cargando.set(false);
      },
      //si hay un error en la búsqueda
      error: (err) => {
        console.error('Error al buscar álbumes:', err);
        this.error.set('Error al buscar álbumes. Por favor, intenta de nuevo.');
        this.cargando.set(false);
        this.albumsFiltrados.set([]); //limpia los resultados
      }
    });
  }


  //obtiene información detallada de un álbum específico
  //se ejecuta cuando el usuario hace clic en un álbum de la lista
  getInfo(artista: string, titulo: string) {
    //activa el estado de carga de detalles y limpia errores
    this.cargandoDetalle.set(true);
    this.error.set('');

    //hace la petición al backend para obtener los detalles del álbum
    this.apiService.getInfo(artista, titulo).subscribe({
      //si la petición es exitosa
      next: (album: Album) => {
        //convierte el álbum a formato detallado con datos formateados
        const detalle: AlbumDetallado = {
          titulo: album.titulo,
          artista: album.artista,
          foto: album.foto,
          fechaLanzamiento: this.formatearFecha(album.fechaLanzamiento), //formatea la fecha
          reproducciones: this.formatearNumero(album.reproducciones), //formatea el número
          oyentes: this.formatearNumero(album.oyentes), //formatea el número
          info: album.info || 'No hay descripción disponible.', //usa mensaje por defecto si no hay info
          cantidadCanciones: album.cantidadCanciones || 0 //usa 0 si no hay cantidad
        };
        //actualiza el álbum seleccionado y desactiva el estado de carga
        this.albumSeleccionado.set(detalle);
        this.cargandoDetalle.set(false);
      },
      //si hay un error al obtener los detalles
      error: (err) => {
        console.error('Error al obtener información del álbum:', err);
        this.error.set('Error al obtener información del álbum. Por favor, intenta de nuevo.');
        this.cargandoDetalle.set(false);
      }
    });
  }

  //limpia la selección del álbum y vuelve a mostrar la lista de resultados
  limpiarSeleccion() {
    this.albumSeleccionado.set(null);
    this.error.set('');
  }

  //formatea un número agregando separadores de miles (comas)
  //ejemplo: 1000000 -> "1.000.000" (formato español)
  private formatearNumero(numero: number | string): string {
    //si es string, lo convierte a número
    if (typeof numero === 'string') {
      numero = parseInt(numero, 10);
    }
    //si no es un número válido, retorna '0'
    if (isNaN(numero)) {
      return '0';
    }
    //formatea el número con separadores de miles en formato español
    return numero.toLocaleString('es-ES');
  }

  //formatea una fecha en formato legible en español
  //ejemplo: "2023-01-15" -> "15 de enero de 2023"
  private formatearFecha(fecha: string | null | undefined): string {
    //si no hay fecha, retorna mensaje por defecto
    if (!fecha) {
      return 'Fecha no disponible';
    }
    try {
      //intenta parsear la fecha
      const fechaObj = new Date(fecha);
      //si no es una fecha válida, retorna la fecha original
      if (isNaN(fechaObj.getTime())) {
        return fecha;
      }
      //formatea la fecha en español con formato largo
      return fechaObj.toLocaleDateString('es-ES', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      });
    } catch {
      //si hay error, retorna la fecha original
      return fecha;
    }
  }
}
