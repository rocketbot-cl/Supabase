



# Supabase

Supabase es una plataforma open-source basada en Postgres para construir backends con autenticación, APIs y storage. Este módulo permite conectarse y ejecutar operaciones desde Rocketbot.

*Read this in other languages: [English](Manual_Supabase.md), [Português](Manual_Supabase.pr.md), [Español](Manual_Supabase.es.md)*

![banner](imgs/Banner_Supabase.png o jpg)
## Como instalar este módulo

Para instalar el módulo en Rocketbot Studio, se puede hacer de dos formas:
1. Manual: __Descargar__ el archivo .zip y descomprimirlo en la carpeta modules. El nombre de la carpeta debe ser el mismo al del módulo y dentro debe tener los siguientes archivos y carpetas: \__init__.py, package.json, docs, example y libs. Si tiene abierta la aplicación, refresca el navegador para poder utilizar el nuevo modulo.
2. Automática: Al ingresar a Rocketbot Studio sobre el margen derecho encontrara la sección de **Addons**, seleccionar **Install Mods**, buscar el modulo deseado y presionar install.



## Como usar este modulo

Use este modulo para conectar Rocketbot con Supabase y ejecutar operaciones de base de datos, Storage, RPC y embeddings.

Uso basico:
1. Cree o seleccione un proyecto Supabase.
2. Copie el Project URL y una API key desde Supabase.
3. Ejecute Connect antes de usar los otros comandos.
4. Use los comandos de tablas para CRUD, los comandos de Storage para buckets/archivos y los comandos RPC para funciones Postgres.

API keys y RLS:
- Las API keys de Supabase identifican el componente de aplicacion que accede al proyecto. Por si solas no identifican al usuario final.
- Use preferentemente `sb_publishable_...` para contextos publicos/client-side. Es una clave de bajo privilegio y el acceso lo controlan las politicas RLS.
- Use `sb_secret_...` solo para automatizaciones backend seguras. Las secret keys tienen acceso elevado y pueden omitir RLS, por eso no deben exponerse en navegadores, repositorios publicos, logs, chats o URLs.
- Las claves legacy `anon` y 
`service_role` pueden seguir existiendo. Trate `anon` como acceso publicable y `service_role` como acceso secreto/backend.
- Si un comando falla por permisos, revise las politicas de la tabla, el rol permitido por la clave o use una clave backend solo cuando corresponda.

Comandos de embeddings:
Los comandos de embeddings son avanzados. Rocketbot genera embeddings y llama a Supabase, pero Supabase debe tener creados previamente los objetos necesarios para guardar y comparar vectores.

Flujo de uso:
1. Ejecute Connect.
2. Ejecute Embeddings Connect para guardar proveedor, API key y modelo por defecto.
3. En Supabase, cree una tabla compatible, por ejemplo `documents`.
4. Habilite la extension `vector` y cree una columna vectorial, por ejemplo `embedding vector(384)`. La dimension debe coincidir con la salida del modelo.
5. Cree una funcion RPC, por ejemplo `match_documents`, que reciba `query_embedding`, `match_threshold` y `match_count`, y compare vectores.
6. Ejecute Generate And 
Store Embedding para dividir texto, generar vectores e insertar las filas.
7. Ejecute Retrieve Documents para generar el embedding de consulta y llamar la funcion RPC.

Notas importantes:
- Supabase guarda embeddings usando Postgres y pgvector.
- La busqueda semantica compara significado, no palabras exactas.
- La funcion RPC pertenece al proyecto del cliente. Ajuste nombres de tablas, columnas, dimensiones, filtros y columnas de retorno segun el esquema del cliente.
- Para tablas grandes, agregue un indice vectorial. Supabase generalmente recomienda HNSW por rendimiento y robustez; IVFFlat existe para casos especificos.
- Si los documentos tienen permisos, aplique RLS o filtros de permisos en Supabase para que la busqueda vectorial devuelva solo filas permitidas.

