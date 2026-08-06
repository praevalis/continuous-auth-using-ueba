from enum import StrEnum


class ProviderType(StrEnum):
	IDP = 'idp'
	SIEM = 'siem'


class ProviderConnectionMethod(StrEnum):
	API_TOKEN = 'api_token'
	OAUTH_CLIENT_CREDENTIALS = 'oauth_client_credentials'
	SERVICE_ACCOUNT = 'service_account'


class TenantProviderConnectionStatus(StrEnum):
	ACTIVE = 'active'
	DISABLED = 'disabled'
	TEST_FAILED = 'test_failed'
