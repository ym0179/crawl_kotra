"""
KOTRA 크롤러 - 궁극의 Colab 해결책
모든 Chrome/ChromeDriver 문제를 해결합니다
"""

print("=" * 70)
print("🔧 Chrome/ChromeDriver 완전 재설치 시작")
print("=" * 70)

import subprocess
import sys
import os

# 1단계: 기존 Chrome/ChromeDriver 완전 제거
print("\n1️⃣ 기존 설치 제거 중...")
subprocess.run(['apt-get', 'remove', '-y', '-qq', 'chromium-browser', 'chromium-chromedriver'],
               capture_output=True, check=False)
subprocess.run(['apt-get', 'autoremove', '-y', '-qq'], capture_output=True, check=False)

# 2단계: 최신 Chrome 및 ChromeDriver 설치
print("2️⃣ 최신 Chrome 및 ChromeDriver 설치 중...")
subprocess.run(['apt-get', 'update', '-qq'], capture_output=True, check=False)

# Chrome 설치
subprocess.run(['apt-get', 'install', '-y', '-qq',
               'chromium-browser',
               'chromium-chromedriver'],
              capture_output=True, check=False)

# 추가 필수 라이브러리 설치
subprocess.run(['apt-get', 'install', '-y', '-qq',
               'fonts-liberation',
               'libasound2',
               'libatk-bridge2.0-0',
               'libatk1.0-0',
               'libatspi2.0-0',
               'libcups2',
               'libdbus-1-3',
               'libdrm2',
               'libgbm1',
               'libgtk-3-0',
               'libnspr4',
               'libnss3',
               'libwayland-client0',
               'libxcomposite1',
               'libxdamage1',
               'libxfixes3',
               'libxkbcommon0',
               'libxrandr2',
               'xdg-utils'],
              capture_output=True, check=False)

# 3단계: Python 패키지 설치
print("3️⃣ Python 패키지 설치 중...")
subprocess.run([sys.executable, '-m', 'pip', 'install', '-q',
               'selenium', 'pandas', 'openpyxl'],
              capture_output=True, check=True)

# 4단계: ChromeDriver 확인 및 설정
print("4️⃣ ChromeDriver 설정 중...")

# ChromeDriver 경로 찾기
chromedriver_paths = [
    '/usr/bin/chromedriver',
    '/usr/lib/chromium-browser/chromedriver',
    '/snap/bin/chromium.chromedriver'
]

chromedriver_path = None
for path in chromedriver_paths:
    if os.path.exists(path):
        chromedriver_path = path
        print(f"   ✅ ChromeDriver 발견: {path}")
        break

if not chromedriver_path:
    print("   ⚠️ ChromeDriver를 찾을 수 없습니다. 기본 경로 사용...")
    chromedriver_path = '/usr/bin/chromedriver'

# 실행 권한 부여
subprocess.run(['chmod', '+x', chromedriver_path], capture_output=True, check=False)

# 5단계: Chrome 버전 확인
print("\n5️⃣ Chrome 버전 확인 중...")
result = subprocess.run(['chromium-browser', '--version'],
                       capture_output=True, text=True, check=False)
if result.returncode == 0:
    print(f"   Chrome: {result.stdout.strip()}")
else:
    print("   ⚠️ Chrome 버전 확인 실패")

result = subprocess.run([chromedriver_path, '--version'],
                       capture_output=True, text=True, check=False)
if result.returncode == 0:
    print(f"   ChromeDriver: {result.stdout.strip()}")
else:
    print("   ⚠️ ChromeDriver 버전 확인 실패")

print("\n✅ 설치 완료!\n")

# ============================================================
# 크롤러 코드
# ============================================================

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
import pandas as pd
import time
from typing import List, Dict
import re


class KotraSeleniumCrawler:
    def __init__(self):
        """Selenium 기반 크롤러 초기화 (Colab 전용 - 강화 버전)"""

        chrome_options = Options()

        # 모든 가능한 headless 옵션 추가
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-software-rasterizer')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-setuid-sandbox')

        # 추가 안정성 옵션
        chrome_options.add_argument('--remote-debugging-port=9222')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-accelerated-2d-canvas')
        chrome_options.add_argument('--disable-accelerated-jpeg-decoding')
        chrome_options.add_argument('--disable-background-timer-throttling')
        chrome_options.add_argument('--disable-backgrounding-occluded-windows')
        chrome_options.add_argument('--disable-breakpad')
        chrome_options.add_argument('--disable-component-extensions-with-background-pages')
        chrome_options.add_argument('--disable-features=TranslateUI,BlinkGenPropertyTrees')
        chrome_options.add_argument('--disable-ipc-flooding-protection')
        chrome_options.add_argument('--disable-renderer-backgrounding')
        chrome_options.add_argument('--enable-features=NetworkService,NetworkServiceInProcess')
        chrome_options.add_argument('--force-color-profile=srgb')
        chrome_options.add_argument('--hide-scrollbars')
        chrome_options.add_argument('--metrics-recording-only')
        chrome_options.add_argument('--mute-audio')

        # 창 크기 및 User Agent
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

        # Chrome 바이너리 명시적 지정
        chrome_binaries = [
            '/usr/bin/chromium-browser',
            '/usr/bin/chromium',
            '/usr/bin/google-chrome',
            '/snap/bin/chromium'
        ]

        for binary in chrome_binaries:
            if os.path.exists(binary):
                chrome_options.binary_location = binary
                print(f"✅ Chrome 바이너리 사용: {binary}")
                break

        # ChromeDriver 서비스 설정
        service = Service(
            chromedriver_path,
            log_path='/tmp/chromedriver.log'
        )

        try:
            print("🚀 Chrome 브라우저 시작 중...")
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            print("✅ Chrome 브라우저 시작 성공!")
        except Exception as e:
            print(f"\n❌ Chrome 시작 실패: {str(e)}")
            print("\n📋 ChromeDriver 로그:")
            if os.path.exists('/tmp/chromedriver.log'):
                with open('/tmp/chromedriver.log', 'r') as f:
                    print(f.read())
            raise

        self.wait = WebDriverWait(self.driver, 20)
        self.base_url = "https://www.kotra.or.kr/bigdata/partner/search"

    def setup_page(self, country_code: str, hs_code: str):
        """페이지 설정: 국가 선택 및 HS CODE 입력"""
        try:
            self.driver.get(self.base_url)
            time.sleep(3)

            country_select = self.wait.until(
                EC.presence_of_element_located((By.ID, "country-list-ex"))
            )
            select = Select(country_select)
            select.select_by_value(country_code)
            time.sleep(1)

            hs_input = self.driver.find_element(By.ID, "hscode-input-ex")
            hs_input.clear()
            hs_input.send_keys(hs_code)
            time.sleep(1)

            search_button = self.driver.find_element(By.CSS_SELECTOR, "button.btn-search")
            search_button.click()
            time.sleep(3)

            return True
        except Exception as e:
            print(f"⚠️ 페이지 설정 중 오류: {str(e)}")
            return False

    def extract_table_data(self) -> List[Dict]:
        """현재 페이지의 AG Grid 테이블 데이터 추출"""
        data = []
        try:
            rows = self.driver.find_elements(By.CSS_SELECTOR, "div[role='row'][row-index]")

            for row in rows:
                try:
                    cells = row.find_elements(By.CSS_SELECTOR, "div[role='gridcell']")

                    if len(cells) >= 7:
                        company_name = cells[1].text.strip()

                        def parse_number(text):
                            cleaned = re.sub(r'[,\s]', '', text)
                            try:
                                return int(cleaned)
                            except:
                                return 0

                        row_data = {
                            '수입기업': company_name,
                            '거래국가수': parse_number(cells[2].text),
                            '거래건수': parse_number(cells[3].text),
                            '총거래금액(USD)': parse_number(cells[4].text),
                            '수입예측값': parse_number(cells[5].text),
                            '한국수입여부': cells[6].text.strip()
                        }
                        data.append(row_data)
                except:
                    continue

            return data
        except Exception as e:
            print(f"⚠️ 테이블 데이터 추출 오류: {str(e)}")
            return []

    def go_to_next_page(self) -> bool:
        """다음 페이지로 이동"""
        try:
            next_button = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Next Page']")
            if 'disabled' in next_button.get_attribute('class'):
                return False
            next_button.click()
            time.sleep(2)
            return True
        except:
            return False

    def crawl_country(self, country_code: str, country_name: str, hs_code: str) -> List[Dict]:
        """단일 국가 크롤링"""
        print(f"\n{'='*60}")
        print(f"🔍 크롤링 시작: {country_name} ({country_code})")
        print(f"{'='*60}")

        all_data = []

        if not self.setup_page(country_code, hs_code):
            print(f"❌ {country_name} 크롤링 실패")
            return []

        page = 1
        while True:
            print(f"  📄 페이지 {page} 처리 중...")

            page_data = self.extract_table_data()

            if not page_data:
                print(f"  ℹ️ 데이터가 없습니다.")
                break

            for item in page_data:
                item['수입국가'] = country_name
                item['수입국가코드'] = country_code

            all_data.extend(page_data)
            print(f"  ✅ {len(page_data)}개 데이터 수집 완료")

            if not self.go_to_next_page():
                print(f"  🎉 전체 {len(all_data)}건 수집 완료")
                break

            page += 1
            time.sleep(1)

        return all_data

    def crawl_all_countries(self, countries: List[Dict], hs_code: str) -> pd.DataFrame:
        """모든 국가 크롤링"""
        all_data = []

        for i, country in enumerate(countries, 1):
            print(f"\n📊 진행률: {i}/{len(countries)} ({i*100//len(countries)}%)")

            country_data = self.crawl_country(country['code'], country['name'], hs_code)
            all_data.extend(country_data)

            print(f"✅ {country['name']} 완료: {len(country_data)}건")
            time.sleep(2)

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


