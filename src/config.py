from dotenv import load_dotenv
import os

class Config:
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
        return cls._instance
    
    def __init__(self) -> None:
        # Eğer daha önce initialize edilmişse tekrar yapma
        if Config._initialized:
            return
            
        # Load .env file
        self._load_env_file()
        
        # PostgreSQL configuration
        self.postgres_host = self._get_postgres_host()
        self.postgres_port = self._get_postgres_port()
        self.postgres_db = self._get_postgres_db()
        self.postgres_user = self._get_postgres_user()
        self.postgres_password = self._get_postgres_password()
        self.postgres_echo = self._get_postgres_echo()
        self.postgres_pool_size = self._get_postgres_pool_size()
        self.postgres_max_overflow = self._get_postgres_max_overflow()
        
        # Admin API configuration
        self.admin_api_key = self._get_admin_api_key()
        
        # Application configuration
        self.app_name = self._get_app_name()
        self.app_version = self._get_app_version()
        self.app_port = self._get_app_port()
        self.app_env = self._get_app_env()
        
        Config._initialized = True
        
    def _load_env_file(self) -> None:
        env_path = os.getenv("ENV_PATH")
        if env_path:
            load_dotenv(env_path)
        elif os.path.exists(".env.example"):
            load_dotenv(".env.example")
        elif os.path.exists(".env"):
            load_dotenv(".env")
        else:
            # Don't raise an error, use defaults instead
            pass
    def _get_admin_api_key(self) -> str:
        """Get admin API key from environment variable"""
        return os.getenv("ADMIN_API_KEY", "")
    
    def _get_app_name(self) -> str:
        """Get application name from environment variable"""
        return os.getenv("APP_NAME", "Chat Marketplace Service")
    
    def _get_app_version(self) -> str:
        """Get application version from environment variable"""
        return os.getenv("APP_VERSION", "2.0.0")
        return os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
    
    def _get_app_port(self) -> int:
        """Get application port from environment variable"""
        return int(os.getenv("APP_PORT", "8080"))
    
    def _get_app_env(self) -> str:
        """Get application environment from environment variable"""
        return os.getenv("APP_ENV", "development")
    
    # PostgreSQL configuration getters
    def _get_postgres_host(self) -> str:
        """Get PostgreSQL host from environment variable"""
        return os.getenv("POSTGRES_HOST", "localhost")
    
    def _get_postgres_port(self) -> int:
        """Get PostgreSQL port from environment variable"""
        return int(os.getenv("POSTGRES_PORT", "5432"))
    
    def _get_postgres_db(self) -> str:
        """Get PostgreSQL database name from environment variable"""
        return os.getenv("POSTGRES_DB", "chat_marketplace")
    
    def _get_postgres_user(self) -> str:
        """Get PostgreSQL user from environment variable"""
        return os.getenv("POSTGRES_USER", "postgres")
    
    def _get_postgres_password(self) -> str:
        """Get PostgreSQL password from environment variable"""
        return os.getenv("POSTGRES_PASSWORD", "password")
    
    def _get_postgres_echo(self) -> bool:
        """Get PostgreSQL echo setting from environment variable"""
        return os.getenv("POSTGRES_ECHO", "false").lower() == "true"
    
    def _get_postgres_pool_size(self) -> int:
        """Get PostgreSQL pool size from environment variable"""
        return int(os.getenv("POSTGRES_POOL_SIZE", "10"))
    
    def _get_postgres_max_overflow(self) -> int:
        """Get PostgreSQL max overflow from environment variable"""
        return int(os.getenv("POSTGRES_MAX_OVERFLOW", "20"))
    
    
    @property
    def postgres_url(self) -> str:
        """Get PostgreSQL connection URL for asyncpg"""
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
    
    @property
    def postgres_sync_url(self) -> str:
        """Get PostgreSQL connection URL for psycopg2 (sync)"""
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
    
    def validate_config(self) -> bool:
        """Validate configuration values"""
        try:
            # PostgreSQL validation
            if not self.postgres_host:
                return False
            if not self.postgres_port or self.postgres_port <= 0:
                return False
            if not self.postgres_db:
                return False
            if not self.postgres_user:
                return False
            if not self.postgres_password:
                return False
            if self.postgres_pool_size <= 0:
                return False
            if self.postgres_max_overflow < 0:
                return False
            
            return True
        except Exception:
            return False
    
    def is_admin_enabled(self) -> bool:
        """Check if admin features are enabled"""
        return bool(self.admin_api_key and self.admin_api_key.strip())