"""
KOTRA 해외바이어 크롤러 - Google Colab 전용 버전 (에러 수정됨)
Google Colab에서 바로 실행 가능
"""

# ============================================================
# 1단계: 필요한 패키지 설치
# ============================================================
print("=" * 60)
print("KOTRA 해외바이어 크롤러 설치 시작")
print("=" * 60)

import subprocess
import sys

print("\n📦 Chrome 및 필요한 패키지 설치 중...")
print("(약 1-2분 소요됩니다. 잠시만 기다려주세요...)\n")

# Chrome 및 ChromeDriver 설치
subprocess.run(['apt-get', 'update', '-qq'], capture_output=True)
subprocess.run(['apt-get', 'install', '-y', '-qq',
               'chromium-browser', 'chromium-chromedriver'],
              capture_output=True)

# Python 패키지 설치
subprocess.run([sys.executable, '-m', 'pip', 'install', '-q',
               'selenium', 'pandas', 'openpyxl'],
              capture_output=True)

print("✅ 설치 완료!\n")


# ============================================================
# 2단계: 크롤러 클래스 정의
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
        """Selenium 기반 크롤러 초기화 (Colab 전용)"""
        chrome_options = Options()

        # Colab 환경에 최적화된 설정
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

        # ChromeDriver 서비스 설정
        service = Service('/usr/bin/chromedriver')
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.wait = WebDriverWait(self.driver, 20)
        self.base_url = "https://www.kotra.or.kr/bigdata/partner/search"

    def setup_page(self, country_code: str, hs_code: str):
        """페이지 설정: 국가 선택 및 HS CODE 입력"""
        try:
            self.driver.get(self.base_url)
            time.sleep(2)

            # 국가 드롭다운 선택
            country_select = self.wait.until(
                EC.presence_of_element_located((By.ID, "country-list-ex"))
            )
            select = Select(country_select)
            select.select_by_value(country_code)
            time.sleep(1)

            # HS CODE 입력
            hs_input = self.driver.find_element(By.ID, "hscode-input-ex")
            hs_input.clear()
            hs_input.send_keys(hs_code)
            time.sleep(1)

            # 검색 버튼 클릭
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
# 3단계: 크롤링 설정
# ============================================================
print("\n" + "=" * 60)
print("크롤링 설정")
print("=" * 60)

# 크롤링할 국가 목록 (전체 22개국)
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

# HS CODE 설정
hs_code = '391810'

print(f"✅ 대상 국가: {len(countries)}개국")
print(f"✅ HS CODE: {hs_code}")
print("\n⚠️ 주의: 전체 크롤링은 30-60분 정도 소요됩니다.")
print("   테스트하려면 countries 리스트에서 일부 국가만 남기고 실행하세요.")


# ============================================================
# 4단계: 크롤링 실행
# ============================================================
print("\n" + "=" * 60)
print("크롤링 시작")
print("=" * 60)

# 크롤러 초기화
crawler = KotraSeleniumCrawler()

try:
    # 크롤링 실행
    df = crawler.crawl_all_countries(countries, hs_code)

    print("\n\n" + "=" * 60)
    print("✅ 크롤링 완료!")
    print("=" * 60)
    print(f"총 수집 데이터: {len(df)}건")

    if len(df) > 0:
        # 결과 미리보기
        print("\n📊 데이터 미리보기:")
        print(df.head(10))

        print("\n📈 국가별 통계:")
        country_stats = df.groupby('수입국가').size().reset_index(name='기업수')
        print(country_stats)

        # 엑셀 파일 저장
        excel_file = f'kotra_buyers_{hs_code}.xlsx'
        df.to_excel(excel_file, index=False, engine='openpyxl')
        print(f"\n✅ 엑셀 파일 저장: {excel_file}")

        # 탭 구분 텍스트 파일 저장
        txt_file = f'kotra_buyers_{hs_code}.txt'
        df.to_csv(txt_file, sep='\t', index=False, encoding='utf-8-sig')
        print(f"✅ TXT 파일 저장: {txt_file}")

        # 파일 다운로드 (Colab)
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
    # 브라우저 종료
    crawler.close()
    print("\n✅ 브라우저 종료 완료")
