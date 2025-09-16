#!/usr/bin/env python3
from pydantic import BaseModel, Field
from typing import List, Optional, Union
import json
import random
import asyncio

from fastmcp import FastMCP

# Data Models with proper Pydantic v2 syntax
class HoldingInvoice(BaseModel):
    """홀딩된 인보이스 정보"""
    model_config = {"json_schema_extra": {"example": {"id": "INV-001", "status": "holding", "reason": "발주금액 불일치"}}}
    
    id: str = Field(..., description="인보이스 ID")
    status: str = Field(..., description="인보이스 상태")
    reason: str = Field(..., description="홀딩 사유")

class HoldingReasonDetail(BaseModel):
    """홀딩 사유 상세 정보"""
    model_config = {"json_schema_extra": {"example": {
        "invoice_id": "INV-001",
        "reason": "발주금액 불일치",
        "detail": "발주서의 단가(₩15,000)와 인보이스의 단가(₩18,000)가 일치하지 않습니다.",
        "search_query": "발주금액 불일치 처리 절차"
    }}}
    
    invoice_id: str = Field(..., description="인보이스 ID")
    reason: str = Field(..., description="홀딩 사유")
    detail: str = Field(..., description="상세 설명")
    search_query: str = Field(..., description="관련 검색 키워드")

class ErrorResponse(BaseModel):
    """에러 응답"""
    error: str = Field(..., description="에러 메시지")
    available_ids: Optional[List[str]] = Field(None, description="사용 가능한 ID 목록")

class InvoiceStatistics(BaseModel):
    """인보이스 통계 정보"""
    model_config = {"json_schema_extra": {"example": {
        "total_holding": 10,
        "reason_distribution": {"발주금액 불일치": 1, "수량 불일치": 1},
        "most_common_reason": "발주금액 불일치",
        "most_common_count": 1,
        "unique_reasons": 8
    }}}
    
    total_holding: int = Field(..., description="총 홀딩 인보이스 수")
    reason_distribution: dict = Field(..., description="사유별 분포")
    most_common_reason: str = Field(..., description="가장 많은 사유")
    most_common_count: int = Field(..., description="가장 많은 사유의 건수")
    unique_reasons: int = Field(..., description="고유 사유 수")

# Mock 데이터
MOCK_HOLDING_INVOICES = [
    {"id": "INV-001", "status": "holding", "reason": "발주금액 불일치"},
    {"id": "INV-002", "status": "holding", "reason": "수량 불일치"},
    {"id": "INV-003", "status": "holding", "reason": "재고 부족"},
    {"id": "INV-004", "status": "holding", "reason": "승인자 부재"},
    {"id": "INV-005", "status": "holding", "reason": "예산 초과"},
    {"id": "INV-006", "status": "holding", "reason": "공급업체 신용도 검토 필요"},
    {"id": "INV-007", "status": "holding", "reason": "계약서 조건 불일치"},
    {"id": "INV-008", "status": "holding", "reason": "세금 계산 오류"},
    {"id": "INV-009", "status": "holding", "reason": "배송정보 누락"},
    {"id": "INV-010", "status": "holding", "reason": "중복 인보이스"},
]

# 홀딩 사유별 상세 정보
HOLDING_REASON_DETAILS = {
    "INV-001": {
        "reason": "발주금액 불일치",
        "detail": "발주서의 단가(₩15,000)와 인보이스의 단가(₩18,000)가 일치하지 않습니다. 총 금액 차이: ₩30,000 (10개 항목)",
        "search_query": "발주금액 불일치 처리 절차 단가 차이 승인"
    },
    "INV-002": {
        "reason": "수량 불일치", 
        "detail": "발주 수량 100개에 대해 인보이스 수량이 85개로 15개 부족합니다. 부분 납품에 대한 확인이 필요합니다.",
        "search_query": "수량 불일치 부분납품 처리방법 검수확인"
    },
    "INV-003": {cha
        "reason": "재고 부족",
        "detail": "현재 재고량 50개, 발주량 200개로 재고가 150개 부족합니다. 추가 발주 또는 납기 조정이 필요합니다.",
        "search_query": "재고부족 시 처리절차 추가발주 납기조정"
    },
    "INV-004": {
        "reason": "승인자 부재",
        "detail": "담당 승인자(김부장)가 출장 중이며, 대리 승인자 지정이 필요합니다. 승인 한도: ₩5,000,000",
        "search_query": "승인자 부재 대리승인 권한위임 절차"
    },
    "INV-005": {
        "reason": "예산 초과",
        "detail": "해당 부서 월 예산 ₩10,000,000 중 이미 ₩9,500,000 사용. 인보이스 금액 ₩800,000로 예산 초과",
        "search_query": "예산초과 처리방법 추경예산 승인절차"
    },
    "INV-006": {
        "reason": "공급업체 신용도 검토 필요",
        "detail": "신규 공급업체로 신용평가가 미완료 상태입니다. 신용등급 확인 및 보증보험 가입 여부 검토 필요",
        "search_query": "신규공급업체 신용평가 보증보험 검토절차"
    },
    "INV-007": {
        "reason": "계약서 조건 불일치",
        "detail": "계약서상 지불조건 Net 30일이나 인보이스는 Net 15일로 표시. 계약 조건 재확인 필요",
        "search_query": "계약조건 불일치 지불조건 수정절차"
    },
    "INV-008": {
        "reason": "세금 계산 오류",
        "detail": "부가세 계산이 잘못됨. 공급가액 ₩1,000,000에 대해 부가세 ₩90,000 (9%)로 계산되어야 하나 ₩100,000 (10%)로 계산됨",
        "search_query": "세금계산 오류 부가세 수정 세무처리"
    },
    "INV-009": {
        "reason": "배송정보 누락",
        "detail": "배송지 주소, 담당자 연락처가 인보이스에 누락되어 있습니다. 물류 처리를 위해 정보 보완 필요",
        "search_query": "배송정보 누락 주소확인 물류처리절차"
    },
    "INV-010": {
        "reason": "중복 인보이스",
        "detail": "동일한 발주번호(PO-2024-001)에 대해 이미 처리된 인보이스(INV-001)가 존재합니다. 중복 처리 방지 필요",
        "search_query": "중복인보이스 처리 발주번호 확인절차"
    }
}

