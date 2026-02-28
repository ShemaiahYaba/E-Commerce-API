"""
Simple in-memory rate limiter using a sliding-window counter.
Designed to mirror the Week 4 project pattern: decorator-based,
configurable per-route, keyed by IP (or JWT subject when available).
"""

import time
from collections import defaultdict
from functools import wraps
from threading import Lock

from flask import request, jsonify

# ──────────────────────────────────────────────
# Storage: { key: [(timestamp, ...) ] }          
# ──────────────────────────────────────────────
_buckets: dict[str, list[float]] = defaultdict(list)
_lock = Lock()


def _get_request_key() -> str:
    """Return a stable key for the current caller.

    Prefers the JWT 'sub' claim (user ID) when present so
    authenticated users share a bucket across IPs.  Falls back
    to the remote IP for unauthenticated requests.
    """
    try:
        from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
        verify_jwt_in_request(optional=True)
        identity = get_jwt_identity()
        if identity:
            return f"user:{identity}"
    except Exception:
        pass
    return f"ip:{request.remote_addr}"


def rate_limit(max_calls: int = 60, period: int = 60, scope: str | None = None):
    """Decorator — sliding-window rate limiter.

    Args:
        max_calls: Maximum requests allowed in *period* seconds.
        period:    Time window in seconds.
        scope:     Optional label to share a bucket across multiple
                   routes (e.g. ``scope="auth"``).  Defaults to the
                   view function name.

    Usage::

        @auth_bp.route("/login", methods=["POST"])
        @rate_limit(max_calls=5, period=60, scope="auth")
        def login():
            ...
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            bucket_label = scope or fn.__name__
            key = f"{bucket_label}:{_get_request_key()}"
            now = time.monotonic()
            window_start = now - period

            with _lock:
                # Evict timestamps outside the sliding window
                _buckets[key] = [t for t in _buckets[key] if t > window_start]

                if len(_buckets[key]) >= max_calls:
                    retry_after = int(period - (now - _buckets[key][0])) + 1
                    resp = jsonify({
                        "success": False,
                        "message": f"Rate limit exceeded. Try again in {retry_after}s.",
                        "retry_after": retry_after,
                    })
                    resp.status_code = 429
                    resp.headers["Retry-After"] = str(retry_after)
                    resp.headers["X-RateLimit-Limit"] = str(max_calls)
                    resp.headers["X-RateLimit-Remaining"] = "0"
                    resp.headers["X-RateLimit-Reset"] = str(int(time.time()) + retry_after)
                    return resp

                _buckets[key].append(now)
                remaining = max_calls - len(_buckets[key])

            response = fn(*args, **kwargs)

            # Attach informational headers to the successful response
            try:
                response.headers["X-RateLimit-Limit"] = str(max_calls)
                response.headers["X-RateLimit-Remaining"] = str(remaining)
            except Exception:
                pass  # Non-Response returns (redirects, tuples) — skip headers

            return response
        return wrapper
    return decorator
