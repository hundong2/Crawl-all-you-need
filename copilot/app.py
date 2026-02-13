"""
AI Web Crawler - LLM 기반 웹사이트 크롤링 & 문서 변환 도구
"""
import streamlit as st
import asyncio
import os
from pathlib import Path

# 시스템 환경 변수만 사용 (os.getenv()로 자동 접근)

# 모듈 임포트
from ai_web_crawler.models.llm_providers import get_llm_provider, LLMProvider
from ai_web_crawler.utils.crawler import create_crawler
from ai_web_crawler.utils.file_exporter import create_exporter


# Streamlit 페이지 설정
st.set_page_config(
    page_title="AI Web Crawler",
    page_icon="🕷️",
    layout="wide"
)

# 타이틀
st.title("🕷️ AI Web Crawler")
st.markdown("**LLM 기반 웹사이트 크롤링 & 문서 변환 도구**")
st.markdown("---")

# 사이드바 설정
with st.sidebar:
    st.header("⚙️ 설정")
    
    # API 키 환경 변수 매핑
    api_key_env_map = {
        "OpenAI (ChatGPT)": "OPENAI_API_KEY",
        "Anthropic (Claude)": "ANTHROPIC_API_KEY",
        "Google (Gemini)": "GEMINI_API_KEY"
    }
    
    # 모든 제공자의 연결 상태 확인
    st.subheader("🔌 연결 상태")
    
    provider_status = {}
    for provider_name, env_var in api_key_env_map.items():
        api_key = os.getenv(env_var, "")
        if api_key:
            try:
                # 임시 제공자 생성하여 연결 확인
                temp_provider = get_llm_provider(provider_name, api_key, "")
                is_connected, status_msg = temp_provider.check_connection()
                provider_status[provider_name] = {
                    "connected": is_connected,
                    "message": status_msg,
                    "api_key": api_key
                }
                # 상태 표시
                if is_connected:
                    st.success(f"**{provider_name.split(' ')[0]}**: {status_msg}")
                else:
                    st.error(f"**{provider_name.split(' ')[0]}**: {status_msg}")
            except Exception as e:
                provider_status[provider_name] = {
                    "connected": False,
                    "message": f"❌ 초기화 실패: {str(e)[:30]}",
                    "api_key": api_key
                }
                st.error(f"**{provider_name.split(' ')[0]}**: ❌ 초기화 실패")
        else:
            provider_status[provider_name] = {
                "connected": False,
                "message": f"⚪ API 키 없음 ({env_var})",
                "api_key": ""
            }
            st.info(f"**{provider_name.split(' ')[0]}**: ⚪ API 키 없음")
    
    st.markdown("---")
    
    # 연결된 제공자만 선택 가능하도록
    available_providers = [
        name for name, status in provider_status.items() 
        if status["connected"]
    ]
    
    if not available_providers:
        st.error("⚠️ 연결된 LLM 제공자가 없습니다. 환경 변수를 설정하세요.")
        st.info("💡 `.env` 파일에 API 키를 추가하거나, 아래에서 직접 입력하세요.")
        
        # 수동 입력 옵션
        manual_provider = st.selectbox(
            "LLM 제공자 선택",
            list(api_key_env_map.keys())
        )
        manual_api_key = st.text_input(
            f"{manual_provider} API 키 입력",
            type="password",
            help=f"{api_key_env_map[manual_provider]} 환경 변수가 설정되지 않았습니다."
        )
        
        if manual_api_key:
            try:
                temp_provider = get_llm_provider(manual_provider, manual_api_key, "")
                is_connected, status_msg = temp_provider.check_connection()
                if is_connected:
                    st.success(f"✅ {status_msg}")
                    provider_name = manual_provider
                    api_key = manual_api_key
                    available_models = temp_provider.get_available_models()
                    selected_model = st.selectbox("모델 선택", available_models)
                else:
                    st.error(f"❌ {status_msg}")
                    selected_model = None
                    provider_name = None
                    api_key = None
            except Exception as e:
                st.error(f"❌ 연결 실패: {e}")
                selected_model = None
                provider_name = None
                api_key = None
        else:
            selected_model = None
            provider_name = None
            api_key = None
    else:
        # 연결된 제공자 중 선택
        provider_name = st.selectbox(
            "LLM 제공자",
            available_providers,
            help="환경 변수에서 자동으로 로드된 제공자"
        )
        
        api_key = provider_status[provider_name]["api_key"]
        
        # 선택된 제공자의 모델 목록 가져오기
        try:
            temp_provider = get_llm_provider(provider_name, api_key, "")
            available_models = temp_provider.get_available_models()
            
            if available_models:
                selected_model = st.selectbox(
                    "모델 선택",
                    available_models,
                    help="API에서 가져온 사용 가능한 모델 목록"
                )
            else:
                st.error("사용 가능한 모델이 없습니다.")
                selected_model = None
        except Exception as e:
            st.error(f"모델 목록 가져오기 실패: {e}")
            selected_model = None
    
    st.markdown("---")
    
    # 크롤링 옵션
    st.subheader("🔧 크롤링 옵션")
    crawl_mode = st.radio(
        "크롤링 모드",
        ["단일 페이지", "전체 사이트"],
        help="단일 페이지: 한 페이지만 크롤링\n전체 사이트: 링크를 따라 여러 페이지 크롤링"
    )
    
    if crawl_mode == "전체 사이트":
        max_pages = st.slider("최대 페이지 수", 1, 100, 20)
    else:
        max_pages = 1
    
    # 출력 포맷
    output_format = st.selectbox(
        "출력 포맷",
        ["Markdown (.md)", "HTML (.html)", "텍스트 (.txt)"]
    )
    
    # LLM 처리 옵션
    use_llm = st.checkbox(
        "LLM으로 콘텐츠 정제",
        value=False,
        help="LLM을 사용하여 크롤링한 콘텐츠를 더 읽기 쉽게 정제"
    )

