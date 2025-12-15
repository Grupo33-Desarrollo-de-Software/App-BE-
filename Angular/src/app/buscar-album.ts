// Define la estructura de un álbum
export interface Album {
  titulo: string;
  artista: string;
  fechaLanzamiento: string;
  reproducciones: number;
  oyentes: number;
  info: string;
  cantidadCanciones: number;
  foto: string; // URL de la imagen
  etiquetas: string;
  duracion: number; // Duración en segundos
}
