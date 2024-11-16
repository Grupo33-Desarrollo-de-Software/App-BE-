import { Component } from "@angular/core";
import { RouterOutlet } from "@angular/router";
import { albumsComponent } from "./album/album.component.ts";

@Component({
  selector: "app-root",
  standalone: true,
  imports: [RouterOutlet, albumsComponent],
  templateUrl: "./app.component.html",
  styleUrl: "./app.component.css",
})
export class AppComponent {
  title = "angular";
}
