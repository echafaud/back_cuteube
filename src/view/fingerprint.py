import fingerprint_pro_server_api_sdk

from src.config import FINGERPRINT_API_KEY, FINGERPRINT_API_REGION

configuration = fingerprint_pro_server_api_sdk.Configuration(
    api_key=FINGERPRINT_API_KEY,
    region=FINGERPRINT_API_REGION
)

fingerprint_instance = fingerprint_pro_server_api_sdk.FingerprintApi(configuration)
