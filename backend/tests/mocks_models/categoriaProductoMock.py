"""Mock directo para la entidad CategoriaProducto."""

from unittest.mock import MagicMock

from app.Productos.models.categoriaProductoModel import CategoriaProducto


def crearCategoriaProductoMock(
    idCategoriaProducto: int = 1,
    nombreCategoria: str = "Categoría",
    activoCategoria: bool = True,
    productos=None,
):
    categoriaMock = MagicMock(spec=CategoriaProducto)
    categoriaMock.idCategoriaProducto = idCategoriaProducto
    categoriaMock.nombreCategoria = nombreCategoria
    categoriaMock.activoCategoria = activoCategoria
    categoriaMock.productos = productos if productos is not None else []
    return categoriaMock
