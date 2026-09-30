# Sistema de Microservicios GraphQL

Sistema de microservicios basado en GraphQL para gestión de **Usuarios**, **Pagos**, **Órdenes** y **Pedidos**.

## Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                    API Gateway (GraphQL)                     │
│                         Puerto: 4000                         │
└────────┬──────────────┬──────────────┬──────────────┬───────┘
         │              │              │              │
    ┌────▼────┐   ┌────▼────┐   ┌────▼────┐   ┌────▼────┐
    │Usuarios │   │  Pagos  │   │ Órdenes │   │ Pedidos │
    │ :4001   │   │  :4002  │   │  :4003  │   │  :4004  │
    └────┬────┘   └────┬────┘   └────┬────┘   └────┬────┘
         │              │              │              │
    ┌────▼────┐   ┌────▼────┐   ┌────▼────┐   ┌────▼────┐
    │Postgres │   │Postgres │   │Postgres │   │Postgres │
    │ :5432   │   │  :5433  │   │  :5434  │   │  :5435  │
    └─────────┘   └─────────┘   └─────────┘   └─────────┘
         │              │              │              │
         └──────────────┴──────┬───────┴──────────────┘
                               │
                        ┌──────▼──────┐
                        │    Redis    │
                        │   :6379     │
                        │  (Eventos)  │
                        └─────────────┘
```

## Estructura del Proyecto

```
E:\trabajo de grahpql\
├── microservicios/
│   ├── api-gateway/          # API Gateway GraphQL
│   ├── servicio-usuarios/    # Microservicio de Usuarios
│   ├── servicio-pagos/       # Microservicio de Pagos
│   ├── servicio-ordenes/     # Microservicio de Órdenes
│   ├── servicio-pedidos/     # Microservicio de Pedidos
│   └── shared/               # Código compartido
├── bruno-api/                # Colección Bruno para endpoints
│   ├── usuarios/
│   ├── pagos/
│   ├── ordenes/
│   ├── pedidos/
│   └── environments/
├── docker-compose.yml        # Orquestación de servicios
├── .env.example              # Variables de entorno
└── README.md
```

## Requisitos

- Docker y Docker Compose
- Python 3.11+ (para desarrollo local)
- Bruno (opcional, para probar endpoints)

## Inicio Rápido

### 1. Clonar y configurar

```bash
cd "E:\trabajo de grahpql"
cp .env.example .env
```

### 2. Levantar servicios con Docker

```bash
docker-compose up -d
```

### 3. Verificar que los servicios estén corriendo

```bash
# API Gateway
curl http://localhost:4000/health

# Microservicio Usuarios
curl http://localhost:4001/health

# Microservicio Pagos
curl http://localhost:4002/health

# Microservicio Órdenes
curl http://localhost:4003/health

# Microservicio Pedidos
curl http://localhost:4004/health
```

### 4. Probar GraphQL

Puedes acceder a la interfaz GraphQL Playground en:
- API Gateway: http://localhost:4000/graphql
- Usuarios: http://localhost:4001/graphql
- Pagos: http://localhost:4002/graphql
- Órdenes: http://localhost:4003/graphql
- Pedidos: http://localhost:4004/graphql

## Desarrollo Local

### Crear entorno virtual

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### Instalar dependencias

```bash
cd microservicios/servicio-usuarios
pip install -r requirements.txt
```

### Ejecutar microservicio

```bash
cd microservicios/servicio-usuarios
uvicorn src.main:app --host 0.0.0.0 --port 4001 --reload
```

## Colección Bruno

La carpeta `bruno-api/` contiene archivos `.bru` para probar todos los endpoints:

### Usuarios
- `crear-usuario.bru` - Crear un nuevo usuario
- `obtener-usuario.bru` - Obtener usuario por ID
- `actualizar-usuario.bru` - Actualizar usuario
- `listar-usuarios.bru` - Listar usuarios
- `eliminar-usuario.bru` - Eliminar usuario

### Pagos
- `procesar-pago.bru` - Procesar un pago
- `consultar-pago.bru` - Consultar pago por ID
- `reembolsar-pago.bru` - Reembolsar un pago
- `listar-pagos.bru` - Listar pagos

### Órdenes
- `crear-orden.bru` - Crear una orden
- `obtener-orden.bru` - Obtener orden por ID
- `actualizar-estado-orden.bru` - Actualizar estado
- `listar-ordenes.bru` - Listar órdenes

### Pedidos
- `crear-pedido.bru` - Crear un pedido
- `obtener-pedido.bru` - Obtener pedido por ID
- `actualizar-estado-pedido.bru` - Actualizar estado
- `listar-pedidos.bru` - Listar pedidos

## Eventos del Sistema

| Evento | Productor | Consumidor | Descripción |
|-------|-----------|------------|-------------|
| `usuario.creado` | Usuarios | Todos | Nuevo usuario registrado |
| `pago.completado` | Pagos | Órdenes | Pago exitoso |
| `pago.fallido` | Pagos | Órdenes | Pago rechazado |
| `orden.creada` | Órdenes | Pedidos | Nueva orden |
| `orden.confirmada` | Órdenes | Pedidos | Orden lista para despacho |
| `pedido.entregado` | Pedidos | Órdenes | Pedido completado |

## Tecnologías

- **Python 3.11+** - Lenguaje de programación
- **Strawberry GraphQL** - Framework GraphQL
- **FastAPI** - Framework web asíncrono
- **SQLAlchemy 2.0** - ORM asíncrono
- **PostgreSQL** - Base de datos
- **Redis** - Pub/Sub para eventos
- **Docker** - Contenedores
- **Bruno** - Cliente de API

## Licencia

MIT
