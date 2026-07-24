



# Supabase

Supabase e uma plataforma open-source baseada em Postgres para criar backends com autenticacao, APIs e storage. Este modulo permite conectar e executar operacoes a partir do Rocketbot.

*Read this in other languages: [English](Manual_Supabase.md), [Português](Manual_Supabase.pr.md), [Español](Manual_Supabase.es.md)*

![banner](imgs/Banner_Supabase.jpg)
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
|URL do projeto|Endereco web do projeto Supabase, por exemplo https//project-ref.supabase.co.|https://<project-ref>.supabase.co|
|Chave de API|Chave de acesso do Supabase usada para autenticar as requisicoes ao projeto.|eyJhbGciOi...|
|Atribuir resultado a variavel|Nome da variavel para armazenar o resultado.|resultado|

### Obter Tabela

Le linhas de uma tabela Supabase, com ordenacao opcional por created_at.
|Parâmetros|Descrição|exemplo|
| --- | --- | --- |
|Nome da tabela|Nome da tabela do Supabase usada por este comando.|public.users|
|Ordenar por created_at (opcional)|Quando ativo, ordena os registros pela coluna created_at.||
|Atribuir resultado a variavel|Nome da variavel para armazenar a lista de registros da tabela. Se nao houver registros, armazena uma lista vazia [].|resultado|

### Filtrar Tabela

Le linhas de uma tabela onde uma coluna coincide com o valor informado.
|Parâmetros|Descrição|exemplo|
| --- | --- | --- |
|Nome da tabela|Nome da tabela do Supabase usada por este comando.|public.users|
|Coluna filtro|Nome da coluna usada para filtrar registros.|id|
|Valor filtro|Valor que deve coincidir com a coluna de filtro.|1|
|Atribuir resultado a variavel|Nome da variavel onde sera armazenada a lista de registros filtrados. Se nao houver correspondencias, armazena uma lista vazia [].|resultado|

### Colunas da tabela

Retorna as colunas de uma tabela como modelo de linha vazio ou como lista de nomes.
|Parâmetros|Descrição|exemplo|
| --- | --- | --- |
|Nome da tabela|Nome da tabela do Supabase usada por este comando.|public.users|
|Retornar como lista|Quando ativo, armazena uma lista simples de nomes de colunas, por exemplo ["id", "nome"]. Quando inativo, armazena um modelo JSON, por exemplo {"columns" [{"id" ""}]}||
|Atribuir resultado a variavel|Nome da variavel para armazenar o resultado usando o formato selecionado.|resultado|

### Inserir Linhas

Insere uma ou mais linhas em uma tabela a partir de um array JSON.
|Parâmetros|Descrição|exemplo|
| --- | --- | --- |
|Nome da tabela|Nome da tabela do Supabase usada por este comando.|public.users|
|Linhas (JSON array)|Array JSON com uma ou mais linhas. Cada objeto representa uma linha.|[{"name":"Alfredo"}]|
|Atribuir resultado a variavel|Nome da variavel para armazenar o resultado.|resultado|

### Atualizar Linhas

Atualiza uma coluna em linhas selecionadas por um filtro de igualdade.
|Parâmetros|Descrição|exemplo|
| --- | --- | --- |
|Nome da tabela|Nome da tabela do Supabase usada por este comando.|public.users|
|Nome da coluna|Nome da coluna que recebera o novo valor.|status|
|Valor|Novo valor que sera atribuido a coluna indicada.|active|
|Coluna filtro|Nome da coluna usada para filtrar registros.|id|
|Valor filtro|Valor que deve coincidir com a coluna de filtro.|1|
|Atribuir resultado a variavel|Nome da variavel para armazenar o resultado.|resultado|

### Atualizar Multiplas

Atualiza multiplas linhas a partir de um datatable JSON, usando id ou uma clausula WHERE.
|Parâmetros|Descrição|exemplo|
| --- | --- | --- |
|Nome da tabela|Nome da tabela do Supabase usada por este comando.|public.users|
|Linhas para atualizar (array JSON)|Array JSON com os dados para atualizar. Pode usar o id de cada linha ou uma condicao WHERE.|[{"id":1,"name":"X"}]|
|WHERE (opcional)|Clausula WHERE opcional para selecionar registros quando nao se usa id por linha.|{"id":1}|
|Atribuir resultado a variavel|Nome da variavel para armazenar o resultado.|resultado|

### Excluir Linhas

