from app.Clientes.modells.clienteModel import Cliente
from app.Clientes.schemas.clienteSchemas import *

class ClienteRepository:
    def __init__(self, dbSession):
        self.dbSession = dbSession

    def listarClientes(self):
        return self.dbSession.query(Cliente).all()

    def obtenerPorId(self, idCliente: int):
        return self.dbSession.query(Cliente).filter(Cliente.idCliente == idCliente).first()

    def validarCedulaExistente(self, cedula: str):
        return self.dbSession.query(Cliente).filter(Cliente.cedulaCliente == cedula).first()

    def crearCliente(self, cliente: ClienteCrearSchema):
        if self.validarCedulaExistente(cliente.cedulaCliente):
            return None
        nuevo = Cliente(
            nombreCliente=cliente.nombreCliente,
            cedulaCliente=cliente.cedulaCliente,
            telefonoCliente=cliente.telefonoCliente,
            direccionCliente=cliente.direccionCliente,
            emailCliente=cliente.emailCliente,
            activoCliente=True
        )
        self.dbSession.add(nuevo)
        self.dbSession.commit()
        self.dbSession.refresh(nuevo)
        return nuevo

    def modificarCliente(self, idCliente: int, clienteActualizar: ClienteActualizarSchema):
        cliente = self.obtenerPorId(idCliente)
        if not cliente:
            return None
        datos = clienteActualizar.model_dump(exclude_unset=True)
        camposValidos = ["nombreCliente", "telefonoCliente", "direccionCliente", "emailCliente", "activoCliente"]
        for campo, valor in datos.items():
            if campo in camposValidos:
                setattr(cliente, campo, valor)
        self.dbSession.commit()
        self.dbSession.refresh(cliente)
        return cliente

    def deshabilitarCliente(self, idCliente: int):
        cliente = self.obtenerPorId(idCliente)
        if not cliente:
            return None
        cliente.activoCliente = False
        self.dbSession.commit()
        self.dbSession.refresh(cliente)
        return cliente

    def crearClientesIniciales(self):
        clientes = [
            {"nombreCliente": "María Gómez", "cedulaCliente": "1712345678", "telefonoCliente": "0998765432", "direccionCliente": "Calle La Pradera N56-78, Quito, Ecuador", "emailCliente": "maria.gomez@example.com", "activoCliente": True},
            {"nombreCliente": "Luis Torres", "cedulaCliente": "1721122233", "telefonoCliente": "0981122334", "direccionCliente": "Av. 10 de Agosto N23-45, Quito, Ecuador", "emailCliente": "luis.torres@example.com", "activoCliente": True},
            {"nombreCliente": "Ana Morales", "cedulaCliente": "1723344556", "telefonoCliente": "0992233445", "direccionCliente": "Calle Los Pinos N12-34, Quito, Ecuador", "emailCliente": "ana.morales@example.com", "activoCliente": True},
            {"nombreCliente": "Carlos Ramírez", "cedulaCliente": "1724455667", "telefonoCliente": "0983344556", "direccionCliente": "Av. Shyris N45-67, Quito, Ecuador", "emailCliente": "carlos.ramirez@example.com", "activoCliente": True},
            {"nombreCliente": "Paola Fernández", "cedulaCliente": "1725566778", "telefonoCliente": "0994455667", "direccionCliente": "Calle Guayaquil N78-90, Quito, Ecuador", "emailCliente": "paola.fernandez@example.com", "activoCliente": True},
            {"nombreCliente": "Consumidor Final", "cedulaCliente": "9999999999", "telefonoCliente": "0000000000", "direccionCliente": "No especifica", "emailCliente": "consumidor.final@ejemplo.com", "activoCliente": True}
        ]
        for c in clientes:
            existe = self.validarCedulaExistente(c["cedulaCliente"]) 
            if not existe:
                nuevo = Cliente(**c)
                self.dbSession.add(nuevo)
        print("Clientes por defecto creados...!")
        self.dbSession.commit()
        self.dbSession.close()