Referencias:
- https://supabase.com/docs/guides/getting-started/api-keys
- https://supabase.com/docs/guides/ai
- https://supabase.com/docs/guides/ai/concepts
- https://supabase.com/docs/guides/ai/vector-columns
- 
https://supabase.com/docs/guides/ai/vector-indexes
- https://supabase.com/docs/guides/ai/semantic-search
- https://supabase.com/docs/guides/ai/rag-with-permissions


## Descripción de los comandos

### Conectar

Conecta con un proyecto Supabase y verifica que la API key tenga acceso.
|Parámetros|Descripción|ejemplo|
| --- | --- | --- |
|Credencial|||
|Project URL||https://<project-ref>.supabase.co|
|API Key||eyJhbGciOi...|
|Asignar resultado a variable|Nombre de la variable donde se guardara el resultado|resultado|

### Obtener Tabla

Lee filas de una tabla Supabase, con orden opcional por created_at.
|Parámetros|Descripción|ejemplo|
| --- | --- | --- |
|Nombre de tabla||public.users|
|Ordenar por created_at (opcional)|||
|Asignar resultado a variable|Nombre de la variable donde se guardara el resultado|resultado|

### Filtrar Tabla

Lee filas de una tabla donde una columna coincide con el valor indicado.
|Parámetros|Descripción|ejemplo|
| --- | --- | --- |
|Nombre de tabla||public.users|
|Columna filtro||id|
|Valor filtro||1|
|Asignar resultado a variable|Nombre de la variable donde se guardara el resultado|resultado|

### Columnas (template)

Crea una plantilla JSON vacia usando las columnas detectadas en una tabla.
|Parámetros|Descripción|ejemplo|
| --- | --- | --- |
|Nombre de tabla||public.users|
|Asignar resultado a variable|Nombre de la variable donde se guardara el resultado|resultado|

### Listar Columnas

Devuelve los nombres de columnas disponibles en una tabla.
|Parámetros|Descripción|ejemplo|
| --- | --- | --- |
|Nombre de tabla||public.users|
|Asignar resultado a variable|Nombre de la variable donde se guardara el resultado|resultado|

### Insertar Filas

Inserta una o mas filas en una tabla desde un array JSON.
|Parámetros|Descripción|ejemplo|
| --- | --- | --- |
|Nombre de tabla||public.users|
|Filas (JSON array)||[{"name":"Alfredo"}]|
|Asignar resultado a variable|Nombre de la variable donde se guardara el resultado|resultado|

### Actualizar Filas

Actualiza una columna en filas seleccionadas por un filtro de igualdad.
|Parámetros|Descripción|ejemplo|
| --- | --- | --- |
|Nombre de tabla||public.users|
|Nombre de columna||status|
|Valor||active|
|Columna filtro||id|
|Valor filtro||1|
|Asignar resultado a variable|Nombre de la variable donde se guardara el resultado|resultado|

### Actualizar Multiples

Actualiza multiples filas desde un datatable JSON, usando id o una clausula WHERE.
|Parámetros|Descripción|ejemplo|
| --- | --- | --- |
|Nombre de tabla||public.users|
|Datatable (JSON array)||[{"id":1,"name":"X"}]|
|WHERE (opcional)||{"id":1}|
|Asignar resultado a variable|Nombre de la variable donde se guardara el resultado|resultado|

### Borrar Filas

Elimina filas de una tabla donde una columna coincide con el valor indicado.
|Parámetros|Descripción|ejemplo|
| --- | --- | --- |
|Nombre de tabla||public.users|
|Columna filtro||id|
|Valor filtro (valor o JSON array)||1|
|Asignar resultado a variable|Nombre de la variable donde se guardara el resultado|resultado|

### Listar Buckets

Lista los buckets de Storage disponibles en el proyecto Supabase conectado.
|Parámetros|Descripción|ejemplo|
| --- | --- | --- |
|Asignar resultado a variable|Nombre de la variable donde se guardara el resultado|resultado|

### Crear Bucket

Crea un bucket de Storage y permite configurar visibilidad, limite y tipos MIME.
|Parámetros|Descripción|ejemplo|
| --- | --- | --- |
|Nombre bucket||my-bucket|
|Publico|||
|Limite tamano (opcional)||10000000|
|Mimes permitidos (opcional)||image/png,image/jpeg|
|Asignar resultado a variable|Nombre de la variable donde se guardara el resultado|resultado|

