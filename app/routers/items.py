from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Item, User
from app.schemas import (
    CategoryDensity,
    CategoryDensityResponse,
    ItemCreate,
    ItemListResponse,
    ItemResponse,
    ItemUpdate,
)
from app.security import get_current_user

router = APIRouter(prefix="/api/items", tags=["items"])


@router.post("", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(
    item_data: ItemCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    new_item = Item(
        name=item_data.name,
        description=item_data.description,
        category=item_data.category,
        status=item_data.status,
    )

    db.add(new_item)
    await db.flush()
    await db.refresh(new_item)

    return new_item


def verify_item(item):
    if not item:
        raise HTTPException(status_code=404, detail="Item not found.")


@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(
    item_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Item).where(Item.id == item_id, not Item.is_deleted))
    item = result.scalar_one_or_none()

    verify_item(item)

    return item


@router.get("", response_model=ItemListResponse)
async def list_items(
    page: int = Query(1, ge=1),
    per_page: int = Query(5, ge=1, le=20),
    category: Optional[str] = Query(None),
    sort_by: Optional[str] = Query("created_at"),
    order: str = Query("desc", regex="^(asc|desc)$"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    query = select(Item).where(not Item.is_deleted)
    count_query = select(func.count()).select_from(Item).where(not Item.is_deleted)

    if category:
        query = query.where(Item.category == category)
        count_query = count_query.where(Item.category == category)

    total_result = await db.execute(count_query)
    total = total_result.scalar()

    allowed_sort_fields = {
        "created_at": Item.created_at,
        "name": Item.name,
        "category": Item.category,
    }

    sort_column = allowed_sort_fields.get(sort_by, Item.created_at)
    query = query.order_by(sort_column.desc() if order == "desc" else sort_column.asc())

    offset = (page - 1) * per_page
    query = query.offset(offset).limit(per_page)

    result = await db.execute(query)
    items = result.scalars().all()

    total_pages = (total + per_page - 1) // per_page

    return ItemListResponse(
        items=items, total=total, page=page, per_page=per_page, pages=total_pages
    )


@router.patch("/{item_id}", response_model=ItemResponse)
async def update_item(
    item_id: int,
    data: ItemUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Item).where(Item.id == item_id, not Item.is_deleted))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    if data.name is not None:
        item.name = data.name

    if data.description is not None:
        item.description = data.description

    if data.category is not None:
        item.category = data.category

    if data.status is not None:
        item.status = data.status

    await db.flush()
    await db.refresh(item)

    return item


@router.get("/analytics/category-density", response_model=CategoryDensityResponse)
async def category_density(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    total_result = await db.execute(
        select(func.count()).select_from(Item).where(not Item.is_deleted)
    )
    total_items = total_result.scalar() or 0

    if total_items == 0:
        return CategoryDensityResponse(total_items=0, categories=[])

    result = await db.execute(
        select(Item.category, func.count(Item.id).label("count"))
        .where(not Item.is_deleted)
        .group_by(Item.category)
    )

    rows = result.all()

    categories = [
        CategoryDensity(
            category=category, count=count, percentage=round((count / total_items) * 100, 2)
        )
        for category, count in rows
    ]

    return CategoryDensityResponse(total_items=total_items, categories=categories)
