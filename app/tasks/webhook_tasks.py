"""Webhook processing is synchronous so idempotency stays in one DB transaction.

Celery is reserved for non-critical follow-up work such as confirmation logs.
This module is kept so the assignment layout stays easy to explain.
"""
