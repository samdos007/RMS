"""Earnings endpoints."""

import csv
import io
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies import get_current_user
from app.models.earnings import Earnings, PeriodType
from app.models.folder import Folder
from app.models.user import User
from app.schemas.earnings import (
    EarningsCreate,
    EarningsListResponse,
    EarningsResponse,
    EarningsUpdate,
)
from app.services.earnings_service import fetch_earnings_from_yfinance

router = APIRouter(tags=["earnings"])


def earnings_to_response(earnings: Earnings) -> EarningsResponse:
    """Convert Earnings model to response schema."""
    return EarningsResponse(
        id=earnings.id,
        folder_id=earnings.folder_id,
        ticker=earnings.ticker,
        period_type=earnings.period_type,
        period=earnings.period,
        fiscal_quarter=earnings.fiscal_quarter,
        period_end_date=earnings.period_end_date,
        estimate_eps=earnings.estimate_eps,
        actual_eps=earnings.actual_eps,
        estimate_rev=earnings.estimate_rev,
        actual_rev=earnings.actual_rev,
        estimate_ebitda=earnings.estimate_ebitda,
        actual_ebitda=earnings.actual_ebitda,
        estimate_fcf=earnings.estimate_fcf,
        actual_fcf=earnings.actual_fcf,
        my_estimate_eps=earnings.my_estimate_eps,
        my_estimate_rev=earnings.my_estimate_rev,
        my_estimate_ebitda=earnings.my_estimate_ebitda,
        my_estimate_fcf=earnings.my_estimate_fcf,
        eps_surprise=earnings.eps_surprise,
        eps_surprise_pct=earnings.eps_surprise_pct,
        rev_surprise=earnings.rev_surprise,
        rev_surprise_pct=earnings.rev_surprise_pct,
        ebitda_surprise_pct=earnings.ebitda_surprise_pct,
        fcf_surprise_pct=earnings.fcf_surprise_pct,
        notes=earnings.notes,
        created_at=earnings.created_at,
        updated_at=earnings.updated_at,
    )


@router.get("/folders/{folder_id}/earnings", response_model=EarningsListResponse)
async def list_earnings(
    folder_id: str,
    ticker: Optional[str] = Query(None, description="Filter by specific ticker"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EarningsListResponse:
    """
    List earnings for a folder.

    For PAIR folders, you can filter by ticker to see earnings for just one leg.
    """
    folder = db.query(Folder).filter(Folder.id == folder_id).first()
    if not folder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Folder not found",
        )

    query = db.query(Earnings).filter(Earnings.folder_id == folder_id)

    if ticker:
        query = query.filter(Earnings.ticker == ticker.upper())

    earnings_list = query.order_by(Earnings.fiscal_quarter.desc()).all()

    return EarningsListResponse(
        earnings=[earnings_to_response(e) for e in earnings_list],
        total=len(earnings_list),
    )


@router.post("/earnings", response_model=EarningsResponse, status_code=status.HTTP_201_CREATED)
async def create_earnings(
    request: EarningsCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EarningsResponse:
    """
    Create a new earnings record.
    """
    folder = db.query(Folder).filter(Folder.id == request.folder_id).first()
    if not folder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Folder not found",
        )

    # Validate ticker belongs to folder
    if request.ticker.upper() not in folder.tickers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ticker {request.ticker} does not belong to folder {folder.name}",
        )

    # Check for duplicate
    existing = (
        db.query(Earnings)
        .filter(
            Earnings.folder_id == request.folder_id,
            Earnings.ticker == request.ticker.upper(),
            Earnings.fiscal_quarter == request.fiscal_quarter,
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Earnings for {request.ticker} {request.fiscal_quarter} already exists",
        )

    earnings = Earnings(
        folder_id=request.folder_id,
        ticker=request.ticker.upper(),
        period_type=request.period_type,
        period=request.period or request.fiscal_quarter,
        fiscal_quarter=request.fiscal_quarter,
        period_end_date=request.period_end_date,
        estimate_eps=request.estimate_eps,
        actual_eps=request.actual_eps,
        estimate_rev=request.estimate_rev,
        actual_rev=request.actual_rev,
        estimate_ebitda=request.estimate_ebitda,
        actual_ebitda=request.actual_ebitda,
        estimate_fcf=request.estimate_fcf,
        actual_fcf=request.actual_fcf,
        my_estimate_eps=request.my_estimate_eps,
        my_estimate_rev=request.my_estimate_rev,
        my_estimate_ebitda=request.my_estimate_ebitda,
        my_estimate_fcf=request.my_estimate_fcf,
        notes=request.notes,
    )

    db.add(earnings)
    db.commit()
    db.refresh(earnings)

    return earnings_to_response(earnings)


@router.get("/earnings/{earnings_id}", response_model=EarningsResponse)
async def get_earnings(
    earnings_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EarningsResponse:
    """
    Get earnings by ID.
    """
    earnings = db.query(Earnings).filter(Earnings.id == earnings_id).first()
    if not earnings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Earnings not found",
        )

    return earnings_to_response(earnings)


@router.put("/earnings/{earnings_id}", response_model=EarningsResponse)
async def update_earnings(
    earnings_id: str,
    request: EarningsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EarningsResponse:
    """
    Update earnings data.
    """
    earnings = db.query(Earnings).filter(Earnings.id == earnings_id).first()
    if not earnings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Earnings not found",
        )

    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(earnings, field, value)

    db.commit()
    db.refresh(earnings)

    return earnings_to_response(earnings)


@router.delete("/earnings/{earnings_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_earnings(
    earnings_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """
    Delete earnings record.
    """
    earnings = db.query(Earnings).filter(Earnings.id == earnings_id).first()
    if not earnings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Earnings not found",
        )

    db.delete(earnings)
    db.commit()


@router.get("/folders/{folder_id}/earnings/export")
async def export_earnings_csv(
    folder_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StreamingResponse:
    """
    Export earnings data as CSV.
    """
    folder = db.query(Folder).filter(Folder.id == folder_id).first()
    if not folder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Folder not found",
        )

    earnings_list = (
        db.query(Earnings)
        .filter(Earnings.folder_id == folder_id)
        .order_by(Earnings.ticker, Earnings.fiscal_quarter)
        .all()
    )

    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow([
        "ticker",
        "fiscal_quarter",
        "period_end_date",
        "estimate_eps",
        "actual_eps",
        "estimate_rev",
        "actual_rev",
        "notes",
    ])

    # Write data rows
    for e in earnings_list:
        writer.writerow([
            e.ticker,
            e.fiscal_quarter,
            e.period_end_date.isoformat() if e.period_end_date else "",
            str(e.estimate_eps) if e.estimate_eps is not None else "",
            str(e.actual_eps) if e.actual_eps is not None else "",
            str(e.estimate_rev) if e.estimate_rev is not None else "",
            str(e.actual_rev) if e.actual_rev is not None else "",
            e.notes or "",
        ])

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={folder.name}_earnings.csv"
        },
    )


