# 🚀 Colab 한글 폰트 설정 가이드

## 📋 간단한 사용법 (v2.2.0)

### ✨ 새로운 방식 (권장)
```python
import urllib.request
# 모듈 다운로드
url = "https://raw.githubusercontent.com/c0z0c/jupyter_hangul/master/helper_c0z0c_dev.py"
urllib.request.urlretrieve(url, "helper_c0z0c_dev.py")
# 모듈 import 및 설정
import helper_c0z0c_dev as helper
helper.setup();  # 재부팅 없이 바로 완료!
```

**🎉 간소화된 출력**:
```
🚀 Jupyter/Colab 한글 환경 설정 중... (helper v2.2.0)
✅ 한글 폰트가 이미 설정되어 있습니다.
🎉 설정 완료! 한글폰트 및 pandas 확장 기능 사용 가능
```

### 🔧 이전 방식 (호환성)
문제 발생 시에만 사용하세요.

## 🆕 v2.2.0의 주요 개선사항

### ⚡ 무재부팅 시스템
- **기존**: 폰트 설치 후 런타임 재시작 필요
- **v2.2.0**: 재부팅 없이 즉시 한글 폰트 사용 가능 ✨

### 🎯 스마트 설치
- 한글 폰트가 이미 있으면 재설치하지 않음
- 필요한 경우에만 시스템 재시작 (폰트 로딩 실패 시)

### 📝 깔끔한 출력
- 기존 15줄 → 3-4줄로 간소화
- 불필요한 True 출력 제거 (`;` 사용)

## 🔄 폰트 설치 과정 (참고용)

### 📌 v2.2.0의 스마트 설치 과정
- **1단계**: 기존 한글 폰트 확인 (있으면 스킵)
- **2단계**: 필요시에만 폰트 다운로드/설치
- **3단계**: matplotlib 캐시 갱신 (재부팅 없이)
- **4단계**: 즉시 사용 가능! 🎉

### 📌 이전 방식 (참고용)
- Colab에서 폰트 설치 후 Python 프로세스가 폰트를 인식하려면 재시작이 필요했습니다
- 캐시 삭제만으로는 이미 로드된 폰트 정보를 갱신할 수 없었습니다

### 🎯 v2.2.0 실행 과정
1. **스마트 체크**: 한글 폰트 존재 여부 확인
2. **조건부 설치**: 필요시에만 폰트 다운로드/설치  
3. **즉시 적용**: matplotlib 설정 갱신 (재부팅 없이)
4. **완료**: 바로 한글 폰트 사용 가능! ✨

### 🎯 이전 방식 (참고용)
1. **폰트 설치**: `fonts-nanum` 패키지 설치
2. **캐시 갱신**: `fc-cache -fv` 실행  
3. **안내 메시지**: 재시작 후 실행할 코드 안내
4. **자동 재시작**: `os.kill(os.getpid(), 9)` 실행
5. **수동 실행**: 재시작 후 사용자가 코드 실행

### 📋 v2.2.0에서 제공되는 기능들
- ✅ 한글 폰트 설정 (matplotlib) - **재부팅 불필요**
- ✅ pandas 확장 기능
- ✅ 유틸리티 함수들
- ✅ Google Drive 연결 (Colab)
- ✅ 캐시 기능 (v2.2.0 신규)

## 🛠️ 추가 함수들

### 캐시 기능 (v2.2.0)
```python
# 머신러닝 실험에서 캐시 활용
params = {'alpha': 0.1, 'n_estimators': 100, 'random_state': 42}
cache_key = helper.cache_key(params)

# 캐시에서 모델 로드 또는 새로 훈련
if helper.cache_exists(cache_key):
    print("캐시에서 모델 로드")
    model = helper.cache_load(cache_key)
else:
    print("새로운 모델 훈련 및 캐시 저장")
    model = RandomForestClassifier(**params)
    model.fit(X_train, y_train)
    helper.cache_save(cache_key, model)

# 캐시 관리
helper.cache_list()           # 저장된 캐시 목록
helper.cache_info()           # 캐시 저장 위치 정보
helper.cache_size()           # 캐시 디렉토리 크기

# Colab에서는 Google Drive에 영구 저장
# 경로: /content/drive/MyDrive/cache.json
```

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
# 기본 사용법 (Colab/로컬 자동 감지)
df = helper.pd_read_csv('data.csv')

# pandas.read_csv의 모든 옵션 지원
df = helper.pd_read_csv('data.csv', encoding='utf-8', sep=',')
df = helper.pd_read_csv('한글파일.csv', encoding='cp949')