# 메인 영역
col1, col2 = st.columns([2, 1])

with col1:
    url = st.text_input(
        "🌐 크롤링할 URL",
        placeholder="https://example.com",
        help="크롤링하고 싶은 웹사이트 URL을 입력하세요"
    )

with col2:
    st.write("")
    st.write("")
    start_button = st.button("🚀 크롤링 시작", type="primary", use_container_width=True)

# 크롤링 실행
if start_button:
    if not url:
        st.error("URL을 입력해주세요")
    elif not url.startswith(("http://", "https://")):
        st.error("올바른 URL 형식이 아닙니다 (http:// 또는 https://로 시작)")
    elif not api_key or not selected_model:
        st.warning("LLM 제공자와 API 키를 설정해주세요")
    else:
        # 진행 상태 표시
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # 크롤러 생성
            crawler = create_crawler()
            
            # 진행 상태 콜백
            def update_progress(message, progress=None):
                status_text.text(message)
                if progress is not None:
                    progress_bar.progress(min(progress, 1.0))
            
            # 콘텐츠 정제 함수 (LLM 사용 시)
            content_processor = None
            if use_llm and selected_model:
                try:
                    provider = get_llm_provider(provider_name, api_key, selected_model)
                    
                    async def refine_content_async(content: str) -> str:
                        """비동기 콘텐츠 정제"""
                        if len(content) > 30000:
                            return content + "\n\n(콘텐츠가 너무 길어 LLM 처리를 건너뛰었습니다)"
                            
                        refine_prompt = """다음 크롤링된 웹 페이지 내용을 정리해주세요.
- 불필요한 메뉴, 네비게이션, 푸터 제거
- 핵심 본문 내용 유지
- 깔끔한 Markdown 포맷으로 재구성"""
                        
                        # 동기 함수를 비동기로 실행
                        return await asyncio.to_thread(
                            provider.process_content,
                            content,
                            refine_prompt
                        )
                    
                    content_processor = refine_content_async
                except Exception as e:
                    st.error(f"LLM 제공자 초기화 실패: {e}")

            # 크롤링 실행
            status_text.text("크롤링 시작...")
            
            if crawl_mode == "단일 페이지":
                result = asyncio.run(crawler.crawl_single_page(
                    url, 
                    update_progress,
                    content_processor=content_processor
                ))
                crawled_data = [result] if result["success"] else []
            else:
                crawled_data = asyncio.run(
                    crawler.crawl_website(
                        url, 
                        max_pages, 
                        True, 
                        update_progress,
                        content_processor=content_processor
                    )
                )
            
            if not crawled_data:
                st.error("크롤링 실패: 데이터를 가져올 수 없습니다")
            else:
                # Markdown 콘텐츠 생성
                status_text.text("콘텐츠 병합 중...")
                markdown_content = crawler.get_markdown_content()
                
                # 파일 저장
                status_text.text("파일 저장 중...")
                exporter = create_exporter()
                
                if output_format == "Markdown (.md)":
                    filepath = exporter.save_markdown(markdown_content)
                elif output_format == "HTML (.html)":
                    filepath = exporter.save_html(markdown_content)
                else:
                    filepath = exporter.save_text(markdown_content)
                
                # 완료
                progress_bar.progress(1.0)
                status_text.text("✅ 완료!")
                
                st.success(f"크롤링 완료! {len(crawled_data)}개 페이지")
                
                # 다운로드 버튼
                with open(filepath, "rb") as f:
                    st.download_button(
                        label="📥 파일 다운로드",
                        data=f,
                        file_name=Path(filepath).name,
                        mime="text/plain"
                    )
                
                # 미리보기
                with st.expander("📄 콘텐츠 미리보기"):
                    st.markdown(markdown_content[:5000] + "\n\n... (생략)")
                
        except Exception as e:
            st.error(f"오류 발생: {e}")
            import traceback
            with st.expander("상세 오류 정보"):
                st.code(traceback.format_exc())

