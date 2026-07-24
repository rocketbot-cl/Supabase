# coding: utf-8
"""
Base para desarrollo de modulos externos.
Para obtener el modulo/Funcion que se esta llamando:
     GetParams("module")
 
Para obtener las variables enviadas desde formulario/comando Rocketbot:
    var = GetParams(variable)
    Las "variable" se define en forms del archivo package.json
 
Para modificar la variable de Rocketbot:
    SetVar(Variable_Rocketbot, "dato")
 
Para obtener una variable de Rocketbot:
    var = GetVar(Variable_Rocketbot)
 
Para obtener la Opcion seleccionada:
    opcion = GetParams("option")
 
 
Para instalar librerias se debe ingresar por terminal a la carpeta "libs"
 
    pip install <package> -t .
 
"""

import os
import sys

base_path = tmp_global_obj["basepath"]  # type: ignore
module_folder = "Supabase"
libs_path = base_path + "modules" + os.sep + module_folder + os.sep + "libs" + os.sep

if libs_path not in sys.path:
    sys.path.append(libs_path)

from SupabaseObject import SupabaseObject

module = GetParams("module")

global mod_Supabase

try:
    mod_Supabase  # type: ignore[name-defined]
except NameError:
    mod_Supabase = SupabaseObject()

def resolve_rb_value(v):
    """
    Resolve Rocketbot variable references passed as strings:
    - '{var_name}' -> GetVar('var_name')
    - 'var_name' (and GetVar(var_name) exists) -> GetVar('var_name')
    Otherwise returns the original value.
    """
    if v is None:
        return None
    if not isinstance(v, str):
        return v
    s = v.strip()
    if not s:
        return v
    if s.startswith("{") and s.endswith("}") and len(s) > 2:
        inner = s[1:-1].strip()
        if inner:
            try:
                got = GetVar(inner)
                if got is None:
                    return v
                if isinstance(got, str) and got.strip().upper() in ("ERROR_NOT_VAR", "NOT_VAR", "ERROR"):
                    return v
                return got
            except Exception:
                return v
    # Heuristic: allow plain variable names too, but guard Rocketbot sentinels.
    try:
        got = GetVar(s)
        if got is None:
            return v
        if isinstance(got, str) and got.strip().upper() in ("ERROR_NOT_VAR", "NOT_VAR", "ERROR"):
            return v
        return got
    except Exception:
        return v

if module == "connect":
    credential = GetParams("credential")
    # Rocketbot may pass variable references like "{project_url}" / "{api_key}".
    project_url = resolve_rb_value(GetParams("project_url"))
    api_key = resolve_rb_value(GetParams("api_key"))
    res = GetParams("result_var")

    try:
        connected = mod_Supabase.connect(project_url, api_key, credential)
        SetVar(res, bool(connected))
    except Exception as e:
        SetVar(res, False)
        PrintException()
        raise e

elif module == "get_table":
    table_name = GetParams("table_name")
    sort = GetParams("sort")
    res = GetParams("result_var")

    try:
        response = mod_Supabase.get_table_command(table_name, sort)
        if isinstance(response, dict) and isinstance(response.get("table"), list):
            response = response.get("table")
        SetVar(res, response)
    except Exception as e:
        SetVar(res, False)
        PrintException()
        raise e

elif module == "filter_table":
    table_name = GetParams("table_name")
    filter_column = GetParams("filter_column")
    filter_value = GetParams("filter_value")
    res = GetParams("result_var")

    try:
        response = mod_Supabase.filter_table_command(table_name, filter_column, filter_value)
        if isinstance(response, dict) and isinstance(response.get("table"), list):
            response = response.get("table")
        SetVar(res, response)
    except Exception as e:
        SetVar(res, False)
        PrintException()
        raise e

