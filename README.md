# Continuous Authentication using UEBA

Continuous Authentication model for systems using User and Entity Behavior Analytics (UEBA) principles, enabling proactive detection of compromised credentials or insider threats by modeling and monitoring behavioral patterns.

## Setup Instructions

### Clone the Repository

```bash
git clone https://github.com/praevalis/Continuous-Auth-using-UEBA.git
```

```bash
cd Continuous-Auth-using-UEBA
```

### Client Setup (Terminal 1)

1. **Move into client directory**

```bash
cd client
```

2. **Install dependencies**

```bash
npm install
```

3. **Add environment variables**
   Create a `.env` file in the `client` directory and add the following variables,

```bash
VITE_API_URL='http://localhost:8000
```

4. **Run the application**

```bash
npm run dev
```

**You are all set!** The application is now running at `http://localhost:5173`.

### Server Setup (Terminal 2)

1. **Move into server directory**

```bash
cd server
```

2. **Install dependencies**

```bash
uv venv
uv sync
```

3. **Add environment variables**
   Create a `.env` file and add the following variables to it,

```bash
ASSETS_DIR='assets'
GLOBAL_SCALER_PATH='scalers/global_scaler.pkl'
USER_SCALER_PATH='scalers/user_scaler.pkl'
ISOFOREST_PATH='models/isoforest.pkl'
AUTOENCODER_PARAMS_PATH='models/autoencoder.pth'
AUTOENCODER_INPUT_DIM=6
CLIENT_URL=http://localhost:5173
```

4. **Run the server**

```bash
uv run uvicorn src.main:api --reload
# --reload flag is only used during development
```

The server is now running at `http://localhost:8000`.
