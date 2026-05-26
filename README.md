



# Supabase

Supabase is an open-source Postgres-based platform for building backends with authentication, APIs, and storage. This module lets you connect and run operations from Rocketbot.

*Read this in other languages: [English](README.md), [Português](README.pr.md), [Español](README.es.md)*

## How to install this module

To install the module in Rocketbot Studio, it can be done in two ways:
1. Manual: __Download__ the .zip file and unzip it in the modules folder. The folder name must be the same as the module and inside it must have the following files and folders: \__init__.py, package.json, docs, example and libs. If you have the application open, refresh your browser to be able to use the new module.
2. Automatic: When entering Rocketbot Studio on the right margin you will find the **Addons** section, select **Install Mods**, search for the desired module and press install.


## Overview


1. Connect
Connect to a Supabase project and verify that the API key can access the project.

2. Get Table
Read rows from a Supabase table, with optional sorting by created_at.

3. Filter Table
Read rows from a table where one column matches the provided value.

4. Get Table Columns
Build a blank JSON row template using the columns detected in a table.

5. List Table Columns
Return the available column names for a table.

6. Insert Rows
Insert one or more rows into a table from a JSON array.

7. Update Rows
Update one column in rows selected by an equality filter.

8. Update Multiple Rows
Update multiple rows from a JSON datatable, using id or a WHERE clause to match rows.

9. Delete Rows
Delete rows from a table where a column matches the provided value.

10. List Buckets
List the Storage buckets available in the connected Supabase project.

11. Create Bucket
Create a Storage bucket and optionally configure visibility, size limit, and MIME types.

12. Get Bucket
Get bucket details and optionally include the files stored at the bucket root.

13. List Files
List files in a Storage bucket, optionally filtering by path or prefix.

14. Upload File
Upload a local file to a Storage bucket, with optional object path and upsert.

15. Download File
Download a Storage object from a bucket into a selected local folder or file path.

16. Execute Postgres Function
Execute a Postgres RPC function in Supabase with optional JSON parameters.

17. Embeddings Connect
Configure the embedding provider API key and return the available embedding models.

18. Generate And Store Embedding
Split text into chunks, generate embeddings, and insert the vectors into a table.

19. Retrieve Documents
Generate a query embedding and call a vector-search RPC to retrieve matching documents.

20. Trigger Supabase
Poll a table for rows with id greater than the last processed id.




----
### OS

- windows
- mac
- linux

### Dependencies

### License

![MIT](https://camo.githubusercontent.com/107590fac8cbd65071396bb4d04040f76cde5bde/687474703a2f2f696d672e736869656c64732e696f2f3a6c6963656e73652d6d69742d626c75652e7376673f7374796c653d666c61742d737175617265)
[MIT](http://opensource.org/licenses/mit-license.ph)