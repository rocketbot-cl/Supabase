from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import hashlib
import json
import ast
import math
import re

import requests


def parse_supabase_credential(credential: Any) -> tuple[str | None, str | None]:
    """
    Accepts multiple credential shapes, depending on how Rocketbot passes them:
    - JSON string with {"projectURL": "...", "apiKey": "..."}
    - JSON string with {"project_url": "...", "api_key": "..."} (snake_case)
    - dict with those fields
    """
    if not credential:
        return None, None

    obj: Any = credential
    if isinstance(credential, str):
        s = credential.strip()
        if not s:
            return None, None
        try:
            obj = json.loads(s)
        except Exception:
            try:
                obj = ast.literal_eval(s)
            except Exception:
                return None, None

    if not isinstance(obj, dict):
        return None, None

    project_url = obj.get("projectURL") or obj.get("project_url") or obj.get("url")
    api_key = obj.get("apiKey") or obj.get("api_key") or obj.get("key")
    return (str(project_url).strip() if project_url else None, str(api_key).strip() if api_key else None)

def looks_like_sqlstate(code: str) -> bool:
    # SQLSTATE is 5 chars, usually digits with some letters (e.g. 42P01, P0001).
    code = (code or "").strip()
    return len(code) == 5 and code.isalnum()


def postgrest_error_meta(code: str | None, *, status_code: int | None = None) -> dict[str, Any]:
    """
    Best-effort classification for PostgREST errors based on Supabase docs:
    https://supabase.com/docs/guides/api/rest/postgrest-error-codes
    """
    code = (code or "").strip() or None
    if not code:
        return {}

    # API-level errors (PGRST*)
    if code.startswith("PGRST"):
        pgrst_map: dict[str, tuple[str, str, bool]] = {
            "PGRST000": ("connection", "Could not connect with the database (bad connection string or Postgres not running).", True),
            "PGRST001": ("connection", "Could not connect with the database due to an internal error.", True),
            "PGRST002": ("connection", "Could not connect with the database when building the schema cache.", True),
            "PGRST003": ("timeout", "Timed out waiting for a connection from PostgREST's internal pool.", True),
            "PGRST100": ("bad_request", "Parsing error in the query string parameter.", False),
            "PGRST101": ("method_not_allowed", "Only GET and POST are allowed for database functions.", False),
            "PGRST102": ("bad_request", "Invalid request body (empty body or malformed JSON).", False),
            "PGRST103": ("range", "Invalid range was specified for limits.", False),
            "PGRST105": ("method_not_allowed", "Invalid UPDATE/UPSERT request.", False),
            "PGRST106": ("not_acceptable", "Requested schema is not exposed to the API.", False),
            "PGRST107": ("unsupported_media_type", "Invalid Content-Type header.", False),
            "PGRST108": ("bad_request", "Filter applied to an embedded resource not present in select.", False),
            "PGRST111": ("internal", "Invalid response.headers was set.", False),
            "PGRST112": ("internal", "Status code must be a positive integer.", False),
            "PGRST114": ("bad_request", "UPSERT using PUT can't be combined with limits/offsets.", False),
            "PGRST115": ("bad_request", "UPSERT using PUT has mismatched primary key between query and body.", False),
            "PGRST116": ("not_acceptable", "Singular response requested but did not return exactly one item.", False),
            "PGRST117": ("method_not_allowed", "HTTP verb is not supported.", False),
            "PGRST118": ("bad_request", "Cannot order via related table (no suitable relationship).", False),
            "PGRST120": ("bad_request", "Embedded resources can only be filtered with is.null/not.is.null.", False),
            "PGRST121": ("internal", "API can't parse JSON objects in RAISE PGRST error.", False),
            "PGRST122": ("bad_request", "Invalid Prefer header with Prefer: handling=strict.", False),
            "PGRST123": ("bad_request", "Aggregate functions are disabled.", False),
            "PGRST124": ("bad_request", "max-affected preference is violated.", False),
            "PGRST125": ("not_found", "Invalid path in request URL.", False),
            "PGRST126": ("not_found", "OpenAPI config is disabled but API root path is accessed.", False),
            "PGRST127": ("bad_request", "Requested feature is not implemented (see details).", False),
            "PGRST128": ("bad_request", "max-affected preference is violated on RPC call.", False),
            "PGRST200": ("schema_cache", "Stale FK relationships or embedded resource/relationship missing.", False),
            "PGRST201": ("schema_cache", "Ambiguous embedding request.", False),
            "PGRST202": ("schema_cache", "Stale function signature or function missing.", False),
            "PGRST203": ("schema_cache", "Overloaded function ambiguity; rename or adjust argument names.", False),
            "PGRST204": ("schema_cache", "Column specified in columns query parameter not found.", False),
            "PGRST205": ("schema_cache", "Table specified in the URI not found.", False),
            "PGRST300": ("auth", "PostgREST does not have an active JWT secret to validate requests.", False),
            "PGRST301": ("auth", "JWT couldn't be decoded or is invalid.", False),
            "PGRST302": ("auth", "Missing Auth: Bearer header while anonymous role is disabled.", False),
            "PGRST303": ("auth", "JWT claims validation or parsing failed.", False),
        }
        if code in pgrst_map:
            category, description, retryable = pgrst_map[code]
            return {"category": category, "description": description, "retryable": retryable}
        # Unknown PGRST; treat as bad_request by default.
        return {"category": "bad_request", "description": "PostgREST error.", "retryable": False}

    # Database-level errors (SQLSTATE)
    if looks_like_sqlstate(code):
        exact: dict[str, tuple[str, str, bool]] = {
            "23503": ("conflict", "Foreign key violation.", False),
            "23505": ("conflict", "Uniqueness violation.", False),
            "25006": ("method_not_allowed", "Read-only SQL transaction.", False),
            "53400": ("resource_limit", "Config limit exceeded.", False),
            "P0001": ("bad_request", "Default code for RAISE.", False),
            "42883": ("not_found", "Undefined function.", False),
            "42P01": ("not_found", "Undefined table.", False),
            "42P17": ("internal", "Infinite recursion.", False),
            "42501": ("auth", "Insufficient privileges." if status_code in (401, 403) else "Insufficient privileges (SQLSTATE 42501).", False),
        }
        if code in exact:
            category, description, retryable = exact[code]
            return {"category": category, "description": description, "retryable": retryable}
        prefixes: list[tuple[str, str, str, bool]] = [
            ("08", "connection", "Connection error.", True),
            ("40", "internal", "Transaction rollback.", True),
            ("53", "resource_limit", "Insufficient resources.", True),
            ("57", "internal", "Operator intervention.", True),
            ("58", "internal", "System error.", True),
            ("XX", "internal", "Internal error.", False),
        ]
        for pref, category, description, retryable in prefixes:
            if code.startswith(pref):
                return {"category": category, "description": description, "retryable": retryable}
        return {"category": "db", "description": "Database error (SQLSTATE).", "retryable": False}

    return {}