@router.post("/folders/{folder_id}/earnings/import")
async def import_earnings_csv(
    folder_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """
    Import earnings data from CSV.

    CSV should have columns: ticker, fiscal_quarter, period_end_date,
    estimate_eps, actual_eps, estimate_rev, actual_rev, notes

    Existing records with same ticker+fiscal_quarter will be updated.
    """
    folder = db.query(Folder).filter(Folder.id == folder_id).first()
    if not folder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Folder not found",
        )

    # Read CSV content
    content = await file.read()
    text = content.decode("utf-8")
    reader = csv.DictReader(io.StringIO(text))

    created_count = 0
    updated_count = 0
    errors = []

    for row_num, row in enumerate(reader, start=2):  # Start at 2 to account for header
        try:
            ticker = row.get("ticker", "").strip().upper()
            fiscal_quarter = row.get("fiscal_quarter", "").strip()

            if not ticker or not fiscal_quarter:
                errors.append(f"Row {row_num}: ticker and fiscal_quarter are required")
                continue

            # Validate ticker belongs to folder
            if ticker not in folder.tickers:
                errors.append(f"Row {row_num}: ticker {ticker} not in folder")
                continue

            # Parse optional fields
            period_end_date = None
            if row.get("period_end_date"):
                try:
                    period_end_date = date.fromisoformat(row["period_end_date"])
                except ValueError:
                    errors.append(f"Row {row_num}: invalid date format")
                    continue

            def parse_decimal(value: str) -> Optional[Decimal]:
                if not value or not value.strip():
                    return None
                try:
                    return Decimal(value.strip())
                except InvalidOperation:
                    return None

            # Check if exists
            existing = (
                db.query(Earnings)
                .filter(
                    Earnings.folder_id == folder_id,
                    Earnings.ticker == ticker,
                    Earnings.fiscal_quarter == fiscal_quarter,
                )
                .first()
            )

            if existing:
                # Update existing
                existing.period_end_date = period_end_date
                existing.estimate_eps = parse_decimal(row.get("estimate_eps", ""))
                existing.actual_eps = parse_decimal(row.get("actual_eps", ""))
                existing.estimate_rev = parse_decimal(row.get("estimate_rev", ""))
                existing.actual_rev = parse_decimal(row.get("actual_rev", ""))
                existing.notes = row.get("notes", "").strip() or None
                updated_count += 1
            else:
                # Create new
                earnings = Earnings(
                    folder_id=folder_id,
                    ticker=ticker,
                    fiscal_quarter=fiscal_quarter,
                    period_end_date=period_end_date,
                    estimate_eps=parse_decimal(row.get("estimate_eps", "")),
                    actual_eps=parse_decimal(row.get("actual_eps", "")),
                    estimate_rev=parse_decimal(row.get("estimate_rev", "")),
                    actual_rev=parse_decimal(row.get("actual_rev", "")),
                    notes=row.get("notes", "").strip() or None,
                )
                db.add(earnings)
                created_count += 1

        except Exception as e:
            errors.append(f"Row {row_num}: {str(e)}")

    db.commit()

    return {
        "created": created_count,
        "updated": updated_count,
        "errors": errors[:10] if errors else [],  # Limit error messages
        "total_errors": len(errors),
    }


