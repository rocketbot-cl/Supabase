



# Supabase

Supabase is an open-source Postgres-based platform for building backends with authentication, APIs, and storage. This module lets you connect and run operations from Rocketbot.

*Read this in other languages: [English](Manual_Supabase.md), [Português](Manual_Supabase.pr.md), [Español](Manual_Supabase.es.md)*

![banner](imgs/Banner_Supabase.jpg)
## How to install this module

To install the module in Rocketbot Studio, it can be done in two ways:
1. Manual: __Download__ the .zip file and unzip it in the modules folder. The folder name must be the same as the module and inside it must have the following files and folders: \__init__.py, package.json, docs, example and libs. If you have the application open, refresh your browser to be able to use the new module.
2. Automatic: When entering Rocketbot Studio on the right margin you will find the **Addons** section, select **Install Mods**, search for the desired module and press install.

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
- Legacy `anon` and `service_role` JWT keys may still exist. Treat `anon` like publishable access and `service_role` 
like secret backend access.
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
7. Run Retrieve Documents to generate a query embedding and 
call the RPC function.

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


## Description of the commands

### Connect

Connect to a Supabase project and verify that the API key can access the project.
|Parameters|Description|example|
| --- | --- | --- |
|Project URL|Supabase project URL, for example https//project-ref.supabase.co.|https://<project-ref>.supabase.co|
|API Key|Supabase API key used to authenticate requests to the project.|eyJhbGciOi...|
|Assign result to variable|Variable name to store the result.|result|

### Get Table

Read rows from a Supabase table, with optional sorting by created_at.
|Parameters|Description|example|
| --- | --- | --- |
|Table name|Name of the Supabase table used by this command.|public.users|
|Sort by created_at (optional)|When enabled, sorts the rows by the created_at column.||
|Assign result to variable|Variable name to store the list of table rows. If there are no rows, it stores an empty list [].|result|

### Filter Table

Read rows from a table where one column matches the provided value.
|Parameters|Description|example|
| --- | --- | --- |
|Table name|Name of the Supabase table used by this command.|public.users|
|Filter column|Name of the column used to filter rows.|id|
|Filter value|Value that must match the filter column.|1|
|Assign result to variable|Variable name to store the filtered row list. If there are no matches, it stores an empty list [].|result|

### Get Table Columns

Return table columns as a blank row template or as a list of column names.
|Parameters|Description|example|
| --- | --- | --- |
|Table name|Name of the Supabase table used by this command.|public.users|
|Return as list|When enabled, stores a simple list of column names, for example ["id", "name"]. When disabled, stores a JSON template, for example {"columns" [{"id" ""}]}||
|Assign result to variable|Variable name to store the result using the selected output format.|result|

### Insert Rows

Insert one or more rows into a table from a JSON array.
|Parameters|Description|example|
| --- | --- | --- |
|Table name|Name of the Supabase table used by this command.|public.users|
|Rows (JSON array)|JSON array with one or more rows. Each object represents one row.|[{"name":"Alfredo"}]|
|Assign result to variable|Variable name to store the result.|result|

### Update Rows

Update one column in rows selected by an equality filter.
|Parameters|Description|example|
| --- | --- | --- |
|Table name|Name of the Supabase table used by this command.|public.users|
|Column name|Name of the column that will receive the new value.|status|
|Value|New value to assign to the selected column.|active|
|Filter column|Name of the column used to filter rows.|id|
|Filter value|Value that must match the filter column.|1|
|Assign result to variable|Variable name to store the result.|result|

### Update Multiple Rows

Update multiple rows from a JSON datatable, using id or a WHERE clause to match rows.
|Parameters|Description|example|
| --- | --- | --- |
|Table name|Name of the Supabase table used by this command.|public.users|
|Datatable (JSON array)|JSON array with the data to update. It can use a row id or a WHERE clause.|[{"id":1,"name":"X"}]|
|WHERE clause (optional, JSON or col = 'value')|Optional WHERE clause to select rows when a row id is not used.|{"id":1}|
|Assign result to variable|Variable name to store the result.|result|

### Delete Rows

Delete rows from a table where a column matches the provided value.
|Parameters|Description|example|
| --- | --- | --- |
|Table name|Name of the Supabase table used by this command.|public.users|
|Filter column|Name of the column used to filter rows.|id|
|Filter value (value or JSON array)|Value that must match the filter column.|1|
|Assign result to variable|Variable name to store the result.|result|

### List Buckets

List the Storage buckets available in the connected Supabase project.
|Parameters|Description|example|
| --- | --- | --- |
|Assign result to variable|Variable name to store the list of bucket names, for example ["vault", "vault1"].|result|

### Create Bucket

Create a Storage bucket and optionally configure visibility, size limit, and MIME types.
|Parameters|Description|example|
| --- | --- | --- |
|Bucket name|Name of the Storage bucket.|my-bucket|
|Public|Indicates whether the bucket files will be public.||
|File size limit (optional)|Optional file size limit in bytes. Default 10000000 bytes.|10000000|
|Allowed MIME types (optional)|MIME types allowed when uploading files to the bucket. Use a JSON array, for example ["image/png", "image/jpeg", "application/pdf"]. Check MDN or the IANA registry for other types such as text/plain, application/json, or application/zip.|image/png,image/jpeg|
|Assign result to variable|Variable name to store True when the bucket was created successfully or False when it could not be created.|result|