# ============================================================
# 실행 코드
# ============================================================

print("\n" + "=" * 70)
print("크롤링 설정")
print("=" * 70)

# 테스트용: 2개 국가만 (빠른 테스트)
countries = [
    {'code': 'US', 'name': '미국'},
    {'code': 'VN', 'name': '베트남'},
]

# 전체 국가로 실행하려면 아래 주석을 해제하세요
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

print(f"✅ 대상 국가: {len(countries)}개국")
print(f"✅ HS CODE: {hs_code}")

print("\n" + "=" * 70)
print("크롤링 시작")
print("=" * 70)

crawler = KotraSeleniumCrawler()

try:
    df = crawler.crawl_all_countries(countries, hs_code)

    print("\n\n" + "=" * 70)
    print("✅ 크롤링 완료!")
    print("=" * 70)
    print(f"총 수집 데이터: {len(df)}건")

    if len(df) > 0:
        print("\n📊 데이터 미리보기:")
        print(df.head(10))

        print("\n📈 국가별 통계:")
        country_stats = df.groupby('수입국가').size().reset_index(name='기업수')
        print(country_stats)

        excel_file = f'kotra_buyers_{hs_code}.xlsx'
        df.to_excel(excel_file, index=False, engine='openpyxl')
        print(f"\n✅ 엑셀 파일 저장: {excel_file}")

        txt_file = f'kotra_buyers_{hs_code}.txt'
        df.to_csv(txt_file, sep='\t', index=False, encoding='utf-8-sig')
        print(f"✅ TXT 파일 저장: {txt_file}")

        from google.colab import files
        print("\n📥 파일 다운로드 중...")
        files.download(excel_file)
        files.download(txt_file)

        print("\n🎉 모든 작업이 완료되었습니다!")
    else:
        print("\n⚠️ 수집된 데이터가 없습니다.")

except Exception as e:
    print(f"\n❌ 오류 발생: {str(e)}")
    import traceback
    traceback.print_exc()

finally:
    crawler.close()
    print("\n✅ 브라우저 종료 완료")
