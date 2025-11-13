"""
KOTRA 해외바이어 크롤러 - API 직접 호출 방식
Google Colab 환경에서 실행 가능
"""

import requests
import pandas as pd
import time
from typing import List, Dict
import json

class KotraCrawler:
    def __init__(self):
        self.base_url = "https://www.kotra.or.kr"
        self.api_endpoint = "/bigdata/partner/getBLBuyersList"  # API 엔드포인트 (추정)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Content-Type': 'application/json;charset=UTF-8',
            'Origin': 'https://www.kotra.or.kr',
            'Referer': 'https://www.kotra.or.kr/bigdata/partner/search'
        })

    def fetch_data(self, country_code: str, hs_code: str, page: int = 1, page_size: int = 20) -> Dict:
        """
        API를 호출하여 데이터 가져오기

        Parameters:
        - country_code: 국가 코드 (US, RU, VN 등)
        - hs_code: HS CODE (391810)
        - page: 페이지 번호
        - page_size: 페이지당 항목 수
        """
        # API 요청 파라미터
        payload = {
            "impNatCode": country_code,
            "hsCode": hs_code,
            "hsCodeDigits": "6",  # 6자리
            "page": page,
            "pageSize": page_size,
            "sortBy": "",
            "sortOrder": "desc"
        }

        try:
            response = self.session.post(
                self.base_url + self.api_endpoint,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error: Status code {response.status_code}")
                return None

        except Exception as e:
            print(f"Error fetching data: {str(e)}")
            return None

    def parse_company_name(self, company_data: str) -> str:
        """
        회사명 파싱 (HTML 태그 제거)
        """
        if isinstance(company_data, dict):
            return company_data.get('title', '') or company_data.get('name', '')
        return str(company_data).replace('<em style="color: #005da4"></em>', '')

    def crawl_all_countries(self, countries: List[Dict], hs_code: str) -> pd.DataFrame:
        """
        모든 국가에 대해 크롤링 수행

        Parameters:
        - countries: [{'code': 'US', 'name': '미국'}, ...] 형식의 국가 리스트
        - hs_code: HS CODE
        """
        all_data = []

        for country in countries:
            country_code = country['code']
            country_name = country['name']

            print(f"\n{'='*60}")
            print(f"크롤링 시작: {country_name} ({country_code})")
            print(f"{'='*60}")

            page = 1
            while True:
                print(f"  페이지 {page} 처리 중...")

                result = self.fetch_data(country_code, hs_code, page)

                if not result or not result.get('data'):
                    print(f"  더 이상 데이터가 없습니다.")
                    break

                # 데이터 파싱
                items = result.get('data', {}).get('list', [])

                if not items:
                    break

                for item in items:
                    company_data = {
                        '수입국가': country_name,
                        '수입국가코드': country_code,
                        '수입기업': self.parse_company_name(item.get('impCoName', '')),
                        '거래국가수': item.get('natCnt', 0),
                        '거래건수': item.get('totCnt', 0),
                        '총거래금액(USD)': item.get('totImpAmt', 0),
                        '수입예측값': item.get('korImpPredVal', 0),
                        '한국수입여부': item.get('korExpYn', 'N')
                    }
                    all_data.append(company_data)

                print(f"  {len(items)}개 데이터 수집 완료")

                # 다음 페이지 확인
                total_count = result.get('data', {}).get('totalCount', 0)
                if page * 20 >= total_count:
                    print(f"  전체 {total_count}건 수집 완료")
                    break

                page += 1
                time.sleep(1)  # API 부하 방지

            print(f"{country_name} 크롤링 완료: 총 {len([d for d in all_data if d['수입국가코드'] == country_code])}건")
            time.sleep(2)  # 국가 간 대기

        return pd.DataFrame(all_data)

    def save_to_excel(self, df: pd.DataFrame, filename: str):
        """엑셀 파일로 저장"""
        df.to_excel(filename, index=False, engine='openpyxl')
        print(f"\n엑셀 파일 저장 완료: {filename}")

    def save_to_txt(self, df: pd.DataFrame, filename: str):
        """탭으로 구분된 txt 파일로 저장"""
        df.to_csv(filename, sep='\t', index=False, encoding='utf-8-sig')
        print(f"\nTXT 파일 저장 완료: {filename}")


def main():
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
    crawler = KotraCrawler()

    # 크롤링 시작
    print("KOTRA 해외바이어 크롤링 시작")
    print(f"HS CODE: {hs_code}")
    print(f"대상 국가: {len(countries)}개국")

    df = crawler.crawl_all_countries(countries, hs_code)

    # 결과 저장
    print(f"\n\n총 수집 데이터: {len(df)}건")

    # 엑셀 저장
    crawler.save_to_excel(df, f'kotra_buyers_{hs_code}.xlsx')

    # TXT 저장
    crawler.save_to_txt(df, f'kotra_buyers_{hs_code}.txt')

    # 결과 미리보기
    print("\n=== 데이터 미리보기 ===")
    print(df.head(10))
    print("\n=== 국가별 통계 ===")
    print(df.groupby('수입국가').size())


if __name__ == "__main__":
    main()
