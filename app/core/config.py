from pydantic_settings import BaseSettings
from typing import List
import os
import json
import socket

class Settings(BaseSettings):
    PROJECT_NAME: str = "Karaokati API"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    
    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_DAYS: int = 2
    
    # 🆕 Email Configuration
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.zoho.eu")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_TLS: bool = os.getenv("SMTP_TLS", "True").lower() == "true"
    SMTP_USER: str = os.getenv("SMTP_USER", "user")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "passsword")
    EMAIL_FROM: str = os.getenv("EMAIL_FROM", "from")

    @property
    def FRONTEND_URL(self) -> str:
        """FRONTEND_URL dinamico"""
        # Se c'è variabile d'ambiente, usala
        env_url = os.getenv("FRONTEND_URL")
        if env_url:
            return env_url
        
        # Altrimenti auto-detect (stesso codice che hai già per CORS)
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            
            if not local_ip.startswith("127."):
                return f"http://{local_ip}:5173"  # Telefono
            else:
                return "http://localhost:5173"    # PC
        except:
            return "http://localhost:5173"        # Fallback
        
    @property
    def BACKEND_URL(self) -> str:
        """BACKEND_URL dinamico - autoconsistente per sviluppo e produzione"""
        # Prima priorità: variabile d'ambiente (produzione/Render)
        env_url = os.getenv("BACKEND_URL")
        if env_url:
            return env_url
        
        # Sviluppo: auto-detect come FRONTEND_URL
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            
            if not local_ip.startswith("127."):
                return f"http://{local_ip}:{self.PORT}"  # Rete locale
            else:
                return f"http://localhost:{self.PORT}"   # PC
        except:
            return f"http://localhost:{self.PORT}"       # Fallback
    
    # CORS
    BACKEND_CORS_ORIGINS: str = os.getenv("BACKEND_CORS_ORIGINS", "[]")
    
    @property
    def CORS_ORIGINS(self) -> List[str]:
        try:
            origins = json.loads(self.BACKEND_CORS_ORIGINS)
        except:
            origins = []
        
        # 🆕 Rileva automaticamente l'IP locale
        def get_local_ip():
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                local_ip = s.getsockname()[0]
                s.close()
                return local_ip
            except:
                return None
        
        # Origins di base per sviluppo
        default_origins = [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:3000",
        ]
        
        # Aggiungi automaticamente l'IP locale per accesso da telefono
        local_ip = get_local_ip()
        if local_ip:
            default_origins.extend([
                f"http://{local_ip}:5173",
                f"http://{local_ip}:3000",
            ])
        
        return list(set(origins + default_origins))
    
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    PORT: int = int(os.getenv("PORT", 8000))
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()