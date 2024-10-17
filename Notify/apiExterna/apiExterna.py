import requests

API_URL = "http://ws.audioscrobbler.com/2.0/"
KEY = "490431c7a4b3aa2e25808893a53d2742"

################################ ALBUM ################################
def parsearAlbum(album):
    resultado = {
        "titulo": album["name"],
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

def buscarAlbum(mbid):
    params = {
        "method": "album.getinfo",
        "api_key": KEY,
        "mbid": mbid,
        "format": "json",
    }
    r = requests.get(API_URL, params=params)
    albumJson = r.json()
    return albumJson

def parsearAlbum2(album):
    aux = album["album"]
    resultado = {
        "titulo": aux["name"],
        "artista": aux["artist"],
#        "fecha de lanzamiento": aux["wiki"]["published"],
        "playcount" : aux["playcount"],
        "listeners" : aux["listeners"],
#        "info" : aux["wiki"]["sumary"],
       "cantidadcanciones" : len(list(aux["tracks"])),
        "foto": aux["image"][3]["#text"],
  #      "tags" : aux["tags"]["tag"][1]["name"]
    }
    return resultado
#title, genre, releaseDate, length, country, released, playcount





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
