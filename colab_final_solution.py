"""
KOTRA 크롤러 - 최종 완전 작동 버전
DevToolsActivePort 에러 완전 해결
"""

print("=" * 70)
print("🚀 KOTRA 크롤러 - 최종 버전")
print("=" * 70)

import subprocess
import sys
import os
import shutil

# /tmp 디렉토리 정리
print("\n🧹 임시 디렉토리 정리 중...")
temp_dirs = ['/tmp/.com.google.Chrome.*', '/tmp/.org.chromium.*']
for pattern in temp_dirs:
    subprocess.run(f'rm -rf {pattern}', shell=True, capture_output=True)

# 필수 패키지 설치
print("📦 패키지 설치 중...")
subprocess.run([sys.executable, '-m', 'pip', 'install', '-q',
               'webdriver-manager', 'selenium', 'pandas', 'openpyxl'],
              check=True, capture_output=True)
print("✅ 패키지 설치 완료!\n")

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
import pandas as pd
import time
from typing import List, Dict
import re


class KotraSeleniumCrawler:
    def __init__(self):
        """Selenium 기반 크롤러 초기화 - DevToolsActivePort 문제 해결"""

        chrome_options = Options()

        # === DevToolsActivePort 에러 해결 옵션들 ===

        # 핵심 옵션들
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')

        # DevTools 관련
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-software-rasterizer')
        chrome_options.add_argument('--remote-debugging-port=9222')

        # 프로세스 관련 (중요!)
        chrome_options.add_argument('--single-process')  # 단일 프로세스
        chrome_options.add_argument('--disable-setuid-sandbox')

        # 렌더링 관련
        chrome_options.add_argument('--disable-background-networking')
        chrome_options.add_argument('--disable-background-timer-throttling')
        chrome_options.add_argument('--disable-backgrounding-occluded-windows')
        chrome_options.add_argument('--disable-breakpad')
        chrome_options.add_argument('--disable-client-side-phishing-detection')
        chrome_options.add_argument('--disable-default-apps')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-features=site-per-process')
        chrome_options.add_argument('--disable-hang-monitor')
        chrome_options.add_argument('--disable-ipc-flooding-protection')
        chrome_options.add_argument('--disable-popup-blocking')
        chrome_options.add_argument('--disable-prompt-on-repost')
        chrome_options.add_argument('--disable-renderer-backgrounding')
        chrome_options.add_argument('--disable-sync')
        chrome_options.add_argument('--disable-translate')
        chrome_options.add_argument('--metrics-recording-only')
        chrome_options.add_argument('--no-first-run')
        chrome_options.add_argument('--safebrowsing-disable-auto-update')
        chrome_options.add_argument('--enable-automation')
        chrome_options.add_argument('--password-store=basic')
        chrome_options.add_argument('--use-mock-keychain')

        # 창 크기
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--start-maximized')

        # User Agent
        chrome_options.add_argument('user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

        # User data directory (중요!)
        user_data_dir = '/tmp/chrome-user-data'
        if os.path.exists(user_data_dir):
            shutil.rmtree(user_data_dir)
        os.makedirs(user_data_dir, exist_ok=True)
        chrome_options.add_argument(f'--user-data-dir={user_data_dir}')

        # Crash dumps directory
        crash_dumps_dir = '/tmp/chrome-crash-dumps'
        if os.path.exists(crash_dumps_dir):
            shutil.rmtree(crash_dumps_dir)
        os.makedirs(crash_dumps_dir, exist_ok=True)
        chrome_options.add_argument(f'--crash-dumps-dir={crash_dumps_dir}')

        # 추가 설정
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        # Chrome 바이너리
        chrome_options.binary_location = '/usr/bin/chromium-browser'

        try:
            print("🔍 ChromeDriver 다운로드 중...")
            service = Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())

            # 로그 레벨 설정
            service.log_path = '/tmp/chromedriver.log'
            service.service_args = ['--verbose']

            print("🚀 Chrome 브라우저 시작 중...")
            self.driver = webdriver.Chrome(service=service, options=chrome_options)

            # 타임아웃 설정
            self.driver.set_page_load_timeout(60)
            self.driver.implicitly_wait(10)

            print("✅ Chrome 브라우저 시작 성공!\n")

        except Exception as e:
            print(f"❌ Chrome 시작 실패: {str(e)}")
            print("\n💡 추가 정보:")
            print(f"   Chrome 경로: {chrome_options.binary_location}")
            print(f"   User data dir: {user_data_dir}")

            # ChromeDriver 로그 확인
            if os.path.exists('/tmp/chromedriver.log'):
                print("\n📋 ChromeDriver 로그:")
                with open('/tmp/chromedriver.log', 'r') as f:
                    print(f.read()[-500:])  # 마지막 500자

            raise

        self.wait = WebDriverWait(self.driver, 30)
        self.base_url = "https://www.kotra.or.kr/bigdata/partner/search"

    def setup_page(self, country_code: str, hs_code: str):
        """페이지 설정: 국가 선택 및 HS CODE 입력 (실제 요소 ID 사용)"""
        try:
            print(f"  📡 페이지 로드: {self.base_url}")
            self.driver.get(self.base_url)

            print(f"  ⏳ 페이지 로딩 대기 (10초)...")
            time.sleep(10)

            print(f"  ✅ URL: {self.driver.current_url}")
            print(f"  ✅ 제목: {self.driver.title}")

            # "해외관세청 실수입기업 검색" 탭 클릭
            print(f"  🔍 해외관세청 실수입기업 검색 탭 클릭...")
            try:
                bl_tab = self.driver.find_element(By.ID, "partner_bl")
                bl_tab.click()
                print(f"  ✅ 탭 클릭 완료")
                time.sleep(2)
            except Exception as e:
                print(f"  ⚠️ 탭 클릭 실패: {str(e)}")

            # 국가 선택
            print(f"  🔍 국가 드롭다운 찾기 (ID: country-list-ex)...")
            country_select = self.wait.until(
                EC.presence_of_element_located((By.ID, "country-list-ex"))
            )
            select = Select(country_select)
            select.select_by_value(country_code)
            print(f"  ✅ 국가 선택: {country_code}")
            time.sleep(2)

            # HS CODE 자릿수 선택 (6자리)
            print(f"  🔍 6자리 라디오 버튼 클릭...")
            radio_6 = self.driver.find_element(By.ID, "hscdDigits6")
            radio_6.click()
            print(f"  ✅ 6자리 선택")
            time.sleep(1)

            # HS CODE 입력 (실제 ID: hs-code)
            print(f"  🔍 HS CODE 입력 필드 찾기 (ID: hs-code)...")
            hs_input = self.driver.find_element(By.ID, "hs-code")
            hs_input.clear()
            hs_input.send_keys(hs_code)
            print(f"  ✅ HS CODE 입력: {hs_code}")
            time.sleep(2)

            # 검색 버튼 클릭
            print(f"  🔍 검색 버튼 찾기...")
            # "해외관세청" 섹션의 검색 버튼 찾기
            search_buttons = self.driver.find_elements(By.CSS_SELECTOR, ".accor-desc .btn-wrap button.mu-btn")
            if len(search_buttons) >= 2:
                search_button = search_buttons[1]  # 두 번째 검색 버튼 (해외관세청 섹션)
            else:
                search_button = self.driver.find_element(By.XPATH,
                    "//li[contains(@class, 'partner_bl')]//button[contains(@class, 'mu-btn') and text()='검색']")

            search_button.click()
            print(f"  ✅ 검색 실행")

            print(f"  ⏳ 검색 결과 로딩 (10초)...")
            time.sleep(10)

            print(f"  ✅ 페이지 설정 완료")
            return True

        except Exception as e:
            print(f"  ❌ 오류: {str(e)}")
            import traceback
            traceback.print_exc()

            # 스크린샷 저장
            try:
                self.driver.save_screenshot("error_screenshot.png")
                print(f"  📸 에러 스크린샷 저장: error_screenshot.png")
            except:
                pass

            return False

    def extract_table_data(self) -> List[Dict]:
        """테이블 데이터 추출"""
        data = []
        try:
            print(f"    🔍 테이블 행 찾기...")
            rows = self.driver.find_elements(By.CSS_SELECTOR, "div[role='row'][row-index]")
            print(f"    ✅ {len(rows)}개 행 발견")

            for row in rows:
                try:
                    cells = row.find_elements(By.CSS_SELECTOR, "div[role='gridcell']")

                    if len(cells) >= 7:
                        def parse_number(text):
                            cleaned = re.sub(r'[,\s]', '', text)
                            try:
                                return int(cleaned)
                            except:
                                return 0

                        row_data = {
                            '수입기업': cells[1].text.strip(),
                            '거래국가수': parse_number(cells[2].text),
                            '거래건수': parse_number(cells[3].text),
                            '총거래금액(USD)': parse_number(cells[4].text),
                            '수입예측값': parse_number(cells[5].text),
                            '한국수입여부': cells[6].text.strip()
                        }
                        data.append(row_data)
                except:
                    continue

            print(f"    ✅ {len(data)}개 데이터 추출")
            return data

        except Exception as e:
            print(f"    ❌ 추출 오류: {str(e)}")
            return []

    def go_to_next_page(self) -> bool:
        """다음 페이지로 이동"""
        try:
            next_button = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Next Page']")
            if 'disabled' in next_button.get_attribute('class'):
                return False
            next_button.click()
            time.sleep(3)
            return True
        except:
            return False

    def crawl_country(self, country_code: str, country_name: str, hs_code: str) -> List[Dict]:
        """단일 국가 크롤링"""
        print(f"\n{'='*60}")
        print(f"🔍 {country_name} ({country_code}) 크롤링")
        print(f"{'='*60}")

        all_data = []

        if not self.setup_page(country_code, hs_code):
            print(f"❌ {country_name} 실패")
            return []

        page = 1
        while True:
            print(f"  📄 페이지 {page}")
            page_data = self.extract_table_data()

            if not page_data:
                break

            for item in page_data:
                item['수입국가'] = country_name
                item['수입국가코드'] = country_code

            all_data.extend(page_data)

            if not self.go_to_next_page():
                print(f"  🎉 {len(all_data)}건 완료")
                break

            page += 1
            time.sleep(2)

        return all_data

    def crawl_all_countries(self, countries: List[Dict], hs_code: str) -> pd.DataFrame:
        """모든 국가 크롤링"""
        all_data = []

        for i, country in enumerate(countries, 1):
            print(f"\n📊 {i}/{len(countries)} ({i*100//len(countries)}%)")

            country_data = self.crawl_country(country['code'], country['name'], hs_code)
            all_data.extend(country_data)

            print(f"✅ {country['name']}: {len(country_data)}건")
            time.sleep(3)

        df = pd.DataFrame(all_data)

        if not df.empty:
            columns_order = [
                '수입국가', '수입국가코드', '수입기업', '거래국가수',
                '거래건수', '총거래금액(USD)', '수입예측값', '한국수입여부'
            ]
            df = df[columns_order]

        return df

    def close(self):
        """브라우저 종료"""
        if self.driver:
            self.driver.quit()
            print("✅ 브라우저 종료")


