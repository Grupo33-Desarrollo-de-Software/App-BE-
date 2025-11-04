import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { HttpClientModule } from '@angular/common/http';

import { AppRoutingModule } from './app-routing.module'; // <-- IMPORTA ESTE
import { AppComponent } from './app.component';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';

// Importa el componente standalone
import { BuscarAlbumComponent } from './buscar-album/buscar-album.component';

// Importa el módulo de Angular Material
import { MatToolbarModule } from '@angular/material/toolbar';

@NgModule({
  declarations: [
    AppComponent
    // Recuerda, BuscarAlbumComponent NO va aquí
  ],
  imports: [
    BrowserModule,
    AppRoutingModule, // <-- AÑÁDELO AQUÍ
    BrowserAnimationsModule,
    HttpClientModule, // <-- AÑÁDELO AQUÍ para habilitar HttpClient
    BuscarAlbumComponent, // <-- AÑÁDELO AQUÍ (porque es standalone)
    MatToolbarModule // <-- AÑÁDELO AQUÍ
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }