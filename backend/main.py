from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="麻雀点数計算API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ScoreRequest(BaseModel):
    han: int
    fu: int
    is_dealer: bool
    is_tsumo: bool


class ScoreResponse(BaseModel):
    basic_points: int
    dealer_payment: Optional[int]
    non_dealer_payment: Optional[int]
    dealer_tsumo: Optional[int]
    non_dealer_tsumo: Optional[int]


def round_up_to_100(points: int) -> int:
    return ((points + 99) // 100) * 100


def calculate_basic_points(han: int, fu: int) -> int:
    return fu * (2 ** (han + 2))


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/score", response_model=ScoreResponse)
def calculate_score(req: ScoreRequest) -> ScoreResponse:
    han, fu, is_dealer, is_tsumo = req.han, req.fu, req.is_dealer, req.is_tsumo

    # 満貫以上の固定点数
    if han >= 13:
        basic = 8000
    elif han >= 11:
        basic = 6000
    elif han >= 8:
        basic = 4000
    elif han >= 6:
        basic = 3000
    elif han >= 5 or (han >= 4 and fu >= 30) or (han >= 3 and fu >= 70):
        basic = 2000
    else:
        basic = calculate_basic_points(han, fu)
        basic = min(basic, 2000)

    response = ScoreResponse(
        basic_points=basic,
        dealer_payment=None,
        non_dealer_payment=None,
        dealer_tsumo=None,
        non_dealer_tsumo=None,
    )

    if is_dealer:
        if is_tsumo:
            response.dealer_tsumo = round_up_to_100(basic * 2)
        else:
            response.dealer_payment = round_up_to_100(basic * 6)
    else:
        if is_tsumo:
            response.dealer_tsumo = round_up_to_100(basic * 2)
            response.non_dealer_tsumo = round_up_to_100(basic)
        else:
            response.dealer_payment = round_up_to_100(basic * 4)
            response.non_dealer_payment = round_up_to_100(basic * 2)

    return response
