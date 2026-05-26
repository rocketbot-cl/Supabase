



# Supabase

Supabase e uma plataforma open-source baseada em Postgres para criar backends com autenticacao, APIs e storage. Este modulo permite conectar e executar operacoes a partir do Rocketbot.

*Read this in other languages: [English](Manual_Supabase.md), [Português](Manual_Supabase.pr.md), [Español](Manual_Supabase.es.md)*

![banner](imgs/Banner_Supabase.png o jpg)
## Como instalar este módulo

Para instalar o módulo no Rocketbot Studio, pode ser feito de duas formas:
1. Manual: __Baixe__ o arquivo .zip e descompacte-o na pasta módulos. O nome da pasta deve ser o mesmo do módulo e dentro dela devem ter os seguintes arquivos e pastas: \__init__.py, package.json, docs, example e libs. Se você tiver o aplicativo aberto, atualize seu navegador para poder usar o novo módulo.
2. Automático: Ao entrar no Rocketbot Studio na margem direita você encontrará a seção **Addons**, selecione **Install Mods**, procure o módulo desejado e aperte instalar.



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
- As chaves legacy `anon` e `service_role` ainda podem existir. 
Trate `anon` como acesso publicavel e `service_role` como acesso secreto/backend.
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
7. 
Execute Retrieve Documents para gerar o embedding de consulta e chamar a funcao RPC.

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
-
 https://supabase.com/docs/guides/ai/rag-with-permissions


## Descrição do comando

### Conectar

Conecta a um projeto Supabase e verifica se a API key tem acesso.
|Parâmetros|Descrição|exemplo|
| --- | --- | --- |
|Credencial|||
|Project URL||https://<project-ref>.supabase.co|
|API Key||eyJhbGciOi...|
|Atribuir resultado a variavel|Nome da variavel para armazenar o resultado|resultado|

### Obter Tabela

Le linhas de uma tabela Supabase, com ordenacao opcional por created_at.
|Parâmetros|Descrição|exemplo|
| --- | --- | --- |
|Nome da tabela||public.users|
|Ordenar por created_at (opcional)|||
|Atribuir resultado a variavel|Nome da variavel para armazenar o resultado|resultado|

### Filtrar Tabela

Le linhas de uma tabela onde uma coluna coincide com o valor informado.
|Parâmetros|Descrição|exemplo|
| --- | --- | --- |
|Nome da tabela||public.users|
|Coluna filtro||id|
|Valor filtro||1|
|Atribuir resultado a variavel|Nome da variavel para armazenar o resultado|resultado|

### Colunas (template)

Cria um modelo JSON vazio usando as colunas detectadas em uma tabela.
|Parâmetros|Descrição|exemplo|
| --- | --- | --- |
|Nome da tabela||public.users|
|Atribuir resultado a variavel|Nome da variavel para armazenar o resultado|resultado|

### Listar Colunas

Retorna os nomes de colunas disponiveis em uma tabela.
|Parâmetros|Descrição|exemplo|
| --- | --- | --- |
|Nome da tabela||public.users|
|Atribuir resultado a variavel|Nome da variavel para armazenar o resultado|resultado|

### Inserir Linhas

Insere uma ou mais linhas em uma tabela a partir de um array JSON.
|Parâmetros|Descrição|exemplo|
| --- | --- | --- |
|Nome da tabela||public.users|
|Linhas (JSON array)||[{"name":"Alfredo"}]|
|Atribuir resultado a variavel|Nome da variavel para armazenar o resultado|resultado|

### Atualizar Linhas

Atualiza uma coluna em linhas selecionadas por um filtro de igualdade.
|Parâmetros|Descrição|exemplo|
| --- | --- | --- |
|Nome da tabela||public.users|
|Nome da coluna||status|
|Valor||active|
|Coluna filtro||id|
|Valor filtro||1|
|Atribuir resultado a variavel|Nome da variavel para armazenar o resultado|resultado|

### Atualizar Multiplas

Atualiza multiplas linhas a partir de um datatable JSON, usando id ou uma clausula WHERE.
|Parâmetros|Descrição|exemplo|
| --- | --- | --- |
|Nome da tabela||public.users|
|Datatable (JSON array)||[{"id":1,"name":"X"}]|
|WHERE (opcional)||{"id":1}|
|Atribuir resultado a variavel|Nome da variavel para armazenar o resultado|resultado|

### Excluir Linhas

Exclui linhas de uma tabela onde uma coluna coincide com o valor informado.
|Parâmetros|Descrição|exemplo|
| --- | --- | --- |
|Nome da tabela||public.users|
|Coluna filtro||id|
|Valor filtro (valor ou JSON array)||1|
|Atribuir resultado a variavel|Nome da variavel para armazenar o resultado|resultado|

