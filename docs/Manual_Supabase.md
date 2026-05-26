



# Supabase

Supabase is an open-source Postgres-based platform for building backends with authentication, APIs, and storage. This module lets you connect and run operations from Rocketbot.

*Read this in other languages: [English](Manual_Supabase.md), [Português](Manual_Supabase.pr.md), [Español](Manual_Supabase.es.md)*

![banner](imgs/Banner_Supabase.png o jpg)
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
|Credential|||
|Project URL||https://<project-ref>.supabase.co|
|API Key||eyJhbGciOi...|
|Assign result to variable|Variable name to store the result|result|

### Get Table

Read rows from a Supabase table, with optional sorting by created_at.
|Parameters|Description|example|
| --- | --- | --- |
|Table name||public.users|
|Sort by created_at (optional)|||
|Assign result to variable|Variable name to store the result|result|

### Filter Table

Read rows from a table where one column matches the provided value.
|Parameters|Description|example|
| --- | --- | --- |
|Table name||public.users|
|Filter column||id|
|Filter value||1|
|Assign result to variable|Variable name to store the result|result|

### Get Table Columns

Build a blank JSON row template using the columns detected in a table.
|Parameters|Description|example|
| --- | --- | --- |
|Table name||public.users|
|Assign result to variable|Variable name to store the result|result|

### List Table Columns

Return the available column names for a table.
|Parameters|Description|example|
| --- | --- | --- |
|Table name||public.users|
|Assign result to variable|Variable name to store the result|result|

### Insert Rows

Insert one or more rows into a table from a JSON array.
|Parameters|Description|example|
| --- | --- | --- |
|Table name||public.users|
|Rows (JSON array)||[{"name":"Alfredo"}]|
|Assign result to variable|Variable name to store the result|result|

### Update Rows

Update one column in rows selected by an equality filter.
|Parameters|Description|example|
| --- | --- | --- |
|Table name||public.users|
|Column name||status|
|Value||active|
|Filter column||id|
|Filter value||1|
|Assign result to variable|Variable name to store the result|result|

### Update Multiple Rows

Update multiple rows from a JSON datatable, using id or a WHERE clause to match rows.
|Parameters|Description|example|
| --- | --- | --- |
|Table name||public.users|
|Datatable (JSON array)||[{"id":1,"name":"X"}]|
|WHERE clause (optional, JSON or col = 'value')||{"id":1}|
|Assign result to variable|Variable name to store the result|result|

### Delete Rows

Delete rows from a table where a column matches the provided value.
|Parameters|Description|example|
| --- | --- | --- |
|Table name||public.users|
|Filter column||id|
|Filter value (value or JSON array)||1|
|Assign result to variable|Variable name to store the result|result|

### List Buckets

List the Storage buckets available in the connected Supabase project.
|Parameters|Description|example|
| --- | --- | --- |
|Assign result to variable|Variable name to store the result|result|

### Create Bucket

Create a Storage bucket and optionally configure visibility, size limit, and MIME types.
|Parameters|Description|example|
| --- | --- | --- |
|Bucket name||my-bucket|
|Public|||
|File size limit (optional)||10000000|
|Allowed mime types (optional)||image/png,image/jpeg|
|Assign result to variable|Variable name to store the result|result|

### Get Bucket

Get bucket details and optionally include the files stored at the bucket root.
|Parameters|Description|example|
| --- | --- | --- |
|Bucket name||my-bucket|
|Include files|||
|Assign result to variable|Variable name to store the result|result|

### List Files

List files in a Storage bucket, optionally filtering by path or prefix.
|Parameters|Description|example|
| --- | --- | --- |
|Bucket||my-bucket|
|Path/prefix (optional)|||
|Assign result to variable|Variable name to store the result|result|

### Upload File

Upload a local file to a Storage bucket, with optional object path and upsert.
|Parameters|Description|example|
| --- | --- | --- |
|Bucket||my-bucket|
|Local file|Select the local file to upload|C:/Users/User/Desktop/file.png|
|Object path (optional)||folder/file.png|
|Upsert (optional)|||
|Assign result to variable|Variable name to store the result|result|

### Download File

Download a Storage object from a bucket into a selected local folder or file path.
|Parameters|Description|example|
| --- | --- | --- |
|Bucket||my-bucket|
|Object path||folder/file.png|
|Local destination folder|Select the local folder where the file will be downloaded|C:/Users/User/Downloads|
|Assign result to variable|Variable name to store the result|result|

### Execute Postgres Function

Execute a Postgres RPC function in Supabase with optional JSON parameters.
|Parameters|Description|example|
| --- | --- | --- |
|Function name||my_function|
|Params (JSON object)||{}|
|Assign result to variable|Variable name to store the result|result|

### Embeddings Connect

Configure the embedding provider API key and return the available embedding models.
|Parameters|Description|example|
| --- | --- | --- |
|Provider|||
|API Key||...|
|Default embedding model (optional)||text-embedding-3-small|
|Assign result to variable|Variable name to store the result|result|

### Generate And Store Embedding

Split text into chunks, generate embeddings, and insert the vectors into a table.
|Parameters|Description|example|
| --- | --- | --- |
|Embedding model||text-embedding-3-small|
|Table name||documents|
|Input text||text...|
|Chunk size (optional)||1024|
|Chunk overlap (optional)||128|
|Embedding dim (optional)||384|
|Content column (optional)||content|
|Embedding column (optional)||embedding|
|Metadata column (optional)||metadata|
|Extra metadata (JSON object)||{}|
|Assign result to variable|Variable name to store the result|result|

### Retrieve Documents

Generate a query embedding and call a vector-search RPC to retrieve matching documents.
|Parameters|Description|example|
| --- | --- | --- |
|Embedding model||text-embedding-3-small|
|Function name||match_documents|
|Query text||query...|
|Number of results||5|
|Embedding dim (optional)||384|
|Filter (JSON object)||{}|
|Match threshold (optional)||0.8|
|Extra RPC params (JSON object)||{}|
|Assign result to variable|Variable name to store the result|result|

### Trigger Supabase

Poll a table for rows with id greater than the last processed id.
|Parameters|Description|example|
| --- | --- | --- |
|Table||public.users|
|Last id (optional)||0|
|Assign result to variable|Variable name to store the result|result|
