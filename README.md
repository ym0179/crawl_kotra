# KOTRA 해외바이어 크롤러

KOTRA 해외바이어 정보 사이트(https://www.kotra.or.kr/bigdata/partner/search)에서 데이터를 수집하는 크롤러입니다.

## 📋 기능

- **대상 국가**: 22개국 (러시아, 멕시코, 미국, 방글라데시, 베트남, 아르헨티나, 에콰도르, 우간다, 우즈베키스탄, 인도, 인도네시아, 일본, 칠레, 카자흐스탄, 케냐, 콜롬비아, 튀르키예, 파나마, 파라과이, 파키스탄, 페루, 필리핀)
- **HS CODE**: 391810 (6자리)
- **수집 데이터**:
  - 수입국가 / 수입국가코드
  - 수입기업명
  - 거래국가수
  - 거래건수
  - 총거래금액(USD)
  - 수입예측값
  - 한국수입여부

- **출력 형식**: Excel (.xlsx) 또는 탭 구분 텍스트 파일 (.txt)

## 📁 파일 구성

### 1. `kotra_crawler_selenium.py` ⭐ **추천**
Selenium을 사용한 브라우저 자동화 방식입니다.

**장점:**
- ✅ 실제 웹사이트 UI를 통해 동작하므로 안정적
- ✅ Google Colab에서 바로 실행 가능
- ✅ 자동으로 필요한 패키지 설치

**단점:**
- ⏱️ 상대적으로 느림 (브라우저 렌더링 필요)

### 2. `kotra_crawler_api.py`
API 직접 호출 방식입니다.

**장점:**
- ⚡ 빠른 속도
- 💾 적은 리소스 사용

**단점:**
- ⚠️ API 엔드포인트가 추정값이므로 작동하지 않을 수 있음
- ⚠️ API 구조 변경 시 수정 필요

## 🚀 Google Colab에서 사용하기 (추천)

### Selenium 버전 사용 (추천)

```python
# 1. GitHub에서 파일 다운로드
!wget https://raw.githubusercontent.com/YOUR_REPO/kotra_crawler_selenium.py

# 2. 실행
!python kotra_crawler_selenium.py
```

또는 직접 코드를 Colab 셀에 복사하여 실행:

```python
# kotra_crawler_selenium.py의 전체 코드를 복사
# 그리고 마지막에 실행
if __name__ == "__main__":
    main()
```

### 실행 결과

- `kotra_buyers_391810.xlsx` - 엑셀 파일 자동 다운로드
- `kotra_buyers_391810.txt` - 탭 구분 텍스트 파일 자동 다운로드

## 💻 로컬 환경에서 사용하기

### 1. 필요한 패키지 설치

```bash
pip install selenium pandas openpyxl requests
```

### 2. ChromeDriver 설치

- Chrome 브라우저가 설치되어 있어야 합니다
- ChromeDriver는 자동으로 관리됩니다 (Selenium 4.x)

### 3. 실행

```bash
# Selenium 버전 (추천)
python kotra_crawler_selenium.py

# API 버전 (API 엔드포인트 확인 후)
python kotra_crawler_api.py
```

## 📊 출력 파일 형식

### Excel 파일 (.xlsx)
```
| 수입국가 | 수입국가코드 | 수입기업 | 거래국가수 | 거래건수 | 총거래금액(USD) | 수입예측값 | 한국수입여부 |
|----------|--------------|----------|------------|----------|-----------------|------------|--------------|
| 미국     | US           | ABC Corp | 5          | 120      | 1500000         | 85000      | Y            |
```

### 텍스트 파일 (.txt)
탭(\t)으로 구분된 형식:
```
수입국가	수입국가코드	수입기업	거래국가수	거래건수	총거래금액(USD)	수입예측값	한국수입여부
미국	US	ABC Corp	5	120	1500000	85000	Y
```

## ⚙️ 커스터마이징

### 다른 HS CODE 사용

```python
# main() 함수에서 수정
hs_code = '391810'  # <- 여기를 원하는 HS CODE로 변경
```

### 특정 국가만 크롤링

```python
# countries 리스트에서 원하는 국가만 남기기
countries = [
    {'code': 'US', 'name': '미국'},
    {'code': 'VN', 'name': '베트남'},
]
```

### 크롤링 속도 조절

```python
# kotra_crawler_selenium.py에서
time.sleep(1)  # <- 페이지 간 대기 시간 조절
time.sleep(2)  # <- 국가 간 대기 시간 조절
```

## 🔍 API 버전 사용 시 주의사항

API 버전을 사용하려면 먼저 실제 API 엔드포인트를 확인해야 합니다:

1. 브라우저에서 https://www.kotra.or.kr/bigdata/partner/search 접속
2. 개발자 도구 열기 (F12)
3. Network 탭 선택
4. 국가와 HS CODE 선택 후 검색
5. XHR/Fetch 요청 확인
6. 실제 API 엔드포인트와 요청 형식을 `kotra_crawler_api.py`에 반영

## ⚠️ 주의사항

1. **크롤링 예의**: 서버에 부담을 주지 않도록 적절한 대기 시간을 설정하세요
2. **이용 약관**: KOTRA 웹사이트의 이용 약관을 확인하세요
3. **데이터 사용**: 수집한 데이터는 개인적 용도로만 사용하세요
4. **오류 처리**: 네트워크 오류 등으로 일부 국가 데이터가 누락될 수 있습니다

## 📝 문제 해결

### Selenium에서 ChromeDriver 오류
```bash
# ChromeDriver 수동 설치
pip install webdriver-manager
```

```python
# 코드에 추가
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

service = Service(ChromeDriverManager().install())
self.driver = webdriver.Chrome(service=service, options=chrome_options)
```

### Colab에서 파일 다운로드 안됨
```python
# 수동 다운로드
from google.colab import files
files.download('kotra_buyers_391810.xlsx')
files.download('kotra_buyers_391810.txt')
```

## 📄 라이선스

개인 및 교육 목적으로 자유롭게 사용 가능합니다.

## 🤝 기여

버그 리포트나 개선 제안은 이슈로 등록해주세요.