@dataclass(frozen=True)
class SupabaseApiError(Exception):
    service: str
    status_code: int
    url: str
    context: dict[str, Any]
    code: str | None = None
    message: str | None = None
    hint: str | None = None
    details: Any | None = None
    raw_body: str | None = None
    category: str | None = None
    description: str | None = None
    retryable: bool | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "service": self.service,
            "status_code": self.status_code,
            "url": self.url,
            "context": self.context,
            "code": self.code,
            "message": self.message,
            "hint": self.hint,
            "details": self.details,
            "raw_body": self.raw_body,
            "category": self.category,
            "description": self.description,
            "retryable": self.retryable,
        }

    def __str__(self) -> str:
        parts: list[str] = [f"{self.service} request failed ({self.status_code})"]
        if self.code:
            parts.append(f"code={self.code}")
        if self.category:
            parts.append(f"category={self.category}")
        if self.description:
            parts.append(f"description={self.description}")
        if self.retryable is True:
            parts.append("retryable=true")
        elif self.retryable is False:
            parts.append("retryable=false")
        if self.message:
            parts.append(f"message={self.message}")
        if self.hint:
            parts.append(f"hint={self.hint}")
        parts.append(f"url={self.url}")
        if self.context:
            parts.append(f"context={self.context}")
        return " ".join(parts)


@dataclass(frozen=True)
class SupabaseConfig:
    project_url: str
    api_key: str


def normalize_url(url: str) -> str:
    url = (url or "").strip()
    if not url:
        return url
    return url[:-1] if url.endswith("/") else url


def detect_key_type(api_key: str) -> str:
    s = (api_key or "").strip()
    if not s:
        return "unknown"
    if s.startswith("sb_publishable_"):
        return "sb_publishable"
    if s.startswith("sb_secret_"):
        return "sb_secret"
    if s.startswith("eyJ"):
        return "jwt"
    return "unknown"


def build_headers(api_key: str) -> dict[str, str]:
    api_key = (api_key or "").strip()
    headers = {"apikey": api_key, "Content-Type": "application/json"}
    if detect_key_type(api_key) == "jwt":
        headers["Authorization"] = f"Bearer {api_key}"
    return headers


def supabase_http_error(service: str, resp: requests.Response, url: str, context: dict[str, Any]) -> SupabaseApiError:
    ct = (resp.headers.get("content-type") or "").lower()
    payload: dict[str, Any] | None = None
    if "application/json" in ct:
        try:
            payload = resp.json()
        except Exception:
            payload = None

    if isinstance(payload, dict):
        code = payload.get("code")
        msg = payload.get("message") or ""
        hint = payload.get("hint") or ""
        det = payload.get("details")

        meta: dict[str, Any] = {}
        if service == "postgrest":
            meta = postgrest_error_meta(str(code) if code else None, status_code=resp.status_code)

        if not hint and resp.status_code in (401, 403):
            hint = "Check your API key type and permissions (RLS policies can also cause 401/403)."

        return SupabaseApiError(
            service=service,
            status_code=resp.status_code,
            url=url,
            context=context,
            code=str(code) if code else None,
            message=str(msg) if msg else None,
            hint=str(hint) if hint else None,
            details=det,
            raw_body=None,
            category=meta.get("category"),
            description=meta.get("description"),
            retryable=meta.get("retryable"),
        )

    hint = None
    if resp.status_code in (401, 403):
        hint = "Check your API key type and permissions (RLS policies can also cause 401/403)."
    return SupabaseApiError(
        service=service,
        status_code=resp.status_code,
        url=url,
        context=context,
        raw_body=resp.text,
        hint=hint,
    )


def healthcheck(cfg: SupabaseConfig, timeout_s: int = 20) -> dict[str, Any]:
    url = f"{normalize_url(cfg.project_url)}/auth/v1/health"
    r = requests.get(url, headers=build_headers(cfg.api_key), timeout=timeout_s)
    if r.status_code >= 400:
        raise supabase_http_error("auth", r, url, context={})
    return r.json() if r.headers.get("content-type", "").startswith("application/json") else {"raw": r.text}


def data_api_probe(cfg: SupabaseConfig, timeout_s: int = 20) -> dict[str, Any]:
    url = f"{normalize_url(cfg.project_url)}/rest/v1/"
    r = requests.get(url, headers=build_headers(cfg.api_key), timeout=timeout_s)
    ct = (r.headers.get("content-type") or "").lower()
    body: Any
    if "application/json" in ct:
        try:
            body = r.json()
        except Exception:
            text = (r.text or "").lstrip("\ufeff").strip()
            try:
                body = json.loads(text)
            except Exception:
                body = None
    else:
        text = (r.text or "").lstrip("\ufeff").strip()
        try:
            body = json.loads(text)
        except Exception:
            body = None

    summary: dict[str, Any] = {"status_code": r.status_code, "ok": 200 <= int(r.status_code) < 400, "content_type": ct or None}

    if isinstance(body, dict):
        info = body.get("info") if isinstance(body.get("info"), dict) else {}
        summary["schema_title"] = info.get("title")
        summary["schema_version"] = info.get("version")

        paths = body.get("paths")
        if isinstance(paths, dict):
            table_names: list[str] = []
            for p in paths.keys():
                if not isinstance(p, str):
                    continue
                if p == "/" or not p.startswith("/"):
                    continue
                name = p[1:].strip()
                if not name:
                    continue
                table_names.append(name)
            table_names = sorted(set(table_names))
            summary["tables_count"] = len(table_names)
            summary["tables_sample"] = table_names[:25]

    return summary


def select_table(
    cfg: SupabaseConfig,
    table: str,
    *,
    filter_column: str | None = None,
    filter_value: Any | None = None,
    filters: list[tuple[str, str, Any]] | None = None,
    order_by: str | None = None,
    ascending: bool = False,
    limit: int | None = None,
    timeout_s: int = 30,
) -> list[dict[str, Any]]:
    base = normalize_url(cfg.project_url)
    table = (table or "").strip()
    if not table:
        raise ValueError("table_name is required")

    params: dict[str, Any] = {"select": "*"}

    if filter_column and filter_value is not None:
        params[filter_column] = f"eq.{filter_value}"

    if filters:
        for col, op, val in filters:
            col = (col or "").strip()
            op = (op or "").strip()
            if not col or not op:
                continue
            if op == "in" and isinstance(val, (list, tuple)):
                joined = ",".join(str(v) for v in val)
                params[col] = f"in.({joined})"
            else:
                params[col] = f"{op}.{val}"

    if order_by:
        direction = "asc" if ascending else "desc"
        params["order"] = f"{order_by}.{direction}"

    if limit is not None:
        params["limit"] = str(int(limit))

    url = f"{base}/rest/v1/{table}"
    r = requests.get(url, headers=build_headers(cfg.api_key), params=params, timeout=timeout_s)
    if r.status_code >= 400:
        raise supabase_http_error("postgrest", r, url, context={"params": params})
    data = r.json()
    if not isinstance(data, list):
        raise RuntimeError(f"Unexpected response (expected list): {data!r}")
    return data


def insert_rows(
    cfg: SupabaseConfig,
    table: str,
    rows: list[dict[str, Any]],
    *,
    return_rows: bool = True,
    timeout_s: int = 30,
) -> list[dict[str, Any]]:
    base = normalize_url(cfg.project_url)
    table = (table or "").strip()
    if not table:
        raise ValueError("table_name is required")
    if not isinstance(rows, list) or not rows:
        raise ValueError("rows must be a non-empty list of objects")

    url = f"{base}/rest/v1/{table}"
    headers = build_headers(cfg.api_key)
    if return_rows:
        headers["Prefer"] = "return=representation"

    r = requests.post(url, headers=headers, json=rows, timeout=timeout_s)
    if r.status_code >= 400:
        raise supabase_http_error("postgrest", r, url, context={"rows_count": len(rows)})
    data = r.json()
    if not isinstance(data, list):
        raise RuntimeError(f"Unexpected response (expected list): {data!r}")
    return data