Exclui linhas de uma tabela onde uma coluna coincide com o valor informado.
|Parâmetros|Descrição|exemplo|
| --- | --- | --- |
|Nome da tabela|Nome da tabela do Supabase usada por este comando.|public.users|
|Coluna filtro|Nome da coluna usada para filtrar registros.|id|
|Valor filtro (valor ou JSON array)|Valor que deve coincidir com a coluna de filtro.|1|
|Atribuir resultado a variavel|Nome da variavel para armazenar o resultado.|resultado|

### Listar recipientes de arquivos

Lista os buckets de Storage disponiveis no projeto Supabase conectado.
|Parâmetros|Descrição|exemplo|
| --- | --- | --- |
|Atribuir resultado a variavel|Nome da variavel para armazenar a lista de nomes de recipientes de arquivos, por exemplo ["vault", "vault1"].|resultado|

### Criar recipiente de arquivos

Cria um bucket de Storage e permite configurar visibilidade, limite e tipos MIME.
|Parâmetros|Descrição|exemplo|
| --- | --- | --- |
|Nome do recipiente de arquivos|Nome do recipiente de arquivos de Storage.|my-bucket|
|Publico|Indica se os arquivos do recipiente serao publicos.||
|Limite de tamanho de arquivo (opcional)|Limite opcional de tamanho de arquivo, em bytes. Por padrao 10000000 bytes.|10000000|
|Tipos de arquivo permitidos (opcional)|Tipos de arquivo permitidos para enviar ao recipiente. Use um array JSON, por exemplo ["image/png", "image/jpeg", "application/pdf"]. Tambem pode usar text/plain, application/json ou application/zip.|image/png,image/jpeg|
|Atribuir resultado a variavel|Nome da variavel para armazenar True se o recipiente de arquivos foi criado corretamente ou False se nao foi possivel criar.|resultado|

### Obter recipiente de arquivos

Obtem detalhes de um bucket e opcionalmente lista seus arquivos na raiz.
|Parâmetros|Descrição|exemplo|
| --- | --- | --- |
|Nome do recipiente de arquivos|Nome do recipiente de arquivos de Storage.|my-bucket|
|Incluir arquivos|Quando ativo, inclui os arquivos localizados na pasta principal do recipiente.||
|Atribuir resultado a variavel|Nome da variavel para armazenar o resultado.|resultado|

### Listar Arquivos

Lista arquivos de um bucket de Storage, com filtro opcional por path ou prefixo.
|Parâmetros|Descrição|exemplo|
| --- | --- | --- |
|Recipiente de arquivos|Nome do recipiente de arquivos de Storage.|my-bucket|
|Pasta ou prefixo (opcional)|Pasta ou inicio de caminho opcional dentro do recipiente para filtrar arquivos.||
|Atribuir resultado a variavel|Nome da variavel para armazenar a lista de arquivos encontrados no recipiente. Se nao houver arquivos, armazena uma lista vazia [].|resultado|

### Enviar Arquivo

Envia um arquivo local para um bucket de Storage, com object path e upsert opcionais.
|Parâmetros|Descrição|exemplo|
| --- | --- | --- |
|Recipiente de arquivos|Nome do recipiente de arquivos de Storage.|my-bucket|
|Arquivo local|Caminho do arquivo local que sera enviado ao Supabase.|C:/Users/Usuario/Desktop/arquivo.png|
|Caminho de destino do arquivo (opcional)|Caminho do arquivo dentro do recipiente de Storage.|folder/file.png|
|Atualizar ou inserir se ja existir (opcional)|Quando ativo, substitui o arquivo se ele ja existir no mesmo caminho; se nao existir, insere.||
|Atribuir resultado a variavel|Nome da variavel para armazenar True se o arquivo foi enviado corretamente ou False se nao foi possivel enviar.|resultado|

### Baixar Arquivo

Baixa um objeto de Storage de um bucket para uma pasta ou rota local.
|Parâmetros|Descrição|exemplo|
| --- | --- | --- |
|Recipiente de arquivos|Nome do recipiente de arquivos de Storage.|my-bucket|
|Caminho do arquivo no Supabase|Caminho do arquivo dentro do recipiente de Storage.|folder/file.png|
|Pasta destino local|Pasta ou caminho local onde o arquivo baixado sera salvo.|C:/Users/Usuario/Downloads|
|Atribuir resultado a variavel|Nome da variavel para armazenar True se o arquivo foi baixado corretamente ou False se nao foi possivel baixar.|resultado|

### Executar Funcao

Executa uma funcao RPC do Postgres no Supabase com parametros JSON opcionais.
|Parâmetros|Descrição|exemplo|
| --- | --- | --- |
|Nome da funcao|Nome da funcao RPC/Postgres que sera executada no Supabase.|my_function|
|Parametros (objeto JSON)|Objeto JSON opcional com os parametros passados para a funcao. Por padrao {}.|{}|
|Obter resposta completa da API|Quando ativo, retorna toda a resposta da funcao. Quando desativado, retorna apenas o valor message quando existir.||
|Atribuir resultado a variavel|Nome da variavel para armazenar o valor message retornado pela funcao. Se Obter resposta completa da API estiver ativo, armazena toda a resposta.|resultado|

