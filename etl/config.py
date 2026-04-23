from pydantic_settings import BaseSettings


class ETLSettings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/ulsan_port"
    upa_api_key: str = ""
    upa_api_base: str = "https://api.ulsan.go.kr"
    kma_api_key: str = ""
    kma_api_base: str = "https://apis.data.go.kr/1360000"
    raw_data_dir: str = "data/raw"
    request_timeout: int = 30
    max_retries: int = 3

    model_config = {"env_prefix": "ETL_", "env_file": ".env"}


etl_settings = ETLSettings()
