"""
Chrome/ChromeDriver 문제 진단 스크립트
에러가 발생하면 이 스크립트를 먼저 실행하세요
"""

import subprocess
import sys
import os

print("=" * 70)
print("🔍 Chrome/ChromeDriver 환경 진단")
print("=" * 70)

# 1. Chrome 설치 확인
print("\n1️⃣ Chrome 브라우저 확인")
print("-" * 70)

chrome_binaries = [
    '/usr/bin/chromium-browser',
    '/usr/bin/chromium',
    '/usr/bin/google-chrome',
    '/snap/bin/chromium'
]

chrome_found = False
for binary in chrome_binaries:
    if os.path.exists(binary):
        print(f"✅ 발견: {binary}")
        result = subprocess.run([binary, '--version'],
                               capture_output=True, text=True, check=False)
        if result.returncode == 0:
            print(f"   버전: {result.stdout.strip()}")
        chrome_found = True
    else:
        print(f"❌ 없음: {binary}")

if not chrome_found:
    print("\n⚠️ Chrome이 설치되어 있지 않습니다!")
    print("   해결: !apt-get install -y chromium-browser")

# 2. ChromeDriver 확인
print("\n2️⃣ ChromeDriver 확인")
print("-" * 70)

chromedriver_paths = [
    '/usr/bin/chromedriver',
    '/usr/lib/chromium-browser/chromedriver',
    '/snap/bin/chromium.chromedriver'
]

chromedriver_found = False
for path in chromedriver_paths:
    if os.path.exists(path):
        print(f"✅ 발견: {path}")
        result = subprocess.run([path, '--version'],
                               capture_output=True, text=True, check=False)
        if result.returncode == 0:
            print(f"   버전: {result.stdout.strip()}")

        # 실행 권한 확인
        if os.access(path, os.X_OK):
            print(f"   권한: ✅ 실행 가능")
        else:
            print(f"   권한: ❌ 실행 불가 (chmod +x 필요)")

        chromedriver_found = True
    else:
        print(f"❌ 없음: {path}")

if not chromedriver_found:
    print("\n⚠️ ChromeDriver가 설치되어 있지 않습니다!")
    print("   해결: !apt-get install -y chromium-chromedriver")

# 3. Python 패키지 확인
print("\n3️⃣ Python 패키지 확인")
print("-" * 70)

packages = ['selenium', 'pandas', 'openpyxl']
for package in packages:
    result = subprocess.run([sys.executable, '-m', 'pip', 'show', package],
                           capture_output=True, text=True, check=False)
    if result.returncode == 0:
        # 버전 추출
        for line in result.stdout.split('\n'):
            if line.startswith('Version:'):
                version = line.split(':')[1].strip()
                print(f"✅ {package}: {version}")
                break
    else:
        print(f"❌ {package}: 설치되지 않음")
        print(f"   해결: !pip install {package}")

# 4. 환경 변수 확인
print("\n4️⃣ 환경 변수 확인")
print("-" * 70)

path_env = os.environ.get('PATH', '')
print(f"PATH: {path_env}")

if '/usr/bin' in path_env:
    print("✅ /usr/bin이 PATH에 포함됨")
else:
    print("⚠️ /usr/bin이 PATH에 없음")

# 5. 필수 라이브러리 확인
print("\n5️⃣ 필수 시스템 라이브러리 확인")
print("-" * 70)

required_libs = [
    'libnss3',
    'libgconf-2-4',
    'libfontconfig1'
]

for lib in required_libs:
    result = subprocess.run(['dpkg', '-l', lib],
                           capture_output=True, text=True, check=False)
    if result.returncode == 0 and 'ii' in result.stdout:
        print(f"✅ {lib}: 설치됨")
    else:
        print(f"⚠️ {lib}: 설치되지 않음 (선택사항)")

# 6. /dev/shm 확인
print("\n6️⃣ /dev/shm 공간 확인")
print("-" * 70)

result = subprocess.run(['df', '-h', '/dev/shm'],
                       capture_output=True, text=True, check=False)
if result.returncode == 0:
    print(result.stdout)
else:
    print("⚠️ /dev/shm 정보를 가져올 수 없음")

# 7. Google Colab 환경 확인
print("\n7️⃣ 실행 환경 확인")
print("-" * 70)

try:
    import google.colab
    print("✅ Google Colab 환경")
except ImportError:
    print("❌ 로컬 환경 (Colab 아님)")

# 8. Selenium 테스트
print("\n8️⃣ Selenium 기본 테스트")
print("-" * 70)

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service

    print("Selenium 임포트: ✅")

    # 최소한의 옵션으로 테스트
    chrome_options = Options()
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    # Chrome 바이너리 찾기
    for binary in chrome_binaries:
        if os.path.exists(binary):
            chrome_options.binary_location = binary
            print(f"Chrome 바이너리 사용: {binary}")
            break

    # ChromeDriver 경로 찾기
    chromedriver_path = None
    for path in chromedriver_paths:
        if os.path.exists(path):
            chromedriver_path = path
            break

    if chromedriver_path:
        print(f"ChromeDriver 경로: {chromedriver_path}")

        service = Service(chromedriver_path)

        print("\nChrome 시작 테스트 중...")
        driver = webdriver.Chrome(service=service, options=chrome_options)
        print("✅ Chrome 시작 성공!")

        print("간단한 페이지 로드 테스트 중...")
        driver.get("https://www.google.com")
        print("✅ 페이지 로드 성공!")

        driver.quit()
        print("✅ Chrome 종료 성공!")

        print("\n🎉 모든 테스트 통과! 크롤러가 정상 작동할 것입니다.")

    else:
        print("❌ ChromeDriver를 찾을 수 없습니다.")

except Exception as e:
    print(f"\n❌ Selenium 테스트 실패: {str(e)}")
    import traceback
    print("\n상세 에러:")
    traceback.print_exc()

# 9. 추천 해결 방법
print("\n" + "=" * 70)
print("💡 추천 해결 방법")
print("=" * 70)

if not chrome_found or not chromedriver_found:
    print("\n1️⃣ 먼저 다음 명령어로 재설치하세요:")
    print("```")
    print("!apt-get update")
    print("!apt-get install -y chromium-browser chromium-chromedriver")
    print("!pip install selenium pandas openpyxl")
    print("```")

print("\n2️⃣ 그 다음 'colab_ultimate_fix.py' 파일을 사용하세요:")
print("   이 파일은 모든 문제를 자동으로 해결합니다.")

print("\n3️⃣ 여전히 안되면 Colab Runtime을 재시작하세요:")
print("   런타임 → 런타임 다시 시작")

print("\n" + "=" * 70)
