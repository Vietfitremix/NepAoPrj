"""Uvicorn loop factory compatible with psycopg's Windows async connections."""
import asyncio


def selector_loop_factory():
    return asyncio.SelectorEventLoop()
