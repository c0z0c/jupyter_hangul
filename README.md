# Jupyter 한글 환경 설정 모듈

> 🚀 **간단 사용법**: `helper.setup()` 한 번으로 모든 설정 완료!

Jupyter Notebook과 Google Colab에서 한글 폰트 설정 및 pandas 확장 기능을 제공하는 모듈입니다.

https://youtu.be/8kfbuseTN-A

## 🎯 빠른 사용법

```python
from urllib.request import urlretrieve; urlretrieve("https://raw.githubusercontent.com/c0z0c/jupyter_hangul/refs/heads/beta/helper_c0z0c_dev.py", "helper_c0z0c_dev.py")
import helper_c0z0c_dev as helper # 한번에 모든 설정 완료
```

**🎉 출력 예시**:
```
🚀 Jupyter/Colab 한글 환경 설정 중... (helper v2.2.0)
✅ 한글 폰트 및 pandas 확장 기능 설정 완료
🎉 사용 가능: 한글 폰트, CSV 읽기, DataFrame.head_att(), 캐시 기능
```

**사용 가능한 기능:**
- 🎨 한글 폰트 지원 (matplotlib)
- 📊 pandas 확장 기능 (한글 컬럼 설명)
- 📁 파일 읽기: `helper.pd_read_csv("파일명.csv")`
- 🔍 유틸리티: `helper.dir_start(객체, "접두사")`
- 💾 캐시 기능: `helper.cache_*()` 함수들

## 주요 기능

- 🎨 **한글 폰트 자동 설정**: NanumGothic 폰트를 자동으로 다운로드하고 matplotlib에 적용
- 📊 **pandas 확장 기능**: DataFrame/Series에 한글 컬럼 설명 기능 추가 (다양한 출력 형식 지원)
- 🔧 **편의 함수들**: 파일 읽기, 라이브러리 도움말 검색 등
- 💾 **캐시 기능**: ML 모델 및 데이터 캐싱 시스템

## 빠른 시작

### 1. 모듈 다운로드 및 설치

```python
# Jupyter Notebook 또는 Google Colab에서 실행
!wget https://raw.githubusercontent.com/c0z0c/jupyter_hangul/master/helper_c0z0c_dev.py > /dev/null 2>&1
```

또는

```python
from urllib.request import urlretrieve; urlretrieve("https://raw.githubusercontent.com/c0z0c/jupyter_hangul/refs/heads/beta/helper_c0z0c_dev.py", "helper_c0z0c_dev.py")
```

### 2. 모듈 import 및 설정

```python
import helper_c0z0c_dev as helper # 한번에 모든 설정 완료!
# import helper_c0z0c_dev as helper setup() 자동 호출
# helper.setup()  # 한번에 모든 설정 완료!
```

## 사용 예제

### 한글 폰트 사용

```python
import matplotlib.pyplot as plt

# 한글 폰트가 자동으로 적용됨
plt.figure(figsize=(10, 6))
plt.plot([1, 2, 3, 4], [1, 4, 2, 3])
plt.title('한글 제목')
plt.xlabel('X축 라벨')
plt.ylabel('Y축 라벨')
plt.show()
```

### pandas 확장 기능

```python
import pandas as pd

# 샘플 데이터 생성
df = pd.DataFrame({
    'id': [1, 2, 3],
    'name': ['홍길동', '김철수', '이영희'],
    'age': [25, 30, 35]
})

# 컬럼 설명 설정
df.set_head_att({
    'id': 'ID',
    'name': '이름',
    'age': '나이'
})

# 한글 설명이 포함된 DataFrame 출력 (다양한 형식 지원)
df.head_att()              # 기본 print 형식
df.head_att(out='html')    # HTML 형식 (Jupyter/Colab에서 예쁘게 표시)
df.head_att(out='str')     # 문자열 형식

# Series도 지원
series = df['name']
series.head_att()
```

### 문제 해결

```python
# 문제 발생 시 helper.setup() 다시 실행하면 대부분 해결됨
helper.setup()
```

### 편의 함수들

```python
# 파일 읽기 (Colab/로컬 자동 인식, pandas.read_csv의 모든 옵션 지원)
df = helper.pd_read_csv('data.csv')
df = helper.pd_read_csv('data.csv', encoding='utf-8', sep=';')

# 다양한 입력 타입 지원
df = helper.pd_read_csv('data.csv')                    # 로컬 파일 경로 (자동 변환)
df = helper.pd_read_csv('https://example.com/data.csv') # URL (그대로 전달)
df = helper.pd_read_csv(file_object)                   # 파일 객체
from io import StringIO
df = helper.pd_read_csv(StringIO(csv_string))          # StringIO 객체

# 라이브러리 도움말 검색
helper.dir_start(pd.DataFrame, 'head')  # 'head'로 시작하는 메서드 검색
```

### 캐시 기능

```python
# 캐시 키 생성 (딕셔너리 형태의 파라미터 기반)
params = {'alpha': 0.1, 'beta': 0.2, 'model': 'RF'}
cache_key = helper.cache_key(params)

# 데이터 캐시 저장/로드
if helper.cache_exists(cache_key):
    model = helper.cache_load(cache_key)
    print("캐시에서 모델 로드")
else:
    # 새로운 모델 훈련
    model = train_model(params)
    helper.cache_save(cache_key, model)
    print("모델 훈련 완료 및 캐시 저장")

# 캐시 관리
helper.cache_list()    # 저장된 캐시 목록
helper.cache_clear()   # 캐시 전체 삭제
helper.cache_info()    # 캐시 저장 위치 정보
```