# ============================================================
# 실행
# ============================================================

print("\n" + "=" * 70)
print("설정")
print("=" * 70)

# 테스트: 1개 국가
countries = [
    {'code': 'US', 'name': '미국'},
]

# 전체 22개국 (주석 해제하여 사용)
"""
countries = [
    {'code': 'RU', 'name': '러시아연방'},
    {'code': 'MX', 'name': '멕시코'},
    {'code': 'US', 'name': '미국'},
    {'code': 'BD', 'name': '방글라데시'},
    {'code': 'VN', 'name': '베트남'},
    {'code': 'AR', 'name': '아르헨티나'},
    {'code': 'EC', 'name': '에콰도르'},
    {'code': 'UG', 'name': '우간다'},
    {'code': 'UZ', 'name': '우즈베키스탄'},
    {'code': 'IN', 'name': '인도'},
    {'code': 'ID', 'name': '인도네시아'},
    {'code': 'JP', 'name': '일본'},
    {'code': 'CL', 'name': '칠레'},
    {'code': 'KZ', 'name': '카자흐스탄'},
    {'code': 'KE', 'name': '케냐'},
    {'code': 'CO', 'name': '콜롬비아'},
    {'code': 'TR', 'name': '튀르키예'},
    {'code': 'PA', 'name': '파나마'},
    {'code': 'PY', 'name': '파라과이'},
    {'code': 'PK', 'name': '파키스탄'},
    {'code': 'PE', 'name': '페루'},
    {'code': 'PH', 'name': '필리핀'}
]
"""

