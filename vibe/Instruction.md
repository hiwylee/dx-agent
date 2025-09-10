당신은 FastMCP 전문가이자 업무 프로세스 설계 전문가입니다. 
다음 요구사항에 따라 완전한 인보이스 홀딩 관리 시스템을 생성해주세요.

### 시스템 요구사항
**도메인**: {구매} (예: 인보이스 홀딩, 구매 승인, 재고 관리 등)
**포트**: {포트번호} (기본값: 3000)
**홀딩 사유**: {홀딩_사유_목록} (기본값: 10가지 표준 사유)
**Transport 방식**: streamable-http

### 필수 생성 항목
1. **FastMCP 서버 코드** (Python)
   - Mock 데이터와 실제 사용 가능한 도구 함수
   - 포트 설정 및 transport 옵션 포함
   - Error handling 및 validation 로직

2. **MCP 클라이언트 코드** (Python)
   - OCI Agent 연동 코드
   - 자동 테스트 케이스 및 대화형 모드
   - 실제 환경에 맞는 설정 가이드

3. **Vector 검색 최적화 규정집** (Markdown)
   - 각 홀딩 사유별 상세 해결 절차
   - 키워드 중심의 검색 최적화 구조
   - 실무진이 바로 활용 가능한 가이드라인

### 기술 스펙
- **언어**: Python 3.12+
- **프레임워크**: FastMCP, OCI ADK
- **데이터 형식**: JSON, Pydantic Models
- **문서 형식**: Markdown (Vector DB 임베딩 최적화)

### 코드 품질 기준
- Type hints 필수 사용
- Error handling 및 validation 포함
- 실제 운영 환경에서 바로 사용 가능한 수준
- 확장성과 유지보수성 고려


지금 바로 완전한 시스템을 생성해주세요.



```python

@mcp.tool()
def list_holding_invoice() -> List[dict]:
    """
    홀딩된 인보이스 목록을 반환합니다.
    
    Returns:
        List[dict]: 홀딩된 인보이스 목록 (id, status, reason 포함)
    """
    return MOCK_HOLDING_INVOICES
```
### 구매 도메인별 특화 실무에서 자주 발생하는 10가지 

- 발주금액 불일치
- 수량 불일치
- 재고 부족
- 승인자 부재
- 예산 초과
- 공급업체 신용도 검토 필요
- 계약서 조건 불일치
- 세금 계산 오류
- 배송정보 누락
- 중복 인보이스

## 코드 형식 샘플