### Configurar busca semantica

Configura a API key do provedor de embeddings e retorna os modelos disponiveis.
|Parâmetros|Descrição|exemplo|
| --- | --- | --- |
|Provedor|Provedor de embeddings que sera configurado para gerar vetores.||
|Chave de API|Chave de acesso do provedor de embeddings.|...|
|Modelo de embeddings padrao (opcional)|Modelo de embeddings padrao usado quando outros comandos nao indicam um. Por padrao text-embedding-3-small.|text-embedding-3-small|
|Atribuir resultado a variavel|Nome da variavel para armazenar o resultado.|resultado|

### Gerar vetor de texto

Divide texto em partes, gera embeddings e insere os vetores em uma tabela.
|Parâmetros|Descrição|exemplo|
| --- | --- | --- |
|Modelo de embeddings|Modelo usado para gerar embeddings. Por padrao text-embedding-3-small.|text-embedding-3-small|
|Nome da tabela|Nome da tabela do Supabase usada por este comando.|documents|
|Texto|Texto fonte que sera processado para gerar embeddings.|text...|
|Tamanho do fragmento (opcional)|Tamanho maximo opcional de cada fragmento de texto. Por padrao 1024.|1024|
|Sobreposicao entre fragmentos (opcional)|Quantidade opcional de caracteres repetidos entre fragmentos consecutivos para manter contexto. Por padrao 128.|128|
|Dimensao do vetor (opcional)|Dimensao esperada do vetor gerado. Deve coincidir com o modelo e a coluna vetorial. Por padrao 384.|384|
|Coluna content (opcional)|Coluna onde sera armazenado o conteudo de cada fragmento. Por padrao content.|content|
|Coluna do vetor (opcional)|Coluna vetorial onde o vetor gerado sera armazenado. Por padrao embedding.|embedding|
|Coluna metadata (opcional)|Coluna onde serao armazenados os dados adicionais de cada fragmento. Por padrao metadata.|metadata|
|Dados adicionais (objeto JSON)|Objeto JSON opcional com dados adicionais para armazenar junto a cada fragmento. Por padrao {}.|{}|
|Atribuir resultado a variavel|Nome da variavel para armazenar o resultado.|resultado|

### Buscar Documentos

Gera um embedding de consulta e chama um RPC vetorial para buscar documentos.
|Parâmetros|Descrição|exemplo|
| --- | --- | --- |
|Modelo de embeddings|Modelo usado para gerar embeddings. Por padrao text-embedding-3-small.|text-embedding-3-small|
|Nome da funcao|Nome da funcao RPC/Postgres que sera executada no Supabase. Por padrao match_documents.|match_documents|
|Texto a buscar|Texto da consulta que sera convertido em embedding para buscar documentos similares.|query...|
|Numero de resultados|Quantidade maxima de documentos similares a retornar. Por padrao 5.|5|
|Dimensao do vetor (opcional)|Dimensao esperada do vetor gerado. Deve coincidir com o modelo e a coluna vetorial. Por padrao 384.|384|
|Filtro (objeto JSON)|Objeto JSON opcional com filtros adicionais para a busca semantica. Por padrao {}.|{}|
|Limiar match (opcional)|Limiar opcional minimo de similaridade para aceitar resultados. Por padrao 0.8.|0.8|
|Parametros RPC extras (objeto JSON)|Objeto JSON opcional com parametros extras enviados para a funcao RPC. Por padrao {}.|{}|
|Obter mais detalhes|Quando ativo, retorna todas as informacoes encontradas, incluindo id, metadata e similaridade. Quando desativado, retorna apenas o conteudo de cada documento.||
|Atribuir resultado a variavel|Nome da variavel para armazenar a lista de conteudos encontrados. Se Obter mais detalhes estiver ativo, armazena todas as informacoes retornadas pela busca.|resultado|

### Consultar novos registros

Consulta uma tabela buscando linhas com id maior que o ultimo id processado.
|Parâmetros|Descrição|exemplo|
| --- | --- | --- |
|Tabela|Tabela que sera consultada para detectar novos registros.|public.users|
|Ultimo id (opcional)|Ultimo id processado. O comando retorna linhas com id maior que este valor. Por padrao 0.|0|
|Atribuir resultado a variavel|Nome da variavel para armazenar o resultado.|resultado|
