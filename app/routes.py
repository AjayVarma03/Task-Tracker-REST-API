"""
REST API routes for the Task resource.

Endpoints:
    GET    /tasks            -> list all tasks (supports ?status= filter)
    POST   /tasks             -> create a task
    GET    /tasks/<id>        -> get a single task
    PUT    /tasks/<id>        -> full update of a task
    PATCH  /tasks/<id>        -> partial update of a task
    DELETE /tasks/<id>        -> delete a task
"""
from flask import Blueprint, request, jsonify, current_app
from bson import ObjectId
from bson.errors import InvalidId

from .validation import validate_task_payload

bp = Blueprint("tasks", __name__, url_prefix="/tasks")


def _serialize(task: dict) -> dict:
    task = dict(task)
    task["id"] = str(task.pop("_id"))
    return task


def _get_object_id(task_id: str):
    try:
        return ObjectId(task_id)
    except (InvalidId, TypeError):
        return None


@bp.get("")
def list_tasks():
    db = current_app.db
    query = {}
    status = request.args.get("status")
    if status:
        query["status"] = status

    tasks = [_serialize(t) for t in db.tasks.find(query)]
    return jsonify(tasks), 200


@bp.post("")
def create_task():
    data = request.get_json(silent=True) or {}
    is_valid, error = validate_task_payload(data)
    if not is_valid:
        return jsonify({"error": error}), 400

    task = {
        "title": data["title"].strip(),
        "description": data.get("description", ""),
        "status": data.get("status", "TODO"),
        "priority": data.get("priority", 3),
    }

    db = current_app.db
    result = db.tasks.insert_one(task)
    task["_id"] = result.inserted_id
    return jsonify(_serialize(task)), 201


@bp.get("/<task_id>")
def get_task(task_id):
    oid = _get_object_id(task_id)
    if oid is None:
        return jsonify({"error": "Invalid task id."}), 400

    db = current_app.db
    task = db.tasks.find_one({"_id": oid})
    if not task:
        return jsonify({"error": "Task not found."}), 404

    return jsonify(_serialize(task)), 200


@bp.put("/<task_id>")
def update_task_full(task_id):
    return _update_task(task_id, partial=False)


@bp.patch("/<task_id>")
def update_task_partial(task_id):
    return _update_task(task_id, partial=True)


def _update_task(task_id: str, partial: bool):
    oid = _get_object_id(task_id)
    if oid is None:
        return jsonify({"error": "Invalid task id."}), 400

    data = request.get_json(silent=True) or {}
    is_valid, error = validate_task_payload(data, partial=partial)
    if not is_valid:
        return jsonify({"error": error}), 400

    db = current_app.db
    existing = db.tasks.find_one({"_id": oid})
    if not existing:
        return jsonify({"error": "Task not found."}), 404

    update_fields = {
        k: v for k, v in data.items() if k in {"title", "description", "status", "priority"}
    }
    if update_fields:
        db.tasks.update_one({"_id": oid}, {"$set": update_fields})

    updated = db.tasks.find_one({"_id": oid})
    return jsonify(_serialize(updated)), 200


@bp.delete("/<task_id>")
def delete_task(task_id):
    oid = _get_object_id(task_id)
    if oid is None:
        return jsonify({"error": "Invalid task id."}), 400

    db = current_app.db
    result = db.tasks.delete_one({"_id": oid})
    if result.deleted_count == 0:
        return jsonify({"error": "Task not found."}), 404

    return "", 204
