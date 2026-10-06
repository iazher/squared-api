import uuid

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import func, select

from squared_api.dependencies import CurrentUser, SessionDep
from squared_api.models import Group, GroupMember, User
from squared_api.schemas.group import GroupCreate, GroupOut

router = APIRouter(prefix="/groups", tags=["groups"])


@router.get("", response_model=list[GroupOut])
async def list_my_groups(current_user: CurrentUser, session: SessionDep) -> list[GroupOut]:
    # Query 1: the groups I'm an active member of. This filter IS the authorization:
    # groups I'm not in are never even loaded.
    groups = (
        await session.scalars(
            select(Group)
            .join(GroupMember, GroupMember.group_id == Group.id)
            .where(GroupMember.user_id == current_user.id, GroupMember.removed_at.is_(None))
            .order_by(Group.created_at.desc())
        )
    ).all()
    if not groups:
        return []

    # Query 2: every active member of those groups, all at once (not one query per group).
    rows = await session.execute(
        select(GroupMember.group_id, GroupMember.user_id).where(
            GroupMember.group_id.in_([g.id for g in groups]),
            GroupMember.removed_at.is_(None),
        )
    )
    members: dict[uuid.UUID, list[uuid.UUID]] = {g.id: [] for g in groups}
    for group_id, user_id in rows:
        members[group_id].append(user_id)

    return [
        GroupOut(id=g.id, name=g.name, member_ids=members[g.id], created_at=g.created_at)
        for g in groups
    ]


@router.post("", response_model=GroupOut, status_code=status.HTTP_201_CREATED)
async def create_group(body: GroupCreate, current_user: CurrentUser, session: SessionDep) -> GroupOut:
    member_ids = set(body.member_ids) | {current_user.id}  # the creator is always a member

    found = await session.scalar(select(func.count()).select_from(User).where(User.id.in_(member_ids)))
    if found != len(member_ids):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="One or more member IDs don't match a user",
        )

    group = Group(name=body.name, created_by=current_user.id)
    session.add(group)
    await session.flush()  # gives the group its id before we add members that point to it

    for user_id in member_ids:
        session.add(GroupMember(group_id=group.id, user_id=user_id))
    await session.commit()
    await session.refresh(group)  # load created_at, which the database filled in

    return GroupOut(id=group.id, name=group.name, member_ids=list(member_ids), created_at=group.created_at)