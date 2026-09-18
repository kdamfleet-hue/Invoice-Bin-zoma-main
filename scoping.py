"""Central, fail-closed branch scoping for SQLAlchemy models.

Branch isolation today is enforced by convention: each route is supposed to
remember to add `.filter_by(branch_id=...)` (or use helpers.branch_scope()).
An audit found ~59% of the direct query call sites on branch-owned models
skip that filter, including a driver-delete endpoint that lets a branch
manager delete another branch's driver by id.

Models added to ENFORCED_MODELS can no longer be queried without an active
scope: every SELECT/UPDATE/DELETE issued through the ORM for that model is
automatically filtered to the current branch (or raises, if no scope was
ever set), so a forgotten manual filter can no longer leak another branch's
rows. Rolled out one model at a time — see the model's own comment at the
call site where it's added — since this is a live app used daily for real
fleet operations, not something to flip on for all 22 models at once.
"""
from contextlib import contextmanager
from contextvars import ContextVar

from sqlalchemy import event
from sqlalchemy.orm import Session, with_loader_criteria

from models.schema import CustodyItem, Driver, SparePart, Vehicle

ALL_BRANCHES = "__ALL__"

# Grows one model at a time as each is verified safe to enforce. Vehicle/CustodyItem/
# SparePart added together while building real (safely isolated) operational tabs for
# SaaS trial companies — see routes/saas.py register_company()'s auto-provisioned
# per-company branch. The single .get() call found on Vehicle was converted to
# scoped_get (routes/fleet.py); CustodyItem and SparePart had none.
ENFORCED_MODELS = {Driver, Vehicle, CustodyItem, SparePart}

_scope = ContextVar("_branch_scope", default=None)


class ScopeNotSet(RuntimeError):
    """Raised instead of silently returning unfiltered rows for an enforced model."""


def set_scope(branch_id):
    _scope.set(branch_id)


@contextmanager
def unscoped():
    """Explicit, auditable escape hatch for access that is legitimately not
    branch-scoped: an admin tool that intentionally spans branches, or the
    driver self-service portal, which authenticates a single driver by
    iqama+phone and isn't a branch/staff session at all."""
    token = _scope.set(ALL_BRANCHES)
    try:
        yield
    finally:
        _scope.reset(token)


@event.listens_for(Session, "do_orm_execute")
def _enforce_branch_scope(orm_execute_state):
    if not (
        (orm_execute_state.is_select or orm_execute_state.is_update or orm_execute_state.is_delete)
        and not orm_execute_state.is_column_load
        and not orm_execute_state.is_relationship_load
    ):
        return
    for mapper in orm_execute_state.all_mappers:
        cls = mapper.class_
        if cls not in ENFORCED_MODELS:
            continue
        bid = _scope.get()
        if bid is None:
            raise ScopeNotSet(f"{cls.__name__} query executed with no branch scope set")
        if bid == ALL_BRANCHES:
            continue
        # `bid` MUST be a genuine closure variable here, not a `lambda c, bid=bid:`
        # default-argument capture. SQLAlchemy's lambda-SQL cache extracts bound
        # values by inspecting the lambda's closure cells, not its `__defaults__` —
        # a default-argument value is invisible to it, so with `bid=bid` every call
        # silently reused whichever bid was bound the FIRST time this lambda's byte-
        # code shape was compiled, no matter what scope was actually active on later
        # calls. (SQLAlchemy also flatly rejects calling _scope.get() *inside* the
        # lambda: "lambda SQL constructs should not invoke functions from closure
        # variables to produce literal values.") Reproduced and confirmed fixed with
        # a real query switching scope 8 -> 1 within one process.
        orm_execute_state.statement = orm_execute_state.statement.options(
            with_loader_criteria(cls, lambda c: c.branch_id == bid, include_aliases=True)
        )


def _scoped_query(model, pk):
    bid = _scope.get()
    if bid is None:
        raise ScopeNotSet(f"{model.__name__} lookup with no branch scope set")
    q = model.query.filter(model.id == pk)
    if bid != ALL_BRANCHES:
        q = q.filter(model.branch_id == bid)
    return q


def scoped_get_or_404(model, pk):
    """Fetch by primary key, but only within the caller's active branch scope.
    Use instead of Model.query.get()/get_or_404(): those are served from the
    identity map and bypass loader-criteria filtering entirely, so an
    enforced model's .get() would otherwise stay silently unscoped."""
    from flask import abort
    row = _scoped_query(model, pk).first()
    if row is None:
        abort(404)
    return row


def scoped_get(model, pk):
    """Soft variant of scoped_get_or_404: returns None instead of aborting when
    the row doesn't exist or belongs to another branch. For informational,
    display-only lookups that should degrade gracefully rather than fail the
    whole request."""
    return _scoped_query(model, pk).first()
