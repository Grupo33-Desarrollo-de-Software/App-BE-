//punto de entrada principal de la aplicación Angular
//este archivo inicia la aplicación cuando se carga en el navegador
import { platformBrowserDynamic } from '@angular/platform-browser-dynamic';
import { AppModule } from './app/app.module';

//inicia la aplicación Angular usando el módulo principal (AppModule)
//ngZoneEventCoalescing: optimiza el rendimiento agrupando eventos del DOM
platformBrowserDynamic().bootstrapModule(AppModule, {
  ngZoneEventCoalescing: true,
})
  //si hay un error al iniciar, lo muestra en la consola
  .catch(err => console.error(err));
