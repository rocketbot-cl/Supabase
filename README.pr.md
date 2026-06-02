



# Supabase

Supabase e uma plataforma open-source baseada em Postgres para criar backends com autenticacao, APIs e storage. Este modulo permite conectar e executar operacoes a partir do Rocketbot.

*Read this in other languages: [English](README.md), [Português](README.pr.md), [Español](README.es.md)*

## Como instalar este módulo

Para instalar o módulo no Rocketbot Studio, pode ser feito de duas formas:
1. Manual: __Baixe__ o arquivo .zip e descompacte-o na pasta módulos. O nome da pasta deve ser o mesmo do módulo e dentro dela devem ter os seguintes arquivos e pastas: \__init__.py, package.json, docs, example e libs. Se você tiver o aplicativo aberto, atualize seu navegador para poder usar o novo módulo.
2. Automático: Ao entrar no Rocketbot Studio na margem direita você encontrará a seção **Addons**, selecione **Install Mods**, procure o módulo desejado e aperte instalar.


## Overview


1. Conectar
Conecta a um projeto Supabase e verifica se a API key tem acesso.

2. Obter Tabela
Le linhas de uma tabela Supabase, com ordenacao opcional por created_at.

3. Filtrar Tabela
Le linhas de uma tabela onde uma coluna coincide com o valor informado.

4. Colunas (template)
Cria um modelo JSON vazio usando as colunas detectadas em uma tabela.

5. Listar Colunas
Retorna os nomes de colunas disponiveis em uma tabela.

6. Inserir Linhas
Insere uma ou mais linhas em uma tabela a partir de um array JSON.

7. Atualizar Linhas
Atualiza uma coluna em linhas selecionadas por um filtro de igualdade.

8. Atualizar Multiplas
Atualiza multiplas linhas a partir de um datatable JSON, usando id ou uma clausula WHERE.

9. Excluir Linhas
Exclui linhas de uma tabela onde uma coluna coincide com o valor informado.

10. Listar recipientes de arquivos
Lista os buckets de Storage disponiveis no projeto Supabase conectado.

11. Criar recipiente de arquivos
Cria um bucket de Storage e permite configurar visibilidade, limite e tipos MIME.

12. Obter recipiente de arquivos
Obtem detalhes de um bucket e opcionalmente lista seus arquivos na raiz.

13. Listar Arquivos
Lista arquivos de um bucket de Storage, com filtro opcional por path ou prefixo.

14. Enviar Arquivo
Envia um arquivo local para um bucket de Storage, com object path e upsert opcionais.

15. Baixar Arquivo
Baixa um objeto de Storage de um bucket para uma pasta ou rota local.

16. Executar Funcao
Executa uma funcao RPC do Postgres no Supabase com parametros JSON opcionais.

17. Configurar busca semantica
Configura a API key do provedor de embeddings e retorna os modelos disponiveis.

18. Gerar vetor de texto
Divide texto em partes, gera embeddings e insere os vetores em uma tabela.

19. Buscar Documentos
Gera um embedding de consulta e chama um RPC vetorial para buscar documentos.

20. Consultar novos registros
Consulta uma tabela buscando linhas com id maior que o ultimo id processado.




----
### OS

- windows
- mac
- linux

### Dependencies

### License

![MIT](https://camo.githubusercontent.com/107590fac8cbd65071396bb4d04040f76cde5bde/687474703a2f2f696d672e736869656c64732e696f2f3a6c6963656e73652d6d69742d626c75652e7376673f7374796c653d666c61742d737175617265)
[MIT](http://opensource.org/licenses/mit-license.ph)