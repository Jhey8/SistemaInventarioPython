class InventarioError(Exception):

    codigo_http = 400

class ProductoNoEncontradoError(InventarioError):

    codigo_http = 404

class DatosInvalidosError(InventarioError):

    codigo_http = 400

class StockInsuficienteError(InventarioError):

    codigo_http = 409

class CategoriaNoEncontradaError(InventarioError):
    codigo_http = 404

class ProveedorNoEncontradoError(InventarioError):

    codigo_http = 404

class PerfilNoEncontradoError(InventarioError):

    codigo_http = 404

class UsuarioNoEncontradoError(InventarioError):

    codigo_http = 404

class CredencialesInvalidasError(InventarioError):

    codigo_http = 401

class NoAutenticadoError(InventarioError):

    codigo_http = 401

class NoAutorizadoError(InventarioError):

    codigo_http = 403
