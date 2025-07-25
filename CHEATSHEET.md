# 🚀 Jupyter 한글 환경 설정 치트시트

## 📥 설치 (한 줄로 끝!)

```python
!wget https://raw.githubusercontent.com/c0z0c/jupyter_hangul/master/helper_c0z0c_dev.py
import helper_c0z0c_dev as helper
helper.setup();  # 모든 설정 완료! (;로 반환값 숨김)
```

**🎉 v2.2.0 간소화된 출력**:
```
🚀 Jupyter/Colab 한글 환경 설정 중... (helper v2.2.0)
✅ 한글 폰트가 이미 설정되어 있습니다.
🎉 설정 완료! 한글폰트 및 pandas 확장 기능 사용 가능
```

## 🎯 주요 특징

### ⚡ v2.2.0 개선사항
- **재부팅 불필요**: 안정적인 한글 폰트 로딩
- **간소화된 출력**: 3-4줄 깔끔한 메시지
- **True 출력 억제**: 세미콜론(;) 사용으로 더 깔끔

### 한글 폰트 설정
```python
# 자동으로 완료됨 - 추가 작업 불필요!
plt.title("한글 제목")  # 바로 사용 가능
```

### pandas 확장 기능
```python
# 컬럼 설명 설정
df.set_head_att({"id": "아이디", "name": "이름"})

# 한글 설명 포함 출력 (다양한 형식 지원)
df.head_att()              # 기본 print 형식
df.head_att(out='html')    # HTML 형식 (예쁘게 표시)
df.head_att(out='str')     # 문자열 반환
```

### 편의 함수
```python
# 파일 읽기 (Colab/로컬 자동 인식)
df = helper.pd_read_csv('data.csv')

# 라이브러리 도움말 검색
helper.dir_start(pd.DataFrame, 'head')
```

### 캐시 기능 (v2.2.0)
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

# 캐시 함수들 (v2.2.0)
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
- v2.2.0에서는 재부팅 없이 안정적으로 작동
- 한글 컬럼 설명은 HTML 형태로 예쁘게 출력 가능 (`out='html'`)
- Series 객체도 DataFrame과 동일한 기능 지원
- 기존 pandas 기능은 그대로 유지
- **캐시 기능으로 ML 실험 시간 단축**: 반복 실험에서 모델/데이터 재사용
- **Colab에서 캐시 영구 보존**: Google Drive에 자동 저장으로 세션 재시작 후에도 유지
- **문제 발생 시**: `helper.setup()` 다시 실행하면 대부분 해결

## 🆘 문제 해결

```python
# Colab에서 문제 발생 시
helper.setup()                 # 다시 설정 (재부팅 불필요)

# 캐시 관련 문제
helper.cache_info()            # 캐시 저장 위치 확인
helper.cache_clear()           # 캐시 전체 삭제
```

## 📍 캐시 저장 위치

- **Colab**: `/content/drive/MyDrive/cache.json` (Google Drive 영구 저장)
- **로컬**: `./cache.json` (현재 디렉토리)
