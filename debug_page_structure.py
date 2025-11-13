"""
KOTRA 웹사이트 구조 확인 스크립트
실제 페이지의 HTML을 확인하여 요소 ID를 찾습니다
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

print("=" * 70)
print("KOTRA 웹사이트 구조 분석")
print("=" * 70)

# Chrome 옵션 설정
chrome_options = Options()
chrome_options.add_argument('--start-maximized')
chrome_options.add_argument('--disable-blink-features=AutomationControlled')

# ChromeDriver 자동 설치
print("\n🔍 ChromeDriver 설치 중...")
service = Service(ChromeDriverManager().install())

# 브라우저 시작
print("🚀 Chrome 브라우저 시작 중...")
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    url = "https://www.kotra.or.kr/bigdata/partner/search"
    print(f"\n📡 페이지 로드: {url}")
    driver.get(url)

    print("⏳ 페이지 로딩 대기 (10초)...")
    time.sleep(10)

    print(f"\n✅ 현재 URL: {driver.current_url}")
    print(f"✅ 페이지 제목: {driver.title}")

    # 스크린샷 저장
    screenshot_file = "kotra_page_debug.png"
    driver.save_screenshot(screenshot_file)
    print(f"\n📸 스크린샷 저장: {screenshot_file}")

    # 페이지 소스 저장
    html_file = "kotra_page_source.html"
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(driver.page_source)
    print(f"📄 페이지 소스 저장: {html_file}")

    # 모든 input 요소 찾기
    print("\n" + "=" * 70)
    print("📋 페이지의 모든 INPUT 요소:")
    print("=" * 70)

    inputs = driver.find_elements(By.TAG_NAME, "input")
    print(f"\n총 {len(inputs)}개의 input 요소 발견:\n")

    for i, inp in enumerate(inputs, 1):
        inp_id = inp.get_attribute('id')
        inp_name = inp.get_attribute('name')
        inp_class = inp.get_attribute('class')
        inp_type = inp.get_attribute('type')
        inp_placeholder = inp.get_attribute('placeholder')

        if inp_id or inp_name or 'hs' in str(inp_placeholder).lower():
            print(f"{i}. INPUT 요소:")
            print(f"   - ID: {inp_id}")
            print(f"   - NAME: {inp_name}")
            print(f"   - CLASS: {inp_class}")
            print(f"   - TYPE: {inp_type}")
            print(f"   - PLACEHOLDER: {inp_placeholder}")
            print()

    # 모든 select 요소 찾기
    print("=" * 70)
    print("📋 페이지의 모든 SELECT 요소:")
    print("=" * 70)

    selects = driver.find_elements(By.TAG_NAME, "select")
    print(f"\n총 {len(selects)}개의 select 요소 발견:\n")

    for i, sel in enumerate(selects, 1):
        sel_id = sel.get_attribute('id')
        sel_name = sel.get_attribute('name')
        sel_class = sel.get_attribute('class')

        print(f"{i}. SELECT 요소:")
        print(f"   - ID: {sel_id}")
        print(f"   - NAME: {sel_name}")
        print(f"   - CLASS: {sel_class}")

        # 옵션 개수
        options = sel.find_elements(By.TAG_NAME, "option")
        print(f"   - OPTIONS: {len(options)}개")
        if len(options) > 0 and len(options) < 30:
            print(f"   - 첫 3개 옵션:")
            for opt in options[:3]:
                print(f"     • {opt.get_attribute('value')} : {opt.text}")
        print()

    # 모든 button 요소 찾기
    print("=" * 70)
    print("📋 페이지의 모든 BUTTON 요소:")
    print("=" * 70)

    buttons = driver.find_elements(By.TAG_NAME, "button")
    print(f"\n총 {len(buttons)}개의 button 요소 발견:\n")

    for i, btn in enumerate(buttons, 1):
        btn_id = btn.get_attribute('id')
        btn_class = btn.get_attribute('class')
        btn_text = btn.text
        btn_type = btn.get_attribute('type')

        if btn_text or '검색' in str(btn_class):
            print(f"{i}. BUTTON 요소:")
            print(f"   - ID: {btn_id}")
            print(f"   - CLASS: {btn_class}")
            print(f"   - TYPE: {btn_type}")
            print(f"   - TEXT: {btn_text}")
            print()

    # 특정 ID나 CLASS 패턴 검색
    print("=" * 70)
    print("🔍 HS CODE 관련 요소 검색:")
    print("=" * 70)

    # CSS selector로 hs 관련 요소 찾기
    hs_elements = driver.find_elements(By.CSS_SELECTOR,
        "[id*='hs'], [name*='hs'], [class*='hs'], [placeholder*='HS']")

    print(f"\n총 {len(hs_elements)}개의 HS 관련 요소 발견:\n")

    for i, elem in enumerate(hs_elements, 1):
        print(f"{i}. {elem.tag_name.upper()} 요소:")
        print(f"   - ID: {elem.get_attribute('id')}")
        print(f"   - NAME: {elem.get_attribute('name')}")
        print(f"   - CLASS: {elem.get_attribute('class')}")
        print(f"   - PLACEHOLDER: {elem.get_attribute('placeholder')}")
        print()

    # 국가 관련 요소 검색
    print("=" * 70)
    print("🔍 국가(Country) 관련 요소 검색:")
    print("=" * 70)

    country_elements = driver.find_elements(By.CSS_SELECTOR,
        "[id*='country'], [name*='country'], [class*='country']")

    print(f"\n총 {len(country_elements)}개의 국가 관련 요소 발견:\n")

    for i, elem in enumerate(country_elements, 1):
        print(f"{i}. {elem.tag_name.upper()} 요소:")
        print(f"   - ID: {elem.get_attribute('id')}")
        print(f"   - NAME: {elem.get_attribute('name')}")
        print(f"   - CLASS: {elem.get_attribute('class')}")
        print()

    # iframe 확인
    print("=" * 70)
    print("🔍 IFRAME 확인:")
    print("=" * 70)

    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    print(f"\n총 {len(iframes)}개의 iframe 발견")

    if len(iframes) > 0:
        print("\n⚠️ 페이지에 iframe이 있습니다!")
        print("   iframe 내부의 요소에 접근하려면 driver.switch_to.frame()을 사용해야 합니다.")

        for i, iframe in enumerate(iframes, 1):
            iframe_id = iframe.get_attribute('id')
            iframe_name = iframe.get_attribute('name')
            iframe_src = iframe.get_attribute('src')

            print(f"\n{i}. IFRAME:")
            print(f"   - ID: {iframe_id}")
            print(f"   - NAME: {iframe_name}")
            print(f"   - SRC: {iframe_src}")

    print("\n" + "=" * 70)
    print("✅ 분석 완료!")
    print("=" * 70)
    print("\n💡 다음 파일들을 확인하세요:")
    print(f"   1. {screenshot_file} - 페이지 스크린샷")
    print(f"   2. {html_file} - 전체 HTML 소스")
    print("\n💡 위 출력에서 실제 요소의 ID/NAME/CLASS를 확인하고")
    print("   크롤러 코드에서 해당 값을 사용하세요!")

    # 사용자가 페이지를 볼 수 있도록 30초 대기
    print("\n⏳ 브라우저를 30초간 열어둡니다. 직접 확인해보세요...")
    print("   (강제 종료하려면 Ctrl+C)")
    time.sleep(30)

except Exception as e:
    print(f"\n❌ 오류 발생: {str(e)}")
    import traceback
    traceback.print_exc()

finally:
    print("\n🔚 브라우저 종료")
    driver.quit()
