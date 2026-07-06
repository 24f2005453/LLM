import re
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class ExtractRequest(BaseModel):
    text: str


class ExtractResponse(BaseModel):
    vendor: str
    amount: float
    currency: str
    date: str


@app.post("/extract", response_model=ExtractResponse)
def extract(req: ExtractRequest):
    text = req.text.strip()

    if not text:
        return ExtractResponse(
            vendor="",
            amount=0.0,
            currency="",
            date=""
        )

    vendor = ""
    amount = 0.0
    currency = ""
    date = ""

    # YYYY-MM-DD
    m = re.search(r"\b(2026-\d{2}-\d{2})\b", text)
    if m:
        date = m.group(1)

    # Currency
    m = re.search(r"\b(USD|EUR|GBP|INR)\b", text, re.IGNORECASE)
    if m:
        currency = m.group(1).upper()

    # Amount
    m = re.search(
        r"(?:Total(?:\s+Due)?|Amount(?:\s+Due)?|Due|Pay(?:able)?)[^\d]*([0-9]+(?:\.[0-9]+)?)",
        text,
        re.IGNORECASE,
    )
    if not m:
        m = re.search(r"([0-9]+(?:\.[0-9]+)?)", text)

    if m:
        amount = float(m.group(1))

    # Vendor
    patterns = [
        r"Vendor[:\s]+(.+?)(?:\n|$)",
        r"From[:\s]+(.+?)(?:\n|$)",
        r"Supplier[:\s]+(.+?)(?:\n|$)",
        r"Bill From[:\s]+(.+?)(?:\n|$)",
    ]

    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            vendor = m.group(1).strip()
            break

    if not vendor:
        lines = [x.strip() for x in text.splitlines() if x.strip()]
        if lines:
            vendor = lines[0]

    return ExtractResponse(
        vendor=vendor,
        amount=amount,
        currency=currency,
        date=date,
    )


@app.get("/")
def root():
    return {"status": "ok"}
