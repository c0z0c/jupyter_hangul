# 🚀 Jupyter 한글 환경 설정 치트시트

## 📥 설치 (한 줄로 끝!)

```python
!wget https://raw.githubusercontent.com/c0z0c/jupyter_hangul/master/helper.c0z0c.dev.py
import helper.c0z0c.dev as helper
helper.setup()  # 모든 설정 완료!
```

## 🎯 주요 기능

### 한글 폰트 설정
```python
# 자동으로 완료됨 - 추가 작업 불필요!
plt.title("한글 제목")  # 바로 사용 가능
```

### pandas 확장 기능
```python
# 컬럼 설명 설정
df.set_head_att({"id": "아이디", "name": "이름"})

# 한글 설명 포함 출력
df.head_att()  # 또는 df.head_att(10)
```

### 편의 함수
```python
# 파일 읽기 (Colab/로컬 자동 인식)
df = helper.pd_read_csv('data.csv')

# 라이브러리 도움말 검색
helper.dir_start(pd.DataFrame, 'head')
```

## 🛠️ 개별 함수 사용법

```python
# 필요한 기능만 선택적으로 실행
helper.font_download()        # 폰트 다운로드만
helper.load_font()           # 폰트 로딩만
helper.set_pandas_extension() # pandas 확장만
```

## 🎨 컬럼 설명 관리

```python
# 여러 컬럼 한번에 설정
df.set_head_att({"col1": "설명1", "col2": "설명2"})

# 단일 컬럼 설정
df.set_head_att("col1", "새로운 설명")

# 설명 조회
df.get_head_att()

# 설명 삭제
df.remove_head_att("col1")  # 특정 컬럼
df.clear_head_att()         # 모든 컬럼
```

## 📊 출력 옵션

```python
df.head_att()      # 기본 5행
df.head_att(10)    # 10행
df.head_att("all") # 모든 행
df.head_att(0)     # 헤더만
```

## 💡 팁

- `setup()` 한 번만 실행하면 모든 설정 완료
- Colab에서는 런타임 재시작 후 다시 실행 필요
- 한글 컬럼 설명은 HTML 형태로 예쁘게 출력됨
- 기존 pandas 기능은 그대로 유지