def update_rows(
    cfg: SupabaseConfig,
    table: str,
    update_data: dict[str, Any],
    *,
    where: dict[str, Any] | None = None,
    timeout_s: int = 30,
) -> list[dict[str, Any]]:
    base = normalize_url(cfg.project_url)
    table = (table or "").strip()
    if not table:
        raise ValueError("table_name is required")
    if not isinstance(update_data, dict) or not update_data:
        raise ValueError("update_data must be a non-empty object")

    params: dict[str, Any] = {}
    if where:
        for k, v in where.items():
            params[k] = f"eq.{v}"

    url = f"{base}/rest/v1/{table}"
    headers = build_headers(cfg.api_key)
    headers["Prefer"] = "return=representation"

    r = requests.patch(url, headers=headers, params=params, json=update_data, timeout=timeout_s)
    if r.status_code >= 400:
        raise supabase_http_error(
            "postgrest",
            r,
            url,
            context={"where": where or {}, "update_keys": list(update_data.keys()), "params": params},
        )
    data = r.json()
    if not isinstance(data, list):
        raise RuntimeError(f"Unexpected response (expected list): {data!r}")
    return data


def delete_rows(
    cfg: SupabaseConfig,
    table: str,
    *,
    where: dict[str, Any] | None = None,
    where_in: tuple[str, list[Any]] | None = None,
    timeout_s: int = 30,
) -> list[dict[str, Any]]:
    base = normalize_url(cfg.project_url)
    table = (table or "").strip()
    if not table:
        raise ValueError("table_name is required")

    params: dict[str, Any] = {}
    if where:
        for k, v in where.items():
            params[k] = f"eq.{v}"
    if where_in:
        col, values = where_in
        joined = ",".join(str(v) for v in values)
        params[col] = f"in.({joined})"

    url = f"{base}/rest/v1/{table}"
    headers = build_headers(cfg.api_key)
    headers["Prefer"] = "return=representation"

    r = requests.delete(url, headers=headers, params=params, timeout=timeout_s)
    if r.status_code >= 400:
        raise supabase_http_error("postgrest", r, url, context={"where": where or {}, "where_in": where_in, "params": params})
    data = r.json()
    if not isinstance(data, list):
        raise RuntimeError(f"Unexpected response (expected list): {data!r}")
    return data


def rpc(
    cfg: SupabaseConfig,
    function_name: str,
    params: dict[str, Any] | None = None,
    *,
    timeout_s: int = 30,
) -> Any:
    base = normalize_url(cfg.project_url)
    function_name = (function_name or "").strip()
    if not function_name:
        raise ValueError("function_name is required")

    url = f"{base}/rest/v1/rpc/{function_name}"
    r = requests.post(url, headers=build_headers(cfg.api_key), json=(params or {}), timeout=timeout_s)
    if r.status_code >= 400:
        raise supabase_http_error("postgrest", r, url, context={"params_keys": list((params or {}).keys())})
    ct = (r.headers.get("content-type") or "").lower()
    return r.json() if "application/json" in ct else r.text


def list_buckets(cfg: SupabaseConfig, *, timeout_s: int = 30) -> list[dict[str, Any]]:
    url = f"{normalize_url(cfg.project_url)}/storage/v1/bucket"
    r = requests.get(url, headers=build_headers(cfg.api_key), timeout=timeout_s)
    if r.status_code >= 400:
        raise supabase_http_error("storage", r, url, context={})
    data = r.json()
    if not isinstance(data, list):
        raise RuntimeError(f"Unexpected response (expected list): {data!r}")
    return data


def get_bucket(cfg: SupabaseConfig, bucket_name: str, *, timeout_s: int = 30) -> dict[str, Any]:
    bucket_name = (bucket_name or "").strip()
    if not bucket_name:
        raise ValueError("bucket_name is required")
    url = f"{normalize_url(cfg.project_url)}/storage/v1/bucket/{bucket_name}"
    r = requests.get(url, headers=build_headers(cfg.api_key), timeout=timeout_s)
    if r.status_code >= 400:
        raise supabase_http_error("storage", r, url, context={"bucket": bucket_name})
    data = r.json()
    if not isinstance(data, dict):
        raise RuntimeError(f"Unexpected response (expected object): {data!r}")
    return data


def create_bucket(
    cfg: SupabaseConfig,
    bucket_name: str,
    *,
    public: bool = False,
    file_size_limit: int | None = None,
    allowed_mime_types: list[str] | None = None,
    timeout_s: int = 30,
) -> dict[str, Any]:
    bucket_name = (bucket_name or "").strip()
    if not bucket_name:
        raise ValueError("bucket_name is required")
    url = f"{normalize_url(cfg.project_url)}/storage/v1/bucket"
    payload: dict[str, Any] = {"id": bucket_name, "name": bucket_name, "public": bool(public)}
    if file_size_limit is not None:
        payload["fileSizeLimit"] = int(file_size_limit)
    if allowed_mime_types:
        payload["allowedMimeTypes"] = allowed_mime_types

    r = requests.post(url, headers=build_headers(cfg.api_key), json=payload, timeout=timeout_s)
    if r.status_code >= 400:
        raise supabase_http_error("storage", r, url, context={"bucket": bucket_name})
    data = r.json()
    if not isinstance(data, dict):
        raise RuntimeError(f"Unexpected response (expected object): {data!r}")
    return data


def list_files(
    cfg: SupabaseConfig,
    bucket_name: str,
    *,
    path: str = "",
    limit: int = 1000,
    offset: int = 0,
    timeout_s: int = 30,
) -> list[dict[str, Any]]:
    bucket_name = (bucket_name or "").strip()
    if not bucket_name:
        raise ValueError("bucket is required")
    url = f"{normalize_url(cfg.project_url)}/storage/v1/object/list/{bucket_name}"
    payload = {"prefix": path or "", "limit": int(limit), "offset": int(offset), "sortBy": {"column": "name", "order": "asc"}}
    r = requests.post(url, headers=build_headers(cfg.api_key), json=payload, timeout=timeout_s)
    if r.status_code >= 400:
        raise supabase_http_error("storage", r, url, context={"bucket": bucket_name, "path": path})
    data = r.json()
    if not isinstance(data, list):
        raise RuntimeError(f"Unexpected response (expected list): {data!r}")
    return data


def upload_file(
    cfg: SupabaseConfig,
    bucket_name: str,
    object_path: str,
    content: bytes,
    *,
    content_type: str = "application/octet-stream",
    upsert: bool = False,
    timeout_s: int = 60,
) -> dict[str, Any]:
    bucket_name = (bucket_name or "").strip()
    object_path = (object_path or "").lstrip("/")
    if not bucket_name or not object_path:
        raise ValueError("bucket and object_path are required")
    url = f"{normalize_url(cfg.project_url)}/storage/v1/object/{bucket_name}/{object_path}"
    headers = build_headers(cfg.api_key)
    headers["Content-Type"] = content_type
    headers["x-upsert"] = "true" if upsert else "false"
    r = requests.post(url, headers=headers, data=content, timeout=timeout_s)
    if r.status_code >= 400:
        raise supabase_http_error("storage", r, url, context={"bucket": bucket_name, "object_path": object_path})
    data = r.json()
    if not isinstance(data, dict):
        raise RuntimeError(f"Unexpected response (expected object): {data!r}")
    return data