# FastMCP 앱 초기화
mcp = FastMCP("Invoice Holding Management Server")

@mcp.tool()
def list_holding_invoices() -> List[HoldingInvoice]:
    """
    홀딩된 인보이스 목록을 반환합니다.
    
    현재 시스템에서 홀딩 상태인 모든 인보이스의 기본 정보를 조회할 수 있습니다.
    각 인보이스는 고유 ID, 상태, 그리고 홀딩 사유를 포함합니다.
    
    Returns:
        List[HoldingInvoice]: 홀딩된 인보이스 목록
        
    Example:
        ```json
        [
            {
                "id": "INV-001",
                "status": "holding", 
                "reason": "발주금액 불일치"
            },
            {
                "id": "INV-002",
                "status": "holding",
                "reason": "수량 불일치"
            }
        ]
        ```
    """
    return [HoldingInvoice(**invoice) for invoice in MOCK_HOLDING_INVOICES]

@mcp.tool()
def get_holding_reason_detail(invoice_id: str) -> Union[HoldingReasonDetail, ErrorResponse]:
    """
    특정 홀딩 인보이스의 상세 사유를 반환합니다.
    
    지정된 인보이스 ID에 대한 상세한 홀딩 사유, 처리 가이드라인,
    그리고 관련 검색 키워드를 제공합니다.
    
    Args:
        invoice_id: 조회할 인보이스 ID (예: INV-001)
        
    Returns:
        HoldingReasonDetail: 상세 사유 정보
        ErrorResponse: 인보이스를 찾을 수 없는 경우
        
    Example:
        ```json
        {
            "invoice_id": "INV-001",
            "reason": "발주금액 불일치",
            "detail": "발주서의 단가(₩15,000)와 인보이스의 단가(₩18,000)가 일치하지 않습니다.",
            "search_query": "발주금액 불일치 처리 절차 단가 차이 승인"
        }
        ```
    """
    if invoice_id not in HOLDING_REASON_DETAILS:
        return ErrorResponse(
            error=f"Invoice ID '{invoice_id}' not found in holding list",
            available_ids=list(HOLDING_REASON_DETAILS.keys())
        )
    
    detail_info = HOLDING_REASON_DETAILS[invoice_id]
    return HoldingReasonDetail(
        invoice_id=invoice_id,
        reason=detail_info["reason"],
        detail=detail_info["detail"],
        search_query=detail_info["search_query"]
    )

@mcp.tool()
def get_all_holding_reason_details() -> List[HoldingReasonDetail]:
    """
    모든 홀딩 인보이스의 상세 사유를 반환합니다.
    
    시스템의 모든 홀딩된 인보이스에 대한 상세 정보를 한 번에 조회할 수 있습니다.
    각 항목에는 홀딩 사유, 상세 설명, 처리 가이드라인이 포함됩니다.
    
    Returns:
        List[HoldingReasonDetail]: 모든 홀딩 사유 상세 정보 목록
        
    Note:
        이 기능은 대량의 데이터를 반환할 수 있으므로 필요한 경우에만 사용하세요.
        특정 인보이스 정보만 필요한 경우 get_holding_reason_detail을 사용하는 것이 효율적입니다.
    """
    result = []
    for invoice_id, detail_info in HOLDING_REASON_DETAILS.items():
        result.append(HoldingReasonDetail(
            invoice_id=invoice_id,
            reason=detail_info["reason"],
            detail=detail_info["detail"],
            search_query=detail_info["search_query"]
        ))
    return result

