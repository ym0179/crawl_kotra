"""
KOTRA 크롤러 - 실제 웹사이트 구조에 맞춰 수정된 버전
실제 요소 ID를 사용합니다
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
from typing import List, Dict
import re
import os

print("=" * 70)
print("KOTRA 해외바이어 크롤러 (수정 버전)")
print("=" * 70)


class KotraSeleniumCrawler:
    def __init__(self, headless: bool = False):
        """
        Selenium 기반 크롤러 초기화

        Parameters:
        - headless: 브라우저를 백그라운드에서 실행할지 여부
        """
        chrome_options = Options()

        if headless:
            chrome_options.add_argument('--headless=new')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')

        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

        # ChromeDriver 자동 다운로드
        print("\n🔍 ChromeDriver 설정 중...")
        service = Service(ChromeDriverManager().install())

        print("🚀 Chrome 브라우저 시작 중...")
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

        # 타임아웃 설정
        self.driver.set_page_load_timeout(60)
        self.driver.implicitly_wait(10)

        print("✅ Chrome 브라우저 시작 성공!\n")

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

            # 국가 선택 (요소가 클릭 가능할 때까지 대기)
            print(f"  🔍 국가 드롭다운 찾기 (ID: country-list-ex)...")
            country_select = self.wait.until(
                EC.element_to_be_clickable((By.ID, "country-list-ex"))
            )
            select = Select(country_select)
            select.select_by_value(country_code)
            print(f"  ✅ 국가 선택: {country_code}")
            time.sleep(2)

            # HS CODE 자릿수 선택 (6자리)
            print(f"  🔍 6자리 라디오 버튼 클릭...")
            radio_6 = self.wait.until(
                EC.element_to_be_clickable((By.ID, "hscdDigits6"))
            )
            self.driver.execute_script("arguments[0].click();", radio_6)
            print(f"  ✅ 6자리 선택")
            time.sleep(1)

            # HS CODE 입력 (실제 ID: hs-code)
            print(f"  🔍 HS CODE 입력 필드 찾기 (ID: hs-code)...")
            hs_input = self.wait.until(
                EC.element_to_be_clickable((By.ID, "hs-code"))
            )
            hs_input.clear()
            hs_input.send_keys(hs_code)
            print(f"  ✅ HS CODE 입력: {hs_code}")
            time.sleep(2)

            # 검색 버튼 클릭 (두 번째 검색 버튼)
            print(f"  🔍 검색 버튼 찾기 (두 번째 검색 버튼)...")
            try:
                # 모든 검색 버튼 찾기
                search_buttons = self.driver.find_elements(By.CSS_SELECTOR, "button.mu-btn")
                search_btn_list = [btn for btn in search_buttons if '검색' in btn.text]

                if len(search_btn_list) >= 2:
                    # 두 번째 검색 버튼 클릭
                    self.driver.execute_script("arguments[0].click();", search_btn_list[1])
                    print(f"  ✅ 검색 실행 (두 번째 검색 버튼)")
                else:
                    print(f"  ⚠️ 검색 버튼이 {len(search_btn_list)}개만 발견됨")
                    if len(search_btn_list) >= 1:
                        self.driver.execute_script("arguments[0].click();", search_btn_list[0])
                        print(f"  ⚠️ 첫 번째 검색 버튼으로 대체")
            except Exception as e:
                print(f"  ❌ 검색 버튼 클릭 실패: {str(e)}")

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
        """AG Grid 테이블 데이터 추출"""
        data = []
        try:
            print(f"    🔍 AG Grid 테이블 행 찾기...")

            # AG Grid 행 찾기
            rows = self.driver.find_elements(By.CSS_SELECTOR, "div[role='row'][row-index]")
            print(f"    ✅ {len(rows)}개 행 발견 (중복 포함 가능)")

            # row-index 기준으로 중복 제거
            seen_indices = set()
            unique_rows = []

            for row in rows:
                row_idx = row.get_attribute('row-index')
                if row_idx and row_idx not in seen_indices:
                    seen_indices.add(row_idx)
                    unique_rows.append((int(row_idx), row))

            # row-index 순서로 정렬
            unique_rows.sort(key=lambda x: x[0])
            print(f"    ✅ {len(unique_rows)}개 고유 행 (중복 제거 후)")

            for idx, (row_index, row) in enumerate(unique_rows):
                try:
                    # 진행 상황 표시 (매 5개마다)
                    if idx == 0 or (idx + 1) % 5 == 0:
                        print(f"    📊 진행: {idx + 1}/{len(unique_rows)} 행 처리 중...")

                    cells = row.find_elements(By.CSS_SELECTOR, "div[role='gridcell']")

                    if len(cells) >= 7:
                        # 회사명 추출 (title 속성에서 가져오기)
                        try:
                            company_name_elem = cells[1].find_element(By.CSS_SELECTOR, "span[title]")
                            company_name = company_name_elem.get_attribute('title').strip()
                        except:
                            # title 속성이 없으면 텍스트로 가져오기
                            company_name = cells[1].text.strip()

                        # 회사명이 비어있으면 스킵
                        if not company_name:
                            continue

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
                            print(f"    📝 첫 번째 데이터: {company_name}")

                except Exception as e:
                    if idx < 3:  # 처음 3개 행에서 에러 발생 시 디버깅 정보 출력
                        print(f"    ⚠️ 행 {idx} 처리 중 오류: {str(e)}")
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
                if page == 1:
                    print(f"  ⚠️ 첫 페이지에 데이터 없음")
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

if __name__ == "__main__":
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
    print(f"✅ Headless: False (브라우저 보이기 모드)")

    print("\n" + "=" * 70)
    print("크롤링 시작")
    print("=" * 70)

    crawler = KotraSeleniumCrawler(headless=False)  # 브라우저 보이기

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

            print("\n🎉 모든 작업 완료!")
        else:
            print("\n⚠️ 데이터 없음")

    except Exception as e:
        print(f"\n❌ 오류: {str(e)}")
        import traceback
        traceback.print_exc()

    finally:
        crawler.close()