# 사용 방법 안내
with st.expander("📖 사용 방법"):
    st.markdown("""
    ### 사용 방법
    
    1. **자동 연결 확인**: 환경 변수에서 API 키를 자동 로드하고 연결 상태 확인
       - ✅ 녹색: 연결 성공, 사용 가능
       - ❌ 빨간색: 연결 실패 (API 키 확인 필요)
       - ⚪ 회색: API 키 없음 (수동 입력 가능)
    2. **LLM 제공자 선택**: 연결된 제공자 중 선택 (또는 수동 입력)
    3. **모델 선택**: API에서 자동으로 가져온 최신 모델 목록에서 선택
    4. **URL 입력**: 크롤링할 웹사이트 URL 입력
    5. **크롤링 모드**: 단일 페이지 또는 전체 사이트 선택
    6. **출력 포맷**: 원하는 파일 포맷 선택
    7. **크롤링 시작**: 버튼 클릭하여 실행
    
    ### 주요 기능
    
    - ✅ 여러 LLM 제공자 지원 (OpenAI, Anthropic, Google)
    - ✅ 자동 환경 변수 감지 및 API 키 로드
    - ✅ 실시간 연결 상태 표시
    - ✅ 동적 모델 목록 로딩 (API에서 직접 가져오기)
    - ✅ 단일 페이지 또는 전체 사이트 크롤링
    - ✅ Markdown, HTML, 텍스트 출력 지원
    - ✅ LLM 기반 콘텐츠 정제 (선택적)
    - ✅ 실시간 진행 상태 표시
    - ✅ 로컬 실행 가능
    
    ### API 키 설정
    
    **시스템 환경 변수에 API 키를 설정하세요** (권장):
    
    **macOS/Linux**:
    ```bash
    # ~/.zshrc 또는 ~/.bashrc에 추가
    export OPENAI_API_KEY="your_key_here"
    export ANTHROPIC_API_KEY="your_key_here"
    export GEMINI_API_KEY="your_key_here"
    ```
    
    **Windows (PowerShell)**:
    ```powershell
    [System.Environment]::SetEnvironmentVariable('OPENAI_API_KEY', 'your_key_here', 'User')
    [System.Environment]::SetEnvironmentVariable('ANTHROPIC_API_KEY', 'your_key_here', 'User')
    [System.Environment]::SetEnvironmentVariable('GEMINI_API_KEY', 'your_key_here', 'User')
    ```
    

    """)

# 푸터
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
    🕷️ AI Web Crawler | Powered by Crawl4AI
    </div>
    """,
    unsafe_allow_html=True
)
