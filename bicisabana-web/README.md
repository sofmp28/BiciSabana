# BiciSabana — interfaz de Claude + Python + Supabase + Vercel

**Paquete de integración preparado.** Se conserva el diseño de Claude (logos, fotografías y 10 pantallas) y se añade conexión entre los botones y el archivo Python original. **Aún no está publicado ni probado contra una base de datos Supabase real**: faltan crear el proyecto, configurar sus credenciales y publicar desde la cuenta del propietario.

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
├── tests/test_api.py           9 pruebas de integración con BD simulada
├── vercel.json                 Configuración de Vercel
├── requirements.txt            Dependencia Python fijada
├── .python-version             Python 3.12
├── .env.example                Variables de entorno, SIN claves reales
└── package.json                Comando para demo local
```

## Dos modos claramente identificados

**Modo demostración:** se abre sin clave de operador, utiliza datos ficticios y conserva las operaciones simuladas en JavaScript. El aviso amarillo indica que **NO** está guardando en Python/Supabase.

**Modo real:** después de publicar la API y configurar las variables, pulsar **«MODO DEMO / Conectar estación real»**, introducir la clave de operador, y la interfaz obtiene el inventario real. Cada operación llama a `/api/...`, ejecuta los métodos de `backend/bicisabana.py` y confirma los cambios en Supabase. El estado se actualiza aproximadamente cada 15 segundos.

> La aplicación usa una clave de operador compartida con fines académicos. Para un uso institucional real se recomienda autenticar a cada monitor por separado (Supabase Auth + permisos por rol).

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
   - `BICISABANA_ACCESS_KEY` = frase larga y aleatoria para acceso de monitores (mínimo 20 caracteres recomendado).

3. Desplegar. Vercel sirve `public/` y ejecuta `api/index.py` como función Python.
4. Abrir el enlace HTTPS de Vercel. Verás **MODO DEMO** hasta conectar la estación.
5. Pulsar **Conectar estación real** e introducir la clave que fijaste en `BICISABANA_ACCESS_KEY`.
6. Comprobar que aparezcan las 30 bicicletas de Supabase y la etiqueta **EN LÍNEA**.
7. Probar un préstamo, verificarlo en Supabase y luego devolverlo. Confirmar en otra pestaña que el estado compartido cambió.

**Si no existe proyecto Supabase o no hay conexión de Vercel, no puede proporcionarse todavía un enlace real.** El frontend se puede ver en modo demo sin configurar una base.

## Paso 3. Pruebas

En un computador con Python 3.12, desde la carpeta `bicisabana-web`:

```bash
python -m unittest discover -s tests -v
```

Las **9 pruebas de integración** usan una base simulada y no requieren credenciales ni instalar Supabase. Se comprueban préstamos, devoluciones, rechazos, inventario, mantenimiento, movilidad y HTTP con clave correcta/incorrecta.

Desde el editor o con Node.js, el script `tests/test_frontend.cjs` comprueba las ocho rutas del diseño y su transformación de datos:

```bash
node tests/test_frontend.cjs
```

Para una **vista previa de diseño**, ejecutar:

```bash
npm run dev
```

La vista previa muestra el MODO DEMO si no existe la API. Requiere servir los archivos vía HTTP (no abrir `index.html` con doble clic).

## Endpoints privados

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

Las rutas exigen el encabezado `X-BiciSabana-Access` con la clave del operador. Responden JSON con `ok`, `resultado` o `error`. No se exponen claves de Supabase al navegador.

## Alcance y limitaciones

- El backend mantiene la lógica orientada a objetos de Python. La capa web usa JavaScript para presentar datos y prevalidar formularios; cuando aparece **EN LÍNEA**, las decisiones y cambios se ejecutan en Python.
- **No es un despliegue real todavía**. La integración ha sido probada localmente contra una base simulada; la validación en Supabase real y la revisión de Vercel están pendientes.
- La base incluye datos ficticios. No ingresar información estudiantil real antes de completar las aprobaciones y políticas de privacidad correspondientes.
- La opción **restablecer/vaciar** solo afecta al modo DEMO. No borra datos reales. La carga de 30 bicicletas reales funciona únicamente con estación vacía.
- Requiere una cuenta y permisos de creación de proyectos en Supabase, y autorización para conectar Vercel.
- Para la entrega de Fundamentos de Programación también se debe preparar la documentación de DevSecOps, la revisión de compañeros y la tabla comparativa entre botones y métodos.
