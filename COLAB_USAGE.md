# 🚀 Colab 한글 폰트 설정 가이드

## 📋 간단한 사용법

### 1️⃣ 첫 번째 실행
```python
# 모듈 다운로드 및 로드
import urllib.request
import importlib.util
import sys

# 모듈 다운로드
url = "https://raw.githubusercontent.com/c0z0c/jupyter_hangul/master/helper_c0z0c_dev.py"
urllib.request.urlretrieve(url, "helper_c0z0c_dev.py")

# 모듈 로드
spec = importlib.util.spec_from_file_location("helper", "helper_c0z0c_dev.py")
helper = importlib.util.module_from_spec(spec)
sys.modules["helper"] = helper
spec.loader.exec_module(helper)

# 설정 시작
helper.setup()
```

### 2️⃣ 재시작 후 실행
재시작이 완료되면 **새로운 셀**에서 다음 코드를 실행:

```python
# 재시작 후 실행
import importlib.util
import sys

# 모듈 다시 로드
spec = importlib.util.spec_from_file_location("helper", "helper_c0z0c_dev.py")
helper = importlib.util.module_from_spec(spec)
sys.modules["helper"] = helper
spec.loader.exec_module(helper)

# 설정 완료
helper.setup()
```

## 🔄 자동 재시작 과정

### 📌 재시작이 필요한 이유
- Colab에서 폰트 설치 후 Python 프로세스가 폰트를 인식하려면 재시작이 필요합니다
- 캐시 삭제만으로는 이미 로드된 폰트 정보를 갱신할 수 없습니다

### 🎯 재시작 과정
1. **폰트 설치**: `fonts-nanum` 패키지 설치
2. **캐시 갱신**: `fc-cache -fv` 실행
3. **안내 메시지**: 재시작 후 실행할 코드 안내
4. **자동 재시작**: `os.kill(os.getpid(), 9)` 실행
5. **수동 실행**: 재시작 후 사용자가 코드 실행

### 📋 재시작 후 실행되는 것들
- ✅ 한글 폰트 설정 (matplotlib)
- ✅ pandas 확장 기능
- ✅ 유틸리티 함수들
- ✅ Google Drive 연결 (Colab)

## 🛠️ 추가 함수들

### `reset_colab_fonts()` - 폰트 문제 해결
```python
# Google Drive 인증 오류나 폰트 문제 발생 시
helper.reset_colab_fonts()  # 폰트 완전 리셋 (런타임 재시작됨)
```
**주요 기능:**
- 기존 fonts-nanum 패키지 완전 제거
- 폰트 캐시 완전 정리 (matplotlib, fontconfig)
- 패키지 목록 업데이트 후 재설치
- 자동 런타임 재시작

### `check_font_status()` - 폰트 상태 확인
```python
helper.check_font_status()  # 현재 폰트 설정 상태 확인
```
**확인 항목:**
- matplotlib 폰트 패밀리 설정
- 설치된 한글 폰트 목록
- Colab/로컬 환경 구분
- Google Drive 마운트 상태

## 🎨 사용 가능한 기능들

### 한글 폰트 지원
```python
import matplotlib.pyplot as plt
plt.figure(figsize=(10, 6))
plt.plot([1, 2, 3, 4], [1, 4, 2, 3])
plt.title('한글 제목')
plt.xlabel('X축 한글')
plt.ylabel('Y축 한글')
plt.show()
```

### pandas 확장 기능
```python
import pandas as pd
df = pd.DataFrame({'이름': ['김철수', '이영희'], '나이': [25, 30]})

# 컬럼 설명 추가
df.set_head_att({'이름': '사용자 이름', '나이': '사용자 나이'})

# 한글 설명과 함께 출력 (다양한 형식 지원)
df.head_att()              # 기본 print 형식
df.head_att(out='html')    # HTML 형식 (Colab에서 예쁘게 표시)
df.head_att(out='str')     # 문자열 형식

# Series도 지원
series = df['이름']
series.set_head_att('이름', '사용자 이름')
series.head_att(out='html')
```

### 파일 읽기 함수
```python
# Colab/로컬 자동 감지
df = helper.pd_read_csv('data.csv')
```

## ❓ 자주 묻는 질문

### Q: 재시작 후 변수가 모두 사라졌어요
A: 정상입니다. 재시작 후 필요한 변수들을 다시 설정하세요.

### Q: 한글이 여전히 깨져요
A: 재시작 후 `helper.setup()`을 다시 실행했는지 확인하세요.

### Q: Google Drive 인증 오류가 발생해요
A: `helper.reset_colab_fonts()`를 실행하여 완전히 리셋하세요.

### Q: 에러가 계속 발생해요
A: 런타임을 완전히 재시작하고 처음부터 다시 시도하세요.

### Q: DataFrame의 한글 컬럼 설명이 안 보여요
A: `df.head_att(out='html')`을 사용하면 Colab에서 예쁘게 표시됩니다.

## 🔧 문제 해결

### 1. Google Drive 인증 오류 해결
```python
# 완전한 폰트 리셋 (권장)
helper.reset_colab_fonts()  # 자동으로 재시작됨

# 재시작 후
helper.setup()
```

### 2. 수동 설정 방법
```python
# 1. 폰트 다운로드만
helper.font_download()

# 2. 폰트 로딩만
helper.load_font()

# 3. pandas 확장만
helper.set_pandas_extension()
```

### 3. 폰트 문제 진단
```python
# 폰트 상태 확인
helper.check_font_status()

# 현재 폰트 설정 확인
import matplotlib.pyplot as plt
print(f"현재 폰트: {plt.rcParams['font.family']}")

# 설치된 한글 폰트 확인
import matplotlib.font_manager as fm
fonts = [f.name for f in fm.fontManager.ttflist]
korean_fonts = [f for f in fonts if 'Nanum' in f or 'Gothic' in f or 'Barun' in f]
print(f"한글 폰트: {korean_fonts}")
```

### 4. 환경별 경로 확인
```python
# 현재 환경 확인
if helper.is_colab:
    print("Colab 환경")
    print("파일 경로: /content/drive/MyDrive/")
else:
    print("로컬 환경")
    print("현재 디렉토리 사용")
```

## 📞 지원

문제가 지속되면 다음을 확인하세요:
- 런타임 유형 (GPU/TPU 사용 시 동작이 다를 수 있음)
- 네트워크 연결 상태
- Colab 버전 및 업데이트 상태

---
*작성자: 김명환 | 날짜: 2025.07.13 | 버전: v2.1*
