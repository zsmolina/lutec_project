# Lutec

Extracción por lote de facturas en PDF (dentro de un ZIP) con IA y consolidado en Excel.

## Estructura

```
lutec-project/
├── backend/          # API FastAPI + motor de extracción
├── frontend/         # Interfaz React + Vite
├── scripts/          # dev.ps1 (backend + frontend)
└── .github/workflows # CI
```

## Requisitos

- Python 3.12+
- Node.js 20+
- Clave de OpenAI (`OPENAI_API_KEY`)

## Configuración

```powershell
cd backend
copy .env.example .env
# Editar .env y configurar OPENAI_API_KEY
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

cd ..\frontend
npm install
copy .env.example .env
```

## Desarrollo

**Script único** (desde la raíz del repo o desde `frontend`):

```powershell
.\scripts\dev.ps1
```

**Dos terminales:**

```powershell
# Terminal 1 — backend
cd backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8000

# Terminal 2 — frontend
cd frontend
npm run dev
```

- Frontend: http://localhost:5173
- API / docs: http://127.0.0.1:8000/docs

## API principal

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/v1/health` | Estado del servicio y límites |
| GET | `/api/v1/formats` | Formatos de factura soportados |
| POST | `/api/v1/formap/consolidate` | Excel Formap → informe unificado (.xlsx) |
| GET | `/api/v1/retailers` | Comercializadores y formatos soportados |
| POST | `/api/v1/extractions/batch` | Inicia lote (`retailer` + ZIP; formato auto por factura) |
| GET | `/api/v1/extractions/jobs/{id}` | Estado del job |
| DELETE | `/api/v1/extractions/jobs/{id}` | Cancelar job |
| GET | `/api/v1/extractions/jobs/{id}/download` | Descargar Excel |

Comercializadores: **Air-e** (`aire`) y **Afinia** (`afinia`). El usuario elige comercializador; el año se detecta automáticamente por factura.

| Comercializador | Formatos (auto) |
|-----------------|-----------------|
| Air-e | 2023, 2024, 2025_2026 |
| Afinia | 2024 (1 hoja), 2025_2026 (2 hojas PDF) |

## Formato Formap (CLI)

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python run_formap.py -i "..\Consolidado AE - FORMAP Esquema.xlsx" -o "..\Reporte_Bloques_Estilizado_Auditoria.xlsx"
```

Desde la raíz también puede usar `consolidar_bloques_estilizados.py` (delega al mismo servicio).

## CLI de lote de facturas (sin interfaz)

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python run_batch.py --retailer aire --zip "C:\ruta\facturas.zip" --output storage\out\salida.xlsx
python run_batch.py --retailer afinia --zip "C:\ruta\afinia.zip" --output storage\out\afinia.xlsx
```

## Variables de entorno

### Backend (`backend/.env`)

| Variable | Descripción |
|----------|-------------|
| `OPENAI_API_KEY` | Clave OpenAI (obligatoria) |
| `OPENAI_MODEL` | Modelo de extracción (default `gpt-4o`) |
| `OPENAI_CLASSIFIER_MODEL` | Modelo de clasificación de año (default `gpt-4o-mini`) |
| `MAX_ZIP_SIZE_MB` | Tamaño máximo del ZIP (default 100) |
| `MAX_FORMAP_EXCEL_MB` | Tamaño máximo Excel Formap (default 50) |
| `MAX_PDF_COUNT` | PDFs máximos por ZIP (default 500) |
| `MAX_PDF_SIZE_MB` | Tamaño máximo por PDF (default 25) |
| `JOB_TTL_HOURS` | Horas antes de limpiar temporales (default 24) |
| `CORS_ORIGINS` | Orígenes permitidos, separados por coma |
| `TEMP_DIR` | Carpeta temporal (opcional; default `storage/tmp`) |

### Frontend (`frontend/.env`)

| Variable | Descripción |
|----------|-------------|
| `VITE_API_BASE_URL` | URL del backend en producción (vacío = proxy Vite en dev) |

## Almacenamiento

- `backend/storage/tmp` — ZIPs y jobs en proceso (se limpian por TTL)
- `backend/storage/out` — salidas del CLI `run_batch.py`

## Producción (frontend)

```powershell
cd frontend
npm run build
```

## Docker

Requisitos: [Docker Desktop](https://www.docker.com/products/docker-desktop/) (o Docker Engine + Compose v2).

1. Configure el backend (si aún no lo hizo):

```powershell
copy backend\.env.example backend\.env
# Editar backend\.env y poner OPENAI_API_KEY real
```

2. Levantar la aplicación:

```powershell
docker compose up --build
```

| Servicio | URL |
|----------|-----|
| Interfaz (nginx + proxy `/api`) | http://localhost:8080 |
| API directa (opcional) | http://localhost:8000/docs |

El frontend en Docker usa nginx: las peticiones a `/api` se reenvían al contenedor `backend`. No hace falta `VITE_API_BASE_URL` en la imagen.

Los temporales de jobs se guardan en el volumen `lutec-storage` (`/app/storage` en el backend).

Comandos útiles:

```powershell
docker compose up -d --build   # en segundo plano
docker compose logs -f backend
docker compose down
docker compose down -v         # elimina también el volumen de storage
```

Solo backend (sin interfaz):

```powershell
docker compose up --build backend
```

## CI

GitHub Actions ejecuta import del backend y `npm run build` del frontend en cada push/PR a `main` o `master`.
