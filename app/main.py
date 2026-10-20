from fastapi import FastAPI
from app.config.settings import get_settings
from dotenv import load_dotenv

load_dotenv()


settings = get_settings()

app = FastAPI(
    title=settings.app_name
)


@app.get("/")
def hello() -> dict[str, str]:
    return {"message": "Hello, World!"}


def main() -> None:
    import uvicorn

    uvicorn.run("app.main:app", host=settings.api_host, port=int(settings.api_port), reload=True)


if __name__ == "__main__":
    main()
