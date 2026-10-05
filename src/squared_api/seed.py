"""Fill the local database with the same data as the iOS app's MockData.

Run from the project root with:
    uv run python -m squared_api.seed

It deletes every existing row first, so it refuses to run against
anything other than a database on this computer.
"""

import asyncio
import json
import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

from sqlalchemy import delete
from sqlalchemy.engine import make_url

from squared_api.config import settings
from squared_api.security import hash_password
from squared_api.database import SessionLocal, engine
from squared_api.models import (
    Expense,
    ExpenseSplit,
    Group,
    GroupMember,
    Settlement,
    SplitMethod,
    User,
)

DATA_FILE = Path(__file__).parent / "seed_data.json"

# Every seeded account can sign in with this password. Local development only.
SEED_PASSWORD = "squared-dev-password"

# Any fixed UUID works here. Combined with a mock ID like "user-1", it always
# produces the same UUID, so IDs stay stable every time you re-seed.
NAMESPACE = uuid.UUID("5b1d8a2e-0c3f-4e7a-9a61-2f4b8c7d9e10")


def stable_id(mock_id: str) -> uuid.UUID:
    return uuid.uuid5(NAMESPACE, mock_id)


def days_ago(days: Decimal) -> datetime:
    return datetime.now(timezone.utc) - timedelta(days=float(days))


async def seed() -> None:
    host = make_url(settings.database_url).host
    if host not in ("localhost", "127.0.0.1"):
        raise SystemExit(f"Refusing to seed a non-local database (host: {host}).")

    # parse_float=Decimal: money goes straight from text to Decimal, never through float.
    data = json.loads(DATA_FILE.read_text(), parse_float=Decimal)

    async with SessionLocal() as session:
        # Delete children before parents, so nothing is removed while another row still points at it.
        for model in (ExpenseSplit, Expense, Settlement, GroupMember, Group, User):
            await session.execute(delete(model))

        seed_hash = hash_password(SEED_PASSWORD)  # hashing is slow on purpose, so do it once
        for u in data["users"]:
            session.add(
                User(
                    id=stable_id(u["id"]),
                    name=u["name"],
                    email=u["email"],
                    password_hash=seed_hash,
                )
            )
        await session.flush()  # send the users to the database now, so groups can point at them

        for g in data["groups"]:
            session.add(
                Group(
                    id=stable_id(g["id"]),
                    name=g["name"],
                    created_by=stable_id(g["createdBy"]),
                    created_at=days_ago(g["daysAgo"]),
                )
            )
        await session.flush()

        for g in data["groups"]:
            for member_id in g["memberIDs"]:
                session.add(
                    GroupMember(
                        group_id=stable_id(g["id"]),
                        user_id=stable_id(member_id),
                        joined_at=days_ago(g["daysAgo"]),
                    )
                )

        for e in data["expenses"]:
            split_total = sum(s["amount"] for s in e["splits"])
            if split_total != e["amount"]:
                raise SystemExit(f"{e['id']}: splits add up to {split_total}, not {e['amount']}")

            session.add(
                Expense(
                    id=stable_id(e["id"]),
                    group_id=stable_id(e["groupID"]),
                    paid_by_user_id=stable_id(e["paidByUserID"]),
                    title=e["title"],
                    amount=e["amount"],
                    split_method=SplitMethod(e["splitMethod"]),
                    created_at=days_ago(e["daysAgo"]),
                )
            )
        await session.flush()

        for e in data["expenses"]:
            for s in e["splits"]:
                session.add(
                    ExpenseSplit(
                        expense_id=stable_id(e["id"]),
                        user_id=stable_id(s["userID"]),
                        amount=s["amount"],
                    )
                )

        for s in data["settlements"]:
            session.add(
                Settlement(
                    id=stable_id(s["id"]),
                    group_id=stable_id(s["groupID"]),
                    from_user_id=stable_id(s["fromUserID"]),
                    to_user_id=stable_id(s["toUserID"]),
                    amount=s["amount"],
                    settled_at=days_ago(s["daysAgo"]),
                )
            )

        await session.commit()  # everything above becomes permanent here, all at once

    await engine.dispose()

    split_count = sum(len(e["splits"]) for e in data["expenses"])
    print(
        f"Seeded {len(data['users'])} users, {len(data['groups'])} groups, "
        f"{len(data['expenses'])} expenses ({split_count} splits), "
        f"{len(data['settlements'])} settlement(s)."
    )


if __name__ == "__main__":
    asyncio.run(seed())