def download_file(
    cfg: SupabaseConfig,
    bucket_name: str,
    object_path: str,
    *,
    timeout_s: int = 60,
) -> bytes:
    bucket_name = (bucket_name or "").strip()
    object_path = (object_path or "").lstrip("/")
    if not bucket_name or not object_path:
        raise ValueError("bucket and object_path are required")
    url = f"{normalize_url(cfg.project_url)}/storage/v1/object/{bucket_name}/{object_path}"
    r = requests.get(url, headers=build_headers(cfg.api_key), timeout=timeout_s)
    if r.status_code >= 400:
        raise supabase_http_error("storage", r, url, context={"bucket": bucket_name, "object_path": object_path})
    return r.content


def parse_where_clause(clause: str | dict[str, Any] | None) -> dict[str, Any]:
    if not clause:
        return {}
    if isinstance(clause, dict):
        return dict(clause)
    if not isinstance(clause, str):
        raise ValueError("Invalid WHERE clause type")
    s = clause.strip()
    if not s:
        return {}
    try:
        obj = json.loads(s)
        if isinstance(obj, dict):
            return obj
    except Exception:
        pass
    m = re.match(r"^(\\w+)\\s*=\\s*'?([^']*)'?\\s*$", s)
    if not m:
        raise ValueError("Invalid WHERE clause format. Use {\"column\": \"value\"} or column = 'value'")
    return {m.group(1): m.group(2)}


