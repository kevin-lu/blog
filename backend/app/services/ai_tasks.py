"""
In-memory task store for AI rewrite jobs.
"""
from copy import deepcopy
from datetime import datetime
from threading import Lock
from typing import Any, Dict, List, Optional
from uuid import uuid4


_TASKS: Dict[str, Dict[str, Any]] = {}
_LOCK = Lock()


def _serialize_task(task: Dict[str, Any]) -> Dict[str, Any]:
    result = deepcopy(task)
    for key in ('created_at', 'completed_at'):
        value = result.get(key)
        if isinstance(value, datetime):
            result[key] = value.isoformat()
    return result


def create_task(task: Dict[str, Any]) -> Dict[str, Any]:
    task_id = f"task_{uuid4().hex[:12]}"
    payload = {
        'id': task_id,
        'status': 'pending',
        'progress': 0,
        'message': '',
        'created_at': datetime.utcnow(),
        **task,
    }
    with _LOCK:
        _TASKS[task_id] = payload
        return _serialize_task(payload)


def get_task(task_id: str) -> Optional[Dict[str, Any]]:
    with _LOCK:
        task = _TASKS.get(task_id)
        return _serialize_task(task) if task else None


def update_task(task_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    with _LOCK:
        task = _TASKS.get(task_id)
        if not task:
            return None
        task.update(updates)
        return _serialize_task(task)


def list_tasks(limit: int = 20) -> List[Dict[str, Any]]:
    with _LOCK:
        tasks = sorted(
            _TASKS.values(),
            key=lambda item: item.get('created_at') or datetime.min,
            reverse=True,
        )
        return [_serialize_task(task) for task in tasks[:limit]]


def clear_finished_tasks() -> int:
    with _LOCK:
        task_ids = [
            task_id
            for task_id, task in _TASKS.items()
            if task.get('status') in ('completed', 'failed')
        ]
        for task_id in task_ids:
            _TASKS.pop(task_id, None)
        return len(task_ids)
