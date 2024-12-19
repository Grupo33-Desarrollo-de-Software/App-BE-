import { Component, OnInit } from '@angular/core';
import { ServiceAPI } from "../service-api.service";

@Component({
  selector: 'app-buscar-album',
  standalone: false,

  templateUrl: './buscar-album.component.html',
  styleUrl: './buscar-album.component.css'
})
export class BuscarAlbumComponent implements OnInit {

  constructor(private ServiceAPI: ServiceAPI) { }

  ngOnInit(): void {
    this.ServiceAPI.getServiceAPI(); // antes estaba this.getServiceAPI() pero no lo encontraba.
  }

  getServiceAPI() {
    this.ServiceAPI.getServiceAPI().subscribe({
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