### Obtener Bucket

Obtiene detalles de un bucket y opcionalmente lista sus archivos en la raiz.
|Parámetros|Descripción|ejemplo|
| --- | --- | --- |
|Nombre bucket||my-bucket|
|Incluir archivos|||
|Asignar resultado a variable|Nombre de la variable donde se guardara el resultado|resultado|

### Listar Archivos

Lista archivos de un bucket de Storage, con filtro opcional por path o prefijo.
|Parámetros|Descripción|ejemplo|
| --- | --- | --- |
|Bucket||my-bucket|
|Path/prefix (opcional)|||
|Asignar resultado a variable|Nombre de la variable donde se guardara el resultado|resultado|

### Subir Archivo

Sube un archivo local a un bucket de Storage, con object path y upsert opcionales.
|Parámetros|Descripción|ejemplo|
| --- | --- | --- |
|Bucket||my-bucket|
|Archivo local|Seleccione el archivo local a subir|C:/Users/Usuario/Desktop/archivo.png|
|Object path (opcional)||folder/file.png|
|Upsert (opcional)|||
|Asignar resultado a variable|Nombre de la variable donde se guardara el resultado|resultado|

### Descargar Archivo

Descarga un objeto de Storage desde un bucket a una carpeta o ruta local.
|Parámetros|Descripción|ejemplo|
| --- | --- | --- |
|Bucket||my-bucket|
|Object path||folder/file.png|
|Carpeta destino local|Seleccione la carpeta local donde se descargara el archivo|C:/Users/Usuario/Descargas|
|Asignar resultado a variable|Nombre de la variable donde se guardara el resultado|resultado|

### Ejecutar Funcion

Ejecuta una funcion RPC de Postgres en Supabase con parametros JSON opcionales.
|Parámetros|Descripción|ejemplo|
| --- | --- | --- |
|Nombre de funcion||my_function|
|Params (JSON object)||{}|
|Asignar resultado a variable|Nombre de la variable donde se guardara el resultado|resultado|

### Conectar Embeddings

Configura la API key del proveedor de embeddings y devuelve los modelos disponibles.
|Parámetros|Descripción|ejemplo|
| --- | --- | --- |
|Proveedor|||
|API Key||...|
|Modelo embedding por defecto (opcional)||text-embedding-3-small|
|Asignar resultado a variable|Nombre de la variable donde se guardara el resultado|resultado|

### Generar Embedding

Divide texto en fragmentos, genera embeddings e inserta los vectores en una tabla.
|Parámetros|Descripción|ejemplo|
| --- | --- | --- |
|Modelo embedding||text-embedding-3-small|
|Nombre de tabla||documents|
|Texto||text...|
|Chunk size (opcional)||1024|
|Chunk overlap (opcional)||128|
|Dim embedding (opcional)||384|
|Columna content (opcional)||content|
|Columna embedding (opcional)||embedding|
|Columna metadata (opcional)||metadata|
|Metadata extra (JSON object)||{}|
|Asignar resultado a variable|Nombre de la variable donde se guardara el resultado|resultado|

### Buscar Documentos

Genera un embedding de consulta y llama un RPC vectorial para buscar documentos.
|Parámetros|Descripción|ejemplo|
| --- | --- | --- |
|Modelo embedding||text-embedding-3-small|
|Nombre de funcion||match_documents|
|Texto a buscar||query...|
|Numero de resultados||5|
|Dim embedding (opcional)||384|
|Filtro (JSON object)||{}|
|Umbral match (opcional)||0.8|
|Params RPC extra (JSON object)||{}|
|Asignar resultado a variable|Nombre de la variable donde se guardara el resultado|resultado|

### Trigger Supabase

Consulta una tabla buscando filas con id mayor al ultimo id procesado.
|Parámetros|Descripción|ejemplo|
| --- | --- | --- |
|Tabla||public.users|
|Ultimo id (opcional)||0|
|Asignar resultado a variable|Nombre de la variable donde se guardara el resultado|resultado|
