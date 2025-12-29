import bcrypt
from datetime import datetime, timedelta
import jwt, random, string

from app.core.config import settings

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se la password in chiaro corrisponde all'hash"""
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )

def get_password_hash(password: str) -> str:
    """Genera l'hash della password"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def create_access_token(data: dict) -> str:
    """Crea un token JWT"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.ACCESS_TOKEN_EXPIRE_DAYS)
    #expire = datetime.utcnow() + timedelta(seconds=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

# def generate_qr_code_id(stage_name: str, db) -> str:
#     """Genera un QR code ID univoco per il DJ"""
#     from app.models.dj import DJ
#     from datetime import datetime
    
#     base_qr = f"{stage_name.upper().replace(' ', '-')}-{datetime.now().year}"
#     qr_code_id = base_qr
#     counter = 1
    
#     while db.query(DJ).filter(DJ.qr_code_id == qr_code_id).first():
#         qr_code_id = f"{base_qr}-{counter}"
#         counter += 1
    
#     return qr_code_id

def generate_qr_code_id(stage_name: str) -> str:
    """Genera un QR code ID unico per il DJ con suffisso randomico di 8 caratteri"""
    
    # Normalizza il nome del palco
    base_qr = stage_name.upper().replace(' ', '-')
    
    # Anno corrente
    year = datetime.utcnow().year
    
    # Suffix random di 8 caratteri (lettere maiuscole + numeri)
    random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    
    qr_code_id = f"{base_qr}-{year}-{random_suffix}"
    return qr_code_id