# Jupyter 한글 환경 설정 모듈

Jupyter Notebook과 Google Colab에서 한글 폰트 설정 및 pandas 확장 기능을 제공하는 모듈입니다.

## 주요 기능

- 🎨 **한글 폰트 자동 설정**: NanumGothic 폰트를 자동으로 다운로드하고 matplotlib에 적용
- 📊 **pandas 확장 기능**: DataFrame/Series에 한글 컬럼 설명 기능 추가
- 🔧 **편의 함수들**: 파일 읽기, 라이브러리 도움말 검색 등

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

# 한글 설명이 포함된 DataFrame 출력
df.head_att()
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

### 편의 함수

- `pd_read_csv(path)`: Colab/로컬 환경에 맞는 파일 읽기
- `dir_start(object, cmd)`: 객체의 메서드/속성 검색

### pandas 확장 메서드

- `df.set_head_att(descriptions)`: 컬럼 설명 설정
- `df.get_head_att()`: 컬럼 설명 반환
- `df.remove_head_att(column)`: 특정 컬럼 설명 삭제
- `df.clear_head_att()`: 모든 컬럼 설명 초기화
- `df.head_att(rows=5)`: 한글 설명이 포함된 DataFrame 출력

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
- Google Drive 연동 지원
- 경로: `/content/drive/MyDrive/codeit/online/`

### Jupyter Notebook
- 폰트 다운로드만 진행 (재시작 불필요)
- 로컬 파일 시스템 사용
- 폴더별 폰트 다운로드 가능

## 라이센스

MIT License

## 작성자

김명환 (2025.07.12)

## 업데이트 내역

### v1.0.0 (2025.07.12)
- 초기 릴리스
- 한글 폰트 자동 설정
- pandas 확장 기능 추가
- Jupyter/Colab 환경 지원
