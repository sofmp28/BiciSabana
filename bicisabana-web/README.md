# BiciSabana — interfaz de Claude + Python + Supabase + Vercel

**Versión de conexión automática.** Conserva el diseño de Claude, con API Python y Supabase en Vercel. En producción los visitantes cargan directamente el inventario real, sin introducir contraseña de operador.

## ¿Qué contiene?

```text
bicisabana-web/
├── public/
│   ├── index.html              Diseño original + conexión a API Python
│   ├── support.js              Motor de renderizado del prototipo de Claude
│   ├── image-slot.js           Imágenes en sus ubicaciones de diseño
│   ├── .image-slots.state.json Datos originales de imágenes
│   └── assets/                 Logos y fotografías .webp
├── backend/bicisabana.py       4 clases Python y RF-01 a RF-21
├── api/index.py                API serverless para Vercel (control de acceso)
├── supabase/schema.sql         Tablas, índices, RLS y operaciones atómicas
├── tests/test_api.py           13 pruebas automáticas con BD simulada
├── vercel.json                 Configuración de Vercel
├── requirements.txt            Dependencia Python fijada
├── .python-version             Python 3.12
├── .env.example                Variables de entorno, SIN claves reales
└── package.json                Comando para demo local
```

## Acceso automático y protección

- La página se conecta a Supabase mediante el servidor Python automáticamente al abrirse. **No solicita una clave para consultar bicicletas, registrar préstamos ni devoluciones.** Si falla la conexión, la interfaz muestra un aviso y NO permite operaciones ficticias que aparenten haberse guardado.
- `GET /api/estado` abre una sesión anónima temporal mediante una cookie `HttpOnly`, `SameSite=Strict` firmada en el servidor. Los códigos estudiantiles de otros préstamos se muestran parcialmente ocultos.
- `POST /api/prestamos` y `/api/devoluciones` requieren esa cookie y una comprobación de origen. La sesión no equivale a identificar al usuario ni impide que alguien que abra el sitio realice operaciones: **el sitio es una demostración académica de escritura pública**.
- La administración del inventario (registrar, mantenimiento, reactivar, mover, retirar y cargar ejemplos) **mantiene autorización con clave**, solicitada únicamente al intentar esas acciones. Así no queda la gestión completa expuesta a cualquier visitante.
- `SUPABASE_SERVICE_ROLE_KEY` y `BICISABANA_ACCESS_KEY` se mantienen **solo en las variables privadas de Vercel**, nunca en JavaScript, HTML ni GitHub. La segunda se usa para firmar las sesiones y autorizar tareas administrativas.
- Para un despliegue institucional real, añadir identidad de monitores, roles, limitación distribuida de frecuencia de solicitudes y trazabilidad. Usar solo **códigos ficticios**, no datos reales de estudiantes, mientras sea una demostración pública.

## Paso 1. Crear un proyecto en Supabase

1. Entrar a https://supabase.com/dashboard y seleccionar la organización donde se quiera crear el proyecto **BiciSabana**.
2. Crear un **proyecto nuevo**. Revisar los costos/plan antes de confirmarlo.
3. Ir a **SQL Editor** y ejecutar TODO el archivo `supabase/schema.sql` **en la base nueva**.
4. Comprobar en Table Editor: 30 bicicletas B01–B30 en `public.bicicletas`, y tablas `prestamos` e `intentos_rechazados` vacías.
5. Revisar RLS: las 3 tablas tienen RLS activo, sin políticas abiertas al público. Los procedimientos de préstamos se conceden solo a `service_role`.
6. Conservar **Project URL** y **secret/service role key** para agregarlas directamente en Vercel. **Nunca** colocar la clave de servicio en `public/`, en Claude ni en GitHub.

El SQL crea funciones PostgreSQL para que un préstamo y el cambio de estado de la bicicleta sean **una sola transacción**. Así se evitan inconsistencias si dos monitores actúan casi simultáneamente.

## Paso 2. Publicar en Vercel