elif module == "insert_rows":
    table_name = GetParams("table_name")
    datatables = GetParams("datatables")
    res = GetParams("result_var")

    try:
        response = mod_Supabase.insert_rows_command(table_name, datatables)
        SetVar(res, response)
    except Exception as e:
        SetVar(res, False)
        PrintException()
        raise e

elif module == "get_table_columns":
    table_name = GetParams("table_name")
    return_as_list = GetParams("return_as_list")
    res = GetParams("result_var")

    try:
        response = mod_Supabase.get_table_columns_command(table_name, return_as_list)
        SetVar(res, response)
    except Exception as e:
        SetVar(res, False)
        PrintException()
        raise e

elif module == "update_rows":
    table_name = GetParams("table_name")
    column_name = GetParams("column_name")
    value = GetParams("value")
    filter_column = GetParams("filter_column")
    filter_value = GetParams("filter_value")
    res = GetParams("result_var")

    try:
        response = mod_Supabase.update_rows_command(
            table_name, column_name, value, filter_column, filter_value
        )
        SetVar(res, response)
    except Exception as e:
        SetVar(res, False)
        PrintException()
        raise e

elif module == "update_multiple_rows":
    table_name = GetParams("table_name")
    datatable = GetParams("datatable")
    where_clause = GetParams("where_clause")
    res = GetParams("result_var")

    try:
        response = mod_Supabase.update_multiple_rows_command(table_name, datatable, where_clause)
        SetVar(res, response)
    except Exception as e:
        SetVar(res, False)
        PrintException()
        raise e

elif module == "delete_rows":
    table_name = GetParams("table_name")
    filter_column = GetParams("filter_column")
    filter_value = GetParams("filter_value")
    res = GetParams("result_var")

    try:
        response = mod_Supabase.delete_rows_command(table_name, filter_column, filter_value)
        SetVar(res, response)
    except Exception as e:
        SetVar(res, False)
        PrintException()
        raise e

elif module == "list_buckets":
    res = GetParams("result_var")

    try:
        response = mod_Supabase.list_buckets_command()
        if isinstance(response, dict) and isinstance(response.get("bucketList"), list):
            response = [
                bucket.get("name") or bucket.get("id") if isinstance(bucket, dict) else bucket
                for bucket in response.get("bucketList")
            ]
        SetVar(res, response)
    except Exception as e:
        SetVar(res, False)
        PrintException()
        raise e

elif module == "create_bucket":
    bucket_name = GetParams("bucket_name")
    public = GetParams("public")
    file_size_limit = GetParams("file_size_limit")
    allowed_mime_types = GetParams("allowed_mime_types")
    res = GetParams("result_var")

    try:
        response = mod_Supabase.create_bucket_command(
            bucket_name, public, file_size_limit, allowed_mime_types
        )
        SetVar(res, bool(response))
    except Exception as e:
        SetVar(res, False)
        PrintException()
        raise e

elif module == "get_bucket":
    bucket_name = GetParams("bucket_name")
    include_files = GetParams("include_files")
    res = GetParams("result_var")

    try:
        response = mod_Supabase.get_bucket_command(bucket_name, include_files)
        SetVar(res, response)
    except Exception as e:
        SetVar(res, False)
        PrintException()
        raise e

elif module == "list_files":
    bucket = GetParams("bucket")
    path = GetParams("path")
    res = GetParams("result_var")

    try:
        response = mod_Supabase.list_files_command(bucket, path)
        if isinstance(response, dict) and isinstance(response.get("fileList"), list):
            response = response.get("fileList")
        SetVar(res, response)
    except Exception as e:
        SetVar(res, False)
        PrintException()
        raise e

elif module == "upload_file":
    bucket = GetParams("bucket")
    local_path = GetParams("local_path")
    object_path = GetParams("object_path")
    upsert = GetParams("upsert")
    res = GetParams("result_var")

    try:
        response = mod_Supabase.upload_file_command(bucket, local_path, object_path, upsert)
        SetVar(res, bool(response))
    except Exception as e:
        SetVar(res, False)
        PrintException()
        raise e

