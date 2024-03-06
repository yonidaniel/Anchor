from fastapi import APIRouter, Body, Depends, HTTPException
from database import get_db
from models import Spreadsheet
from schemas import SheetSchema, CellValueSchema
from flask_sqlalchemy.session import Session
from sqlalchemy import update
import json

router = APIRouter()


@router.post("/sheet", response_model=int, status_code=201)
async def create_sheet(schema: SheetSchema = Body(...), db: Session = Depends(get_db)):
    # Change "double" to "float" - in py there is float and not double - make it easier for me
    json_data = json.dumps(schema.columns, indent=2)
    modified_json = json_data.replace("double", "float")
    schema.columns = json.loads(modified_json)

    new_sheet = Spreadsheet(schema=schema.dict(), data={})
    db.add(new_sheet)
    db.commit()
    db.refresh(new_sheet)  # Refresh object to get assigned ID
    return new_sheet.id


@router.get("/sheet/{sheet_id}")
async def get_sheet(sheet_id: int, db: Session = Depends(get_db)):
    sheet = db.query(Spreadsheet).filter(Spreadsheet.id == sheet_id).first()
    if not sheet:
        raise HTTPException(status_code=404, detail="Sheet not found")
    return sheet


@router.put("/sheets/{sheet_id}/cells/{col}/{row}")
async def set_cell(
        sheet_id: int,
        col: str,
        row: int,
        value: CellValueSchema = Body(...),
        db: Session = Depends(get_db),
):
    try:
        spreadsheet = db.query(Spreadsheet).filter(Spreadsheet.id == sheet_id).first()

        if not spreadsheet:
            raise HTTPException(status_code=404, detail="Spreadsheet not found")

        spreadsheet.set_cell(col, row, value.value)

        update_stmt = update(Spreadsheet).where(Spreadsheet.id == sheet_id) \
            .values(data=spreadsheet.data)
        db.execute(update_stmt)
        db.commit()

        return {"message": "Cell value updated successfully"}

    except Exception as e:  # Catch potential errors
        db.rollback()  # Rollback database changes on error
        raise HTTPException(status_code=500, detail=str(e))