1. Conectar la cuenta de Vercel y subir/importar este proyecto. Si se usa GitHub y el repositorio contiene una carpeta `bicisabana-web`, seleccionar **Root Directory = bicisabana-web**.
2. Configurar 3 variables de entorno del proyecto (Production y, si corresponde, Preview):

   - `SUPABASE_URL` = URL de tu proyecto Supabase.
   - `SUPABASE_SERVICE_ROLE_KEY` = clave **privada** para servidor de Supabase.
   - `BICISABANA_ACCESS_KEY` = secreto interno para firmar sesiones anónimas y permitir administración (mínimo 24 caracteres recomendado); nunca se introduce al entrar.

3. Desplegar. Vercel sirve `public/` y ejecuta `api/index.py` como función Python.
4. Abrir https://bici-sabana.vercel.app/ — la aplicación debe mostrar automáticamente «Estación conectada». No escribir clave.
5. Probar un préstamo y una devolución ficticios; verificar que el historial y el inventario se actualizan también al recargar la página y consultar Supabase.
6. Para tareas administrativas, utilizar la clave solo cuando aparezca el diálogo específico de gestión.

## Paso 3. Pruebas

En un computador con Python 3.12, desde la carpeta `bicisabana-web`:

```bash
python -m unittest discover -s tests -v
```

Las **13 pruebas de integración** usan una base simulada y no requieren credenciales ni instalar Supabase. Se comprueban préstamos, devoluciones, rechazos, inventario, mantenimiento, movilidad y sesiones anónimas, protección CSRF, administración y rutas reescritas de Vercel.

Desde el editor o con Node.js, el script `tests/test_frontend.cjs` comprueba las ocho rutas del diseño y su transformación de datos:

```bash
node tests/test_frontend.cjs
```

Para una **vista previa de diseño**, ejecutar:

```bash
npm run dev
```

La vista previa necesita una API válida: si falla la conexión, los cambios no se guardan ni se simulan. Requiere servir los archivos vía HTTP (no abrir `index.html` con doble clic).

## Endpoints del backend

| Método | Ruta | Función Python |
| --- | --- | --- |
| GET | `/api/estado` | Lee tablas de Supabase |
| POST | `/api/prestamos` | `SistemaBiciSabana.registrar_prestamo()` |
| POST | `/api/devoluciones` | `SistemaBiciSabana.registrar_devolucion()` |
| POST | `/api/bicicletas` | `SistemaBiciSabana.registrar_bicicleta()` |
| POST | `/api/mantenimiento` | `SistemaBiciSabana.marcar_mantenimiento()` |
| POST | `/api/reactivar` | `SistemaBiciSabana.reactivar_bicicleta()` |
| POST | `/api/mover` | `SistemaBiciSabana.mover_bicicleta()` |
| POST | `/api/retirar` | `SistemaBiciSabana.retirar_bicicleta()` |
| POST | `/api/cargar-ejemplo` | `SistemaBiciSabana.cargar_bicicletas_ejemplo()` |

Las rutas públicas de préstamo y devolución exigen una sesión anónima temporal y un origen válido. Las rutas administrativas exigen `X-BiciSabana-Access` con la clave privada del operador. Todas responden JSON con `ok`, `resultado` o `error`. No se exponen claves de Supabase al navegador.

## Alcance y limitaciones

- El backend mantiene la lógica orientada a objetos de Python. La capa web usa JavaScript para presentar datos y prevalidar formularios; cuando aparece **EN LÍNEA**, las decisiones y cambios se ejecutan en Python.
- El proyecto académico está desplegado, pero la versión de conexión automática debe comprobarse de nuevo en producción después de publicar este cambio.
- La base incluye datos ficticios. No ingresar información estudiantil real antes de completar las aprobaciones y políticas de privacidad correspondientes. La consulta pública oculta parcialmente los códigos de terceros.
- La opción **restablecer/vaciar** solo afecta al modo DEMO. No borra datos reales. La carga de 30 bicicletas reales funciona únicamente con estación vacía.
- Requiere una cuenta y permisos de creación de proyectos en Supabase, y autorización para conectar Vercel.
- Para la entrega de Fundamentos de Programación también se debe preparar la documentación de DevSecOps, la revisión de compañeros y la tabla comparativa entre botones y métodos.
