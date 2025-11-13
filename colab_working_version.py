"""
KOTRA 크롤러 - 완전 작동 버전
페이지 로딩 문제 해결 + 디버깅 기능 포함
"""

print("=" * 70)
print("🚀 KOTRA 크롤러 시작")
print("=" * 70)

import subprocess
import sys
import os

# 필수 패키지 설치
print("\n📦 패키지 설치 중...")
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
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
import pandas as pd
import time
from typing import List, Dict
import re


class KotraSeleniumCrawler:
    def __init__(self):
        """Selenium 기반 크롤러 초기화"""

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
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

        # 페이지 로딩 최적화
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.page_load_strategy = 'normal'  # 완전 로딩 대기

        # Chrome 바이너리
        chrome_options.binary_location = '/usr/bin/chromium-browser'

        try:
            print("🔍 ChromeDriver 다운로드 중...")
            service = Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())

            print("🚀 Chrome 브라우저 시작 중...")
            self.driver = webdriver.Chrome(service=service, options=chrome_options)

            # 타임아웃 설정 (더 길게)
            self.driver.set_page_load_timeout(30)
            self.driver.implicitly_wait(10)

            print("✅ Chrome 브라우저 시작 성공!\n")

        except Exception as e:
            print(f"❌ Chrome 시작 실패: {str(e)}")
            raise

        self.wait = WebDriverWait(self.driver, 30)  # 30초로 증가
        self.base_url = "https://www.kotra.or.kr/bigdata/partner/search"

    def save_screenshot(self, filename="debug_screenshot.png"):
        """디버깅용 스크린샷 저장"""
        try:
            self.driver.save_screenshot(filename)
            print(f"📸 스크린샷 저장: {filename}")
        except:
            pass

    def setup_page(self, country_code: str, hs_code: str):
        """페이지 설정: 국가 선택 및 HS CODE 입력 (강화된 버전)"""
        try:
            print(f"  📡 페이지 로드 중: {self.base_url}")
            self.driver.get(self.base_url)

            # 페이지 완전 로딩 대기
            print(f"  ⏳ 페이지 로딩 대기 중... (최대 10초)")
            time.sleep(10)  # 충분한 대기 시간

            # 스크린샷 저장 (디버깅용)
            self.save_screenshot("step1_page_loaded.png")

            # 현재 URL 확인
            current_url = self.driver.current_url
            print(f"  ✅ 현재 URL: {current_url}")

            # 페이지 제목 확인
            page_title = self.driver.title
            print(f"  ✅ 페이지 제목: {page_title}")

            # 국가 드롭다운 찾기 (여러 방법 시도)
            print(f"  🔍 국가 선택 드롭다운 찾는 중...")

            country_select = None
            try:
                # 방법 1: ID로 찾기
                country_select = self.wait.until(
                    EC.presence_of_element_located((By.ID, "country-list-ex"))
                )
                print(f"  ✅ 국가 드롭다운 발견 (ID)")
            except TimeoutException:
                print(f"  ⚠️ ID로 찾기 실패, 다른 방법 시도...")

                # 방법 2: name으로 찾기
                try:
                    country_select = self.driver.find_element(By.NAME, "country")
                    print(f"  ✅ 국가 드롭다운 발견 (NAME)")
                except NoSuchElementException:
                    # 방법 3: CSS selector로 찾기
                    try:
                        country_select = self.driver.find_element(By.CSS_SELECTOR, "select[name*='country'], select[id*='country']")
                        print(f"  ✅ 국가 드롭다운 발견 (CSS)")
                    except NoSuchElementException:
                        print(f"  ❌ 국가 드롭다운을 찾을 수 없습니다")
                        self.save_screenshot("error_no_country_dropdown.png")

                        # 페이지 소스 일부 출력
                        page_source = self.driver.page_source[:500]
                        print(f"  📄 페이지 소스 (처음 500자):\n{page_source}")
                        return False

            if country_select:
                select = Select(country_select)
                select.select_by_value(country_code)
                print(f"  ✅ 국가 선택: {country_code}")
                time.sleep(2)

                self.save_screenshot("step2_country_selected.png")

            # HS CODE 입력 필드 찾기
            print(f"  🔍 HS CODE 입력 필드 찾는 중...")

            hs_input = None
            try:
                # 방법 1: ID로 찾기
                hs_input = self.driver.find_element(By.ID, "hscode-input-ex")
                print(f"  ✅ HS CODE 입력 필드 발견 (ID)")
            except NoSuchElementException:
                print(f"  ⚠️ ID로 찾기 실패, 다른 방법 시도...")

                # 방법 2: name으로 찾기
                try:
                    hs_input = self.driver.find_element(By.NAME, "hsCode")
                    print(f"  ✅ HS CODE 입력 필드 발견 (NAME)")
                except NoSuchElementException:
                    # 방법 3: CSS selector로 찾기
                    try:
                        hs_input = self.driver.find_element(By.CSS_SELECTOR, "input[name*='hs'], input[id*='hs'], input[placeholder*='HS']")
                        print(f"  ✅ HS CODE 입력 필드 발견 (CSS)")
                    except NoSuchElementException:
                        print(f"  ❌ HS CODE 입력 필드를 찾을 수 없습니다")
                        self.save_screenshot("error_no_hscode_input.png")
                        return False

            if hs_input:
                hs_input.clear()
                hs_input.send_keys(hs_code)
                print(f"  ✅ HS CODE 입력: {hs_code}")
                time.sleep(2)

                self.save_screenshot("step3_hscode_entered.png")

            # 검색 버튼 찾기
            print(f"  🔍 검색 버튼 찾는 중...")

            search_button = None
            try:
                # 방법 1: CSS class로 찾기
                search_button = self.driver.find_element(By.CSS_SELECTOR, "button.btn-search")
                print(f"  ✅ 검색 버튼 발견 (CSS)")
            except NoSuchElementException:
                # 방법 2: 텍스트로 찾기
                try:
                    search_button = self.driver.find_element(By.XPATH, "//button[contains(text(), '검색') or contains(text(), 'Search')]")
                    print(f"  ✅ 검색 버튼 발견 (XPATH)")
                except NoSuchElementException:
                    # 방법 3: type으로 찾기
                    try:
                        search_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
                        print(f"  ✅ 검색 버튼 발견 (TYPE)")
                    except NoSuchElementException:
                        print(f"  ❌ 검색 버튼을 찾을 수 없습니다")
                        self.save_screenshot("error_no_search_button.png")
                        return False

            if search_button:
                search_button.click()
                print(f"  ✅ 검색 버튼 클릭")

                # 검색 결과 로딩 대기
                print(f"  ⏳ 검색 결과 로딩 대기 중... (최대 10초)")
                time.sleep(10)

                self.save_screenshot("step4_search_results.png")

            print(f"  ✅ 페이지 설정 완료!")
            return True

        except Exception as e:
            print(f"  ❌ 페이지 설정 중 오류: {str(e)}")
            self.save_screenshot("error_setup.png")

            # 더 자세한 에러 정보
            import traceback
            print(f"  📋 상세 에러:")
            traceback.print_exc()

            return False

    def extract_table_data(self) -> List[Dict]:
        """현재 페이지의 AG Grid 테이블 데이터 추출"""
        data = []
        try:
            print(f"    🔍 테이블 행 찾는 중...")

            # AG Grid 행 찾기 (여러 방법 시도)
            rows = []
            try:
                rows = self.driver.find_elements(By.CSS_SELECTOR, "div[role='row'][row-index]")
                print(f"    ✅ {len(rows)}개 행 발견")
            except:
                print(f"    ⚠️ AG Grid 형식 행을 찾을 수 없습니다")

                # 대안: 일반 테이블 행
                try:
                    rows = self.driver.find_elements(By.CSS_SELECTOR, "tr")
                    print(f"    ✅ {len(rows)}개 행 발견 (일반 테이블)")
                except:
                    print(f"    ❌ 테이블을 찾을 수 없습니다")
                    self.save_screenshot("error_no_table.png")
                    return []

            if not rows:
                print(f"    ℹ️ 행이 없습니다")
                return []

            for idx, row in enumerate(rows):
                try:
                    cells = row.find_elements(By.CSS_SELECTOR, "div[role='gridcell']")

                    if not cells:
                        # 대안: td 요소
                        cells = row.find_elements(By.TAG_NAME, "td")

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

                        if idx == 0:
                            print(f"    📝 첫 번째 데이터 예시: {company_name}")

                except Exception as e:
                    continue

            print(f"    ✅ {len(data)}개 데이터 추출 완료")
            return data

        except Exception as e:
            print(f"    ❌ 테이블 데이터 추출 오류: {str(e)}")
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
                if page == 1:
                    print(f"  ⚠️ 첫 페이지에 데이터가 없습니다. 페이지 로딩 문제일 수 있습니다.")
                else:
                    print(f"  ℹ️ 더 이상 데이터가 없습니다.")
                break

            for item in page_data:
                item['수입국가'] = country_name
                item['수입국가코드'] = country_code

            all_data.extend(page_data)

            if not self.go_to_next_page():
                print(f"  🎉 전체 {len(all_data)}건 수집 완료")
                break

            page += 1
            time.sleep(2)

        return all_data

    def crawl_all_countries(self, countries: List[Dict], hs_code: str) -> pd.DataFrame:
        """모든 국가 크롤링"""
        all_data = []

        for i, country in enumerate(countries, 1):
            print(f"\n📊 진행률: {i}/{len(countries)} ({i*100//len(countries)}%)")

            country_data = self.crawl_country(country['code'], country['name'], hs_code)
            all_data.extend(country_data)

            print(f"✅ {country['name']} 완료: {len(country_data)}건")
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


