"""
AI Web Crawler - LLM 기반 웹사이트 크롤링 & 문서 변환 도구
"""
import streamlit as st
import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

# 환경 변수 로드 (.env 파일이 있으면 로드, 없으면 시스템 환경 변수 사용)
load_dotenv(override=False)

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
    
    # LLM 제공자 선택
    provider_name = st.selectbox(
        "LLM 제공자",
        ["OpenAI (ChatGPT)", "Anthropic (Claude)", "Google (Gemini)"]
    )
    
    # API 키 입력
    api_key_env_map = {
        "OpenAI (ChatGPT)": "OPENAI_API_KEY",
        "Anthropic (Claude)": "ANTHROPIC_API_KEY",
        "Google (Gemini)": "GOOGLE_API_KEY"
    }
    
    env_key = api_key_env_map[provider_name]
    default_key = os.getenv(env_key, "")
    
    if default_key:
        api_key = st.text_input(
            f"{provider_name} API 키",
            value=default_key,
            type="password",
            help=f"✅ 시스템 환경 변수에서 자동 로드됨 ({env_key})"
        )
    else:
        api_key = st.text_input(
            f"{provider_name} API 키",
            value="",
            type="password",
            help=f"⚠️ {env_key} 환경 변수가 설정되지 않았습니다. 직접 입력하거나 환경 변수를 설정하세요."
        )
    
    # 모델 선택
    if api_key:
        try:
            temp_provider = get_llm_provider(provider_name, api_key, "")
            available_models = temp_provider.get_available_models()
            selected_model = st.selectbox("모델 선택", available_models)
        except Exception as e:
            st.error(f"API 키 검증 실패: {e}")
            selected_model = None
    else:
        st.warning("API 키를 입력하세요")
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
            
            # 크롤링 실행
            status_text.text("크롤링 시작...")
            
            if crawl_mode == "단일 페이지":
                result = asyncio.run(crawler.crawl_single_page(url, update_progress))
                crawled_data = [result] if result["success"] else []
            else:
                crawled_data = asyncio.run(
                    crawler.crawl_website(url, max_pages, True, update_progress)
                )
            
            if not crawled_data:
                st.error("크롤링 실패: 데이터를 가져올 수 없습니다")
            else:
                # Markdown 콘텐츠 생성
                status_text.text("콘텐츠 변환 중...")
                markdown_content = crawler.get_markdown_content()
                
                # LLM 처리 (옵션)
                if use_llm and selected_model:
                    status_text.text("LLM으로 콘텐츠 정제 중...")
                    try:
                        provider = get_llm_provider(provider_name, api_key, selected_model)
                        
                        refine_prompt = """다음 크롤링된 웹 콘텐츠를 더 읽기 쉽고 구조화된 문서로 정제해주세요.
- 중요한 정보는 유지
- 중복 제거
- 논리적 구조화
- 깔끔한 Markdown 포맷"""
                        
                        # 콘텐츠가 너무 길면 분할 처리
                        if len(markdown_content) > 50000:
                            st.warning("콘텐츠가 너무 깁니다. LLM 처리를 건너뜁니다.")
                        else:
                            markdown_content = provider.process_content(
                                markdown_content,
                                refine_prompt
                            )
                    except Exception as e:
                        st.warning(f"LLM 처리 실패, 원본 콘텐츠 사용: {e}")
                
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
    
    1. **LLM 제공자 설정**: 좌측 사이드바에서 원하는 LLM 제공자 선택
    2. **API 키 입력**: 해당 제공자의 API 키 입력 (.env 파일에 저장 가능)
    3. **모델 선택**: 사용할 모델 선택
    4. **URL 입력**: 크롤링할 웹사이트 URL 입력
    5. **크롤링 모드**: 단일 페이지 또는 전체 사이트 선택
    6. **출력 포맷**: 원하는 파일 포맷 선택
    7. **크롤링 시작**: 버튼 클릭하여 실행
    
    ### 주요 기능
    
    - ✅ 여러 LLM 제공자 지원 (OpenAI, Anthropic, Google)
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
    export GOOGLE_API_KEY="your_key_here"
    ```
    
    **Windows (PowerShell)**:
    ```powershell
    [System.Environment]::SetEnvironmentVariable('OPENAI_API_KEY', 'your_key_here', 'User')
    [System.Environment]::SetEnvironmentVariable('ANTHROPIC_API_KEY', 'your_key_here', 'User')
    [System.Environment]::SetEnvironmentVariable('GOOGLE_API_KEY', 'your_key_here', 'User')
    ```
    
    **또는 .env 파일 사용** (선택사항):
    ```
    OPENAI_API_KEY=your_key_here
    ANTHROPIC_API_KEY=your_key_here
    GOOGLE_API_KEY=your_key_here
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
