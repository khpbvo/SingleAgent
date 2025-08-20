import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from The_Agents.shared_context_manager import SharedContextManager, TaskPriority


def test_sqlite_persistence(tmp_path):
    db_file = tmp_path / "shared_context.db"
    mgr = SharedContextManager(db_path=str(db_file))

    task_id = mgr.add_task(
        target_agent="code",
        task="Implement feature",
        created_by="architect",
        priority=TaskPriority.HIGH,
    )
    insight_id = mgr.add_insight(
        agent="architect",
        insight="Use SQLite for persistence",
        category="architecture",
    )

    # Recreate manager to ensure data is persisted to disk
    mgr2 = SharedContextManager(db_path=str(db_file))
    assert task_id in mgr2.tasks
    assert insight_id in mgr2.insights