@mcp.tool()
def get_invoice_statistics() -> InvoiceStatistics:
    """
    홀딩 인보이스 통계 정보를 반환합니다.
    
    현재 홀딩된 인보이스의 통계 정보와 사유별 분포를 제공합니다.
    
    Returns:
        InvoiceStatistics: 통계 정보
        
    Example:
        ```json
        {
            "total_holding": 10,
            "reason_distribution": {
                "발주금액 불일치": 1,
                "수량 불일치": 1
            },
            "most_common_reason": "발주금액 불일치"
        }
        ```
    """
    reason_count = {}
    for invoice in MOCK_HOLDING_INVOICES:
        reason = invoice["reason"]
        reason_count[reason] = reason_count.get(reason, 0) + 1
    
    most_common = max(reason_count.items(), key=lambda x: x[1]) if reason_count else ("없음", 0)
    
    return InvoiceStatistics(
        total_holding=len(MOCK_HOLDING_INVOICES),
        reason_distribution=reason_count,
        most_common_reason=most_common[0],
        most_common_count=most_common[1],
        unique_reasons=len(reason_count)
    )

def save_openapi_schema():
    """OpenAPI 스키마를 JSON 파일로 저장합니다."""
    import inspect
    from pydantic._internal._model_serialization import to_jsonable_python
    
    # 간단한 OpenAPI 스키마 생성
    openapi_schema = {
        "openapi": "3.0.0",
        "info": {
            "title": "Invoice Holding Management API",
            "description": "홀딩된 인보이스를 관리하는 MCP 서버",
            "version": "1.0.0",
            "contact": {
                "name": "Invoice Management Team",
                "email": "support@company.com"
            }
        },
        "servers": [
            {
                "url": "http://localhost:3000",
                "description": "Local MCP Server"
            }
        ],
        "paths": {},
        "components": {
            "schemas": {
                "HoldingInvoice": HoldingInvoice.model_json_schema(),
                "HoldingReasonDetail": HoldingReasonDetail.model_json_schema(),
                "ErrorResponse": ErrorResponse.model_json_schema(),
                "InvoiceStatistics": InvoiceStatistics.model_json_schema()
            }
        }
    }
    
    # MCP 도구들을 OpenAPI paths로 변환
    tools = [
        ("list_holding_invoices", "GET", "/api/v1/invoices/holding", "홀딩된 인보이스 목록 조회"),
        ("get_holding_reason_detail", "GET", "/api/v1/invoices/holding/{invoice_id}/reason", "특정 인보이스 홀딩 사유 조회"),
        ("get_all_holding_reason_details", "GET", "/api/v1/invoices/holding/reasons/all", "모든 홀딩 사유 조회"),
        ("get_invoice_statistics", "GET", "/api/v1/invoices/statistics", "인보이스 통계 조회")
    ]
    
    for tool_name, method, path, summary in tools:
        openapi_schema["paths"][path] = {
            method.lower(): {
                "summary": summary,
                "operationId": tool_name,
                "responses": {
                    "200": {
                        "description": "성공적인 응답",
                        "content": {
                            "application/json": {
                                "schema": {"type": "object"}
                            }
                        }
                    }
                }
            }
        }
        
        if "{invoice_id}" in path:
            openapi_schema["paths"][path][method.lower()]["parameters"] = [
                {
                    "name": "invoice_id",
                    "in": "path",
                    "required": True,
                    "schema": {"type": "string"},
                    "description": "인보이스 ID",
                    "example": "INV-001"
                }
            ]
    
    # OpenAPI 스키마를 파일로 저장
    with open("openapi_schema.json", "w", encoding="utf-8") as f:
        json.dump(openapi_schema, f, indent=2, ensure_ascii=False)
    
    print("📄 OpenAPI 스키마가 'openapi_schema.json' 파일로 저장되었습니다.")
    return openapi_schema

if __name__ == "__main__":
    print("🚀 Invoice Holding Management Server 시작")
    print("🌐 MCP Server: http://localhost:3000")
    print("🔧 MCP Tools: 4개의 도구가 등록됨")
    print("")
    print("📚 OpenAPI 문서를 생성하려면:")
    print("   1. 서버를 실행한 후")
    print("   2. 별도 터미널에서 'uvx mcpo --port 8000 -- python hold_resolve_mcp.py' 실행")
    print("   3. http://localhost:8000/docs 에서 Swagger UI 확인")
    print("")
    print("또는 다음 명령으로 OpenAPI 스키마 파일을 생성:")
    print("   python -c \"from hold_resolve_mcp import save_openapi_schema; save_openapi_schema()\"")
    
    # OpenAPI 스키마 파일 자동 생성 (안전하게)
    try:
        save_openapi_schema()
    except Exception as e:
        print(f"⚠️  OpenAPI 스키마 생성을 건너뜁니다: {e}")
    
    print("\n🎯 MCP 서버 시작 중...")
    mcp.run(transport="streamable-http", port=3000)