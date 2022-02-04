import uvicorn
from t4cclient import app

if __name__ == "__main__":
    uvicorn.run(app)