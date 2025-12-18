from .lastfm_provider import LastFMProvider
#en caso de cambiar el proveedor, habria que cambiar el import este y todos los demas

#obtenemos la instancia del proveedor
_provider = LastFMProvider()

#ponemos todos los metodos que debe tener el proveedor
def buscarAlbums(nombre):
    return _provider.buscarAlbums(nombre)

def buscarAlbum(artista, album):
    return _provider.buscarAlbum(artista, album)

def parsearAlbum2(album):
    return _provider.parsearAlbum2(album)

def getArtista(artista):
    return _provider.getArtista(artista)

def parsearArtista2(artista):
    return _provider.parsearArtista2(artista)

def buscarArtista(nombre):
    return _provider.buscarArtista(nombre)

def getAlbumsSimilares(artista):
    return _provider.getAlbumsSimilares(artista)

def getTopAlbumsFromArtista(artista):
    return _provider.getTopAlbumsFromArtista(artista)

def sanitizarURL(string):
    return _provider.sanitizarURL(string)