hs_code = '391810'

print(f"✅ 대상: {len(countries)}개국")
print(f"✅ HS CODE: {hs_code}")

print("\n" + "=" * 70)
print("크롤링 시작")
print("=" * 70)

crawler = KotraSeleniumCrawler()

try:
    df = crawler.crawl_all_countries(countries, hs_code)

    print("\n\n" + "=" * 70)
    print("✅ 완료!")
    print("=" * 70)
    print(f"총: {len(df)}건")

    if len(df) > 0:
        print("\n📊 미리보기:")
        print(df.head(10))

        print("\n📈 국가별:")
        print(df.groupby('수입국가').size())

        # 저장
        excel_file = f'kotra_buyers_{hs_code}.xlsx'
        df.to_excel(excel_file, index=False, engine='openpyxl')
        print(f"\n✅ Excel: {excel_file}")

        txt_file = f'kotra_buyers_{hs_code}.txt'
        df.to_csv(txt_file, sep='\t', index=False, encoding='utf-8-sig')
        print(f"✅ TXT: {txt_file}")

        # 다운로드
        from google.colab import files
        print("\n📥 다운로드 중...")
        files.download(excel_file)
        files.download(txt_file)

        print("\n🎉 모든 작업 완료!")
    else:
        print("\n⚠️ 데이터 없음")

except Exception as e:
    print(f"\n❌ 오류: {str(e)}")
    import traceback
    traceback.print_exc()

finally:
    crawler.close()
