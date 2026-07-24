



# Supabase

Supabase es una plataforma open-source basada en Postgres para construir backends con autenticación, APIs y storage. Este módulo permite conectarse y ejecutar operaciones desde Rocketbot.

*Read this in other languages: [English](README.md), [Português](README.pr.md), [Español](README.es.md)*

## Como instalar este módulo

Para instalar el módulo en Rocketbot Studio, se puede hacer de dos formas:
1. Manual: __Descargar__ el archivo .zip y descomprimirlo en la carpeta modules. El nombre de la carpeta debe ser el mismo al del módulo y dentro debe tener los siguientes archivos y carpetas: \__init__.py, package.json, docs, example y libs. Si tiene abierta la aplicación, refresca el navegador para poder utilizar el nuevo modulo.
2. Automática: Al ingresar a Rocketbot Studio sobre el margen derecho encontrara la sección de **Addons**, seleccionar **Install Mods**, buscar el modulo deseado y presionar install.


## Overview


1. Conectar
Conecta con un proyecto Supabase y verifica que la API key tenga acceso.

2. Obtener Tabla
Lee filas de una tabla Supabase, con orden opcional por created_at.

3. Filtrar Tabla
Lee filas de una tabla donde una columna coincide con el valor indicado.

4. Columnas de tabla
Devuelve las columnas de una tabla como plantilla de fila vacia o como lista de nombres.

5. Insertar Filas
Inserta una o mas filas en una tabla desde un array JSON.

6. Actualizar Filas
Actualiza una columna en filas seleccionadas por un filtro de igualdad.

7. Actualizar Multiples
Actualiza multiples filas desde un datatable JSON, usando id o una clausula WHERE.

8. Borrar Filas
Elimina filas de una tabla donde una columna coincide con el valor indicado.

9. Listar contenedores de archivos
Lista los buckets de Storage disponibles en el proyecto Supabase conectado.

10. Crear contenedor de archivos
Crea un bucket de Storage y permite configurar visibilidad, limite y tipos MIME.

11. Obtener contenedor de archivos
Obtiene detalles de un bucket y opcionalmente lista sus archivos en la raiz.

12. Listar Archivos
Lista archivos de un bucket de Storage, con filtro opcional por path o prefijo.

13. Subir Archivo
Sube un archivo local a un bucket de Storage, con object path y upsert opcionales.

14. Descargar Archivo
Descarga un objeto de Storage desde un bucket a una carpeta o ruta local.

15. Ejecutar Funcion
Ejecuta una funcion RPC de Postgres en Supabase con parametros JSON opcionales.

16. Configurar busqueda semantica
Configura la API key del proveedor de embeddings y devuelve los modelos disponibles.

17. Generar vector de texto
Divide texto en fragmentos, genera embeddings e inserta los vectores en una tabla.

18. Buscar Documentos
Genera un embedding de consulta y llama un RPC vectorial para buscar documentos.

19. Consultar nuevos registros
Consulta una tabla buscando filas con id mayor al ultimo id procesado.




----
### OS

- windows
- mac
- linux

### Dependencies

### License

![MIT](https://camo.githubusercontent.com/107590fac8cbd65071396bb4d04040f76cde5bde/687474703a2f2f696d672e736869656c64732e696f2f3a6c6963656e73652d6d69742d626c75652e7376673f7374796c653d666c61742d737175617265)
[MIT](http://opensource.org/licenses/mit-license.ph)