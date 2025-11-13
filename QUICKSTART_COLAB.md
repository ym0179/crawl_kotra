# Google Colab 빠른 시작 가이드

## ⚡ 가장 빠른 방법 (복사 & 붙여넣기)

에러가 발생했다면 이 방법을 사용하세요!

### 1️⃣ Google Colab 열기
https://colab.research.google.com/ 접속

### 2️⃣ 새 노트북 만들기
- "새 노트북" 클릭

### 3️⃣ 코드 복사 & 실행

**방법 A: GitHub에서 직접 실행**
```python
# 셀 1: 파일 다운로드 및 실행
!wget -q https://raw.githubusercontent.com/YOUR_USERNAME/crawl_kotra/main/kotra_crawler_colab_fixed.py
!python kotra_crawler_colab_fixed.py
```

**방법 B: 코드 직접 복사 (추천)** ⭐

1. `kotra_crawler_colab_fixed.py` 파일을 엽니다
2. 전체 코드를 복사합니다
3. Colab의 새 셀에 붙여넣습니다
4. 실행 (Shift + Enter)

### 4️⃣ 결과 확인
- 크롤링이 완료되면 자동으로 파일이 다운로드됩니다
- `kotra_buyers_391810.xlsx` (엑셀)
- `kotra_buyers_391810.txt` (탭 구분 텍스트)

---

## 🔧 에러 해결 방법

### 에러: `SessionNotCreatedException`

이미 해결되었습니다! `kotra_crawler_colab_fixed.py` 파일을 사용하세요.

**원인:**
- Chrome/ChromeDriver 버전 불일치
- ChromeDriver 경로 문제

**해결책:**
- ✅ 수정된 파일 (`kotra_crawler_colab_fixed.py`) 사용
- ✅ 명시적 ChromeDriver 경로 설정 (`/usr/bin/chromedriver`)
- ✅ Colab 환경에 최적화된 Chrome 옵션 추가

### 에러: `NoSuchElementException`

**원인:**
- 페이지 로딩이 완료되지 않음
- 웹사이트 구조 변경

**해결책:**
```python
# 대기 시간 늘리기
time.sleep(3)  # 2초 → 3초로 변경
```

### 에러: 데이터가 수집되지 않음

**원인:**
- 웹사이트에서 해당 국가/HS CODE 데이터가 없음
- AG Grid 구조 변경

**해결책:**
1. 브라우저에서 수동으로 확인
2. 다른 국가로 테스트
3. HS CODE 변경 테스트

---

## 🎯 테스트 방법 (시간 절약)

전체 22개국을 크롤링하기 전에 먼저 **1-2개 국가만 테스트**하세요:

```python
# 테스트용: 2개 국가만
countries = [
    {'code': 'US', 'name': '미국'},
    {'code': 'VN', 'name': '베트남'},
]
```

테스트 성공 후 전체 국가로 변경:
```python
# 전체 22개국
countries = [
    {'code': 'RU', 'name': '러시아연방'},
    {'code': 'MX', 'name': '멕시코'},
    {'code': 'US', 'name': '미국'},
    # ... 나머지 국가들
]
```

---

## ⏱️ 예상 시간

| 국가 수 | 예상 시간 |
|--------|----------|
| 1개국 | 2-3분 |
| 5개국 | 10-15분 |
| 10개국 | 20-30분 |
| 22개국 (전체) | 40-60분 |

**💡 팁:** 크롤링 중에는 다른 작업을 하시고, 완료 알림을 기다리세요!

---

## 📱 진행 상황 확인

크롤링 중에는 다음과 같은 메시지가 표시됩니다:

```
📊 진행률: 5/22 (22%)
🔍 크롤링 시작: 베트남 (VN)
  📄 페이지 1 처리 중...
  ✅ 20개 데이터 수집 완료
  📄 페이지 2 처리 중...
  ✅ 18개 데이터 수집 완료
  🎉 전체 38건 수집 완료
✅ 베트남 완료: 38건
```

---

## 💾 결과 파일 형식

### Excel 파일
```
수입국가    수입국가코드    수입기업              거래국가수    거래건수    총거래금액(USD)
미국        US            ABC Company          5            120         1500000
베트남      VN            XYZ Corporation      3            85          890000
```

### TXT 파일 (탭 구분)
```
수입국가[TAB]수입국가코드[TAB]수입기업[TAB]거래국가수[TAB]거래건수[TAB]총거래금액(USD)
미국[TAB]US[TAB]ABC Company[TAB]5[TAB]120[TAB]1500000
베트남[TAB]VN[TAB]XYZ Corporation[TAB]3[TAB]85[TAB]890000
```

---

## 🆘 여전히 에러가 발생한다면?

### 1. Runtime 재시작
- Colab 메뉴: `런타임` → `런타임 다시 시작`
- 코드 다시 실행

### 2. 새 노트북 생성
- 완전히 새로운 Colab 노트북 생성
- 코드 다시 복사 & 실행

### 3. Chrome 수동 설치
```python
# 셀 1: Chrome 수동 설치
!apt-get update
!apt-get install -y chromium-browser chromium-chromedriver
!pip install selenium pandas openpyxl
```

```python
# 셀 2: 크롤러 코드 실행
# (kotra_crawler_colab_fixed.py의 "# 2단계" 이후 코드만 복사)
```

---

## ✅ 성공 체크리스트

- [ ] Google Colab 노트북 생성 완료
- [ ] `kotra_crawler_colab_fixed.py` 코드 복사 완료
- [ ] 코드 실행 (Shift + Enter)
- [ ] Chrome 설치 메시지 확인
- [ ] 크롤링 진행 메시지 확인
- [ ] 파일 다운로드 완료
- [ ] Excel/TXT 파일 열어서 데이터 확인

---

## 🎓 커스터마이징

### 다른 HS CODE 사용
```python
hs_code = '123456'  # 원하는 6자리 HS CODE
```

### 특정 국가만 선택
```python
countries = [
    {'code': 'US', 'name': '미국'},
    {'code': 'JP', 'name': '일본'},
    {'code': 'CN', 'name': '중국'},
]
```

### 크롤링 속도 조절
```python
time.sleep(2)  # 국가 간 대기 시간 (초)
                # 더 빠르게: 1초
                # 더 안전하게: 3-5초
```

---

## 🎉 완료!

이제 KOTRA 해외바이어 데이터를 손쉽게 수집할 수 있습니다!

문제가 있으면 GitHub Issues에 등록해주세요.
