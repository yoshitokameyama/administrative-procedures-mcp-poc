"""Allow running as `python -m admin_procedures`."""

import os

from admin_procedures.server import mcp

if port := os.environ.get("ADMIN_PROCEDURES_PORT") or os.environ.get("PORT"):
    # HTTP transport での起動
    # ホスト決定: ADMIN_PROCEDURES_HOST > ADMIN_PROCEDURES_PUBLIC の順で優先
    if os.environ.get("ADMIN_PROCEDURES_HOST"):
        host = os.environ["ADMIN_PROCEDURES_HOST"]
    elif os.environ.get("ADMIN_PROCEDURES_PUBLIC") == "1":
        host = "0.0.0.0"
    else:
        host = "127.0.0.1"
    transport = os.environ.get(
        "ADMIN_PROCEDURES_TRANSPORT", "streamable-http"
    )
    if transport not in {"streamable-http", "sse"}:
        raise ValueError(
            "ADMIN_PROCEDURES_TRANSPORT must be 'streamable-http' or 'sse'"
        )
    path = os.environ.get("ADMIN_PROCEDURES_PATH")
    run_options = {"host": host, "port": int(port)}
    if path:
        run_options["path"] = path
    mcp.run(transport=transport, **run_options)
else:
    mcp.run()