### Listar Buckets

Lista os buckets de Storage disponiveis no projeto Supabase conectado.
|Parâmetros|Descrição|exemplo|
| --- | --- | --- |
|Atribuir resultado a variavel|Nome da variavel para armazenar o resultado|resultado|

### Criar Bucket

Cria um bucket de Storage e permite configurar visibilidade, limite e tipos MIME.
|Parâmetros|Descrição|exemplo|
| --- | --- | --- |
|Nome bucket||my-bucket|
|Publico|||
|Limite tamanho (opcional)||10000000|
|Mimes permitidos (opcional)||image/png,image/jpeg|
|Atribuir resultado a variavel|Nome da variavel para armazenar o resultado|resultado|

### Obter Bucket

Obtem detalhes de um bucket e opcionalmente lista seus arquivos na raiz.
|Parâmetros|Descrição|exemplo|
| --- | --- | --- |
|Nome bucket||my-bucket|
|Incluir arquivos|||
|Atribuir resultado a variavel|Nome da variavel para armazenar o resultado|resultado|

### Listar Arquivos

Lista arquivos de um bucket de Storage, com filtro opcional por path ou prefixo.
|Parâmetros|Descrição|exemplo|
| --- | --- | --- |
|Bucket||my-bucket|
|Path/prefix (opcional)|||
|Atribuir resultado a variavel|Nome da variavel para armazenar o resultado|resultado|

### Enviar Arquivo

Envia um arquivo local para um bucket de Storage, com object path e upsert opcionais.
|Parâmetros|Descrição|exemplo|
| --- | --- | --- |
|Bucket||my-bucket|
|Arquivo local|Selecione o arquivo local para enviar|C:/Users/Usuario/Desktop/arquivo.png|
|Object path (opcional)||folder/file.png|
|Upsert (opcional)|||
|Atribuir resultado a variavel|Nome da variavel para armazenar o resultado|resultado|

### Baixar Arquivo

Baixa um objeto de Storage de um bucket para uma pasta ou rota local.
|Parâmetros|Descrição|exemplo|
| --- | --- | --- |
|Bucket||my-bucket|
|Object path||folder/file.png|
|Pasta destino local|Selecione a pasta local onde o arquivo sera baixado|C:/Users/Usuario/Downloads|
|Atribuir resultado a variavel|Nome da variavel para armazenar o resultado|resultado|

### Executar Funcao

Executa uma funcao RPC do Postgres no Supabase com parametros JSON opcionais.
|Parâmetros|Descrição|exemplo|
| --- | --- | --- |
|Nome da funcao||my_function|
|Params (JSON object)||{}|
|Atribuir resultado a variavel|Nome da variavel para armazenar o resultado|resultado|

### Conectar Embeddings

Configura a API key do provedor de embeddings e retorna os modelos disponiveis.
|Parâmetros|Descrição|exemplo|
| --- | --- | --- |
|Provedor|||
|API Key||...|
|Modelo embedding padrao (opcional)||text-embedding-3-small|
|Atribuir resultado a variavel|Nome da variavel para armazenar o resultado|resultado|

### Gerar Embedding

Divide texto em partes, gera embeddings e insere os vetores em uma tabela.
|Parâmetros|Descrição|exemplo|
| --- | --- | --- |
|Modelo embedding||text-embedding-3-small|
|Nome da tabela||documents|
|Texto||text...|
|Chunk size (opcional)||1024|
|Chunk overlap (opcional)||128|
|Dim embedding (opcional)||384|
|Coluna content (opcional)||content|
|Coluna embedding (opcional)||embedding|
|Coluna metadata (opcional)||metadata|
|Metadata extra (JSON object)||{}|
|Atribuir resultado a variavel|Nome da variavel para armazenar o resultado|resultado|

### Buscar Documentos

Gera um embedding de consulta e chama um RPC vetorial para buscar documentos.
|Parâmetros|Descrição|exemplo|
| --- | --- | --- |
|Modelo embedding||text-embedding-3-small|
|Nome da funcao||match_documents|
|Texto a buscar||query...|
|Numero de resultados||5|
|Dim embedding (opcional)||384|
|Filtro (JSON object)||{}|
|Limiar match (opcional)||0.8|
|Params RPC extra (JSON object)||{}|
|Atribuir resultado a variavel|Nome da variavel para armazenar o resultado|resultado|

### Trigger Supabase

Consulta uma tabela buscando linhas com id maior que o ultimo id processado.
|Parâmetros|Descrição|exemplo|
| --- | --- | --- |
|Tabela||public.users|
|Ultimo id (opcional)||0|
|Atribuir resultado a variavel|Nome da variavel para armazenar o resultado|resultado|