@router.post("/folders/{folder_id}/earnings/fetch")
async def fetch_earnings(
    folder_id: str,
    ticker: str = Query(..., description="Ticker to fetch earnings for"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """
    Fetch earnings data from Yahoo Finance and populate actual values.

    This endpoint fetches:
    - Last 5 quarters of quarterly data
    - Last 3 years of annual data

    Only populates actual_* fields (not estimates).
    Creates or updates earnings records.
    """
    folder = db.query(Folder).filter(Folder.id == folder_id).first()
    if not folder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Folder not found",
        )

    # Validate ticker belongs to folder
    ticker_upper = ticker.upper()
    if ticker_upper not in folder.tickers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ticker {ticker} does not belong to folder {folder.name}",
        )

    # Fetch data from yfinance
    try:
        data = fetch_earnings_from_yfinance(ticker_upper)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch data from Yahoo Finance: {str(e)}",
        )

    created_count = 0
    updated_count = 0

    # Process quarterly data
    for earnings_data in data["quarterly"]:
        existing = (
            db.query(Earnings)
            .filter(
                Earnings.folder_id == folder_id,
                Earnings.ticker == ticker_upper,
                Earnings.fiscal_quarter == earnings_data.period,
            )
            .first()
        )

        if existing:
            # Update only actual values
            existing.period_type = PeriodType.QUARTERLY
            existing.period = earnings_data.period
            existing.period_end_date = earnings_data.period_end_date
            existing.actual_eps = earnings_data.eps
            existing.actual_rev = earnings_data.revenue
            existing.actual_ebitda = earnings_data.ebitda
            existing.actual_fcf = earnings_data.fcf
            updated_count += 1
        else:
            # Create new record with actual values only
            new_earnings = Earnings(
                folder_id=folder_id,
                ticker=ticker_upper,
                period_type=PeriodType.QUARTERLY,
                period=earnings_data.period,
                fiscal_quarter=earnings_data.period,
                period_end_date=earnings_data.period_end_date,
                actual_eps=earnings_data.eps,
                actual_rev=earnings_data.revenue,
                actual_ebitda=earnings_data.ebitda,
                actual_fcf=earnings_data.fcf,
            )
            db.add(new_earnings)
            created_count += 1

    # Process annual data
    for earnings_data in data["annual"]:
        existing = (
            db.query(Earnings)
            .filter(
                Earnings.folder_id == folder_id,
                Earnings.ticker == ticker_upper,
                Earnings.fiscal_quarter == earnings_data.period,
            )
            .first()
        )

        if existing:
            # Update only actual values
            existing.period_type = PeriodType.ANNUAL
            existing.period = earnings_data.period
            existing.period_end_date = earnings_data.period_end_date
            existing.actual_eps = earnings_data.eps
            existing.actual_rev = earnings_data.revenue
            existing.actual_ebitda = earnings_data.ebitda
            existing.actual_fcf = earnings_data.fcf
            updated_count += 1
        else:
            # Create new record with actual values only
            new_earnings = Earnings(
                folder_id=folder_id,
                ticker=ticker_upper,
                period_type=PeriodType.ANNUAL,
                period=earnings_data.period,
                fiscal_quarter=earnings_data.period,
                period_end_date=earnings_data.period_end_date,
                actual_eps=earnings_data.eps,
                actual_rev=earnings_data.revenue,
                actual_ebitda=earnings_data.ebitda,
                actual_fcf=earnings_data.fcf,
            )
            db.add(new_earnings)
            created_count += 1

    db.commit()

    return {
        "ticker": ticker_upper,
        "created": created_count,
        "updated": updated_count,
        "message": f"Fetched {created_count + updated_count} earnings records from Yahoo Finance",
    }