## 📚 API 참조

### 주요 함수

- `setup()`: 전체 설정 (한글 폰트 + pandas 확장)
- `font_download()`: 폰트 다운로드만
- `load_font()`: 폰트 로딩만
- `set_pandas_extension()`: pandas 확장 기능만

### 파일 읽기

- `pd_read_csv(filepath_or_buffer, **kwargs)`: pandas.read_csv 확장 버전

### 유틸리티

- `dir_start(obj, prefix)`: 객체의 속성 중 특정 접두사로 시작하는 것들 검색
- `is_colab`: Colab 환경 여부 확인

### 캐시 함수

- `cache_key(*args, **kwargs)`: 캐시 키 생성
- `cache_save(key, data)`: 데이터 캐시에 저장
- `cache_load(key)`: 캐시에서 데이터 로드
- `cache_exists(key)`: 캐시 키 존재 여부
- `cache_delete(key)`: 특정 캐시 삭제
- `cache_list()`: 캐시 키 목록
- `cache_clear()`: 캐시 전체 삭제
- `cache_info()`: 캐시 정보
- `cache_size()`: 캐시 디렉토리 총 크기
- `cache_get_path()`: 캐시 디렉토리 경로 반환

### pandas 확장 메서드

- `df.set_head_att(descriptions)`: 컬럼 설명 설정
- `df.get_head_att()`: 컬럼 설명 반환
- `df.remove_head_att(column)`: 특정 컬럼 설명 삭제
- `df.head_att(rows=5, out=None)`: 한글 설명이 포함된 DataFrame 출력
  - `out='print'`: 콘솔 출력 (기본값)
  - `out='html'`: HTML 형식 (Jupyter/Colab에서 예쁘게 표시)
  - `out='str'`: 문자열 반환

**Series도 동일한 메서드 지원**

## 환경 지원

- ✅ Jupyter Notebook
- ✅ Google Colab
- ✅ JupyterLab
- ✅ VS Code Jupyter Extension

## 캐시 저장 위치

### Google Colab
- 캐시 파일: `/content/drive/MyDrive/cache.json`
- Google Drive에 영구 저장 (세션 재시작 후에도 유지)
- 자동 파일 생성

### Jupyter Notebook (로컬)
- 캐시 파일: `./cache.json` (현재 작업 디렉토리)
- 로컬 파일 시스템에 저장
- 프로젝트별 독립적 캐시 관리

## 설치 요구사항

모듈은 다음 라이브러리들을 사용합니다:
- matplotlib
- pandas
- numpy
- seaborn (선택사항)

## 환경별 특징

### Google Colab
- 스마트 폰트 설치: 기존 폰트가 있으면 설치 생략
- Google Drive 연동 지원
- 경로: `/content/drive/MyDrive/`
- 캐시 저장: `/content/drive/MyDrive/cache.json` (영구 보존)
- 문제 발생 시 `helper.setup()` 다시 실행

### Jupyter Notebook (로컬)
- 로컬 환경에서 안정적으로 동작
- 현재 디렉토리 기준 파일 경로
- 캐시 저장: `./cache.json` (프로젝트별 관리)

## 문제 해결

### 일반적인 문제
대부분의 문제는 `helper.setup()`을 다시 실행하면 해결됩니다.

```python
helper.setup()  # 문제 해결
```

### 특정 문제별 해결방법

1. **한글 폰트가 깨져 보일 때**
   ```python
   helper.load_font()  # 폰트만 다시 로딩
   ```

2. **pandas 확장 기능이 작동하지 않을 때**
   ```python
   helper.set_pandas_extension()  # pandas 확장만 다시 설정
   ```

3. **Google Drive 연결 문제 (Colab)**
   ```python
   helper.setup()  # 전체 재설정
   ```

## 감사 인사

조하나 강사님의 기능 테스트에 도움을 주신 것에 감사드립니다.

## 업데이트 내역

### v2.2.0 (2025.07.22)
- 🚀 **안정적 한글 폰트 시스템**: 재부팅 없이 폰트 로딩
- 📝 **간소화된 출력**: 15줄 → 3줄로 메시지 간소화
- 💾 **캐시 기능 추가**: ML 모델 및 데이터 캐싱 시스템 구현
- 📁 **환경별 캐시 경로**: Colab(Google Drive), 로컬(현재 디렉토리) 자동 설정
- 🔑 **캐시 키 생성**: 딕셔너리 파라미터 기반 해시 키 자동 생성
- 🛠️ **캐시 관리**: 목록 조회, 삭제, 크기 확인 등 완전한 관리 기능
- ⚡ **성능 최적화**: 반복 실험에서 계산 시간 대폭 단축

### v2.1 (2025.07.13)
- 📊 pandas `head_att()` 메서드 출력 형식 옵션 추가 (html, print, str)
- 📈 Series 객체 지원 강화
- 🔄 향상된 에러 처리 및 복구 로직

### v2.0 (2025.07.12)
- 초기 릴리스
- 한글 폰트 자동 설정
- pandas 확장 기능 추가
- Jupyter/Colab 환경 지원
