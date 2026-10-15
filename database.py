"""Data-access helpers for the Student Profile walking-skeleton slice.

The current v3 prototype still contains direct SQLite queries for several other
screens. This module isolates profile persistence so the milestone's thin slice
has an explicit application-to-data-access boundary.
"""
from __future__ import annotations

import sqlite3
from typing import Any, Mapping


def get_student_profile(database_path: str, row_id: int = 1) -> dict[str, Any] | None:
    """Read the persisted demo/student profile from SQLite."""
    with sqlite3.connect(database_path) as connection:
        connection.row_factory = sqlite3.Row
        row = connection.execute(
            "SELECT * FROM student WHERE id = ?", (row_id,)
        ).fetchone()
        return dict(row) if row is not None else None


def save_student_profile(
    database_path: str, profile: Mapping[str, Any], row_id: int = 1
) -> dict[str, Any] | None:
    """Update a profile and query it back before returning it.

    The database schema is initialized by app.init_db(). All SQL values are
    parameterized; numeric form values are converted before they reach SQLite.
    """
    values = (
        str(profile.get("student_id", "")).strip(),
        str(profile.get("name", "")).strip(),
        str(profile.get("email", "")).strip(),
        str(profile.get("major", "")).strip(),
        str(profile.get("concentration", "")).strip(),
        str(profile.get("catalog_year", "")).strip(),
        str(profile.get("standing", "")).strip(),
        float(profile.get("gpa") or 0),
        int(profile.get("credits_completed") or 0),
        int(profile.get("total_credits") or 128),
        str(profile.get("target_graduation", "")).strip(),
        int(profile.get("pace") or 15),
        row_id,
    )
    with sqlite3.connect(database_path) as connection:
        connection.execute(
            """UPDATE student
               SET student_id=?, name=?, email=?, major=?, concentration=?,
                   catalog_year=?, standing=?, gpa=?, credits_completed=?,
                   total_credits=?, target_graduation=?, pace=?
               WHERE id=?""",
            values,
        )
        connection.commit()
    return get_student_profile(database_path, row_id=row_id)