### Get Bucket

Get bucket details and optionally include the files stored at the bucket root.
|Parameters|Description|example|
| --- | --- | --- |
|Bucket name|Name of the Storage bucket.|my-bucket|
|Include files|When enabled, includes files located at the bucket root.||
|Assign result to variable|Variable name to store the result.|result|

### List Files

List files in a Storage bucket, optionally filtering by path or prefix.
|Parameters|Description|example|
| --- | --- | --- |
|Bucket|Name of the Storage bucket.|my-bucket|
|Path/prefix (optional)|Optional path or prefix inside the bucket used to filter files.||
|Assign result to variable|Variable name to store the list of files found in the bucket. If there are no files, it stores an empty list [].|result|

### Upload File

Upload a local file to a Storage bucket, with optional object path and upsert.
|Parameters|Description|example|
| --- | --- | --- |
|Bucket|Name of the Storage bucket.|my-bucket|
|Local file|Local file path to upload to Supabase.|C:/Users/User/Desktop/file.png|
|Object path (optional)|Path of the object inside the Storage bucket.|folder/file.png|
|Upsert (optional)|When enabled, replaces the object if it already exists at the same path.||
|Assign result to variable|Variable name to store True when the file was uploaded successfully or False when it could not be uploaded.|result|

### Download File

Download a Storage object from a bucket into a selected local folder or file path.
|Parameters|Description|example|
| --- | --- | --- |
|Bucket|Name of the Storage bucket.|my-bucket|
|Object path|Path of the object inside the Storage bucket.|folder/file.png|
|Local destination folder|Local folder or path where the downloaded file will be saved.|C:/Users/User/Downloads|
|Assign result to variable|Variable name to store True when the file was downloaded successfully or False when it could not be downloaded.|result|

### Execute Postgres Function

Execute a Postgres RPC function in Supabase with optional JSON parameters.
|Parameters|Description|example|
| --- | --- | --- |
|Function name|Name of the RPC/Postgres function to execute in Supabase.|my_function|
|Params (JSON object)|Optional JSON object with the parameters passed to the function. Default {}.|{}|
|Get full API response|When enabled, returns the full function response. When disabled, returns only the message value when available.||
|Assign result to variable|Variable name to store the message value returned by the function. If Get full API response is enabled, it stores the full response.|result|

### Connect - Embedding Provider

Configure the embedding provider API key and return the available embedding models.
|Parameters|Description|example|
| --- | --- | --- |
|Provider|Embedding provider to configure for vector generation.||
|API Key|API key for the embedding provider.|...|
|Default embedding model (optional)|Default embedding model used when other commands do not provide one. Default text-embedding-3-small.|text-embedding-3-small|
|Assign result to variable|Variable name to store the result.|result|

### Generate And Store Embedding

Split text into chunks, generate embeddings, and insert the vectors into a table.
|Parameters|Description|example|
| --- | --- | --- |
|Embedding model|Model used to generate embeddings. Default text-embedding-3-small.|text-embedding-3-small|
|Table name|Name of the Supabase table used by this command.|documents|
|Input text|Source text that will be processed to generate embeddings.|text...|
|Chunk size (optional)|Optional maximum size of each text chunk. Default 1024.|1024|
|Chunk overlap (optional)|Optional number of characters shared between consecutive chunks. Default 128.|128|
|Embedding dim (optional)|Expected embedding vector dimension. It must match the model and vector column. Default 384.|384|
|Content column (optional)|Column where each chunk content will be stored. Default content.|content|
|Embedding column (optional)|Vector column where the generated embedding will be stored. Default embedding.|embedding|
|Metadata column (optional)|Column where metadata associated with each chunk will be stored. Default metadata.|metadata|
|Extra metadata (JSON object)|Optional JSON object with additional metadata to store with each chunk. Default {}.|{}|
|Assign result to variable|Variable name to store the result.|result|

### Retrieve Documents

Generate a query embedding and call a vector-search RPC to retrieve matching documents.
|Parameters|Description|example|
| --- | --- | --- |
|Embedding model|Model used to generate embeddings. Default text-embedding-3-small.|text-embedding-3-small|
|Function name|Name of the RPC/Postgres function to execute in Supabase. Default match_documents.|match_documents|
|Query text|Query text that will be converted into an embedding to search similar documents.|query...|
|Number of results|Maximum number of similar documents to return. Default 5.|5|
|Embedding dim (optional)|Expected embedding vector dimension. It must match the model and vector column. Default 384.|384|
|Filter (JSON object)|Optional JSON object with additional filters for the vector search. Default {}.|{}|
|Match threshold (optional)|Optional minimum similarity threshold for accepted results. Default 0.8.|0.8|
|Extra RPC params (JSON object)|Optional JSON object with extra parameters sent to the RPC function. Default {}.|{}|
|Get more details|When enabled, returns all retrieved information, including id, metadata, and similarity. When disabled, returns only each document content.||
|Assign result to variable|Variable name to store the list of retrieved contents. If Get more details is enabled, it stores all information returned by the search.|result|

### Trigger Supabase

Poll a table for rows with id greater than the last processed id.
|Parameters|Description|example|
| --- | --- | --- |
|Table|Table that will be queried to detect new rows.|public.users|
|Last id (optional)|Last processed id. The command returns rows with id greater than this value. Default 0.|0|
|Assign result to variable|Variable name to store the result.|result|
