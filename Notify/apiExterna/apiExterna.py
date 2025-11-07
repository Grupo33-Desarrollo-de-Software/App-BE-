import requests
import time
from datetime import datetime
import pprint

archivo_key = open("apiExterna/key.txt", "r")
KEY = archivo_key.read().strip()

API_URL = "http://ws.audioscrobbler.com/2.0/"


################################ ALBUM ################################
def parsearAlbum(album):
    resultado = {
        "titulo": album["name"],
        "artista": album["artist"],
        "foto": album["image"][3]["#text"],
        "mbid": album.get("mbid"),
    }
    return resultado


def buscarAlbums(nombre):
    albums = []
    params = {
        "method": "album.search",
        "api_key": KEY,
        "album": nombre,
        "format": "json",
    }
    r = requests.get(API_URL, params=params)
    albumsJson = r.json()["results"]["albummatches"]["album"]
    albums = map(parsearAlbum, albumsJson)
    albums = filter(tieneFoto, albums)
    return list(albums)


# Retorna una lista de albums de la forma
# {
#   "titulo": "Doo-Wops & Hooligans",
#   "artista": "Bruno Mars",
#   "foto": "http://www...",
# }
# NOTA: solo retorna álbumes con fotos


def tieneFoto(elem):
    if elem["foto"]:
        return True
    return False


def buscarAlbum(artista, album):
    params = {
        "method": "album.getinfo",
        "api_key": KEY,
        "artist": artista,
        "album": desanitizarURL(album),
        "format": "json",
    }
    r = requests.get(API_URL, params=params)
    albumJson = r.json()
    return parsearAlbum2(albumJson)


def getReleaseDate(aux):
    r = aux.get("wiki", {}).get("published", "")
    if len(r) == 0:
        return None
    return r[0:11]


def parsearAlbum2(album):  # Este parsearAlbum2 es para guardar el album en la bdd
    aux = album["album"]
    resultado = {
        "titulo": aux["name"],
        "artista": aux["artist"],
        "fechaLanzamiento": getReleaseDate(aux),
        "reproducciones": aux["playcount"],
        "oyentes": aux["listeners"],
        "info": aux.get("wiki", {}).get("summary", ""),
        "cantidadCanciones": parsearCantidadCanciones(aux),
        "foto": aux["image"][3]["#text"],
        "etiquetas": parsearTag(aux["tags"]),
        "duracion": calcularDuracion(aux),
    }
    return resultado


# title, genre, releaseDate, length, country, released, playcount


def parsearAlbum3(album):  # Este parsearAlbum3 hacer la busqueda para la API
    aux = album["album"]
    resultado = {
        "title": aux["name"],
        "autor": aux["artist"],
        "releaseDate": getReleaseDate(aux),
        "playcount": aux["playcount"],
        "cover": aux["image"][3]["#text"],
        "tags": parsearTag(aux["tags"]),
        "length": calcularDuracion(aux),
    }
    return resultado


def parsearCantidadCanciones(aux):
    t = aux.get("tracks", [])
    if t:
        return len(list(t["track"]))
    return 0


def parsearTag(tags):
    if not tags:
        return ""
    t = tags.get("tag", None)
    if t:
        if type(t) is dict:
            return t["name"]
        return t[0]["name"]
    return ""


def calcularDuracion(aux):
    duracion = 0
    t = aux.get("tracks", [])
    if not t:
        return 0
    track = t.get("track")
    if not track:
        return 0
    if type(track) == dict:
        return track.get("duration", 0) // 60

    for x in track:
        duracion += x.get("duration", 0) or 0
    return duracion // 60


def sanitizarURL(string):
    return string.replace("/", "%2F")


def desanitizarURL(string):
    return string.replace("%2F", "/")


################################ ARTISTA ################################
def parsearArtista(artista):
    resultado = {
        "nombre": artista["name"],
        "foto": artista["image"][3]["#text"],
        "oyentes": artista["listeners"],
        "pagina": artista["url"],
    }
    return resultado


def parsearArtista2(artista):
    aux = artista["artist"]
    resultado = {
        "nombre": aux["name"],
        "foto": aux["image"][3]["#text"],
        "oyentes": aux["stats"]["listeners"],
        "reproducciones": aux["stats"]["playcount"],
        "resumen": aux["bio"]["summary"],
    }
    return resultado


def oyentes(artista):
    return int(artista["oyentes"])


def buscarArtista(nombre):
    artistas = []
    params = {
        "method": "artist.search",
        "api_key": KEY,
        "artist": nombre,
        "format": "json",
    }
    r = requests.get(API_URL, params=params)
    artistsJson = r.json()["results"]["artistmatches"]["artist"]
    artistas = map(parsearArtista, artistsJson)
    artistas = list(filter(tieneFoto, artistas))
    artistas.sort(reverse=True, key=oyentes)
    return artistas


# Retorna una lista de artistas de la forma
# {
#   "nombre": "Bruno Mars",
#   "foto": "http://www...",
# }
# NOTA: solo retorna artistas con fotos


def getArtista(artista):
    params = {
        "method": "artist.getinfo",
        "api_key": KEY,
        "artist": artista,
        "format": "json",
    }
    r = requests.get(API_URL, params=params)
    artistaJson = r.json()
    return artistaJson


# Retorna una lista de nombres de artistas similares
def getArtistaSimilar(artista):
    params = {
        "method": "artist.getsimilar",
        "api_key": KEY,
        "artist": artista,
        "format": "json",
    }
    r = requests.get(API_URL, params=params)
    similarJSON = r.json()

    lista = []

    contador = 0

    for artist in similarJSON["similarartists"]["artist"]:
        lista.append(artist["name"])
        contador += 1
        if contador > 4:
            break

    return lista


# retorna una lista de albums similares a los que hace el artista
# lo hace con el mismo formato que buscarAlbums
def getAlbumsSimilares(artista):
    artistasSimilares = getArtistaSimilar(artista)

    similares = []

    for nombreArtista in artistasSimilares:
        encontrados = buscarAlbums(nombreArtista)
        similares.extend(encontrados)

    return similares


def getTopAlbumsFromArtista(artista):
    params = {
        "method": "artist.gettopalbums",
        "api_key": KEY,
        "artist": artista,
        "limit": 20,
        "format": "json",
    }
    r = requests.get(API_URL, params=params)
    topJson = r.json().get("topalbums").get("album")
    top = map(parsearAlbum, topJson)
    top = filter(tieneFoto, top)
    top = list(top)

    inicio = time.time()
    topAlbum = []
    for a in top:
        album = buscarAlbum(artista, a["titulo"])
        topAlbum.append(album)
    fin = time.time()
    return topAlbum
