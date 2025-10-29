from pydantic_settings import BaseSettings, SettingsConfigDict

class Variables(BaseSettings):
    ASSETS_DIR: str
    GLOBAL_SCALER_PATH: str
    USER_SCALER_PATH: str
    ISOFOREST_PATH: str

    AUTOENCODER_PARAMS_PATH: str
    AUTOENCODER_INPUT_DIM: int
    ALPHA: float
    THRESHOLD: float

    CLIENT_URL: str

    model_config = SettingsConfigDict(
        env_file=('.env')
    )

vars = Variables() # type: ignore
