from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_inicio():
    response = client.get("/")
    assert response.status_code == 200 #assert se usa en tests unitarios para verificar que el resultado de una operación sea el esperado
    assert response.json() == {"mensaje": "API DALCT Market está lista...!"}
    
