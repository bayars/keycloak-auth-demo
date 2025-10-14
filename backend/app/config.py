from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    keycloak_url: str = "http://keycloak:8080/auth"
    keycloak_realm: str = "lab-test2"
    client_id: str = "myapp"
    
    class Config:
        env_file = ".env"

settings = Settings()
