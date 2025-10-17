import jwt
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from dotenv import load_dotenv
import os


load_dotenv()

logger = logging.getLogger(__name__)


class JWTService:
    """Serviço para gerenciamento de tokens JWT."""

    def __init__(
        self,
        secret_key: str = os.getenv("JWT_SECRET_KEY"),
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 60
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def create_access_token(self, data: Dict[str, Any]) -> str:
        """Cria um token de acesso JWT.

        Args:
            data (Dict[str, Any]): Dados para incluir no token

        Returns:
            str: Token JWT codificado
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire})

        try:
            encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
            logger.info(f"Token JWT criado para usuário: {data.get('sub')}")
            return encoded_jwt
        except Exception as e:
            logger.error(f"Erro ao criar token JWT: {e}")
            raise

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verifica e decodifica um token JWT.

        Args:
            token (str): Token JWT para verificar

        Returns:
            Optional[Dict[str, Any]]: Dados decodificados do token ou None se inválido
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            username: str = payload.get("sub")
            if username is None:
                return None
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token JWT expirado")
            return None
        except jwt.JWTError as e:
            logger.warning(f"Token JWT inválido: {e}")
            return None

    def hash_password(self, password: str) -> str:
        """Gera hash da senha.

        Args:
            password (str): Senha em texto plano

        Returns:
            str: Hash da senha
        """
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verifica se a senha corresponde ao hash.

        Args:
            plain_password (str): Senha em texto plano
            hashed_password (str): Hash da senha

        Returns:
            bool: True se a senha for válida
        """
        return self.pwd_context.verify(plain_password, hashed_password)
