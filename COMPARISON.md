# 두 가지 크롤링 방식 비교

## 📊 한눈에 보기

| 특성 | Selenium 버전 | API 버전 |
|------|--------------|----------|
| **추천도** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **안정성** | 매우 높음 | 불확실 |
| **속도** | 느림 (30-60분) | 빠름 (5-10분) |
| **Colab 호환성** | ✅ 완벽 | ✅ 완벽 |
| **설정 난이도** | 쉬움 (자동) | 중간 (API 확인 필요) |
| **리소스 사용** | 높음 | 낮음 |
| **유지보수** | 쉬움 | 어려움 |

## 🎯 언제 어떤 걸 사용할까?

### Selenium 버전을 사용하세요 (`kotra_crawler_selenium.py`)
- ✅ **처음 사용하는 경우**
- ✅ **확실하게 작동하는 걸 원하는 경우**
- ✅ **Google Colab에서 바로 실행하고 싶은 경우**
- ✅ **웹 개발 지식이 없는 경우**
- ✅ **일회성 또는 가끔 사용하는 경우**

### API 버전을 사용하세요 (`kotra_crawler_api.py`)
- ✅ **빠른 속도가 필요한 경우**
- ✅ **정기적으로 대량 크롤링하는 경우**
- ✅ **API 엔드포인트를 직접 확인할 수 있는 경우**
- ✅ **웹 개발 지식이 있는 경우**
- ✅ **서버 리소스가 제한적인 경우**

## 🔍 상세 비교

### 1. Selenium 버전 (`kotra_crawler_selenium.py`)

#### 작동 원리
- 실제 Chrome 브라우저를 자동으로 제어
- 사람이 웹사이트를 사용하는 것처럼 동작
- 드롭다운 선택, 버튼 클릭, 데이터 읽기 모두 자동화

#### 장점
```
✅ 100% 신뢰성 - 웹사이트가 정상적으로 작동하면 크롤러도 작동
✅ 시각적 - 필요시 브라우저 화면을 볼 수 있음
✅ 유지보수 쉬움 - 웹사이트 UI만 똑같으면 계속 작동
✅ 디버깅 쉬움 - 어디서 문제가 생겼는지 쉽게 파악
```

#### 단점
```
❌ 느린 속도 - 브라우저 렌더링 시간 필요
❌ 많은 리소스 - 메모리와 CPU 사용량 높음
❌ 페이지 로딩 대기 필요
```

#### 예상 실행 시간
- 국가당: 약 2-3분
- 22개국 전체: **약 40-60분**

#### 코드 예시
```python
# 드롭다운에서 국가 선택
select = Select(country_select)
select.select_by_value('US')

# 검색 버튼 클릭
search_button.click()

# 테이블 데이터 읽기
rows = driver.find_elements(By.CSS_SELECTOR, "div[role='row']")
```

---

### 2. API 버전 (`kotra_crawler_api.py`)

#### 작동 원리
- 웹사이트의 내부 API를 직접 호출
- 브라우저 없이 순수 데이터 통신만 사용
- JSON 형식으로 데이터를 주고받음

#### 장점
```
✅ 매우 빠름 - 브라우저 렌더링 불필요
✅ 적은 리소스 - 메모리와 CPU 효율적
✅ 깔끔한 코드 - 간단한 HTTP 요청만 사용
✅ 로그 분석 쉬움 - 요청/응답 데이터 명확
```

#### 단점
```
❌ API 엔드포인트 확인 필요 - 현재는 추정값 사용 중
❌ API 변경 시 작동 안함 - 웹사이트 업데이트 시 수정 필요
❌ 인증/보안 이슈 - CSRF 토큰, 쿠키 등이 필요할 수 있음
```

#### ⚠️ 주의사항
현재 코드의 API 엔드포인트는 **추정값**입니다:
```python
self.api_endpoint = "/bigdata/partner/getBLBuyersList"  # ← 확인 필요!
```

실제 사용 전에 반드시 확인해야 합니다!

#### API 엔드포인트 확인 방법

1. **Chrome 개발자 도구 열기**
   - KOTRA 웹사이트 접속
   - F12 키 누르기

2. **Network 탭 선택**
   - Network 탭 클릭
   - XHR 필터 선택

3. **검색 실행**
   - 국가 선택: 미국
   - HS CODE 입력: 391810
   - 검색 버튼 클릭

