#!/usr/bin/env python3
# # OCI 설정 필요
#export OCI_CONFIG_FILE=~/.oci/config
#export OCI_CONFIG_PROFILE=DXOCIAGENT

import asyncio
from mcp.client.session_group import StreamableHttpParameters
from oci.addons.adk import Agent, AgentClient, tool
from oci.addons.adk.mcp import MCPClientStreamableHttp

async def main():
    # MCP 서버 연결 설정 (FastMCP 서버가 실행되는 주소)
    params = StreamableHttpParameters(
        url="http://localhost:3000/mcp",  # FastMCP 서버 주소
    )

    async with MCPClientStreamableHttp(
        params=params,
        name="Invoice Holding MCP Server",
    ) as mcp_client:

        # OCI Agent Client 설정
        client = AgentClient(
            auth_type="api_key",  # 또는 auth_type="security_token"
            profile="DEFAULT",  # OCI config profile 이름
            region="ap-osaka-1"    # 사용할 OCI 리전
        )

        # Agent 설정 - 인보이스 홀딩 관리를 위한 지시사항 추가
        agent = Agent(
            client=client,
            agent_endpoint_id="ocid1.genaiagentendpoint.oc1.ap-osaka-1.amaaaaaarykjadqah2zw7mxczrxoa6o3ebdneenum4s5g5mqfk2urommiytq",
            instructions="""
            당신은 인보이스 홀딩 관리 전문가입니다. 
            사용자의 질문에 따라 적절한 도구를 사용하여 다음과 같은 작업을 수행하세요:
            1. 홀딩된 인보이스 목록 조회
            2. 특정 인보이스의 홀딩 사유 상세 조회
            3. 규정집 검색을 위한 키워드 제공
            
            한국어로 친절하고 상세하게 답변해주세요.
            """,
            tools=[await mcp_client.as_toolkit()],
        )

        # tool setting 이 안된 경우에만.
        # agent.setup()

        print("=== Invoice Holding Management Client ===\n")

        # 테스트 케이스 1: 홀딩된 인보이스 목록 조회
        input_message = "홀딩된 인보이스 목록을 보여주세요."
        print(f"🔍 실행: {input_message}")
        response = await agent.run_async(input_message)
        response.pretty_print()
        print("\n" + "="*60 + "\n")

        # 테스트 케이스 2: 특정 인보이스 상세 사유 조회
        input_message = "INV-001 인보이스의 홀딩 사유를 자세히 알려주세요."
        print(f"🔍 실행: {input_message}")
        response = await agent.run_async(input_message)
        response.pretty_print()
        print("\n" + "="*60 + "\n")

        # 테스트 케이스 3: 다른 인보이스 조회
        input_message = "INV-005 인보이스는 왜 홀딩되었나요? 규정집 검색 키워드도 알려주세요."
        print(f"🔍 실행: {input_message}")
        response = await agent.run_async(input_message)
        response.pretty_print()
        print("\n" + "="*60 + "\n")

        # 테스트 케이스 4: 존재하지 않는 인보이스 조회
        input_message = "INV-999 인보이스 정보를 알려주세요."
        print(f"🔍 실행: {input_message}")
        response = await agent.run_async(input_message)
        response.pretty_print()
        print("\n" + "="*60 + "\n")

        # 테스트 케이스 5: 모든 홀딩 사유 조회
        input_message = "모든 홀딩된 인보이스의 상세 사유를 보여주세요."
        print(f"🔍 실행: {input_message}")
        response = await agent.run_async(input_message)
        response.pretty_print()
        print("\n" + "="*60 + "\n")

        # 대화형 모드
        print("💬 대화형 모드를 시작합니다. 'quit' 또는 'exit'를 입력하면 종료됩니다.\n")
        
        while True:
            try:
                user_input = input("❓ 질문: ").strip()
                
                if user_input.lower() in ['quit', 'exit', '종료', '나가기']:
                    print("👋 클라이언트를 종료합니다.")
                    break
                
                if not user_input:
                    continue
                
                print(f"\n🔍 처리 중: {user_input}")
                response = await agent.run_async(user_input)
                response.pretty_print()
                print("\n" + "-"*40 + "\n")
                
            except KeyboardInterrupt:
                print("\n\n👋 클라이언트를 종료합니다.")
                break
            except Exception as e:
                print(f"❌ 오류 발생: {e}")
                continue

if __name__ == "__main__":
    print("🚀 Invoice Holding MCP Client 시작...")
    asyncio.run(main())