//módulo principal de la aplicación Angular
//define todos los módulos, componentes y servicios que usa la app
import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { HttpClientModule } from '@angular/common/http';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';

//componentes de la aplicación (standalone components)
import { BuscarAlbumComponent } from './buscar-album/buscar-album.component';
import { LoginComponent } from './login/login.component';
import { MonitoringComponent } from './monitoring/monitoring.component';

//módulos de Material Design para la interfaz de usuario
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatButtonModule } from '@angular/material/button';

@NgModule({
  //componentes que pertenecen a este módulo (no standalone)
  declarations: [
    AppComponent
  ],
  //módulos y componentes que este módulo necesita importar
  imports: [
    BrowserModule, //módulo base para aplicaciones web
    AppRoutingModule, //configuración de rutas
    BrowserAnimationsModule, //soporte para animaciones
    HttpClientModule, //servicio HTTP para hacer peticiones al backend
    BuscarAlbumComponent, //componente para buscar álbumes
    LoginComponent, //componente de login
    MonitoringComponent, //componente de monitoreo (solo admin)
    MatToolbarModule, //barra de herramientas de Material
    MatButtonModule //botones de Material
  ],
  //servicios disponibles en toda la aplicación
  providers: [],
  //componente que se carga al iniciar la aplicación
  bootstrap: [AppComponent]
})
export class AppModule { }