from fastapi import FastAPI

app = FastAPI(
    title="API DALCT Market",
    description="Backend de DALCT Market - lista para desarrollo",
    version="0.1"
)

@app.get("/")
def inicio():
    return {"mensaje": "API DALCT Market está lista...!"}
