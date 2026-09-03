from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models.finance import Transaction
from app.models.user import User

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.get("", summary="List transactions with filtering, search, sort, pagination")
def get_transactions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    search: Optional[str] = None,
    ttype: Optional[str] = Query(None, alias="type"),
    category: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    sort_by: Optional[str] = "date",
    sort_dir: Optional[str] = "desc",
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
):
    query = db.query(Transaction).filter(Transaction.user_id == current_user.id)

    if search:
        query = query.filter(
            (Transaction.description.ilike(f"%{search}%"))
            | (Transaction.category.ilike(f"%{search}%"))
        )
    if ttype and ttype.lower() != "all":
        query = query.filter(
            Transaction.transaction_type == ("credit" if ttype.lower() == "income" else "debit")
        )
    if category:
        query = query.filter(Transaction.category == category)
    if date_from:
        query = query.filter(Transaction.date >= date_from)
    if date_to:
        query = query.filter(Transaction.date <= date_to)

    col = getattr(Transaction, sort_by, Transaction.date)
    query = query.order_by(col.asc() if sort_dir == "asc" else col.desc())

    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()

    data = [
        {
            "id": t.id,
            "date": t.date.isoformat() if t.date else None,
            "description": t.description,
            "category": t.category,
            "amount": t.amount,
            "type": t.transaction_type,
            "balance": t.balance,
        }
        for t in items
    ]

    return {
        "data": data,
        "total": total,
        "page": page,
        "page_size": page_size,
    }
