export interface Album {
  titulo: string;
  artista: string;
  fechaLanzamiento: string;
  reproducciones: number;
  oyentes: number;
  info: string;
  cantidadCanciones: number;
  foto: string; // Es un charfield ya que refiere al link de la imagen
  etiquetas: string;
  duracion: number; // En segundos
}
