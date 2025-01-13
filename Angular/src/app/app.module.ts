import { NgModule } from "@angular/core";
import { BrowserModule } from "@angular/platform-browser";

import { MatToolbarModule } from "@angular/material/toolbar";
import { AppRoutingModule } from "./app-routing.module";
import { AppComponent } from "./app.component";
import { provideAnimationsAsync } from "@angular/platform-browser/animations/async";
import { BuscarAlbumComponent } from "./buscar-album/buscar-album.component";
import { FormsModule } from "@angular/forms";
import { provideHttpClient, withFetch } from "@angular/common/http";

@NgModule({
  declarations: [
    AppComponent,
    BuscarAlbumComponent,
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    MatToolbarModule,
    FormsModule,
  ],
  providers: [
    provideAnimationsAsync(),
    provideHttpClient(withFetch()),
  ],
  bootstrap: [AppComponent],
})
export class AppModule {}