4. **API 요청 찾기**
   - Network 탭에서 새로운 요청 확인
   - `getBuyers`, `search`, `list` 같은 이름 찾기
   - 클릭해서 다음 정보 확인:
     - Request URL (엔드포인트)
     - Request Method (POST/GET)
     - Request Payload (파라미터 구조)
     - Response (응답 데이터 구조)

5. **코드 수정**
   ```python
   # 확인한 정보로 수정
   self.api_endpoint = "/실제/엔드포인트/경로"

   payload = {
       "실제파라미터1": "값",
       "실제파라미터2": "값"
   }
   ```

#### 예상 실행 시간
- 국가당: 약 10-20초
- 22개국 전체: **약 5-10분**

#### 코드 예시
```python
# API에 직접 요청
response = requests.post(
    "https://www.kotra.or.kr/api/endpoint",
    json={"country": "US", "hsCode": "391810"}
)

# JSON 데이터 파싱
data = response.json()
```

---

## 🚀 실전 사용 가이드

### 시나리오 1: 처음 사용하는 초보자
```
추천: Selenium 버전 ⭐⭐⭐⭐⭐

이유:
- 복잡한 설정 없이 바로 실행 가능
- Google Colab 노트북으로 클릭 한 번에 시작
- 에러가 나도 이해하기 쉬움

실행 방법:
1. KOTRA_Crawler_Colab.ipynb 파일을 Google Colab에 업로드
2. 셀을 순서대로 실행
3. 완료될 때까지 대기 (40-60분)
4. 자동으로 파일 다운로드
```

### 시나리오 2: 매주 데이터를 수집해야 하는 경우
```
추천: API 버전 (확인 후) ⭐⭐⭐⭐

이유:
- 빠른 속도로 시간 절약
- 자동화 스크립트로 만들기 쉬움
- 서버 리소스 효율적

준비 단계:
1. 먼저 Selenium 버전으로 데이터 확인
2. Chrome DevTools로 실제 API 엔드포인트 확인
3. kotra_crawler_api.py 파일 수정
4. 테스트 실행으로 검증
5. 정기 실행 스케줄링
```

### 시나리오 3: 일회성으로 대량 데이터 필요
```
추천: Selenium 버전 ⭐⭐⭐⭐⭐

이유:
- 한 번만 실행하면 되므로 속도는 중요하지 않음
- 신뢰성이 가장 중요
- API 확인하는 시간이 더 오래 걸릴 수 있음

실행 방법:
1. Google Colab에서 KOTRA_Crawler_Colab.ipynb 실행
2. 다른 일 하면서 대기
3. 완료 알림 확인
```

### 시나리오 4: 웹 개발자 / 엔지니어
```
추천: API 버전 시도 후 Selenium 대안 ⭐⭐⭐⭐

이유:
- API가 더 효율적이고 깔끔
- 디버깅과 커스터마이징 쉬움
- 장기적으로 유지보수 비용 낮음

실행 방법:
1. Chrome DevTools로 API 분석 (10분)
2. kotra_crawler_api.py 수정 (10분)
3. 테스트 실행 (1-2개 국가)
4. 작동하면 전체 실행, 안되면 Selenium 사용
```

---

## 📝 결론

### 대부분의 경우
**→ Selenium 버전 사용 추천!** (`kotra_crawler_selenium.py` 또는 `KOTRA_Crawler_Colab.ipynb`)

### API 버전을 선택하려면
1. Chrome DevTools를 사용할 수 있어야 함
2. HTTP 요청/응답 구조를 이해해야 함
3. 실제 API 엔드포인트를 확인하고 코드를 수정해야 함
4. 테스트와 검증 과정을 거쳐야 함

### 최선의 방법
1. **일단 Selenium 버전으로 시작**
2. 작동 확인 및 데이터 검증
3. 정기적으로 사용할 예정이라면 API 버전 검토
4. API 확인 및 수정 후 전환

---

## 🎓 추가 학습 자료

### Selenium에 대해 더 알고 싶다면
- [Selenium 공식 문서](https://www.selenium.dev/documentation/)
- [Python Selenium 튜토리얼](https://selenium-python.readthedocs.io/)

### API 크롤링에 대해 더 알고 싶다면
- [Chrome DevTools 사용법](https://developer.chrome.com/docs/devtools/)
- [HTTP 요청 이해하기](https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods)
- [Python Requests 라이브러리](https://requests.readthedocs.io/)
