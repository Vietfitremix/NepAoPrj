"""Các endpoint chính của AI theo workflow: quiz → 3 bộ gợi ý → studio (chấm luật) → Hỏi stylist."""
from typing import Union

from fastapi import APIRouter, Depends, Request

from app.api.deps import client_ip, get_service
from app.models import (
    ClarifyResponse, EvaluateRequest, EvaluateResponse, ExplainRequest, ExplainResponse, OutfitsResponse,
    QuizQuestion, ReviewRequest, ReviewResponse, StylistRequest,
)
from app.services.stylist import StylistService

router = APIRouter(tags=["stylist"])


@router.get("/quiz", response_model=list[QuizQuestion],
            summary="① Bộ câu hỏi bối cảnh: dịp, thời tiết, nơi, buổi, vai trò, phong cách, giới tính, màu")
def quiz(svc: StylistService = Depends(get_service)):
    return svc.quiz()


@router.post("/stylist", response_model=Union[OutfitsResponse, ClarifyResponse],
             summary="② Câu trả lời quiz (và/hoặc câu gõ nhanh) → Gemini chọn 3 bộ hợp bối cảnh")
async def stylist(body: StylistRequest, request: Request, svc: StylistService = Depends(get_service)):
    return await svc.stylist(body.text, body.answers, body.override, ip=client_ip(request))


@router.post("/evaluate", response_model=EvaluateResponse,
             summary="③ Chấm luật văn hóa + điểm màu theo bối cảnh (không gọi Gemini, studio gọi mỗi lần đổi đồ)")
def evaluate(body: EvaluateRequest, svc: StylistService = Depends(get_service)):
    return svc.evaluate(body.state, body.context)


@router.post("/review", response_model=ReviewResponse,
             summary="④ Nút 'Hỏi stylist': đánh giá bộ đang mặc theo bối cảnh + kết luận + 2 phương án nâng cấp")
async def review(body: ReviewRequest, request: Request, svc: StylistService = Depends(get_service)):
    return await svc.review(body.state, body.context, body.userRequest, ip=client_ip(request))


@router.post("/explain", response_model=ExplainResponse, summary="Lời nhận xét của stylist cho 1 bộ")
async def explain(body: ExplainRequest, request: Request, svc: StylistService = Depends(get_service)):
    return await svc.explain_one(body.state, body.context, body.userRequest, ip=client_ip(request))
