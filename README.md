# Jupyter 한글 환경 설정 모듈

> 🚀 **간단 사용법**: `helper.setup()` 한 번으로 모든 설정 완료!

Jupyter Notebook과 Google Colab에서 한글 폰트 설정 및 pandas 확장 기능을 제공하는 모듈입니다.

## 🎯 빠른 사용법

```python
import helper.c0z0c.dev as helper
helper.setup()  # 한번에 모든 설정 완료
```

**사용 가능한 기능:**
- 🎨 한글 폰트 지원 (matplotlib)
- 📊 pandas 확장 기능 (한글 컬럼 설명)
- 📁 파일 읽기: `helper.pd_read_csv("파일명.csv")`
- 🔍 유틸리티: `helper.dir_start(객체, "접두사")`
- 🆘 문제 해결: `helper.reset_colab_fonts()`, `helper.check_font_status()`

💡 **Colab 사용 시**: 세션 재시작 후 Google Drive 인증 오류 발생 시 `helper.reset_colab_fonts()` 실행

## 주요 기능

- 🎨 **한글 폰트 자동 설정**: NanumGothic 폰트를 자동으로 다운로드하고 matplotlib에 적용
- 📊 **pandas 확장 기능**: DataFrame/Series에 한글 컬럼 설명 기능 추가 (다양한 출력 형식 지원)
- 🔧 **편의 함수들**: 파일 읽기, 라이브러리 도움말 검색 등
- 🆘 **문제 해결 기능**: Colab 폰트 리셋, 상태 확인 등

## 빠른 시작

### 1. 모듈 다운로드 및 설치

```python
# Jupyter Notebook 또는 Google Colab에서 실행
!wget https://raw.githubusercontent.com/c0z0c/jupyter_hangul/master/helper.c0z0c.dev.py
```

### 2. 한번에 모든 설정 완료

```python
import helper.c0z0c.dev as helper
helper.setup()  # 폰트 다운로드 + 로딩 + pandas 확장 기능 모두 설정
```

### 3. 개별 설정 (선택사항)

```python
import helper.c0z0c.dev as helper

# 폰트 다운로드
helper.font_download()

# 폰트 로딩
helper.load_font()

# pandas 확장 기능 설정
helper.set_pandas_extension()
```

## 사용법

### 한글 폰트 설정

```python
import matplotlib.pyplot as plt
import helper.c0z0c.dev as helper

helper.setup()  # 한글 폰트 자동 설정

# 이제 matplotlib에서 한글 사용 가능
plt.plot([1, 2, 3, 4])
plt.title("한글 제목")
plt.xlabel("X축 레이블")
plt.ylabel("Y축 레이블")
plt.show()
```

### pandas 확장 기능

```python
import pandas as pd
import helper.c0z0c.dev as helper

helper.setup()

# DataFrame 생성
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
series.set_head_att('name', '사용자 이름')
series.head_att()
```

### 문제 해결 기능

```python
# Colab에서 폰트 관련 문제 발생 시
helper.reset_colab_fonts()    # 폰트 완전 리셋 (런타임 재시작됨)
helper.check_font_status()    # 현재 폰트 상태 확인
```

### 편의 함수들

```python
# 파일 읽기 (Colab/로컬 자동 인식)
df = helper.pd_read_csv('data.csv')

# 라이브러리 도움말 검색
helper.dir_start(pd.DataFrame, 'head')  # 'head'로 시작하는 메서드 검색
```

## API 문서

### 메인 함수

- `setup()`: 모든 설정을 한번에 완료
- `font_download()`: NanumGothic 폰트 다운로드
- `load_font()`: matplotlib에 한글 폰트 적용
- `set_pandas_extension()`: pandas 확장 기능 설정

### 문제 해결 함수

- `reset_colab_fonts()`: Colab 폰트 완전 리셋 (Google Drive 인증 오류 해결)
- `check_font_status()`: 현재 폰트 설정 상태 확인

### 편의 함수

- `pd_read_csv(path)`: Colab/로컬 환경에 맞는 파일 읽기
- `dir_start(object, cmd)`: 객체의 메서드/속성 검색

### pandas 확장 메서드

- `df.set_head_att(descriptions)`: 컬럼 설명 설정
- `df.get_head_att()`: 컬럼 설명 반환
- `df.remove_head_att(column)`: 특정 컬럼 설명 삭제
- `df.clear_head_att()`: 모든 컬럼 설명 초기화
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

## 설치 요구사항

모듈은 다음 라이브러리들을 사용합니다:
- matplotlib
- pandas
- numpy
- seaborn (선택사항)

## 환경별 특징

### Google Colab
- 폰트 설치 후 런타임 자동 재시작
- Google Drive 연동 지원 (인증 오류 자동 해결)
- 경로: `/content/drive/MyDrive/`
- 문제 발생 시 `helper.reset_colab_fonts()` 사용

### Jupyter Notebook
- 폰트 다운로드만 진행 (재시작 불필요)
- 로컬 파일 시스템 사용
- 폴더별 폰트 다운로드 가능

## 💡 Colab 사용 시 주의사항

- 세션 재시작 후 Google Drive 인증 오류 발생 시 `helper.reset_colab_fonts()` 실행
- 문제가 지속되면 런타임 재시작 후 `helper.setup()` 다시 실행
- 폰트 상태 확인은 `helper.check_font_status()` 사용

## 라이센스

MIT License

## 작성자

김명환 (2025.07.12)

## 업데이트 내역

### v2.1 (2025.07.13)
- 🆘 Google Drive 인증 오류 해결 기능 추가
- 🔧 폰트 리셋 기능 (`reset_colab_fonts()`) 추가
- 📊 폰트 상태 확인 기능 (`check_font_status()`) 추가
- 🎨 pandas `head_att()` 메서드 출력 형식 옵션 추가 (html, print, str)
- 📈 Series 객체 지원 강화
- 🔄 향상된 에러 처리 및 복구 로직

### v2.0 (2025.07.12)
- 초기 릴리스
- 한글 폰트 자동 설정
- pandas 확장 기능 추가
- Jupyter/Colab 환경 지원