elif module == "download_file":
    bucket = GetParams("bucket")
    object_path = GetParams("object_path")
    local_dest = GetParams("local_dest")
    res = GetParams("result_var")

    try:
        response = mod_Supabase.download_file_command(bucket, object_path, local_dest)
        SetVar(res, bool(response))
    except Exception as e:
        SetVar(res, False)
        PrintException()
        raise e

elif module == "execute_postgres_function":
    function_name = GetParams("function_name")
    params_json = GetParams("params")
    include_api_response = GetParams("include_api_response")
    res = GetParams("result_var")

    try:
        response = mod_Supabase.execute_postgres_function_command(function_name, params_json)
        if str(include_api_response).lower() not in ("1", "true", "yes", "y"):
            if isinstance(response, dict):
                result = response.get("result")
                if isinstance(result, dict) and "message" in result:
                    response = result.get("message")
                elif "message" in response:
                    response = response.get("message")
        SetVar(res, response)
    except Exception as e:
        SetVar(res, False)
        PrintException()
        raise e

elif module == "generate_and_store_embedding":
    table_name = GetParams("table_name")
    input_text = GetParams("input")
    chunk_size = GetParams("chunk_size")
    chunk_overlap = GetParams("chunk_overlap")
    embedding_dim = GetParams("embedding_dim")
    embedding_model = GetParams("embedding_model")
    content_column = GetParams("content_column")
    embedding_column = GetParams("embedding_column")
    metadata_column = GetParams("metadata_column")
    extra_metadata = GetParams("extra_metadata")
    res = GetParams("result_var")

    try:
        response = mod_Supabase.generate_and_store_embedding_command(
            table_name,
            input_text,
            chunk_size,
            chunk_overlap,
            embedding_dim,
            embedding_model,
            content_column,
            embedding_column,
            metadata_column,
            extra_metadata,
        )
        SetVar(res, response)
    except Exception as e:
        SetVar(res, False)
        PrintException()
        raise e

elif module == "retrieve_documents":
    function_name = GetParams("function_name")
    query_value = GetParams("query_value")
    num_results = GetParams("num_results")
    embedding_dim = GetParams("embedding_dim")
    filter_json = GetParams("filter")
    embedding_model = GetParams("embedding_model")
    match_threshold = GetParams("match_threshold")
    rpc_params = GetParams("rpc_params")
    include_details = GetParams("include_details")
    res = GetParams("result_var")

    try:
        response = mod_Supabase.retrieve_documents_command(
            function_name,
            query_value,
            num_results,
            embedding_dim,
            filter_json,
            embedding_model,
            match_threshold,
            rpc_params,
        )
        if str(include_details).lower() not in ("1", "true", "yes", "y"):
            if isinstance(response, list):
                response = [item.get("content") if isinstance(item, dict) else item for item in response]
            elif isinstance(response, dict) and "content" in response:
                response = response.get("content")
        SetVar(res, response)
    except Exception as e:
        SetVar(res, False)
        PrintException()
        raise e

elif module == "embedding_connect":
    embedding_provider = GetParams("embedding_provider")
    embedding_api_key = GetParams("embedding_api_key")
    default_model = GetParams("default_model")
    res = GetParams("result_var")

    try:
        response = mod_Supabase.embedding_connect_command(embedding_provider, embedding_api_key, default_model)
        SetVar(res, response)
    except Exception as e:
        SetVar(res, False)
        PrintException()
        raise e

elif module == "trigger_supabase":
    table = GetParams("table")
    last_id = GetParams("last_id")
    res = GetParams("result_var")

    try:
        response = mod_Supabase.trigger_supabase_command(table, last_id)
        SetVar(res, response)
    except Exception as e:
        SetVar(res, False)
        PrintException()
        raise e

else:
    raise Exception(f"Module '{module}' is not implemented.")