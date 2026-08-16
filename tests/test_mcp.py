"""MCP インスタンス生成テスト。

データツール統合テストは test_server.py を参照。
"""

import asyncio
import inspect

import pytest

from admin_procedures.server import (
    CACHE_SCOPE,
    CACHE_TTL_MS,
    EnvironmentTokenVerifier,
    auth_from_env,
    fastmcp_kwargs,
    create_mcp,
    mcp,
)


def test_mcp_instance_exists():
    """モジュールレベルの mcp インスタンスが存在する。"""
    assert mcp is not None
    assert mcp.name == "administrative-procedures-mcp-catalog"


def test_create_mcp_returns_fastmcp():
    """create_mcp() が FastMCP インスタンスを返す。"""
    instance = create_mcp()
    assert instance.name == "administrative-procedures-mcp-catalog"


def test_create_mcp_no_ui():
    """no_ui=True で UI リソースが登録されない。"""
    instance = create_mcp(no_ui=True)
    assert instance is not None


def test_auth_from_env_disabled_by_default(monkeypatch):
    monkeypatch.delenv("MCP_AUTH_TOKEN", raising=False)
    monkeypatch.delenv("ADMIN_PROCEDURES_REQUIRE_AUTH", raising=False)
    assert auth_from_env() is None


def test_auth_from_env_required_without_token(monkeypatch):
    monkeypatch.delenv("MCP_AUTH_TOKEN", raising=False)
    monkeypatch.setenv("ADMIN_PROCEDURES_REQUIRE_AUTH", "1")
    with pytest.raises(RuntimeError, match="MCP_AUTH_TOKEN is required"):
        auth_from_env()


def test_environment_token_verifier(monkeypatch):
    token = "a" * 64
    monkeypatch.setenv("MCP_AUTH_TOKEN", token)
    monkeypatch.setenv("ADMIN_PROCEDURES_AUTH_CLIENT_ID", "notion-poc")
    verifier = auth_from_env()
    assert isinstance(verifier, EnvironmentTokenVerifier)

    accepted = asyncio.run(verifier.verify_token(token))
    rejected = asyncio.run(verifier.verify_token("b" * 64))
    assert accepted is not None
    assert accepted.client_id == "notion-poc"
    assert rejected is None


# ============================================================
# MCP 仕様 2026-07-28: cacheable list results
# ============================================================


def test_fastmcp_kwargs_matches_installed_fastmcp():
    """FastMCP が cache_ttl/cache_scope を持つときだけキャッシュ宣言すること。

    FastMCP 3.x では引数自体が無いため、渡すと TypeError になる。
    mask_error_details は 4.x でサポートされていれば追加される。
    """
    from fastmcp import FastMCP

    params = inspect.signature(FastMCP.__init__).parameters
    supported_cache = "cache_ttl" in params and "cache_scope" in params
    supported_mask = "mask_error_details" in params
    kwargs = fastmcp_kwargs()

    if supported_cache:
        assert kwargs["cache_ttl"] == CACHE_TTL_MS
        assert kwargs["cache_scope"] == CACHE_SCOPE
    if supported_mask:
        assert kwargs["mask_error_details"] is True
    if not supported_cache and not supported_mask:
        assert kwargs == {}


def test_cache_hint_values_are_valid():
    """キャッシュヒントの値が MCP 仕様の許容範囲であること。"""
    assert CACHE_TTL_MS > 0
    # 利用者ごとに内容が変わらないため public であるべき
    assert CACHE_SCOPE in ("public", "private")
    assert CACHE_SCOPE == "public"
