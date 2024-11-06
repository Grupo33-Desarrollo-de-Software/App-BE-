import requests
from datetime import datetime

API_URL = "http://ws.audioscrobbler.com/2.0/"
KEY = "490431c7a4b3aa2e25808893a53d2742"

################################ ALBUM ################################
def parsearAlbum(album):
    resultado = {
        "titulo": album["name"],
        "tituloURL": sanitizarURL(album["name"]),
        "artista": album["artist"],
        "foto": album["image"][3]["#text"],
        "mbid" : album["mbid"],
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
    # print(albumsJson)
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
    return albumJson

def parsearAlbum2(album):
    aux = album["album"]
    print(album)
    resultado = {
        "titulo": aux["name"],
        "artista": aux["artist"],
        "releaseDate": aux.get("wiki",{}).get("published",''),#[0:11],
        "playcount" : aux["playcount"],
        "listeners" : aux["listeners"],
        "info" : aux.get("wiki",{}).get("summary",''),
       "cantidadcanciones" : len(list(aux["tracks"]["track"])),
        "foto": aux["image"][3]["#text"],
        "tags" : parsearTag(aux["tags"]),
        "duracion" : calcularDuracion(aux["tracks"]["track"])
    }
    return resultado
#title, genre, releaseDate, length, country, released, playcount

def parsearTag(tags):
    t = tags.get("tag",None)
    if t:
        return t[0]["name"]
    return ""

def calcularDuracion(track):
    duracion = 0
    for x in track:
        duracion += x.get("duration",0) or 0
    return duracion//60

def sanitizarURL(string):
    return string.replace("/","%2F")

def desanitizarURL(string):
    return string.replace("%2F","/")

################################ ARTISTA ################################
def parsearArtista(artista):
    resultado = {
        "nombre": artista["name"],
        "foto": artista["image"][3]["#text"],
        "oyentes": artista["listeners"],
        "pagina": artista["url"],
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