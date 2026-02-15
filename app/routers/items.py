from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.cache import delete_cache, get_cache, set_cache
from app.database import get_db
from app.exceptions import ResourceNotFoundError
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


# A simple helper to keep the routes clean
def verify_item(item, item_id):
    if not item:
        raise ResourceNotFoundError(resource="Item", identifier=item_id)
    return item


@router.get("/analytics/category-density", response_model=CategoryDensityResponse)
async def category_density(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Try cache first
    cache_key = "analytics:category-density"
    cached = await get_cache(cache_key)

    if cached:
        return CategoryDensityResponse(**cached)

    # Cache miss - calculate from DB
    total_result = await db.execute(
        select(func.count()).select_from(Item).where(Item.is_deleted == False)  # noqa: E712
    )
    total_items = total_result.scalar() or 0

    if total_items == 0:
        return CategoryDensityResponse(total_items=0, categories=[])

    # E712 is just flake8 being picky about '== False'
    result = await db.execute(
        select(Item.category, func.count(Item.id).label("count"))
        .where(Item.is_deleted == False)  # noqa: E712
        .group_by(Item.category)
    )

    rows = result.all()

    categories = [
        CategoryDensity(
            category=category,
            count=count,
            percentage=round((count / total_items) * 100, 2),
        )
        for category, count in rows
    ]

    response_data = CategoryDensityResponse(total_items=total_items, categories=categories)

    # Save to cache (5 minutes)
    await set_cache(cache_key, response_data.model_dump(), expire=300)

    return response_data


@router.post("", response_model=ItemResponse, status_code=201)
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

    # Invalidate analytics cache
    await delete_cache("analytics:*")

    return new_item


@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Item).where(Item.id == item_id, Item.is_deleted == False)  # noqa: E712
    )
    item = result.scalar_one_or_none()

    verify_item(item, item_id)
    return item


@router.get("", response_model=ItemListResponse)
async def list_items(
    page: int = Query(1, ge=1),
    per_page: int = Query(5, ge=1, le=20),
    category: Optional[str] = Query(None),
    sort_by: Optional[str] = Query("created_at"),
    order: str = Query("desc", pattern="^(asc|desc)$"),  # regex deprecated, using pattern
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Item).where(Item.is_deleted == False)  # noqa: E712
    count_query = (
        select(func.count()).select_from(Item).where(Item.is_deleted == False)  # noqa: E712
    )

    if category:
        query = query.where(Item.category == category)
        count_query = count_query.where(Item.category == category)

    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Only allow sorting by specific fields
    allowed_sort_fields = {
        "created_at": Item.created_at,
        "name": Item.name,
        "category": Item.category,
    }

    sort_column = allowed_sort_fields.get(sort_by, Item.created_at)
    query = query.order_by(sort_column.desc() if order == "desc" else sort_column.asc())

    # Pagination stuff
    offset = (page - 1) * per_page
    query = query.offset(offset).limit(per_page)

    result = await db.execute(query)
    items = result.scalars().all()

    return ItemListResponse(
        items=items,
        total=total,
        page=page,
        per_page=per_page,
        pages=(total + per_page - 1) // per_page,
    )


@router.patch("/{item_id}", response_model=ItemResponse)
async def update_item(
    item_id: int,
    data: ItemUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Item).where(Item.id == item_id, Item.is_deleted == False)  # noqa: E712
    )
    item = result.scalar_one_or_none()

    verify_item(item, item_id)

    # Let's do this the smart way instead of 100 'if' statements
    update_info = data.model_dump(exclude_unset=True)
    for key, value in update_info.items():
        setattr(item, key, value)

    await db.flush()
    await db.refresh(item)
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Just a soft delete, we're not monsters who destroy data permanently
    result = await db.execute(
        select(Item).where(Item.id == item_id, Item.is_deleted == False)  # noqa: E712
    )
    item = result.scalar_one_or_none()

    verify_item(item, item_id)

    item.is_deleted = True
    await db.flush()

    # Invalidate analytics cache
    await delete_cache("analytics:*")
