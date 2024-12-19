export interface Album {
    title: string,
    tags: string,
    releaseDate: Date,
    length: Number,
    cover: string, //Es un charfield ya que refiere al link de la imagen
    playcount: Number,
    autor: Number
}