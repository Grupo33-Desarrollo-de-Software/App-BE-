import requests

API_URL = "http://ws.audioscrobbler.com/2.0/"
KEY = "490431c7a4b3aa2e25808893a53d2742"

def parsearAlbum(album):
    resultado = {
        "titulo": album["name"],
        "artista": album["artist"],
        "foto": album["image"][3]["#text"],
    }
    return resultado

def tieneFoto(album):
    if album["foto"]:
        return True
    return False

# Retorna una lista de albums de la forma
# {
#   "titulo": "Doo-Wops & Hooligans",
#   "artista": "Bruno Mars",
#   "foto": "http://www...",
# }
# NOTA: solo retorna álbumes con fotos
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

def parsearArtista(artista):
    resultado = {
        "nombre": artista["name"],
        "foto": artista["image"],
    }
    return resultado

# Retorna una lista de artistas de la forma
# {
#   "nombre": "Bruno Mars",
#   "foto": "http://www...",
# }
# NOTA: solo retorna artistas con fotos
# def buscarArtista(nombre):
#     albums = []
#     params = {
#         "method": "album.search",
#         "api_key": KEY,
#         "album": nombre,
#         "format": "json",
#     }
#     r = requests.get(API_URL, params=params)
#     albumsJson = r.json()["results"]["albummatches"]["album"]
#     # print(albumsJson)
#     albums = map(parsearAlbum, albumsJson)
#     albums = filter(tieneFoto, albums)
#
#     return list(albums)
#
