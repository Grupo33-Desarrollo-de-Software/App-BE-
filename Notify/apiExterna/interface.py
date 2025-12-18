from abc import ABC, abstractmethod
from typing import List, Dict, Any


class MusicAPIProvider(ABC):
    #interfaz abstracta para proveedores. en caso de cambiar el proveedor, esta clase queda igual

    @abstractmethod
    def buscarAlbums(self, nombre: str) -> List[Dict[str, Any]]:
        """
        Busca álbumes por nombre.
        
        Args:
            nombre: Nombre del álbum o artista a buscar
            
        Returns:
            Lista de diccionarios con formato:
            {
                "titulo": str,
                "artista": str,
                "foto": str,
                "mbid": str (opcional)
            }
        """
        pass

    @abstractmethod
    def buscarAlbum(self, artista: str, album: str) -> Dict[str, Any]:
        """
        Busca información detallada de un álbum específico.
        
        Args:
            artista: Nombre del artista
            album: Nombre del álbum
            
        Returns:
            Diccionario con información del álbum en formato parseado
        """
        pass

    @abstractmethod
    def parsearAlbum2(self, album: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parsea la respuesta de la API a formato para guardar en BD.
        
        Args:
            album: Diccionario con datos del álbum de la API
            
        Returns:
            Diccionario parseado con formato:
            {
                "titulo": str,
                "artista": str,
                "fechaLanzamiento": str (formato "DD MMM YYYY"),
                "reproducciones": str,
                "oyentes": str,
                "info": str,
                "cantidadCanciones": int,
                "foto": str,
                "etiquetas": str,
                "duracion": int (minutos)
            }
        """
        pass

    @abstractmethod
    def getArtista(self, artista: str) -> Dict[str, Any]:
        """
        Obtiene información de un artista.
        
        Args:
            artista: Nombre del artista
            
        Returns:
            Diccionario con información del artista en formato raw de la API
        """
        pass

    @abstractmethod
    def parsearArtista2(self, artista: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parsea la respuesta de la API de artista a formato estándar.
        
        Args:
            artista: Diccionario con datos del artista de la API
            
        Returns:
            Diccionario parseado con formato:
            {
                "nombre": str,
                "foto": str,
                "oyentes": str,
                "reproducciones": str,
                "resumen": str
            }
        """
        pass

    @abstractmethod
    def buscarArtista(self, nombre: str) -> List[Dict[str, Any]]:
        """
        Busca artistas por nombre.
        
        Args:
            nombre: Nombre del artista a buscar
            
        Returns:
            Lista de diccionarios con formato:
            {
                "nombre": str,
                "foto": str,
                "oyentes": str,
                "pagina": str
            }
        """
        pass

    @abstractmethod
    def getAlbumsSimilares(self, artista: str) -> List[Dict[str, Any]]:
        """
        Obtiene álbumes similares a los de un artista.
        
        Args:
            artista: Nombre del artista
            
        Returns:
            Lista de diccionarios con formato igual a buscarAlbums()
        """
        pass

    @abstractmethod
    def getTopAlbumsFromArtista(self, artista: str) -> List[Dict[str, Any]]:
        """
        Obtiene los álbumes más populares de un artista.
        
        Args:
            artista: Nombre del artista
            
        Returns:
            Lista de diccionarios con información detallada de álbumes
        """
        pass

    @abstractmethod
    def sanitizarURL(self, string: str) -> str:
        """
        Sanitiza una cadena para usarla en URLs.
        
        Args:
            string: Cadena a sanitizar
            
        Returns:
            Cadena sanitizada
        """
        pass

