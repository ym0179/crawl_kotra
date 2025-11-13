"""
KOTRA 해외바이어 크롤러 - Selenium 브라우저 자동화 방식
Google Colab 환경에서 실행 가능
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
import pandas as pd
import time
from typing import List, Dict
import re


class KotraSeleniumCrawler:
    def __init__(self, headless: bool = True):
        """
        Selenium 기반 크롤러 초기화

        Parameters:
        - headless: 브라우저를 백그라운드에서 실행할지 여부 (Colab에서는 True 필수)
        """
        chrome_options = Options()

        if headless:
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')

        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 20)
        self.base_url = "https://www.kotra.or.kr/bigdata/partner/search"

    def setup_page(self, country_code: str, hs_code: str):
        """
        페이지 설정: 국가 선택 및 HS CODE 입력

        Parameters:
        - country_code: 국가 코드 (US, RU, VN 등)
        - hs_code: HS CODE (391810)
        """
        try:
            # 페이지 로드
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

            # 결과 로딩 대기
            time.sleep(3)

            return True

        except Exception as e:
            print(f"페이지 설정 중 오류: {str(e)}")
            return False

    def extract_table_data(self) -> List[Dict]:
        """
        현재 페이지의 AG Grid 테이블 데이터 추출
        """
        data = []

        try:
            # AG Grid 행들 찾기
            # AG Grid는 보통 role="row"를 사용
            rows = self.driver.find_elements(By.CSS_SELECTOR, "div[role='row'][row-index]")

            for row in rows:
                try:
                    cells = row.find_elements(By.CSS_SELECTOR, "div[role='gridcell']")

                    if len(cells) >= 7:
                        # 회사명 추출 (em 태그 제거)
                        company_cell = cells[1]
                        company_name = company_cell.text.strip()

                        # 숫자 데이터 추출 및 변환
                        def parse_number(text):
                            """콤마 제거하고 숫자로 변환"""
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

                except Exception as e:
                    print(f"행 파싱 오류: {str(e)}")
                    continue

            return data

        except Exception as e:
            print(f"테이블 데이터 추출 오류: {str(e)}")
            return []

    def get_total_pages(self) -> int:
        """
        전체 페이지 수 확인
        """
        try:
            # 페이지네이션 정보 찾기
            pagination = self.driver.find_element(By.CSS_SELECTOR, ".ag-paging-panel")
            page_info = pagination.text

            # "1 of 10" 형식에서 숫자 추출
            match = re.search(r'of\s+(\d+)', page_info)
            if match:
                return int(match.group(1))

            return 1

        except:
            return 1

    def go_to_next_page(self) -> bool:
        """
        다음 페이지로 이동
        """
        try:
            # 다음 페이지 버튼 찾기
            next_button = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Next Page']")

            # 버튼이 비활성화되어 있으면 마지막 페이지
            if 'disabled' in next_button.get_attribute('class'):
                return False

            next_button.click()
            time.sleep(2)
            return True

        except:
            return False

    def crawl_country(self, country_code: str, country_name: str, hs_code: str) -> List[Dict]:
        """
        단일 국가 크롤링
        """
        print(f"\n{'='*60}")
        print(f"크롤링 시작: {country_name} ({country_code})")
        print(f"{'='*60}")

        all_data = []

        # 페이지 설정
        if not self.setup_page(country_code, hs_code):
            print(f"{country_name} 크롤링 실패")
            return []

        page = 1
        while True:
            print(f"  페이지 {page} 처리 중...")

            # 현재 페이지 데이터 추출
            page_data = self.extract_table_data()

            if not page_data:
                print(f"  데이터가 없습니다.")
                break

            # 국가 정보 추가
            for item in page_data:
                item['수입국가'] = country_name
                item['수입국가코드'] = country_code

            all_data.extend(page_data)
            print(f"  {len(page_data)}개 데이터 수집 완료")

            # 다음 페이지로 이동
            if not self.go_to_next_page():
                print(f"  전체 {len(all_data)}건 수집 완료")
                break

            page += 1
            time.sleep(1)

        return all_data

    def crawl_all_countries(self, countries: List[Dict], hs_code: str) -> pd.DataFrame:
        """
        모든 국가 크롤링
        """
        all_data = []

        for i, country in enumerate(countries, 1):
            print(f"\n진행률: {i}/{len(countries)}")

            country_data = self.crawl_country(
                country['code'],
                country['name'],
                hs_code
            )

            all_data.extend(country_data)

            print(f"{country['name']} 완료: {len(country_data)}건")
            time.sleep(2)  # 국가 간 대기

        # DataFrame 생성 (컬럼 순서 조정)
        df = pd.DataFrame(all_data)

        if not df.empty:
            # 컬럼 순서 정리
            columns_order = [
                '수입국가', '수입국가코드', '수입기업', '거래국가수',
                '거래건수', '총거래금액(USD)', '수입예측값', '한국수입여부'
            ]
            df = df[columns_order]

        return df

    def save_to_excel(self, df: pd.DataFrame, filename: str):
        """엑셀 파일로 저장"""
        df.to_excel(filename, index=False, engine='openpyxl')
        print(f"\n엑셀 파일 저장 완료: {filename}")

    def save_to_txt(self, df: pd.DataFrame, filename: str):
        """탭으로 구분된 txt 파일로 저장"""
        df.to_csv(filename, sep='\t', index=False, encoding='utf-8-sig')
        print(f"\nTXT 파일 저장 완료: {filename}")

    def close(self):
        """브라우저 종료"""
        if self.driver:
            self.driver.quit()


def install_colab_dependencies():
    """
    Google Colab에서 필요한 패키지 설치
    """
    import subprocess
    import sys

    print("Colab 환경 설정 중...")

    # Chrome 및 ChromeDriver 설치
    subprocess.run(['apt-get', 'update'], check=True)
    subprocess.run(['apt-get', 'install', '-y', 'chromium-chromedriver'], check=True)

    # 파이썬 패키지 설치
    subprocess.run([sys.executable, '-m', 'pip', 'install', '-q',
                   'selenium', 'pandas', 'openpyxl'], check=True)

    # ChromeDriver 경로 설정
    import os
    os.environ['PATH'] += ':/usr/lib/chromium-browser/'

    print("설치 완료!")


def main():
    """
    메인 실행 함수
    """
    # Google Colab 환경인지 확인
    try:
        import google.colab
        IN_COLAB = True
        print("Google Colab 환경 감지")
        install_colab_dependencies()
    except:
        IN_COLAB = False
        print("로컬 환경에서 실행")

    # 크롤링할 국가 목록
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

    # HS CODE
    hs_code = '391810'

    # 크롤러 초기화
    crawler = KotraSeleniumCrawler(headless=IN_COLAB)

    try:
        print("\n" + "="*60)
        print("KOTRA 해외바이어 크롤링 시작")
        print(f"HS CODE: {hs_code}")
        print(f"대상 국가: {len(countries)}개국")
        print("="*60)

        # 크롤링 실행
        df = crawler.crawl_all_countries(countries, hs_code)

        # 결과 저장
        print(f"\n\n총 수집 데이터: {len(df)}건")

        if len(df) > 0:
            # 엑셀 저장
            crawler.save_to_excel(df, f'kotra_buyers_{hs_code}.xlsx')

            # TXT 저장 (탭 구분)
            crawler.save_to_txt(df, f'kotra_buyers_{hs_code}.txt')

            # 결과 미리보기
            print("\n=== 데이터 미리보기 ===")
            print(df.head(10))

            print("\n=== 국가별 통계 ===")
            print(df.groupby('수입국가').size())

            # Colab에서 파일 다운로드
            if IN_COLAB:
                from google.colab import files
                print("\n파일 다운로드 중...")
                files.download(f'kotra_buyers_{hs_code}.xlsx')
                files.download(f'kotra_buyers_{hs_code}.txt')
        else:
            print("수집된 데이터가 없습니다.")

    finally:
        # 브라우저 종료
        crawler.close()
        print("\n크롤링 완료!")


if __name__ == "__main__":
    main()
