"""
KOTRA 크롤러 - 가장 간단한 해결책
ChromeDriver 버전 문제를 완전히 해결합니다
"""

print("=" * 70)
print("🔧 ChromeDriver 버전 문제 해결 시작")
print("=" * 70)

import subprocess
import sys
import os

# 1. Chrome 버전 확인
print("\n1️⃣ Chrome 버전 확인 중...")
result = subprocess.run(['chromium-browser', '--version'],
                       capture_output=True, text=True, check=False)
if result.returncode == 0:
    chrome_version = result.stdout.strip()
    print(f"   {chrome_version}")
    # 버전 번호 추출 (예: Chromium 120.0.6099.109 -> 120)
    import re
    match = re.search(r'Chromium (\d+)', chrome_version)
    if match:
        chrome_major = match.group(1)
        print(f"   주 버전: {chrome_major}")
else:
    chrome_major = None
    print("   ⚠️ Chrome 버전 확인 실패")

# 2. 기존 ChromeDriver 제거
print("\n2️⃣ 기존 ChromeDriver 제거 중...")
subprocess.run(['rm', '-f', '/usr/bin/chromedriver'], check=False, capture_output=True)
subprocess.run(['apt-get', 'remove', '-y', '-qq', 'chromium-chromedriver'],
               check=False, capture_output=True)

# 3. 최신 ChromeDriver 설치 (webdriver-manager 사용)
print("\n3️⃣ ChromeDriver 자동 설치 중...")
subprocess.run([sys.executable, '-m', 'pip', 'install', '-q',
               'webdriver-manager', 'selenium', 'pandas', 'openpyxl'],
              check=True, capture_output=True)

print("\n✅ 설치 완료!\n")

# ============================================================
# 크롤러 코드 (webdriver-manager 사용)
# ============================================================

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
        """Selenium 기반 크롤러 초기화 (webdriver-manager 사용)"""

        chrome_options = Options()

        # 필수 옵션
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-software-rasterizer')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-setuid-sandbox')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

        # Chrome 바이너리 설정
        chrome_options.binary_location = '/usr/bin/chromium-browser'

        try:
            print("🔍 적절한 ChromeDriver 다운로드 중...")
            # webdriver-manager로 자동으로 적절한 버전 다운로드
            service = Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())

            print("🚀 Chrome 브라우저 시작 중...")
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            print("✅ Chrome 브라우저 시작 성공!\n")

        except Exception as e:
            print(f"\n❌ Chrome 시작 실패: {str(e)}")
            print("\n💡 대안 방법을 시도합니다...\n")

            # 대안: 기본 ChromeDriver 사용
            try:
                self.driver = webdriver.Chrome(options=chrome_options)
                print("✅ 기본 ChromeDriver로 시작 성공!\n")
            except Exception as e2:
                print(f"❌ 기본 방법도 실패: {str(e2)}")
                raise

        self.wait = WebDriverWait(self.driver, 20)
        self.base_url = "https://www.kotra.or.kr/bigdata/partner/search"

    def setup_page(self, country_code: str, hs_code: str):
        """페이지 설정: 국가 선택 및 HS CODE 입력 (실제 요소 ID 사용)"""
        try:
            self.driver.get(self.base_url)
            time.sleep(3)

            # "해외관세청 실수입기업 검색" 탭 클릭
            try:
                bl_tab = self.driver.find_element(By.ID, "partner_bl")
                self.driver.execute_script("arguments[0].click();", bl_tab)
                time.sleep(3)  # 탭 전환 애니메이션 대기
            except:
                pass

            # 국가 선택 (클릭 가능할 때까지 대기)
            country_select = self.wait.until(
                EC.element_to_be_clickable((By.ID, "country-list-ex"))
            )
            select = Select(country_select)
            select.select_by_value(country_code)
            time.sleep(1)

            # HS CODE 자릿수 선택 (6자리)
            try:
                radio_6 = self.wait.until(
                    EC.element_to_be_clickable((By.ID, "hscdDigits6"))
                )
                self.driver.execute_script("arguments[0].click();", radio_6)
                time.sleep(1)
            except:
                pass

            # HS CODE 입력 (실제 ID: hs-code)
            hs_input = self.wait.until(
                EC.element_to_be_clickable((By.ID, "hs-code"))
            )
            hs_input.clear()
            hs_input.send_keys(hs_code)
            time.sleep(1)

            # 검색 버튼 클릭 (XPath로 정확하게 타겟팅)
            search_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH,
                    "//li[@id='partner_bl']//button[contains(@class, 'mu-btn') and contains(text(), '검색')]"))
            )
            self.driver.execute_script("arguments[0].click();", search_button)
            time.sleep(3)

            return True
        except Exception as e:
            print(f"⚠️ 페이지 설정 중 오류: {str(e)}")
            import traceback
            traceback.print_exc()
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

# 테스트용: 1개 국가만 (빠른 테스트)
countries = [
    {'code': 'US', 'name': '미국'},
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

        if len(countries) == 1:
            print("\n💡 테스트가 성공했다면:")
            print("   코드에서 countries 주석을 해제하여 전체 22개국으로 실행하세요")
    else:
        print("\n⚠️ 수집된 데이터가 없습니다.")

except Exception as e:
    print(f"\n❌ 오류 발생: {str(e)}")
    import traceback
    traceback.print_exc()

finally:
    crawler.close()
    print("\n✅ 브라우저 종료 완료")
