import { Component, OnInit } from "@angular/core";
import { albumService } from "../album.service.ts";
import { album } from "../album.model.ts";

@Component({
  selector: "app-albums",
  templateUrl: "./albums.component.html",
  styleUrls: ["./albums.component.css"],
})
export class albumsComponent implements OnInit {
  albums: album[] = [];

  constructor(private albumService: albumService) {}

  ngOnInit(): void {
    this.albumService.getalbums().subscribe((data: album[]) => {
      this.albums = data;
    });
  }

  addalbum(title: string, content: string): void {
    const newalbum: album = { title, content } as album;
    this.albumService.addalbum(newalbum).subscribe((album) => {
      this.albums.push(album);
    });
  }
}
