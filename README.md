# API Access Control - FastAPI Project

Un proyecto inicial limpio para construir APIs con FastAPI.

## 🚀 Características

- ✅ FastAPI con estructura modular
- ✅ Configuración con variables de entorno
- ✅ Modelos Pydantic para validación
- ✅ Routers organizados
- ✅ CORS configurado
- ✅ Documentación automática (Swagger/ReDoc)
- ✅ Validación de tipos con TypeHints

## 📁 Estructura del Proyecto

```
api-access-control/
├── main.py              # Aplicación principal simple
├── app_modular.py       # Aplicación con estructura modular
├── requirements.txt     # Dependencias
├── .env                # Variables de entorno
├── app/
│   ├── config.py       # Configuración de la aplicación
│   ├── models.py       # Modelos Pydantic
│   └── routers/
│       └── items.py    # Router de ejemplo
```

## 🛠️ Instalación

1. **Clonar y navegar al proyecto:**
   ```bash
   cd /Users/pierre/Projects/api-access-control
   ```

2. **Activar el entorno virtual:**
   ```bash
   source venv/bin/activate
   ```

3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

## 🚦 Uso

### Ejecutar la aplicación simple:
```bash
python main.py
```

### Ejecutar la aplicación modular:
```bash
python app_modular.py
```

### Ejecutar con uvicorn directamente:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 📚 Documentación

Una vez ejecutando la aplicación, puedes acceder a:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🔗 Endpoints Disponibles

### Generales
- `GET /` - Página principal
- `GET /health` - Estado de la API

### Items (Ejemplo)
- `GET /items/` - Listar todos los items
- `POST /items/` - Crear un nuevo item
- `GET /items/{item_id}` - Obtener item por ID
- `DELETE /items/{item_id}` - Eliminar item

## ⚙️ Configuración

Edita el archivo `.env` para personalizar la configuración:

```env
DEBUG=True
HOST=0.0.0.0
PORT=8000
DATABASE_URL=sqlite:///./test.db
SECRET_KEY=your-secret-key-here
```

## 🎯 Próximos Pasos

1. **Base de datos**: Integrar SQLAlchemy o MongoDB
2. **Autenticación**: Implementar JWT tokens
3. **Testing**: Agregar pytest para pruebas
4. **Docker**: Containerizar la aplicación
5. **Logging**: Configurar logs estructurados

## 📝 Notas de Desarrollo

- Usa `main.py` para proyectos simples
- Usa `app_modular.py` para proyectos más complejos
- Los modelos están en `app/models.py`
- Los routers están organizados en `app/routers/`
- La configuración está centralizada en `app/config.py`
