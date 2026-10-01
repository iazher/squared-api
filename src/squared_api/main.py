from fastapi import FastAPI

# creates server object. Everything gets attached to this app
app = FastAPI(title="Squared API") 

@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}