# 🚀 Jupyter 한글 환경 설정 치트시트 v2.3.0

## 📥 설치

```python
from urllib.request import urlretrieve; urlretrieve("https://raw.githubusercontent.com/c0z0c/jupyter_hangul/refs/heads/beta/helper_c0z0c_dev.py", "helper_c0z0c_dev.py")
import helper_c0z0c_dev as helper # 한번에 모든 설정 완료
```

**🎉 출력 예시**:
```
🚀 Jupyter/Colab 한글 환경 설정 중... (helper v2.3.0)
✅ 한글 폰트 및 pandas 확장 기능 설정 완료
🎉 사용 가능: 한글 폰트, CSV 읽기, DataFrame.head_att(), 캐시 기능
```

## 🎯 주요 특징

- **즉시 사용**: 설정 후 바로 한글 폰트 사용 가능
- **간소화된 출력**: 깔끔한 메시지
- **스마트 설치**: 기존 폰트 있으면 재설치 안함
- **💾 캐시 기능**: 데이터/모델 저장으로 재실행 시간 단축

## 💾 캐시 기능 (신규)
```python
# 캐시 키 생성
key = helper.cache_key("experiment_1", param1="value1")

# 데이터 저장/로드
helper.cache_save(key, data)
loaded_data = helper.cache_load(key)

# 캐시 관리
helper.cache_exists(key)     # 존재 확인
helper.cache_delete(key)     # 삭제
helper.cache_clear()         # 전체 삭제
helper.cache_list_keys()     # 키 목록
helper.cache_size()          # 캐시 크기
```

### 한글 폰트 설정
```python
# 자동으로 완료됨 - 추가 작업 불필요!
plt.title("한글 제목")  # 바로 사용 가능
```

### 📊 pandas 확장 기능
```python
# 컬럼 설명 설정
df.set_head_att({"id": "아이디", "name": "이름", "age": "나이"})

# 한글 설명 포함 출력 (다양한 형식 지원)
df.head_att()              # 기본 print 형식
df.head_att(out='html')    # HTML 형식 (예쁘게 표시)
df.head_att(out='str')     # 문자열 반환

# 컬럼 세트 관리
df.set_head_ext('kr', {'name': '이름', 'age': '나이'})
df.set_head_column('kr')   # 한글 컬럼명으로 변경
df.set_head_column('org')  # 원본 컬럼명으로 복원

# 설명 조회 및 삭제
df.get_head_att()          # 전체 설명 조회
df.get_head_att('name')    # 개별 설명 조회
df.remove_head_att('name') # 설명 삭제
df.clear_head_att()        # 모든 설명 삭제
```

### 편의 함수
```python
# 파일 읽기 (Colab/로컬 자동 인식)
df = helper.pd_read_csv('data.csv')

# 라이브러리 도움말 검색
helper.dir_start(pd.DataFrame, 'head')
```

### 캐시 기능
```python
# 캐시 키 생성 및 데이터 저장/로드
params = {'alpha': 0.1, 'model': 'RF'}
key = helper.cache_key(params)
helper.cache_save(key, model)
model = helper.cache_load(key)

# 캐시 관리
helper.cache_exists(key)      # 존재 확인
helper.cache_list()           # 목록 조회
helper.cache_delete(key)      # 삭제
helper.cache_clear()          # 전체 삭제
helper.cache_info()           # 저장 위치 정보
```

## 🛠️ 개별 함수 사용법

```python
# 메인 함수들
helper.font_download()        # 폰트 다운로드만
helper.load_font()           # 폰트 로딩만
helper.set_pandas_extension() # pandas 확장만

# 캐시 함수들
helper.cache_key(params)     # 캐시 키 생성
helper.cache_save(key, data) # 데이터 저장
helper.cache_load(key)       # 데이터 로드
helper.cache_exists(key)     # 존재 확인
helper.cache_delete(key)     # 캐시 삭제
helper.cache_list()          # 캐시 목록
helper.cache_clear()         # 전체 삭제
helper.cache_info()          # 캐시 정보
helper.cache_size()          # 캐시 크기
helper.cache_get_path()      # 캐시 경로
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
df.remove_head_att("col1")  # 특정 컬럼 (리스트도 지원)
df.clear_head_att()         # 모든 컬럼
```

## 📊 출력 옵션

```python
# DataFrame 출력 옵션
df.head_att()              # 기본 5행, print 형식
df.head_att(10)            # 10행
df.head_att("all")         # 모든 행
df.head_att(0)             # 헤더만

# 출력 형식 옵션
df.head_att(out='print')   # 콘솔 출력 (기본값)
df.head_att(out='html')    # HTML 형식 (예쁘게 표시)
df.head_att(out='str')     # 문자열 반환

# Series도 동일하게 지원
series.head_att()
series.head_att(out='html')
```

## 💡 팁

- `setup()` 한 번만 실행하면 모든 설정 완료
- 한글 컬럼 설명은 HTML 형태로 예쁘게 출력 가능 (`out='html'`)
- Series 객체도 DataFrame과 동일한 기능 지원
- 기존 pandas 기능은 그대로 유지
- **캐시 기능으로 ML 실험 시간 단축**: 반복 실험에서 모델/데이터 재사용
- **Colab에서 캐시 영구 보존**: Google Drive에 자동 저장으로 세션 재시작 후에도 유지
- **문제 발생 시**: `helper.setup()` 다시 실행하면 대부분 해결

## 🆘 문제 해결

```python
# 문제 발생 시
helper.setup()                 # 다시 설정

# 캐시 관련 문제
helper.cache_info()            # 캐시 저장 위치 확인
helper.cache_clear()           # 캐시 전체 삭제
```

## 📍 캐시 저장 위치

- **Colab**: `/content/drive/MyDrive/cache.json` (Google Drive 영구 저장)
- **로컬**: `./cache.json` (현재 디렉토리)
