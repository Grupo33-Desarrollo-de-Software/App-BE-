import requests
import time
from typing import List, Dict, Any
from .interface import MusicAPIProvider


class LastFMProvider(MusicAPIProvider):
    #implementacion de MAP para la api de lastfm
    #estos son los metodos q teniamos definidos en albums
    
    def __init__(self, api_key: str = None, api_url: str = "http://ws.audioscrobbler.com/2.0/"):
        if api_key is None:
            archivo_key = open("apiExterna/key.txt", "r")
            self.key = archivo_key.read().strip()
            archivo_key.close()
        else:
            self.key = api_key
        self.api_url = api_url

    def buscarAlbums(self, nombre: str) -> List[Dict[str, Any]]:
        albums = []
        params = {
            "method": "album.search",
            "api_key": self.key,
            "album": nombre,
            "format": "json",
        }
        r = requests.get(self.api_url, params=params)
        albumsJson = r.json()["results"]["albummatches"]["album"]
        albums = map(self._parsearAlbum, albumsJson)
        albums = filter(self._tieneFoto, albums)
        return list(albums)

    def buscarAlbum(self, artista: str, album: str) -> Dict[str, Any]:
        params = {
            "method": "album.getinfo",
            "api_key": self.key,
            "artist": artista,
            "album": self._desanitizarURL(album),
            "format": "json",
        }
        r = requests.get(self.api_url, params=params)
        albumJson = r.json()
        return self.parsearAlbum2(albumJson)

    def parsearAlbum2(self, album: Dict[str, Any]) -> Dict[str, Any]:
        aux = album["album"]
        resultado = {
            "titulo": aux["name"],
            "artista": aux["artist"],
            "fechaLanzamiento": self._getReleaseDate(aux),
            "reproducciones": aux["playcount"],
            "oyentes": aux["listeners"],
            "info": aux.get("wiki", {}).get("summary", ""),
            "cantidadCanciones": self._parsearCantidadCanciones(aux),
            "foto": aux["image"][3]["#text"],
            "etiquetas": self._parsearTag(aux["tags"]),
            "duracion": self._calcularDuracion(aux),
        }
        return resultado

    def getArtista(self, artista: str) -> Dict[str, Any]:
        params = {
            "method": "artist.getinfo",
            "api_key": self.key,
            "artist": artista,
            "format": "json",
        }
        r = requests.get(self.api_url, params=params)
        artistaJson = r.json()
        return artistaJson

    def parsearArtista2(self, artista: Dict[str, Any]) -> Dict[str, Any]:
        aux = artista["artist"]
        resultado = {
            "nombre": aux["name"],
            "foto": aux["image"][3]["#text"],
            "oyentes": aux["stats"]["listeners"],
            "reproducciones": aux["stats"]["playcount"],
            "resumen": aux["bio"]["summary"],
        }
        return resultado

    def buscarArtista(self, nombre: str) -> List[Dict[str, Any]]:
        artistas = []
        params = {
            "method": "artist.search",
            "api_key": self.key,
            "artist": nombre,
            "format": "json",
        }
        r = requests.get(self.api_url, params=params)
        artistsJson = r.json()["results"]["artistmatches"]["artist"]
        artistas = map(self._parsearArtista, artistsJson)
        artistas = list(filter(self._tieneFoto, artistas))
        artistas.sort(reverse=True, key=self._oyentes)
        return artistas

    def getAlbumsSimilares(self, artista: str) -> List[Dict[str, Any]]:
        artistasSimilares = self._getArtistaSimilar(artista)
        similares = []
        for nombreArtista in artistasSimilares:
            encontrados = self.buscarAlbums(nombreArtista)
            similares.extend(encontrados)
        return similares

    def getTopAlbumsFromArtista(self, artista: str) -> List[Dict[str, Any]]:
        params = {
            "method": "artist.gettopalbums",
            "api_key": self.key,
            "artist": artista,
            "limit": 20,
            "format": "json",
        }
        r = requests.get(self.api_url, params=params)
        topJson = r.json().get("topalbums").get("album")
        top = map(self._parsearAlbum, topJson)
        top = filter(self._tieneFoto, top)
        top = list(top)

        topAlbum = []
        for a in top:
            album = self.buscarAlbum(artista, a["titulo"])
            topAlbum.append(album)
        return topAlbum

    def sanitizarURL(self, string: str) -> str:
        return string.replace("/", "%2F")


    def _parsearAlbum(self, album: Dict[str, Any]) -> Dict[str, Any]:
        resultado = {
            "titulo": album["name"],
            "artista": album["artist"],
            "foto": album["image"][3]["#text"],
            "mbid": album.get("mbid"),
        }
        return resultado

    def _tieneFoto(self, elem: Dict[str, Any]) -> bool:
        if elem["foto"]:
            return True
        return False

    def _getReleaseDate(self, aux: Dict[str, Any]) -> str:
        r = aux.get("wiki", {}).get("published", "")
        if len(r) == 0:
            return None
        return r[0:11]

    def _parsearCantidadCanciones(self, aux: Dict[str, Any]) -> int:
        t = aux.get("tracks", [])
        if t:
            return len(list(t["track"]))
        return 0

    def _parsearTag(self, tags: Dict[str, Any]) -> str:
        if not tags:
            return ""
        t = tags.get("tag", None)
        if t:
            if type(t) is dict:
                return t["name"]
            return t[0]["name"]
        return ""

    def _calcularDuracion(self, aux: Dict[str, Any]) -> int:
        duracion = 0
        t = aux.get("tracks", [])
        if not t:
            return 0
        track = t.get("track")
        if not track:
            return 0
        if type(track) == dict:
            return (track.get("duration", 0) or 0) // 60

        for x in track:
            duracion += x.get("duration", 0) or 0
        return duracion // 60

    def _desanitizarURL(self, string: str) -> str:
        return string.replace("%2F", "/")

    def _parsearArtista(self, artista: Dict[str, Any]) -> Dict[str, Any]:
        resultado = {
            "nombre": artista["name"],
            "foto": artista["image"][3]["#text"],
            "oyentes": artista["listeners"],
            "pagina": artista["url"],
        }
        return resultado

    def _oyentes(self, artista: Dict[str, Any]) -> int:
        return int(artista["oyentes"])

    def _getArtistaSimilar(self, artista: str) -> List[str]:
        params = {
            "method": "artist.getsimilar",
            "api_key": self.key,
            "artist": artista,
            "format": "json",
        }
        r = requests.get(self.api_url, params=params)
        similarJSON = r.json()

        lista = []
        contador = 0

        for artist in similarJSON["similarartists"]["artist"]:
            lista.append(artist["name"])
            contador += 1
            if contador > 4:
                break

        return lista

