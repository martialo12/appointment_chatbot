import os

# project title and project version
PROJECT_TITLE = "Nudge"
PROJECT_VERSION = "1.0.0"

# Supported databases types by name
MONGO_DB = "mongodb"
POSTGRESQL = "postgresql"

# supported authentication providers by name
GOOGLE = "google-oidc"
AZURE = "azure-oidc"
PWC = "pwc-oidc"

# Selected database type to use
DATABASE_TYPE = POSTGRESQL

# MongoDB Replica Set
MONGODB_HOST = os.environ.get("MONGODB_HOST", "127.0.0.1")
MONGODB_PORT = int(os.environ.get("MONGODB_PORT", 27017))
MONGODB_COLLECTION = "testdb"
MONGODB_DATABASE = "testdb"

# Postgresql Replica set
POSTGRESQL_HOST = os.environ.get("POSTGRESQL_HOST", "127.0.0.1")
POSTGRESQL_PORT = int(os.environ.get("POSTGRESQL_PORT", 5432))
POSTGRESQL_DATABASE = os.environ.get("POSTGRESQL_DATABASE", "testdb")
POSTGRESQL_USERNAME = os.environ.get("POSTGRESQL_USERNAME", "postgres")
POSTGRESQL_PASSWORD = os.environ.get("POSTGRESQL_PASSWORD", "postgres")

# google login
GOOGLE_CLIENT_ID = os.environ.get(
    "GOOGLE_CLIENT_ID",
    "823373807502-kiikdv5jojpo2i94tlt2les3af8fkhnb.apps.googleusercontent.com",
)
GOOGLE_CLIENT_SECRET = os.environ.get(
    "GOOGLE_CLIENT_SECRET", "bA8Exib0dXJn8PUAYQHe171W"
)
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"
GOOGLE_REDIRECT_URL = "http://localhost:5000/google-login-callback/"
GOOGLE_MAPS_API_KEY = "AIzaSyB77XjdBi1Qw1OmThsGT_xy8qPu9QnIt4U"

# Azure login
AZURE_CLIENT_ID = os.environ.get("AZURE_CLIENT_ID", None)
AZURE_CLIENT_SECRET = os.environ.get("AZURE_CLIENT_SECRET", None)
AZURE_TENANT_ID = os.environ.get("AZURE_TENANT_ID", "common")
AZURE_AUTHORITY = os.environ.get(
    "AZURE_AUTHORITY", f"https://login.microsoftonline.com/{AZURE_TENANT_ID}"
)
AZURE_DISCOVERY_URL = f"{AZURE_AUTHORITY}/v2.0/.well-known/openid-configuration"
AZURE_REDIRECT_URL = "http://localhost:8000/azure-login-callback/"

# Common configuration for all environments(dev, localhost)
PWC_CLIENT_ID = os.environ.get("PWC_CLIENT_ID", "urn:IT-dev-nfz")
PWC_CLIENT_SECRET = os.environ.get("PWC_CLIENT_SECRET", "RkpG3PQJmwClBbB9Yyq8")
PWC_DISCOVERY_URL = os.environ.get(
    "PWC_DISCOVERY_URL",
    "https://login.pwcinternal.com/openam/oauth2/.well-known/openid-configuration",
)
PWC_REDIRECT_URI = os.environ.get("PWC_REDIRECT_URI", "http://localhost:5000/callback")
SCOPES = "openid profile cloudEmail country email employeeNumber role upwcjobtitle pwcPartyID"
PROVIDER_DOMAIN = os.environ.get(
    "PROVIDER_DOMAIN", "https://login-stg.pwc.com/openam/oauth2"
)
AUTHORITY = os.environ.get("AUTHORITY", "https://login-stg.pwc.com/openam/oauth2")
RESPONSE_TYPE = "code"
POST_LOGOUT_REDIREECT_URI = "/auth/logout-success"
SILENT_REDIRECT_URI = "/static/silent-renew"
ACCESS_TOKEN_EXPIRING_NOTIFICATION_TIME = 10
AUTOMATIC_SILENT_RENEW = True
FILTER_PROTOCOL_CLAIMS = True
LOAD_USER_INFO = True

# Pwc config DEV environment
REDIRECT_URI_DEV = os.environ.get(
    "REDIRECT_URI",
    "https://nudgeforzero.dev-pwc-ita-innovation.itgservices.it/callback",
)

# Pwc config localhost environment
REDIRECT_URI_LOC = os.environ.get("REDIRECT_URI", "http://localhost:8000/callback")

# Frontend endpoint
FRONTEND_URL = "http://localhost:3000"
THUX_LOCALHOST_FRONTEND_URL = "http://localhost:8080"
THUX_DEV_FRONTEND_URL = "https://nfz.pwc.thux.dev"
# jwt access token configuration
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "ssbsfb0625652s5fasfs5a0d5g1agaga")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_MINUTES = 86400
AUTH_TOKEN_EXPIRE_MINUTES = 1

# dev domain url
API_DEV_URL = "https://nudge-api.dev-pwc-ita-innovation.itgservices.it"

# chatbot configuration
CHATBOT_SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/calendar.events",
    "https://www.googleapis.com/auth/calendar.events.readonly",
    "https://www.googleapis.com/auth/calendar.settings.readonly",
    "https://www.googleapis.com/auth/calendar.addons.execute",
    "https://www.googleapis.com/auth/drive.metadata.readonly",
    "https://www.googleapis.com/auth/drive.file",
]
CALENDAR_ID = "c_99lr7bjqf3m35vvvl6ilm6dt4c@group.calendar.google.com"
