## How to use this module

Use this module to connect Rocketbot with Supabase and run database, Storage, RPC, and embedding operations.

Basic usage:
1. Create or select a Supabase project.
2. Copy the Project URL and an API key from Supabase.
3. Run Connect before using the other commands.
4. Use table commands for CRUD operations, Storage commands for buckets/files, and RPC commands for Postgres functions.

API keys and RLS:
- Supabase API keys identify the application component that is accessing the project. They do not identify the end user by themselves.
- Prefer `sb_publishable_...` for public/client contexts. This key is low-privilege and access is controlled by RLS policies.
- Use `sb_secret_...` only for secure backend automation. Secret keys have elevated access and can bypass RLS, so do not expose them in browsers, public repositories, logs, chats, or URLs.
- Legacy `anon` and `service_role` JWT keys may still exist. Treat `anon` like publishable access and `service_role` like secret backend access.
- If a command fails with permission errors, review the table policies, the role allowed by the key, or use a backend key only when appropriate.

Embedding commands:
The embedding commands are advanced. Rocketbot generates embeddings and calls Supabase, but Supabase must already have the database objects needed to store and compare vectors.

Command flow:
1. Run Connect.
2. Run Embeddings Connect to store the embedding provider, API key, and default model.
3. In Supabase, create a compatible table, for example `documents`.
4. Enable the `vector` extension and create a vector column, for example `embedding vector(384)`. The dimension must match the model output.
5. Create an RPC function, for example `match_documents`, that receives `query_embedding`, `match_threshold`, and `match_count`, then compares vectors.
6. Run Generate And Store Embedding to split text, generate vectors, and insert the rows.
7. Run Retrieve Documents to generate a query embedding and call the RPC function.

Important notes:
- Supabase stores embeddings with Postgres and pgvector.
- Semantic search compares meaning, not exact keywords.
- The RPC function belongs to the customer project. Adjust table names, column names, vector dimensions, filters, and return columns to the customer's schema.
- For larger tables, add a vector index. Supabase generally recommends HNSW for performance and robustness; IVFFlat is available for specific cases.
- If documents have permissions, apply RLS or permission-aware filters in Supabase so vector search only returns allowed rows.

References:
- https://supabase.com/docs/guides/getting-started/api-keys
- https://supabase.com/docs/guides/ai
- https://supabase.com/docs/guides/ai/concepts
- https://supabase.com/docs/guides/ai/vector-columns
- https://supabase.com/docs/guides/ai/vector-indexes
- https://supabase.com/docs/guides/ai/semantic-search
- https://supabase.com/docs/guides/ai/rag-with-permissions

---

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
- Las claves legacy `anon` y `service_role` pueden seguir existiendo. Trate `anon` como acceso publicable y `service_role` como acceso secreto/backend.
- Si un comando falla por permisos, revise las politicas de la tabla, el rol permitido por la clave o use una clave backend solo cuando corresponda.

Comandos de embeddings:
Los comandos de embeddings son avanzados. Rocketbot genera embeddings y llama a Supabase, pero Supabase debe tener creados previamente los objetos necesarios para guardar y comparar vectores.

Flujo de uso:
1. Ejecute Connect.
2. Ejecute Embeddings Connect para guardar proveedor, API key y modelo por defecto.
3. En Supabase, cree una tabla compatible, por ejemplo `documents`.
4. Habilite la extension `vector` y cree una columna vectorial, por ejemplo `embedding vector(384)`. La dimension debe coincidir con la salida del modelo.
5. Cree una funcion RPC, por ejemplo `match_documents`, que reciba `query_embedding`, `match_threshold` y `match_count`, y compare vectores.
6. Ejecute Generate And Store Embedding para dividir texto, generar vectores e insertar las filas.
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
- https://supabase.com/docs/guides/ai/vector-indexes
- https://supabase.com/docs/guides/ai/semantic-search
- https://supabase.com/docs/guides/ai/rag-with-permissions

---

## Como usar este modulo

Use este modulo para conectar o Rocketbot ao Supabase e executar operacoes de banco de dados, Storage, RPC e embeddings.

Uso basico:
1. Crie ou selecione um projeto Supabase.
2. Copie o Project URL e uma API key no Supabase.
3. Execute Connect antes de usar os outros comandos.
4. Use os comandos de tabelas para CRUD, os comandos de Storage para buckets/arquivos e os comandos RPC para funcoes Postgres.

API keys e RLS:
- As API keys do Supabase identificam o componente da aplicacao que acessa o projeto. Elas nao identificam o usuario final por si so.
- Prefira `sb_publishable_...` para contextos publicos/client-side. Essa chave tem baixo privilegio e o acesso e controlado por politicas RLS.
- Use `sb_secret_...` somente para automacoes backend seguras. Secret keys tem acesso elevado e podem ignorar RLS, por isso nao devem ser expostas em navegadores, repositorios publicos, logs, chats ou URLs.
- As chaves legacy `anon` e `service_role` ainda podem existir. Trate `anon` como acesso publicavel e `service_role` como acesso secreto/backend.
- Se um comando falhar por permissoes, revise as politicas da tabela, o papel permitido pela chave ou use uma chave backend somente quando apropriado.

Comandos de embeddings:
Os comandos de embeddings sao avancados. O Rocketbot gera embeddings e chama o Supabase, mas o Supabase ja deve ter os objetos necessarios para armazenar e comparar vetores.

Fluxo de uso:
1. Execute Connect.
2. Execute Embeddings Connect para guardar provedor, API key e modelo padrao.
3. No Supabase, crie uma tabela compativel, por exemplo `documents`.
4. Habilite a extensao `vector` e crie uma coluna vetorial, por exemplo `embedding vector(384)`. A dimensao deve coincidir com a saida do modelo.
5. Crie uma funcao RPC, por exemplo `match_documents`, que receba `query_embedding`, `match_threshold` e `match_count`, e compare vetores.
6. Execute Generate And Store Embedding para dividir texto, gerar vetores e inserir as linhas.
7. Execute Retrieve Documents para gerar o embedding de consulta e chamar a funcao RPC.

Notas importantes:
- Supabase armazena embeddings usando Postgres e pgvector.
- A busca semantica compara significado, nao palavras exatas.
- A funcao RPC pertence ao projeto do cliente. Ajuste nomes de tabelas, colunas, dimensoes, filtros e colunas de retorno conforme o esquema do cliente.
- Para tabelas grandes, adicione um indice vetorial. Supabase geralmente recomenda HNSW por desempenho e robustez; IVFFlat existe para casos especificos.
- Se os documentos tiverem permissoes, aplique RLS ou filtros de permissao no Supabase para que a busca vetorial retorne somente linhas permitidas.

Referencias:
- https://supabase.com/docs/guides/getting-started/api-keys
- https://supabase.com/docs/guides/ai
- https://supabase.com/docs/guides/ai/concepts
- https://supabase.com/docs/guides/ai/vector-columns
- https://supabase.com/docs/guides/ai/vector-indexes
- https://supabase.com/docs/guides/ai/semantic-search
- https://supabase.com/docs/guides/ai/rag-with-permissions

---