# 다양한 입력 타입 지원
# 1) 로컬 파일 경로 (Colab에서 자동 경로 변환)
df = helper.pd_read_csv('data/sample.csv')

# 2) URL (그대로 전달, 경로 변환 안됨)
df = helper.pd_read_csv('https://example.com/data.csv')
df = helper.pd_read_csv('http://example.com/data.csv')

# 3) 파일 객체 (그대로 전달)
with open('data.csv', 'r') as f:
    df = helper.pd_read_csv(f)

# 4) StringIO 객체 (그대로 전달)
from io import StringIO
csv_string = "이름,나이\n김철수,25\n이영희,30"
df = helper.pd_read_csv(StringIO(csv_string))
```

### 캐시 기능 (v2.2.0 신규)
```python
# 머신러닝 실험에서 캐시 활용
params = {'alpha': 0.1, 'n_estimators': 100, 'random_state': 42}
cache_key = helper.cache_key(params)

# 캐시에서 모델 로드 또는 새로 훈련
if helper.cache_exists(cache_key):
    print("캐시에서 모델 로드")
    model = helper.cache_load(cache_key)
else:
    print("새로운 모델 훈련 및 캐시 저장")
    model = RandomForestClassifier(**params)
    model.fit(X_train, y_train)
    helper.cache_save(cache_key, model)

# 캐시 관리
helper.cache_list()           # 저장된 캐시 목록
helper.cache_info()           # 캐시 저장 위치 정보
helper.cache_size()           # 캐시 디렉토리 크기

# Colab에서는 Google Drive에 영구 저장
# 경로: /content/drive/MyDrive/cache.json
```

## ❓ 자주 묻는 질문

### Q: 한글이 여전히 깨져요
A: `helper.setup()`을 다시 실행해보세요. v2.2.0에서는 재부팅 없이 해결됩니다.

### Q: Google Drive 인증 오류가 발생해요
A: `helper.setup()`을 다시 실행하면 자동으로 해결됩니다.

### Q: 에러가 계속 발생해요
A: `helper.setup()`을 다시 실행하고, 문제가 지속되면 런타임을 재시작해보세요.

### Q: DataFrame의 한글 컬럼 설명이 안 보여요
A: `df.head_att(out='html')`을 사용하면 Colab에서 예쁘게 표시됩니다.

### Q: 캐시 기능을 사용하고 싶어요
A: `helper.cache_key()`, `helper.cache_save()`, `helper.cache_load()` 함수를 사용하세요. Colab에서는 Google Drive에 자동 저장됩니다.

### Q: 캐시 저장 위치가 궁금해요
A: Colab에서는 `/content/drive/MyDrive/cache.json`에 저장되며, `helper.cache_info()`로 확인 가능합니다.

## 🔧 문제 해결

### 1. Google Drive 인증 오류 해결
```python
# v2.2.0에서는 재부팅 없이 해결
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

### 3. 환경별 경로 확인 및 파일 읽기
```python
# 현재 환경 확인
if helper.is_colab:
    print("Colab 환경")
    print("파일 경로: /content/drive/MyDrive/")
else:
    print("로컬 환경")
    print("현재 디렉토리 사용")

# 파일 읽기 테스트
# 로컬 파일 경로만 자동 변환됨
df1 = helper.pd_read_csv('test.csv')  # 자동 경로 변환

# URL은 경로 변환 안됨 (그대로 전달)
# URL은 경로 변환 안됨 (그대로 전달)
df2 = helper.pd_read_csv('https://raw.githubusercontent.com/user/repo/data.csv')

# 캐시 기능 테스트
params = {'test': True, 'version': '1.0'}
cache_key = helper.cache_key(params)
helper.cache_save(cache_key, df1)
cached_df = helper.cache_load(cache_key)
print(f"캐시된 데이터 형태: {cached_df.shape}")
```

# 직접 경로 지정 (경로 변환 안됨)
df3 = helper.pd_read_csv('/content/drive/MyDrive/data.csv')

# 파일 객체 (그대로 전달)
with open('/content/data.csv', 'r') as f:
    df4 = helper.pd_read_csv(f, encoding='utf-8')
```

## 📞 지원

문제가 지속되면 다음을 확인하세요:
- v2.2.0 사용 여부 (`helper.__version__` 확인)
- `helper.setup()` 재실행
- 네트워크 연결 상태
- Colab 버전 및 업데이트 상태

---
*작성자: 김명환 | 날짜: 2025.07.25 | 버전: v2.2.0*
