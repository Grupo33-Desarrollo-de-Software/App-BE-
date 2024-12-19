import { Component, OnInit } from '@angular/core';
import { ServiceAPI } from "../service-api.service";

@Component({
  selector: 'app-buscar-album',
  standalone: false,

  templateUrl: './buscar-album.component.html',
  styleUrl: './buscar-album.component.css'
})
export class BuscarAlbumComponent implements OnInit {

  constructor(private serviceAPI: ServiceAPI) { }

  ngOnInit(): void {
    this.getServiceAPI(); // antes estaba this.getServiceAPI() pero no lo encontraba.
  }

  getServiceAPI() {
    this.serviceAPI.getServiceAPI().subscribe({
      next: (data) => {
        console.log(data);
      },
      error: (error) => {
        console.log(error);
      }
    }
    )
  }

}