def split_text(text: str, chunk_size: int = 1024, chunk_overlap: int = 128) -> list[str]:
    text = text or ""
    if chunk_size <= 0:
        raise ValueError("chunk_size must be > 0")
    if chunk_overlap < 0:
        chunk_overlap = 0
    if chunk_overlap >= chunk_size:
        chunk_overlap = max(0, chunk_size // 4)
    chunks: list[str] = []
    i = 0
    n = len(text)
    while i < n:
        end = min(n, i + chunk_size)
        chunks.append(text[i:end])
        if end == n:
            break
        i = max(0, end - chunk_overlap)
    return chunks


def hash_embedding(text: str, dim: int = 384) -> list[float]:
    if dim <= 0:
        raise ValueError("dim must be > 0")
    out: list[float] = []
    seed = hashlib.sha256(text.encode("utf-8")).digest()
    counter = 0
    while len(out) < dim:
        h = hashlib.sha256(seed + counter.to_bytes(4, "big")).digest()
        for b in h:
            if len(out) >= dim:
                break
            out.append((b / 127.5) - 1.0)
        counter += 1
    norm = math.sqrt(sum(v * v for v in out)) or 1.0
    return [v / norm for v in out]


def parse_json_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except Exception:
        return default


def parse_json_object(value: Any, default: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    Accept a dict or a JSON string payload. Returns a dict.
    """
    if default is None:
        default = {}
    if value is None:
        return dict(default)
    if isinstance(value, dict):
        return dict(value)
    s = str(value).strip()
    if not s:
        return dict(default)
    try:
        obj = json.loads(s)
    except Exception:
        raise ValueError("Invalid JSON object")
    if not isinstance(obj, dict):
        raise ValueError("JSON must be an object")
    return obj


def openai_embed_texts(*, api_key: str, model: str, texts: list[str], timeout_s: int = 60) -> list[list[float]]:
    """
    Calls OpenAI Embeddings REST API.
    Returns a list of embedding vectors in the same order as input texts.
    """
    api_key = (api_key or "").strip()
    if not api_key:
        raise ValueError("OpenAI API key is required")
    model = (model or "").strip()
    if not model:
        raise ValueError("OpenAI embedding model is required")
    if not texts:
        return []

    url = "https://api.openai.com/v1/embeddings"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"model": model, "input": texts}
    r = requests.post(url, headers=headers, json=payload, timeout=timeout_s)
    if r.status_code >= 400:
        try:
            err = r.json().get("error", {})
            msg = err.get("message") or r.text
        except Exception:
            msg = r.text
        raise Exception(f"OpenAI embeddings request failed ({r.status_code}): {msg}")

    data = r.json().get("data")
    if not isinstance(data, list):
        raise Exception("OpenAI embeddings response missing data[]")

    out: list[list[float]] = []
    for item in data:
        emb = item.get("embedding") if isinstance(item, dict) else None
        if not isinstance(emb, list) or not emb:
            raise Exception("OpenAI embeddings response missing embedding vector")
        out.append([float(x) for x in emb])
    return out


def gemini_embed_texts(*, api_key: str, model: str, texts: list[str], timeout_s: int = 60) -> list[list[float]]:
    """
    Calls Gemini (Google Generative Language) embedContent/batchEmbedContents via REST.
    Returns a list of embedding vectors in the same order as input texts.
    """
    api_key = (api_key or "").strip()
    if not api_key:
        raise ValueError("Gemini API key is required")
    model = (model or "").strip()
    if not model:
        raise ValueError("Gemini embedding model is required")
    if not texts:
        return []

    # Normalize model resource name.
    model_resource = model if model.startswith("models/") else f"models/{model}"
    model_path = model_resource  # used in URL

    # Prefer batch endpoint to reduce roundtrips.
    url = f"https://generativelanguage.googleapis.com/v1beta/{model_path}:batchEmbedContents?key={api_key}"
    payload = {
        "requests": [
            {
                "model": model_resource,
                "content": {"parts": [{"text": t}]},
                "taskType": "RETRIEVAL_DOCUMENT",
            }
            for t in texts
        ]
    }

    r = requests.post(url, json=payload, timeout=timeout_s)
    if r.status_code >= 400:
        # Gemini errors are generally JSON with {error:{message,...}}
        try:
            msg = r.json().get("error", {}).get("message") or r.text
        except Exception:
            msg = r.text
        raise Exception(f"Gemini embeddings request failed ({r.status_code}): {msg}")

    resp = r.json()
    embeddings = resp.get("embeddings")
    if not isinstance(embeddings, list):
        raise Exception("Gemini embeddings response missing embeddings[]")

    out: list[list[float]] = []
    for item in embeddings:
        # Gemini responses vary a bit across endpoints/versions:
        # - batchEmbedContents: {"embeddings":[{"values":[...]}]}
        # - (sometimes)        {"embeddings":[{"embedding":{"values":[...]}}]}
        if not isinstance(item, dict):
            raise Exception("Gemini embeddings response contains an invalid embeddings[] item")

        values = item.get("values")
        if not isinstance(values, list) or not values:
            emb_obj = item.get("embedding")
            if isinstance(emb_obj, dict):
                values = emb_obj.get("values")

        if not isinstance(values, list) or not values:
            keys = ",".join(sorted(item.keys()))
            raise Exception(f"Gemini embeddings response missing embedding vector (expected values[]). Got keys=[{keys}]")
        out.append([float(x) for x in values])
    return out


def mean_pool_token_embeddings(token_embs: list[list[float]]) -> list[float]:
    if not token_embs:
        raise ValueError("Empty token embeddings")
    dim = len(token_embs[0])
    if dim <= 0:
        raise ValueError("Invalid token embedding dimension")
    acc = [0.0] * dim
    count = 0
    for row in token_embs:
        if not isinstance(row, list) or len(row) != dim:
            raise ValueError("Inconsistent token embedding row")
        for i, v in enumerate(row):
            acc[i] += float(v)
        count += 1
    return [v / max(1, count) for v in acc]

def openai_list_models(*, api_key: str, timeout_s: int = 30) -> list[str]:
    api_key = (api_key or "").strip()
    if not api_key:
        raise ValueError("OpenAI API key is required")
    url = "https://api.openai.com/v1/models"
    headers = {"Authorization": f"Bearer {api_key}"}
    r = requests.get(url, headers=headers, timeout=timeout_s)
    if r.status_code >= 400:
        try:
            err = r.json().get("error", {})
            msg = err.get("message") or r.text
        except Exception:
            msg = r.text
        raise Exception(f"OpenAI models request failed ({r.status_code}): {msg}")
    data = r.json().get("data")
    if not isinstance(data, list):
        raise Exception("OpenAI models response missing data[]")
    ids: list[str] = []
    for item in data:
        if isinstance(item, dict):
            mid = item.get("id")
            if isinstance(mid, str) and mid.strip():
                ids.append(mid.strip())
    # Heuristic: show likely embedding models first.
    ids_sorted = sorted(ids)
    emb = [m for m in ids_sorted if "embedding" in m]
    other = [m for m in ids_sorted if m not in emb]
    return emb + other


def gemini_list_models(*, api_key: str, timeout_s: int = 30) -> list[str]:
    api_key = (api_key or "").strip()
    if not api_key:
        raise ValueError("Gemini API key is required")
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    r = requests.get(url, timeout=timeout_s)
    if r.status_code >= 400:
        try:
            msg = r.json().get("error", {}).get("message") or r.text
        except Exception:
            msg = r.text
        raise Exception(f"Gemini models request failed ({r.status_code}): {msg}")
    resp = r.json()
    models = resp.get("models")
    if not isinstance(models, list):
        raise Exception("Gemini models response missing models[]")
    names: list[str] = []
    for m in models:
        if isinstance(m, dict):
            name = m.get("name")
            if isinstance(name, str) and name.strip():
                # name is usually like "models/text-embedding-004"
                names.append(name.strip().replace("models/", "", 1))
    names_sorted = sorted(set(names))
    emb = [n for n in names_sorted if "embedding" in n]
    other = [n for n in names_sorted if n not in emb]
    return emb + other


def list_embedding_models(provider: str, api_key: str) -> dict[str, Any]:
    p = (provider or "").strip().lower()
    if p not in ("openai", "gemini", "huggingface", "cohere"):
        raise Exception("embedding_provider must be one of: openai, gemini, huggingface, cohere")
    if p == "openai":
        models = openai_list_models(api_key=api_key)
        # Filter down to embedding-ish ids to avoid overwhelming RocketBot UI.
        emb_only = [m for m in models if "embedding" in m]
        return {"provider": p, "models": emb_only or models}
    if p == "gemini":
        models = gemini_list_models(api_key=api_key)
        emb_only = [m for m in models if "embedding" in m]
        return {"provider": p, "models": emb_only or models}
    if p == "cohere":
        # Cohere doesn't always expose a simple list-models endpoint for all plans.
        # Provide a small known-good set; user can still type any model id manually.
        return {"provider": p, "models": ["embed-english-v3.0", "embed-multilingual-v3.0", "embed-english-light-v3.0"]}
    # huggingface
    return {
        "provider": p,
        "models": [],
        "note": "HuggingFace model discovery isn't supported here. Use any Hub model id compatible with feature-extraction, e.g. 'sentence-transformers/all-MiniLM-L6-v2'.",
    }


def huggingface_embed_texts(*, api_key: str, model: str, texts: list[str], timeout_s: int = 120) -> list[list[float]]:
    """
    Calls HuggingFace Inference API feature-extraction pipeline.
    Returns one sentence embedding per text by mean-pooling token embeddings.

    Typical model: Supabase/gte-small (384 dims)
    """
    api_key = (api_key or "").strip()
    if not api_key:
        raise ValueError("HuggingFace API key is required")
    model = (model or "").strip()
    if not model:
        raise ValueError("HuggingFace model is required")
    if not texts:
        return []

    url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{model}"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    out: list[list[float]] = []
    for t in texts:
        payload = {"inputs": t}
        r = requests.post(url, headers=headers, json=payload, timeout=timeout_s)
        if r.status_code >= 400:
            try:
                msg = r.json().get("error") or r.text
            except Exception:
                msg = r.text
            raise Exception(f"HuggingFace embeddings request failed ({r.status_code}): {msg}")
        data = r.json()
        # Expected shape: [tokens][dim]
        if not isinstance(data, list) or not data:
            raise Exception("HuggingFace embeddings response missing token embeddings")
        if not isinstance(data[0], list):
            raise Exception("HuggingFace embeddings response has unexpected shape")
        sent = mean_pool_token_embeddings(data)  # type: ignore[arg-type]
        out.append(sent)
    return out


def cohere_embed_texts(
    *,
    api_key: str,
    model: str,
    texts: list[str],
    input_type: str = "search_document",
    timeout_s: int = 60,
) -> list[list[float]]:
    """
    Calls Cohere Embed API.
    """
    api_key = (api_key or "").strip()
    if not api_key:
        raise ValueError("Cohere API key is required")
    model = (model or "").strip()
    if not model:
        raise ValueError("Cohere embedding model is required")
    if not texts:
        return []

    url = "https://api.cohere.com/v1/embed"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"model": model, "texts": texts, "input_type": input_type}
    r = requests.post(url, headers=headers, json=payload, timeout=timeout_s)
    if r.status_code >= 400:
        try:
            msg = r.json().get("message") or r.text
        except Exception:
            msg = r.text
        raise Exception(f"Cohere embeddings request failed ({r.status_code}): {msg}")
    resp = r.json()
    embs = resp.get("embeddings")
    if not isinstance(embs, list) or not embs:
        raise Exception("Cohere embeddings response missing embeddings[]")
    out: list[list[float]] = []
    for emb in embs:
        if not isinstance(emb, list) or not emb:
            raise Exception("Cohere embeddings response contains an invalid embedding vector")
        out.append([float(x) for x in emb])
    return out


@dataclass
class SupabaseSession:
    project_url: str
    api_key: str

    def to_config(self) -> SupabaseConfig:
        return SupabaseConfig(project_url=self.project_url, api_key=self.api_key)


class SupabaseObject:
    """
    Facade/service client for Supabase operations used by Rocketbot commands.
    Holds an in-memory session set by connect().
    """

    def __init__(self) -> None:
        self.session: SupabaseSession | None = None
        self.last_connect_info: dict[str, Any] | None = None
        # In-memory embedding provider session, set via embedding_connect_command().
        # This is separate from Supabase session and only used to avoid repeating API key/model in RocketBot flows.
        # Shape: {"provider": "...", "api_key": "...", "default_model": "...?"}
        self.embedding_session: dict[str, Any] | None = None

    def connect(self, project_url: Any, api_key: Any, credential: Any = None) -> bool:
        """
        Validates credentials and stores a session in memory.
        Returns only True/False for Rocketbot command output.
        Detailed diagnostic data remains available internally in last_connect_info.
        """
        project_url_s = (str(project_url).strip() if project_url is not None else "") or ""
        api_key_s = (str(api_key).strip() if api_key is not None else "") or ""

        if not project_url_s or not api_key_s:
            c_url, c_key = parse_supabase_credential(credential)
            project_url_s = project_url_s or (c_url or "")
            api_key_s = api_key_s or (c_key or "")

        if not project_url_s or not api_key_s:
            raise ValueError("Missing Supabase credentials. Provide project_url + api_key or a valid credential payload.")

        if not (project_url_s.startswith("https://") or project_url_s.startswith("http://")):
            raise ValueError("Invalid project_url. It must start with https://<project-ref>.supabase.co")

        cfg = SupabaseConfig(project_url=project_url_s.rstrip("/"), api_key=api_key_s)
        key_type = detect_key_type(api_key_s)
        warnings: list[str] = []
        if key_type in ("sb_secret",):
            warnings.append("High-privilege key detected (sb_secret). Use only in controlled environments.")

        health: dict[str, Any] | None = None
        probe: dict[str, Any] | None = None
        connected = False

        try:
            health = healthcheck(cfg)
            probe = data_api_probe(cfg)
            connected = bool(probe and probe.get("status_code") == 200 and probe.get("ok") is True)
        except Exception as exc:
            probe = {"ok": False, "error": str(exc)}
            connected = False

        if connected:
            self.session = SupabaseSession(project_url=cfg.project_url, api_key=api_key_s)
        else:
            self.session = None

        self.last_connect_info = {
            "connected": connected,
            "key_type": key_type,
            "warnings": warnings,
            "auth_health": health,
            "data_api_probe": probe,
        }
        return connected

    def require_session(self) -> SupabaseConfig:
        if not self.session:
            raise Exception("Missing Supabase session. Run the 'Connect' command once before calling other commands.")
        return self.session.to_config()

    def connect_command(self, project_url: Any, api_key: Any, credential: Any = None) -> bool:
        return self.connect(project_url, api_key, credential)

    def get_table_command(self, table_name: Any, sort: Any) -> dict[str, Any]:
        try:
            name = (str(table_name or "").strip())
            if not name:
                raise Exception("table_name is required")
            if isinstance(sort, bool):
                sort_created_at = sort
            else:
                sort_created_at = str(sort).strip().lower() in ("1", "true", "yes", "y", "on", "checked", "si")
            rows = self.get_table(name, sort_created_at=sort_created_at)
            return {"table": rows}
        except Exception as exc:
            raise

    def filter_table_command(self, table_name: Any, filter_column: Any, filter_value: Any) -> dict[str, Any]:
        try:
            name = (str(table_name or "").strip())
            col = (str(filter_column or "").strip())
            if not name:
                raise Exception("table_name is required")
            if not col:
                raise Exception("filter_column is required")
            rows = self.filter_table(name, col, filter_value)
            return {"table": rows}
        except Exception as exc:
            raise

    def insert_rows_command(self, table_name: Any, rows: Any) -> dict[str, Any]:
        import json

        try:
            name = (str(table_name or "").strip())
            if not name:
                raise Exception("table_name is required")
            if rows in (None, ""):
                raise Exception("datatables is required (JSON list of objects)")

            parsed = json.loads(rows) if isinstance(rows, str) else rows
            if not isinstance(parsed, list):
                raise Exception("datatables must be a JSON array (list) of objects")

            cleaned: list[dict[str, Any]] = []
            for r in parsed:
                if not isinstance(r, dict):
                    raise Exception("each row must be an object")
                cleaned.append({k: v for k, v in r.items() if v != ""})

            inserted = self.insert_rows(name, cleaned)
            return {"insertedRows": inserted}
        except Exception as exc:
            raise

    def update_rows_command(
        self,
        table_name: Any,
        column_name: Any,
        value: Any,
        filter_column: Any,
        filter_value: Any,
    ) -> dict[str, Any]:
        try:
            t = (str(table_name or "").strip())
            c = (str(column_name or "").strip())
            fc = (str(filter_column or "").strip())
            if not t or not c or value in (None, "") or not fc or filter_value in (None, ""):
                raise Exception("table_name, column_name, value, filter_column and filter_value are required")
            self.update_rows(t, {c: value}, where={fc: filter_value})
            return {"message": "Rows updated successfully"}
        except Exception as exc:
            raise

    def update_multiple_rows_command(self, table_name: Any, datatable_json: Any, where_clause: Any) -> dict[str, Any]:
        try:
            t = (str(table_name or "").strip())
            if not t:
                raise Exception("table_name is required")
            if not datatable_json:
                raise Exception("datatable (JSON array) is required")

            rows = json.loads(datatable_json) if isinstance(datatable_json, str) else datatable_json
            if not isinstance(rows, list) or not rows:
                raise Exception("datatable must be a non-empty JSON array")

            if len(rows) == 1 and not (str(where_clause or "").strip()):
                raise Exception("WHERE clause is required when updating a single row")


            updated: list[dict[str, Any]] = []

            if len(rows) == 1 and (str(where_clause or "").strip()):
                first = rows[0]
                if not isinstance(first, dict):
                    raise Exception("Each row must be an object")
                update_data = {k: v for k, v in first.items() if v not in ("", None)}
                if not update_data:
                    raise Exception("No columns to update")
                where = parse_where_clause(where_clause)
                updated = self.update_rows(t, update_data, where=where)
            else:
                first = rows[0]
                if not isinstance(first, dict):
                    raise Exception("Each row must be an object")

                key_column = "id" if first.get("id") not in (None, "") else next((k for k, v in first.items() if v not in ("", None)), None)
                if not key_column:
                    raise Exception("No key column found. Include an 'id' column or use WHERE clause.")

                for row in rows:
                    if not isinstance(row, dict):
                        continue
                    key_value = row.get(key_column)
                    if key_value in (None, ""):
                        continue
                    update_data = {k: v for k, v in row.items() if k != key_column and v not in ("", None)}
                    if not update_data:
                        continue
                    try:
                        u = self.update_rows(t, update_data, where={key_column: key_value})
                        updated.extend(u or [])
                    except Exception:
                        continue

            return {"table": t, "updatedRows": updated, "rowsAffected": len(updated)}
        except Exception as exc:
            raise

    def delete_rows_command(self, table_name: Any, filter_column: Any, filter_value: Any) -> dict[str, Any]:
        import json

        try:
            t = (str(table_name or "").strip())
            fc = (str(filter_column or "").strip())
            if not t or not fc or filter_value in (None, ""):
                raise Exception("table_name, filter_column and filter_value are required")

            parsed = filter_value
            if isinstance(filter_value, str):
                try:
                    parsed = json.loads(filter_value)
                except Exception:
                    parsed = filter_value

            if isinstance(parsed, list):
                deleted = self.delete_rows(t, where_in=(fc, parsed))
            else:
                deleted = self.delete_rows(t, where={fc: parsed})
            return {"deletedRows": deleted}
        except Exception as exc:
            raise

    def list_buckets_command(self) -> dict[str, Any]:
        try:
            buckets = self.list_buckets()
            bucket_list = [{"id": b.get("id"), "name": b.get("name")} for b in buckets]
            return {"bucketList": bucket_list}
        except Exception as exc:
            raise

    def create_bucket_command(self, bucket_name: Any, public: Any, file_size_limit: Any, allowed_mime_types: Any) -> dict[str, Any]:
        try:
            name = (str(bucket_name or "").strip())
            if not name:
                raise Exception("bucket_name is required")
            public_bool = str(public).lower() in ("1", "true", "yes", "y")
            file_size_limit_s = str(file_size_limit or "").strip()
            fsl = int(file_size_limit_s) if file_size_limit_s else None
            allowed: list[str] = []
            if str(allowed_mime_types or "").strip():
                allowed = [m.strip() for m in str(allowed_mime_types).split(",") if m.strip()]
            bucket = self.create_bucket(name, public=public_bool, file_size_limit=fsl, allowed_mime_types=allowed or None)
            return {"bucket": bucket}
        except Exception as exc:
            raise

    def get_bucket_command(self, bucket_name: Any, include_files: Any) -> dict[str, Any]:
        try:
            name = (str(bucket_name or "").strip())
            if not name:
                raise Exception("bucket_name is required")
            include = str(include_files).lower() in ("1", "true", "yes", "y")
            bucket = self.get_bucket(name)
            files = self.list_files(name, path="") if include else []
            return {"bucket": bucket, "files": files}
        except Exception as exc:
            raise

    def list_files_command(self, bucket: Any, path: Any) -> dict[str, Any]:
        try:
            b = (str(bucket or "").strip())
            p = (str(path or "").strip())
            files = self.list_files(b, path=p)
            return {"fileList": files or []}
        except Exception as exc:
            raise

    def upload_file_command(self, bucket: Any, local_path: Any, object_path: Any, upsert: Any) -> dict[str, Any]:
        import mimetypes
        from pathlib import Path, PurePosixPath

        try:
            b = (str(bucket or "").strip())
            lp = (str(local_path or "").strip())
            if not b or not lp:
                raise Exception("bucket and local_path are required")

            p = Path(lp)
            if not p.is_file():
                raise Exception(f"Local file not found: {lp}")

            op = (str(object_path or "").lstrip("/")) or p.name
            content = p.read_bytes()
            ctype = mimetypes.guess_type(p.name)[0] or "application/octet-stream"
            upsert_bool = str(upsert).lower() in ("1", "true", "yes", "y")
            out = self.upload_file(b, op, content, content_type=ctype, upsert=upsert_bool)
            return {"file": out}
        except Exception as exc:
            raise

    def download_file_command(self, bucket: Any, object_path: Any, local_dest: Any) -> dict[str, Any]:
        from pathlib import Path, PurePosixPath

        try:
            b = (str(bucket or "").strip())
            op = (str(object_path or "").lstrip("/"))
            ld = (str(local_dest or "").strip())
            if not b or not op or not ld:
                raise Exception("bucket, object_path and local_dest are required")
            dest = Path(ld)
            if ld.endswith(("/", "\\")) or (dest.exists() and dest.is_dir()):
                dest = dest / (PurePosixPath(op).name or "download")
            dest.parent.mkdir(parents=True, exist_ok=True)

            content = self.download_file(b, op)
            dest.write_bytes(content)
            return {"local_path": str(dest), "object_path": op}
        except Exception as exc:
            raise

    def execute_postgres_function_command(self, function_name: Any, params_json: Any) -> dict[str, Any]:
        import json

        try:
            fn = (str(function_name or "").strip())
            if not fn:
                raise Exception("function_name is required")
            params = json.loads(params_json) if str(params_json or "").strip() else {}
            if not isinstance(params, dict):
                raise Exception("params must be a JSON object")
            result = self.rpc(fn, params)
            return {"result": result}
        except Exception as exc:
            raise

    def generate_and_store_embedding_command(
        self,
        table_name: Any,
        input_text: Any,
        chunk_size: Any,
        chunk_overlap: Any,
        embedding_dim: Any,
        embedding_model: Any,
        content_column: Any = None,
        embedding_column: Any = None,
        metadata_column: Any = None,
        extra_metadata_json: Any = None,
    ) -> dict[str, Any]:
        t = (str(table_name or "").strip())
        if not t:
            raise Exception("table_name is required")

        text = (str(input_text or "").strip())
        if not text:
            raise Exception("input text is empty")

        cs = parse_json_int(chunk_size, 1024)
        co = parse_json_int(chunk_overlap, 128)
        requested_dim = parse_json_int(embedding_dim, 0)

        sess = self.embedding_session or {}
        provider = (str(sess.get("provider") or "").strip().lower())
        api_key = (str(sess.get("api_key") or "").strip())
        if provider not in ("openai", "gemini", "huggingface", "cohere"):
            raise Exception("Embedding provider session is missing/invalid. Run 'Embeddings Connect' first.")
        if not api_key:
            raise Exception("Embedding API key is missing. Run 'Embeddings Connect' first.")
        model = (str(embedding_model or "").strip()) or (str(sess.get("default_model") or "").strip())
        if not model:
            raise Exception("embedding_model is required")

        chunks = split_text(text, chunk_size=cs, chunk_overlap=co)

        # Generate embeddings in batch.
        if provider == "openai":
            vectors = openai_embed_texts(api_key=api_key, model=model, texts=chunks)
        elif provider == "gemini":
            vectors = gemini_embed_texts(api_key=api_key, model=model, texts=chunks)
        elif provider == "huggingface":
            vectors = huggingface_embed_texts(api_key=api_key, model=model, texts=chunks)
        else:
            vectors = cohere_embed_texts(api_key=api_key, model=model, texts=chunks)

        if len(vectors) != len(chunks):
            raise Exception("Embedding provider returned unexpected number of vectors")

        actual_dim = len(vectors[0]) if vectors else 0
        if requested_dim and actual_dim and requested_dim != actual_dim:
            raise Exception(f"Embedding dim mismatch: requested {requested_dim}, provider returned {actual_dim}")

        # Column mapping: keep current defaults (content, embedding, metadata), but allow customization
        # to match different schemas (e.g. body, embedding, metadata).
        c_col = (str(content_column or "").strip()) or "content"
        e_col = (str(embedding_column or "").strip()) or "embedding"
        m_col = (str(metadata_column or "").strip()) or "metadata"
        extra_meta = parse_json_object(extra_metadata_json, default={})

        records: list[dict[str, Any]] = []
        for idx, chunk in enumerate(chunks):
            emb = vectors[idx]
            if actual_dim and len(emb) != actual_dim:
                raise Exception("Inconsistent embedding dimensions returned by provider")
            md = {
                "source": "text",
                "chunk_size": cs,
                "chunk_number": idx + 1,
                "total_chunks": len(chunks),
                "loc": {"lines": {"from": idx + 1, "to": idx + 1}},
                "embedding_provider": provider,
                "embedding_model": model,
            }
            if extra_meta:
                md.update(extra_meta)
            records.append(
                {
                    c_col: chunk,
                    e_col: emb,
                    m_col: md,
                }
            )

        inserted = self.insert_rows(t, records)
        inserted_ids = [r.get("id") for r in inserted if isinstance(r, dict) and "id" in r]
        return {
            "table": t,
            "inserted_ids": inserted_ids,
            "original_content_length": len(text),
            "total_chunks": len(records),
            "chunk_size": cs,
            "chunk_overlap": co,
            "embedding_dim": actual_dim,
            "embedding_provider": provider,
            "embedding_model": model,
        }

    def retrieve_documents_command(
        self,
        function_name: Any,
        query_value: Any,
        num_results: Any,
        embedding_dim: Any,
        filter_json: Any,
        embedding_model: Any,
        match_threshold: Any = None,
        rpc_params_json: Any = None,
    ) -> Any:
        fn = (str(function_name or "").strip())
        q = (str(query_value or "").strip())
        if not fn:
            raise Exception("function_name is required")
        if not q:
            raise Exception("query_value is required")

        n = parse_json_int(num_results, 5)
        requested_dim = parse_json_int(embedding_dim, 0)
        filter_obj = parse_json_object(filter_json, default={})
        extra_params = parse_json_object(rpc_params_json, default={})

        sess = self.embedding_session or {}
        provider = (str(sess.get("provider") or "").strip().lower())
        api_key = (str(sess.get("api_key") or "").strip())
        if provider not in ("openai", "gemini", "huggingface", "cohere"):
            raise Exception("Embedding provider session is missing/invalid. Run 'Embeddings Connect' first.")
        if not api_key:
            raise Exception("Embedding API key is missing. Run 'Embeddings Connect' first.")
        model = (str(embedding_model or "").strip()) or (str(sess.get("default_model") or "").strip())
        if not model:
            raise Exception("embedding_model is required")

        if provider == "openai":
            query_vec = openai_embed_texts(api_key=api_key, model=model, texts=[q])[0]
        elif provider == "gemini":
            query_vec = gemini_embed_texts(api_key=api_key, model=model, texts=[q])[0]
        elif provider == "huggingface":
            query_vec = huggingface_embed_texts(api_key=api_key, model=model, texts=[q])[0]
        else:
            # For queries, use search_query for Cohere to optimize retrieval quality.
            query_vec = cohere_embed_texts(api_key=api_key, model=model, texts=[q], input_type="search_query")[0]

        actual_dim = len(query_vec)
        if requested_dim and requested_dim != actual_dim:
            raise Exception(f"Embedding dim mismatch: requested {requested_dim}, provider returned {actual_dim}")

        # Default RPC payload (current module contract). Extra params can be added via rpc_params_json.
        params: dict[str, Any] = {"filter": filter_obj, "query_embedding": query_vec, "match_count": n}

        if match_threshold is not None and str(match_threshold).strip() != "":
            try:
                params["match_threshold"] = float(match_threshold)
            except Exception:
                raise Exception("match_threshold must be a number")

        if extra_params:
            params.update(extra_params)

        return self.rpc(fn, params)

    def trigger_supabase_command(self, table: Any, last_id: Any) -> dict[str, Any]:
        t = (str(table or "").strip())
        if not t:
            raise Exception("table is required")

        last_id_val: Any = None
        if str(last_id).strip():
            try:
                last_id_val = int(last_id)
            except Exception:
                last_id_val = last_id

        filters = [("id", "not.is", "null")]
        if last_id_val is not None:
            filters.append(("id", "gt", last_id_val))

        rows = select_table(self.require_session(), t, filters=filters, order_by="id", ascending=True)
        new_last = rows[-1].get("id") if rows else last_id_val
        return {"rows": rows, "lastId": new_last}

    def embedding_connect_command(self, embedding_provider: Any, embedding_api_key: Any, default_model: Any = None) -> dict[str, Any]:
        provider = (str(embedding_provider or "").strip().lower())
        api_key = (str(embedding_api_key or "").strip())
        if not provider:
            raise Exception("embedding_provider is required")
        if not api_key:
            raise Exception("embedding_api_key is required")

        models_info = list_embedding_models(provider, api_key)
        # Store session for reuse by embedding commands.
        dm = (str(default_model or "").strip()) or None
        self.embedding_session = {"provider": provider, "api_key": api_key, "default_model": dm}
        return {
            "session": {"provider": provider, "default_model": dm},
            "available_models": models_info.get("models") or [],
            "note": models_info.get("note"),
        }

    def get_table_columns_template_command(self, table_name: Any) -> dict[str, Any]:
        name = (str(table_name or "").strip())
        if not name:
            raise Exception("table_name is required")

        rows = select_table(self.require_session(), name, limit=1)
        if rows:
            cols = [c for c in rows[0].keys() if c != "created_at"]
        else:
            inserted = self.insert_rows(name, [{}])
            if not inserted:
                raise Exception("Could not infer table columns")
            cols = [c for c in inserted[0].keys() if c != "created_at"]
            if "id" in inserted[0]:
                self.delete_rows(name, where={"id": inserted[0]["id"]})

        template = {c: "" for c in cols}
        return {"columns": [template]}

    def list_table_columns_command(self, table_name: Any) -> dict[str, Any]:
        name = (str(table_name or "").strip())
        if not name:
            raise Exception("table_name is required")

        rows = select_table(self.require_session(), name, limit=1)
        if rows:
            cols = [c for c in rows[0].keys() if c != "created_at"]
        else:
            inserted = self.insert_rows(name, [{}])
            if not inserted:
                return {"columns": []}
            cols = [c for c in inserted[0].keys() if c != "created_at"]
            if "id" in inserted[0]:
                self.delete_rows(name, where={"id": inserted[0]["id"]})

        return {"columns": [{"name": c} for c in cols]}

    def get_table(self, table_name: str, *, sort_created_at: bool = False) -> list[dict[str, Any]]:
        cfg = self.require_session()
        return select_table(cfg, table_name, order_by="created_at" if sort_created_at else None, ascending=False)

    def filter_table(self, table_name: str, filter_column: str, filter_value: Any) -> list[dict[str, Any]]:
        cfg = self.require_session()
        return select_table(cfg, table_name, filter_column=filter_column, filter_value=filter_value)

    def insert_rows(self, table_name: str, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        cfg = self.require_session()
        return insert_rows(cfg, table_name, rows, return_rows=True)

    def update_rows(self, table_name: str, update_data: dict[str, Any], *, where: dict[str, Any]) -> list[dict[str, Any]]:
        cfg = self.require_session()
        return update_rows(cfg, table_name, update_data, where=where)

    def delete_rows(self, table_name: str, *, where: dict[str, Any] | None = None, where_in: tuple[str, list[Any]] | None = None) -> list[dict[str, Any]]:
        cfg = self.require_session()
        return delete_rows(cfg, table_name, where=where, where_in=where_in)

    def rpc(self, function_name: str, params: dict[str, Any] | None = None) -> Any:
        cfg = self.require_session()
        return rpc(cfg, function_name, params or {})

    def list_buckets(self) -> list[dict[str, Any]]:
        cfg = self.require_session()
        return list_buckets(cfg)

    def create_bucket(self, bucket_name: str, *, public: bool = False, file_size_limit: int | None = None, allowed_mime_types: list[str] | None = None) -> dict[str, Any]:
        cfg = self.require_session()
        return create_bucket(cfg, bucket_name, public=public, file_size_limit=file_size_limit, allowed_mime_types=allowed_mime_types)

    def get_bucket(self, bucket_name: str) -> dict[str, Any]:
        cfg = self.require_session()
        return get_bucket(cfg, bucket_name)

    def list_files(self, bucket_name: str, *, path: str = "") -> list[dict[str, Any]]:
        cfg = self.require_session()
        return list_files(cfg, bucket_name, path=path)

    def upload_file(self, bucket_name: str, object_path: str, content: bytes, *, content_type: str, upsert: bool = False) -> dict[str, Any]:
        cfg = self.require_session()
        return upload_file(cfg, bucket_name, object_path, content, content_type=content_type, upsert=upsert)

    def download_file(self, bucket_name: str, object_path: str) -> bytes:
        cfg = self.require_session()
        return download_file(cfg, bucket_name, object_path)


supabase_object = SupabaseObject()
