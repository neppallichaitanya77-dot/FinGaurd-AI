from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models.finance import Loan, LoanPayment
from app.models.user import User

router = APIRouter(prefix="/loans", tags=["Loans"])


def _loan_to_dict(loan: Loan, payments: list = None):
    next_date_str = loan.next_payment_date.isoformat() if loan.next_payment_date else None
    return {
        "id": loan.id,
        "name": loan.name,
        "outstanding_amount": loan.outstanding_amount,
        "outstanding": loan.outstanding_amount,
        "interest_rate": loan.interest_rate,
        "monthly_emi": loan.monthly_emi,
        "emi": loan.monthly_emi,
        "next_payment_date": next_date_str,
        "next_payment": next_date_str,
        "remaining_tenure": loan.remaining_tenure,
        "total_tenure": loan.total_tenure,
        "payments": payments or [],
    }


@router.get("", summary="List active loans")
def get_loans(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    loans = db.query(Loan).filter(Loan.user_id == current_user.id).all()
    result = []
    for loan in loans:
        payments = (
            db.query(LoanPayment).filter(LoanPayment.loan_id == loan.id).all()
        )
        payment_list = [
            {
                "month": p.payment_date.strftime("%b") if p.payment_date else "",
                "principal": p.principal,
                "interest": p.interest,
                "amount": p.amount,
            }
            for p in payments
        ]
        result.append(_loan_to_dict(loan, payment_list))
    return result


@router.get("/{loan_id}", summary="Get a single loan")
def get_loan(
    loan_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    loan = (
        db.query(Loan)
        .filter(Loan.id == loan_id, Loan.user_id == current_user.id)
        .first()
    )
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    return _loan_to_dict(loan)


@router.get("/{loan_id}/payments", summary="Get loan payment history")
def get_loan_payments(
    loan_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    loan = (
        db.query(Loan)
        .filter(Loan.id == loan_id, Loan.user_id == current_user.id)
        .first()
    )
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    payments = db.query(LoanPayment).filter(LoanPayment.loan_id == loan_id).all()
    return [
        {
            "id": p.id,
            "payment_date": p.payment_date.isoformat() if p.payment_date else None,
            "amount": p.amount,
            "principal": p.principal,
            "interest": p.interest,
        }
        for p in payments
    ]