# ============================================================
# 실행 코드
# ============================================================

print("\n" + "=" * 70)
print("크롤링 설정")
print("=" * 70)

# 테스트용: 1개 국가
countries = [
    {'code': 'US', 'name': '미국'},
]

hs_code = '391810'

print(f"✅ 대상 국가: {len(countries)}개국")
print(f"✅ HS CODE: {hs_code}")
print(f"\n💡 디버깅 모드: 각 단계마다 스크린샷이 저장됩니다")

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
        print("\n💡 문제 해결:")
        print("   1. 저장된 스크린샷들을 확인하세요 (step1_page_loaded.png 등)")
        print("   2. KOTRA 웹사이트가 정상 작동하는지 확인하세요")
        print("   3. HS CODE가 올바른지 확인하세요")

        # 스크린샷 다운로드
        try:
            from google.colab import files
            for screenshot in ['step1_page_loaded.png', 'step2_country_selected.png',
                              'step3_hscode_entered.png', 'step4_search_results.png']:
                if os.path.exists(screenshot):
                    files.download(screenshot)
        except:
            pass

except Exception as e:
    print(f"\n❌ 오류 발생: {str(e)}")
    import traceback
    traceback.print_exc()

finally:
    crawler.close()
    print("\n✅ 브라우저 종료 완료")
