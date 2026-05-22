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
| POST | `/api/v1/extractions/batch` | Inicia lote (ZIP + formato) |
| GET | `/api/v1/extractions/jobs/{id}` | Estado del job |
| DELETE | `/api/v1/extractions/jobs/{id}` | Cancelar job |
| GET | `/api/v1/extractions/jobs/{id}/download` | Descargar Excel |

Formatos: `2023`, `2024`, `2025_2026`

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
python run_batch.py --format 2023 --zip "C:\ruta\facturas.zip" --output storage\out\salida.xlsx
```

## Variables de entorno

### Backend (`backend/.env`)

| Variable | Descripción |
|----------|-------------|
| `OPENAI_API_KEY` | Clave OpenAI (obligatoria) |
| `OPENAI_MODEL` | Modelo (default `gpt-4o`) |
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

## CI

GitHub Actions ejecuta import del backend y `npm run build` del frontend en cada push/PR a `main` o `master`.
