export interface Album {
  id?: number;
  title: string;
  tags: string;
  releaseDate?: Date;
  length: number;
  cover: string;
  playcount: number;
  autor: object;
}
