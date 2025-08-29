"""
Jupyter/Colab 한글 폰트 및 pandas 확장 모듈

 기본 사용법:
    import helper.c0z0c.dev as helper
    helper.setup()  # 한번에 모든 설정 완료

개별 실행:
    helper.font_download()      # 폰트 다운로드
    helper.load_font()          # 폰트 로딩
    helper.set_pandas_extension()  # pandas 확장 기능

파일 읽기:
    df = helper.pd_read_csv("파일명.csv")          # 문자열 경로 (자동 변환)
    df = helper.pd_read_csv(file_obj, encoding='utf-8')  # 파일 객체/URL 등

유틸리티:
    helper.dir_start(객체, "접두사")  # 메서드 검색
    df.head_att()  # 한글 컬럼 설명 출력

� 캐시 기능:
    key = helper.cache_key("model", params, random_state=42)  # 키 생성
    helper.cache_save(key, model)                           # 모델 저장
    model = helper.cache_load(key)                          # 모델 로드
    helper.cache_exists(key)                                # 키 존재 확인
    helper.cache_info()                                     # 캐시 정보
    helper.cache_clear()                                    # 캐시 초기화

🆕 v2.2.0 개선사항:
    - 재부팅 없는 안정적 한글 폰트 로딩
    - 간소화된 출력 메시지 (3-4줄)
    - 문제 발생 시 helper.setup() 다시 실행하면 해결

작성자: 김명환
날짜: 2025.07.22
버전: 2.2.0
"""

import os
import matplotlib.pyplot as plt
import pandas as pd
import json
import hashlib
import sys
import time
import shutil
import gzip
import urllib.request
import warnings
import subprocess
import numpy as np
import datetime
import pickle

# 전역 변수
__version__ = "2.3.0"
font_path = ""
is_colab = False

# pandas commit 시스템 전역 변수
_COMMIT_META_FILE = "pandas_df.json"
pd_root_base = None

# 공통 유틸리티 함수
def _in_colab():
    """Colab 환경 감지"""
    try:
        import google.colab
        return True
    except ImportError:
        return False

def _get_text_width(text):
    """텍스트 폭 계산 (한글 2칸, 영문 1칸)"""
    if text is None:
        return 0
    return sum(2 if ord(char) >= 0x1100 else 1 for char in str(text))

def _format_value(value):
    """값을 포맷팅합니다. 실수형은 소수점 이하 4자리로 반올림"""
    try:
        # 배열이나 시리즈인 경우 문자열로 변환
        if hasattr(value, '__iter__') and not isinstance(value, (str, bytes)):
            return str(value)
        
        # pandas NA 체크 (스칼라 값에만 적용)
        if pd.isna(value):
            return str(value)
        elif isinstance(value, (int, np.integer)):
            return str(value)
        elif isinstance(value, (float, np.floating)):
            return f"{value:.4f}".rstrip('0').rstrip('.')
        else:
            return str(value)
    except (ValueError, TypeError):
        # 예외 발생 시 안전하게 문자열로 변환
        return str(value)

def font_download():
    """폰트를 다운로드하거나 설치합니다."""
    global font_path
    
    # matplotlib 경고 억제
    warnings.filterwarnings(action='ignore')
    
    if _in_colab():
        # 이미 설치되어 있는지 확인
        if os.system("dpkg -l | grep fonts-nanum") == 0:
            return True
            
        try:
            # 나눔 폰트 패키지 설치 및 캐시 업데이트 (출력 최소화)
            print("install fonts-nanum")
            subprocess.run(['sudo', 'apt-get', 'install', '-y', 'fonts-nanum', "-qq"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(['sudo', 'fc-cache', '-fv'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(['rm', '-rf', os.path.expanduser('~/.cache/matplotlib')], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)            
            return True
            
        except Exception as e:
            print(f"❌ 폰트 설치 실패: {e}")
            return False
    else:
        font_url = "https://github.com/c0z0c/jupyter_hangul/raw/master/NanumGothic.ttf"
        font_dir = "fonts"
        os.makedirs(font_dir, exist_ok=True)
        font_path = os.path.join(font_dir, "NanumGothic.ttf")
        
        if not os.path.exists(font_path):
            urllib.request.urlretrieve(font_url, font_path)
        
        return True

def _colab_font_reinstall():
    """Colab에서 폰트 재설치"""
    # matplotlib 경고 억제
    warnings.filterwarnings(action='ignore')
    
    print("🔄 폰트 문제 발생 - helper.setup() 다시 실행 권장")
    
    try:
        # 캐시 정리 및 패키지 재설치 (출력 없이)
        subprocess.run(['sudo', 'apt-get', 'remove', '--purge', '-y', 'fonts-nanum'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(['sudo', 'apt-get', 'install', '-y', 'fonts-nanum', "-qq"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(['sudo', 'fc-cache', '-fv'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(['rm', '-rf', os.path.expanduser('~/.cache/matplotlib')], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)            
        time.sleep(1)
        os.kill(os.getpid(), 9)
    except Exception:
        pass

def reset_matplotlib():
    """matplotlib 완전 리셋"""
    # matplotlib 모듈들을 sys.modules에서 제거
    modules_to_remove = [mod for mod in sys.modules if mod.startswith('matplotlib')]
    for mod in modules_to_remove:
        del sys.modules[mod]
    
    # 다시 import
    import matplotlib.pyplot as plt
    import matplotlib.font_manager as fm
    
    # 폰트 캐시 클리어 (중요!)
    try:
        fm._get_fontconfig_fonts.cache_clear()
    except:
        pass
    
    try:
        fm.fontManager.__init__()
    except:
        pass
    
    # 환경별 폰트 설정
    if _in_colab():
        # Colab 환경: 시스템에 설치된 나눔 폰트 사용
        plt.rcParams['font.family'] = 'NanumBarunGothic'
    else:
        # 로컬 환경: 다운로드한 폰트 파일 사용
        global font_path
        if font_path and os.path.exists(font_path):
            # 폰트 파일을 시스템에 등록
            fm.fontManager.addfont(font_path)
            plt.rcParams['font.family'] = 'NanumGothic'
        else:
            # 폰트 파일이 없으면 시스템 한글 폰트 시도
            available_fonts = [f.name for f in fm.fontManager.ttflist]
            korean_fonts = ['Malgun Gothic', 'AppleGothic', 'NanumGothic', 'Noto Sans CJK KR']
            
            for font in korean_fonts:
                if font in available_fonts:
                    plt.rcParams['font.family'] = font
                    break
            else:
                plt.rcParams['font.family'] = 'DejaVu Sans'
                print("⚠️ 한글 폰트를 찾을 수 없습니다. font_download()를 먼저 실행하세요.")
    
    plt.rcParams['axes.unicode_minus'] = False
    plt.rcParams['font.size'] = 10  # 기본 폰트 사이즈 10으로 설정    
    
    print("✅ matplotlib 한글 폰트 설정 완료")
    return plt

def load_font():
    """폰트를 로딩하고 설정합니다."""
    global font_path, is_colab

    try:
        # matplotlib 경고 억제
        warnings.filterwarnings(action='ignore')
        
        if _in_colab():
            is_colab = True
            
            # Google Drive 마운트 시도 (출력 없이)
            try:
                from google.colab import drive
                drive.mount("/content/drive", force_remount=True)
            except Exception:
                pass
            
            
            # 한글 폰트가 이미 설정되어 있는지 확인
            current_font = plt.rcParams.get('font.family', ['default'])
            if isinstance(current_font, list):
                current_font = current_font[0] if current_font else 'default'
            
            if 'nanum' in current_font.lower() or 'gothic' in current_font.lower():
                return True
            
            # 폰트 설정 시도 (출력 최소화)
            try:
                reset_matplotlib()
                return True
                    
            except Exception as font_error:
                _colab_font_reinstall()
                return False
            
        else:
            is_colab = False
            current_font = plt.rcParams.get("font.family", "default")
            if isinstance(current_font, list):
                current_font = current_font[0] if current_font else "default"
                
            if current_font == "NanumGothic":
                return True

            try:
                if font_path and os.path.exists(font_path):
                    reset_matplotlib()
                    return True
                else:
                    return False
            except Exception as e:
                return False
                
    except Exception as e:
        print(f"❌ 예상치 못한 오류: {str(e)}")
        
        if _in_colab():
            _colab_font_reinstall()
        else:
            print("💡 helper.font_download()를 다시 실행해보세요.")
        
        return False

# pandas 옵션 설정
pd.set_option("display.max_rows", 30)
pd.set_option("display.max_columns", 100)

def pd_read_csv(filepath_or_buffer, **kwargs):
    """
    Colab/로컬 환경에 맞춰 CSV 파일을 읽어옵니다.
    
    Parameters:
    -----------
    filepath_or_buffer : str, path object, file-like object
        읽어올 파일 경로, URL, 파일 객체 등 (pd.read_csv와 동일)
        - str 타입이고 로컬 파일 경로일 경우: Colab 환경에서 자동으로 경로 변환
        - URL (http://, https://, ftp://, file://): 그대로 pd.read_csv에 전달
        - 다른 타입일 경우: 그대로 pd.read_csv에 전달
    **kwargs : dict
        pd.read_csv의 추가 매개변수들
    
    Returns:
    --------
    pandas.DataFrame : 읽어온 데이터프레임
    
    Examples:
    ---------
    >>> # 로컬 파일 (환경별 자동 변환)
    >>> df = helper.pd_read_csv('data.csv')
    >>> 
    >>> # URL (그대로 전달)
    >>> df = helper.pd_read_csv('https://example.com/data.csv')
    >>> 
    >>> # 파일 객체 (그대로 전달)
    >>> with open('data.csv') as f:
    >>>     df = helper.pd_read_csv(f)
    """
    # 문자열 경로일 경우에만 경로 변환 처리 (URL 제외)
    if isinstance(filepath_or_buffer, str) and not filepath_or_buffer.startswith(('http://', 'https://', 'ftp://', 'file://')):
        # pd_root_base/pd_root 정책 적용
        full_path = os.path.join(pd_root(), filepath_or_buffer) if not os.path.isabs(filepath_or_buffer) else filepath_or_buffer
        try:
            if not os.path.exists(full_path):
                print(f"❌ 파일을 찾을 수 없습니다: {full_path}")
                return None
            df = pd.read_csv(full_path, **kwargs)
            print(f"✅ 파일 읽기 성공: {df.shape[0]}행 × {df.shape[1]}열")
            return df
        except Exception as e:
            print(f"❌ 파일 읽기 실패: {str(e)}")
            return None
    else:
        # 문자열이 아니거나 URL인 경우 (파일 객체, URL 등) 그대로 전달
        try:
            df = pd.read_csv(filepath_or_buffer, **kwargs)
            print(f"✅ 데이터 읽기 성공: {df.shape[0]}행 × {df.shape[1]}열")
            return df
        except Exception as e:
            print(f"❌ 데이터 읽기 실패: {str(e)}")
            return None

def dir_start(obj, cmd):
    """라이브러리 도움말을 검색합니다."""
    for c in [att for att in dir(obj) if att.startswith(cmd)]:
        print(f"{c}")

def set_pd_root_base(subdir=None):
    """
    pd_root의 기본 경로를 설정합니다. 프로그램 실행 중 지속적으로 영향을 줍니다.
    - subdir이 None이면: Colab은 /content/drive/MyDrive, Jupyter는 현재 폴더
    - subdir이 문자열이면: Colab은 /content/drive/MyDrive/subdir, Jupyter는 ./subdir
    - subdir이 '/'로 시작하면: Colab은 /content/drive/MyDrive/ + subdir, Jupyter는 . + subdir
    """
    global pd_root_base
    if _in_colab():
        base = "/content/drive/MyDrive"
        if subdir is None or subdir == "":
            pd_root_base = base
        elif subdir.startswith("/"):
            pd_root_base = base + subdir
        else:
            pd_root_base = os.path.join(base, subdir)
    else:
        base = "."
        if subdir is None or subdir == "":
            pd_root_base = base
        elif subdir.startswith("/"):
            pd_root_base = base + subdir
        else:
            pd_root_base = os.path.join(base, subdir)

def pd_root(commit_dir=None):
    """
    pandas commit 시스템의 기본 경로를 반환합니다.
    commit_dir이 지정되면 해당 경로를, 없으면 pd_root_base를 반환합니다.
    """
    if commit_dir is not None:
        return commit_dir
    if pd_root_base is not None:
        return pd_root_base
    # 기본값 설정
    if _in_colab():
        return "/content/drive/MyDrive"
    else:
        return "."

def _load_commit_meta(commit_dir=None):
    """커밋 메타데이터를 로드합니다."""
    meta_file = os.path.join(os.path.join(pd_root(commit_dir), ".commit_pandas"), _COMMIT_META_FILE)
    if os.path.exists(meta_file):
        try:
            with open(meta_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    return []

def _save_commit_meta(meta, commit_dir=None):
    """커밋 메타데이터를 저장합니다."""
    meta_file = os.path.join(os.path.join(pd_root(commit_dir), ".commit_pandas"), _COMMIT_META_FILE)
    os.makedirs(os.path.dirname(meta_file), exist_ok=True)
    with open(meta_file, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

def _generate_commit_hash(dt, msg):
    """커밋 해시를 생성합니다."""
    base = f"{dt.strftime('%Y%m%d_%H%M%S')}_{msg}"
    return hashlib.md5(base.encode("utf-8")).hexdigest()[:12]

def set_pandas_extension():
    """pandas DataFrame/Series에 한글 컬럼 설명 기능을 추가합니다."""
    # 기본 기능
    for cls in [pd.DataFrame, pd.Series]:
        setattr(cls, "set_head_att", set_head_att)
        setattr(cls, "get_head_att", get_head_att)
        setattr(cls, "remove_head_att", remove_head_att)
        setattr(cls, "clear_head_att", clear_head_att)
        setattr(cls, "clear_head_ext", clear_head_ext)
    
    # DataFrame/Series별 출력 함수
    setattr(pd.DataFrame, "head_att", pd_head_att)
    setattr(pd.DataFrame, "_print_head_att", _print_head_att)
    setattr(pd.DataFrame, "_html_head_att", _html_head_att)
    setattr(pd.DataFrame, "_string_head_att", _string_head_att)
    setattr(pd.DataFrame, "_init_column_attrs", _init_column_attrs)
    setattr(pd.DataFrame, "_convert_columns", _convert_columns)
    setattr(pd.DataFrame, "_update_column_descriptions", _update_column_descriptions)
    setattr(pd.DataFrame, "_set_head_ext_bulk", _set_head_ext_bulk)
    setattr(pd.DataFrame, "_set_head_ext_individual", _set_head_ext_individual)
    setattr(pd.Series, "head_att", series_head_att)
    
    # 컬럼 세트 관리 기능
    for cls in [pd.DataFrame, pd.Series]:
        setattr(cls, "set_head_ext", set_head_ext)
        setattr(cls, "set_head_column", set_head_column)
        setattr(cls, "get_current_column_set", get_current_column_set)
        setattr(cls, "get_head_ext", get_head_ext)
        setattr(cls, "list_head_ext", list_head_ext)
        setattr(cls, "clear_head_ext", clear_head_ext)
        setattr(cls, "remove_head_ext", remove_head_ext)
    
    # Series에도 새 함수들 추가
    setattr(pd.Series, "_set_head_ext_bulk", _set_head_ext_bulk)
    setattr(pd.Series, "_set_head_ext_individual", _set_head_ext_individual)
    setattr(pd.Series, "_init_column_attrs", _init_column_attrs)
    setattr(pd.Series, "_convert_columns", _convert_columns)
    setattr(pd.Series, "_update_column_descriptions", _update_column_descriptions)

    # pandas commit 시스템 API 바인딩
    setattr(pd.DataFrame, "commit", _df_commit)
    setattr(pd.DataFrame, "checkout", classmethod(_df_checkout))
    setattr(pd.DataFrame, "commit_list", classmethod(_df_commit_list))
    setattr(pd.DataFrame, "commit_rm", classmethod(_df_commit_rm))
    setattr(pd.DataFrame, "commit_has", classmethod(_df_commit_has))

def setup():
    """한번에 모든 설정 완료"""
    
    # matplotlib 경고 억제
    warnings.filterwarnings(action='ignore')
    
    print("🚀 Jupyter/Colab 한글 환경 설정 중... (helper v" + __version__ + ")")
    
    try:
        
        if not _in_colab():
            import os
            os.system('chcp 65001')
            os.environ['PYTHONIOENCODING'] = 'utf-8'

        # 폰트 다운로드/설치 및 로딩 (출력 최소화)
        font_download_success = font_download()
        if font_download_success:
            font_load_success = load_font()
            if font_load_success:
                # pandas 확장 기능 설정
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    set_pandas_extension()
                
                print("✅ 한글 폰트 및 pandas 확장 기능 설정 완료")
                print("🎉 사용 가능: 한글 폰트, CSV 읽기, DataFrame.head_att(), 캐시 기능")
                return
        
        print("❌ 설정 실패")
        return
        
    except Exception as e:
        print(f"❌ 설정 오류: {str(e)}")
        return

# pandas commit 시스템 DataFrame 메소드 wrappers
import pandas as pd  # ensure pandas is imported

def _df_commit(self, msg, commit_dir=None):
    """
    DataFrame의 현재 상태를 커밋합니다.
    사용법:
        df.commit("커밋 메시지")
    """
    return pd_commit(self, msg, commit_dir)



@classmethod
def _df_checkout(cls, idx_or_hash, commit_dir=None):
    """
    DataFrame 커밋 기록에서 특정 커밋을 체크아웃합니다.
    사용법:
        pd.DataFrame.checkout(0)
    """
    return pd_checkout(idx_or_hash, commit_dir)

@classmethod
def _df_commit_list(cls, commit_dir=None):
    """
    DataFrame의 커밋 목록을 반환합니다.
    사용법:
        pd.DataFrame.commit_list()
    """
    return pd_commit_list(commit_dir)

@classmethod
def _df_commit_rm(cls, idx_or_hash, commit_dir=None):
    """
    DataFrame 커밋 기록에서 특정 커밋을 삭제합니다.
    사용법:
        pd.DataFrame.commit_rm(0)
    """
    return pd_commit_rm(idx_or_hash, commit_dir)

@classmethod
def _df_commit_has(cls, idx_or_hash, commit_dir=None):
    """
    DataFrame 커밋이 존재하는지 확인합니다.
    사용법:
        pd.DataFrame.commit_has("메시지")
    """
    return pd_commit_has(idx_or_hash, commit_dir)

# 캐시 관련 helper API 함수들
def cache_key(*datas, **kwargs):
    """
    여러 데이터와 키워드 인자를 받아서 고유한 해시키 생성
    
    Parameters:
    -----------
    *datas : any
        해시키 생성에 사용할 데이터들
    **kwargs : any
        해시키 생성에 사용할 키워드 인자들
    
    Returns:
    --------
    str : MD5 해시 키
    
    Examples:
    ---------
    >>> import helper.c0z0c.dev as helper
    >>> key = helper.cache_key("model_v1", params)
    >>> print(key)  # '1a2b3c4d5e...'
    """
    return DataCatch.key(*datas, **kwargs)

def cache_save(key, value, cache_file=None):
    """
    데이터를 캐시에 저장
    
    Parameters:
    -----------
    key : str
        저장할 때 사용할 키
    value : any
        저장할 데이터 (DataFrame, numpy array, 일반 객체 등)
    cache_file : str, optional
        캐시 파일 경로 
        - None (기본값): 환경별 자동 설정
          * Colab: /content/drive/MyDrive/cache.json
          * 로컬: cache.json
        - 상대 경로: Colab에서 /content/drive/MyDrive/ 하위에 자동 저장
        - 절대 경로: 지정된 경로 그대로 사용
    
    Returns:
    --------
    bool : 저장 성공 여부
    
    Examples:
    ---------
    >>> import helper.c0z0c.dev as helper
    >>> model = train_model()
    >>> key = helper.cache_key("model_v1", params)
    >>> helper.cache_save(key, model)  # 환경별 기본 경로
    >>> helper.cache_save(key, model, "project_a.json")  # Colab: /content/drive/MyDrive/project_a.json
    """
    return DataCatch.save(key, value, cache_file)

def cache_load(key, cache_file=None):
    """
    캐시에서 데이터 로드
    
    Parameters:
    -----------
    key : str
        로드할 데이터의 키
    cache_file : str, optional
        캐시 파일 경로
        - None (기본값): 환경별 자동 설정
          * Colab: /content/drive/MyDrive/cache.json
          * 로컬: cache.json
        - 상대 경로: Colab에서 /content/drive/MyDrive/ 하위에서 자동 탐색
        - 절대 경로: 지정된 경로에서 로드
    
    Returns:
    --------
    any or None : 저장된 데이터 또는 None (키가 없을 경우)
    
    Examples:
    ---------
    >>> import helper.c0z0c.dev as helper
    >>> key = helper.cache_key("model_v1", params)
    >>> model = helper.cache_load(key)  # 환경별 기본 경로에서 로드
    >>> if model:
    >>>     print("캐시에서 모델 로드됨")
    """
    return DataCatch.load(key, cache_file)

def cache_exists(key, cache_file=None):
    """
    캐시에 키가 존재하는지 확인
    
    Parameters:
    -----------
    key : str
        확인할 키
    cache_file : str, optional
        캐시 파일 경로 (기본값: cache.json)
    
    Returns:
    --------
    bool : 키 존재 여부
    
    Examples:
    ---------
    >>> import helper.c0z0c.dev as helper
    >>> key = helper.cache_key("model_v1", params)
    >>> if helper.cache_exists(key):
    >>>     model = helper.cache_load(key)
    """
    return DataCatch.exists(key, cache_file)

def cache_delete(key, cache_file=None):
    """
    캐시에서 특정 키 삭제
    
    Parameters:
    -----------
    key : str
        삭제할 키
    cache_file : str, optional
        캐시 파일 경로 (기본값: cache.json)
    
    Returns:
    --------
    bool : 삭제 성공 여부
    
    Examples:
    ---------
    >>> import helper.c0z0c.dev as helper
    >>> helper.cache_delete("old_model_key")
    """
    return DataCatch.delete(key, cache_file)

def cache_delete_keys(*keys, cache_file=None):
    """
    캐시에서 여러 키를 한번에 삭제
    
    Parameters:
    -----------
    *keys : str
        삭제할 키들
    cache_file : str, optional
        캐시 파일 경로 (기본값: cache.json)
    
    Returns:
    --------
    int : 삭제된 키의 개수
    
    Examples:
    ---------
    >>> import helper.c0z0c.dev as helper
    >>> helper.cache_delete_keys("key1", "key2", "key3")
    """
    return DataCatch.delete_keys(*keys, cache_file=cache_file)

def cache_clear(cache_file=None):
    """
    캐시 전체 초기화
    
    Parameters:
    -----------
    cache_file : str, optional
        캐시 파일 경로 (기본값: cache.json)
    
    Examples:
    ---------
    >>> import helper.c0z0c.dev as helper
    >>> helper.cache_clear()  # 모든 캐시 삭제
    """
    DataCatch.clear_cache(cache_file)
    print("캐시가 전체 초기화되었습니다.")

def cache_info(cache_file=None):
    """
    캐시 정보 출력
    
    Parameters:
    -----------
    cache_file : str, optional
        캐시 파일 경로 (기본값: cache.json)
    
    Examples:
    ---------
    >>> import helper.c0z0c.dev as helper
    >>> helper.cache_info()
    """
    DataCatch.cache_info(cache_file)

def cache_list_keys(cache_file=None):
    """
    저장된 모든 키 목록 반환
    
    Parameters:
    -----------
    cache_file : str, optional
        캐시 파일 경로 (기본값: cache.json)
    
    Returns:
    --------
    list : 키 목록
    
    Examples:
    ---------
    >>> import helper.c0z0c.dev as helper
    >>> keys = helper.cache_list_keys()
    >>> print(f"저장된 키 개수: {len(keys)}")
    """
    return DataCatch.list_keys(cache_file)

def cache_compress(cache_file=None):
    """
    캐시 파일을 압축하여 저장 공간 절약
    
    Parameters:
    -----------
    cache_file : str, optional
        압축할 캐시 파일 경로 (기본값: cache.json)
    
    Examples:
    ---------
    >>> import helper.c0z0c.dev as helper
    >>> helper.cache_compress()  # 캐시 파일 압축
    """
    return DataCatch.compress_cache(cache_file)

def cache_cleanup(days=30, cache_file=None):
    """
    오래된 캐시 항목 정리 (현재는 수동 정리만 지원)
    
    Parameters:
    -----------
    days : int
        보관할 일수 (현재 미구현, 향후 확장용)
    cache_file : str, optional
        정리할 캐시 파일 경로
    
    Examples:
    ---------
    >>> import helper.c0z0c.dev as helper
    >>> helper.cache_cleanup()  # 수동 정리
    """
    return DataCatch.cleanup_cache(days, cache_file)

def cache_size(cache_file=None):
    """
    캐시 크기(항목 수) 반환
    
    Parameters:
    -----------
    cache_file : str, optional
        캐시 파일 경로 (기본값: cache.json)
    
    Returns:
    --------
    int : 캐시에 저장된 항목 수
    
    Examples:
    ---------
    >>> import helper.c0z0c.dev as helper
    >>> size = helper.cache_size()
    >>> print(f"캐시 크기: {size}개")
    """
    return DataCatch.size(cache_file)

# pandas 확장 기능 함수들
def set_head_att(self, key_or_dict, value=None):
    """
    컬럼 설명을 설정합니다.
    
    Parameters:
    -----------
    key_or_dict : dict or str
        - dict: 여러 컬럼 설명을 한 번에 설정 {"컬럼명": "설명"}
        - str: 단일 컬럼명 (value와 함께 사용)
    value : str, optional
        key_or_dict가 str일 때 해당 컬럼의 설명
    
    Examples:
    ---------
    >>> df.set_head_att({"id": "ID", "state": "지역"})
    >>> df.set_head_att("id", "아이디")
    """
    # attrs 초기화
    if not hasattr(self, 'attrs'):
        self.attrs = {}
    if 'column_descriptions' not in self.attrs:
        self.attrs["column_descriptions"] = {}
    
    if isinstance(key_or_dict, dict):
        # 딕셔너리로 여러 개 설정
        self.attrs["column_descriptions"].update(key_or_dict)
    elif isinstance(key_or_dict, str) and value is not None:
        # 개별 설정/수정
        self.attrs["column_descriptions"][key_or_dict] = value
    else:
        raise ValueError("사용법: set_head_att(dict) 또는 set_head_att(key, value)")

def get_head_att(self, key=None):
    """
    컬럼 설명을 반환합니다.
    
    Parameters:
    -----------
    key : str, optional
        특정 컬럼의 설명을 가져올 컬럼명. None이면 전체 딕셔너리 반환
    
    Returns:
    --------
    dict or str : 
        - key가 None이면 전체 컬럼 설명 딕셔너리 반환
        - key가 주어지면 해당 컬럼의 설명 문자열 반환
    
    Raises:
    -------
    KeyError : 존재하지 않는 컬럼명을 요청했을 때
    TypeError : key가 문자열이 아닐 때
    
    Examples:
    ---------
    >>> descriptions = df.get_head_att()           # 전체 딕셔너리
    >>> score_desc = df.get_head_att('score')     # 특정 컬럼 설명
    >>> descriptions['new_col'] = '새로운 설명'    # 딕셔너리 직접 수정 가능
    """
    # attrs 초기화
    if not hasattr(self, 'attrs'):
        self.attrs = {}
    if 'column_descriptions' not in self.attrs:
        self.attrs["column_descriptions"] = {}
    
    # key가 None이면 전체 딕셔너리 반환
    if key is None:
        return self.attrs["column_descriptions"]
    
    # key 타입 검증
    if not isinstance(key, str):
        raise TypeError(f"key는 문자열이어야 합니다. 현재 타입: {type(key)}")
    
    # key 존재 여부 확인
    if key not in self.attrs["column_descriptions"]:
        return key  # 컬럼 설명이 없으면 key 자체 반환 (None 대신)
        #available_keys = list(self.attrs["column_descriptions"].keys())
        #raise KeyError(f"컬럼 '{key}'에 대한 설명이 없습니다. 사용 가능한 컬럼: {available_keys}")
    
    return self.attrs["column_descriptions"][key]

def remove_head_att(self, key):
    """
    특정 컬럼 설명 또는 컬럼 설명 리스트 삭제
    
    Parameters:
    -----------
    key : str or list
        삭제할 컬럼명 또는 컬럼명 리스트
    """
    if not hasattr(self, 'attrs') or 'column_descriptions' not in self.attrs:
        return

    if isinstance(key, str):
        key = [key]

    for k in key:
        if k in self.attrs["column_descriptions"]:
            self.attrs["column_descriptions"].pop(k)
            print(f"컬럼 설명 '{k}' 삭제 완료")
        else:
            print(f"'{k}' 컬럼 설명을 찾을 수 없습니다.")

def clear_head_att(self):
    """모든 컬럼 설명을 초기화합니다."""
    if not hasattr(self, 'attrs'):
        self.attrs = {}
    self.attrs["column_descriptions"] = {}

def _align_text(text, width, align='left'):
    """텍스트를 지정된 폭에 맞춰 정렬"""
    text_str = str(text)
    current_width = _get_text_width(text_str)
    padding = max(0, width - current_width)
    
    if align == 'right':
        return ' ' * padding + text_str
    elif align == 'center':
        left_padding = padding // 2
        right_padding = padding - left_padding
        return ' ' * left_padding + text_str + ' ' * right_padding
    else:  # left (default)
        return text_str + ' ' * padding

def _calculate_column_widths(df_display, labels):
    """컬럼 폭 계산 (pandas 기본 스타일)"""
    widths = []
    
    # 첫 번째 컬럼: 인덱스 폭 계산
    if len(df_display) == 0:
        max_index_width = 1  # 최소 폭
    else:
        max_index_width = max(_get_text_width(str(idx)) for idx in df_display.index)
    
    # 인덱스 컬럼 폭 (pandas 스타일: 최소 여유 공간)
    index_width = max_index_width + 1
    widths.append(index_width)
    
    # 나머지 컬럼들
    for col in df_display.columns:
        korean_name = labels.get(col, col)
        english_name = col
        
        # 데이터가 비어있을 때 처리
        if len(df_display) == 0:
            max_data_width = 0
        else:
            max_data_width = max(_get_text_width(_format_value(val)) for val in df_display[col])
        
        # 각 요소의 최대 폭 계산
        max_width = max(
            _get_text_width(korean_name),
            _get_text_width(english_name),
            max_data_width
        )
        
        # pandas 스타일: 최소 여유 공간 (1칸)
        column_width = max_width + 1
        widths.append(column_width)
    
    return widths

def pd_head_att(self, rows=5, out=None):
    """한글 컬럼 설명이 포함된 DataFrame을 다양한 형태로 출력합니다.
    import pandas as pd
    df.head_att()
    df.head_att(rows=5, out='print')
    df.head_att(rows='all', out='html')
    Parameters:
    -----------
    rows : int or str, optional
        출력할 행 수 (기본값: 5)
    out : str, optional
        출력 형식 (기본값: 'print')
        'print', 'html', 'str' 중 하나를 선택할 수 있습니다.
    Returns:
    --------
    str or None
        - 'print'일 경우 None 반환 (콘솔 출력)
        - 'html'일 경우 HTML 객체 반환
        - 'str'일 경우 문자열 형태로 반환
    Raises:
    -------
    ValueError : 잘못된 out 옵션
    Examples:
    ---------
    >>> df.head_att()  # 기본 출력 (5행)
    >>> df.head_att(rows=10)  # 10행 출력
    >>> df.head_att(out='html')  # HTML 형태로 출력
    >>> df.head_att(rows='all', out='print')  # 전체 데이터 출력 (콘솔)
    """
    labels = self.attrs.get("column_descriptions", {})

    # 출력할 데이터 결정
    if isinstance(rows, str) and rows.lower() == "all":
        df_display = self
    elif isinstance(rows, int):
        if rows == -1:
            df_display = self
        elif rows == 0:
            df_display = self.iloc[0:0]
        else:
            df_display = self.head(rows)
    else:
        df_display = self.head(5)

    # 보조 컬럼명 출력 조건
    # 1. column_descriptions가 완전히 비어 있으면 보조 컬럼명 출력하지 않음 (오리지널 컬럼명만 한 번 출력)
    # 2. column_descriptions가 비어 있지 않고 특정 컬럼만 비어 있으면 기존과 동일하게 처리
    if not labels:
        # 보조 컬럼명 없이 오리지널 컬럼명만 한 번 출력
        def _print_original_only(df_display):
            # 영문 헤더 출력 (오른쪽 정렬)
            column_widths = _calculate_column_widths(df_display, {})
            index_width = column_widths[0]
            data_widths = column_widths[1:]
            english_parts = []
            english_parts.append(_align_text('', index_width, 'right'))
            for col, width in zip(df_display.columns, data_widths):
                english_parts.append(_align_text(col, width, 'right'))
            print(''.join(english_parts))
            # 데이터 출력
            for idx, row in df_display.iterrows():
                row_parts = []
                row_parts.append(_align_text(str(idx), index_width, 'right'))
                for val, width in zip(row, data_widths):
                    row_parts.append(_align_text(_format_value(val), width, 'right'))
                print(''.join(row_parts))
        if out is None or out.lower() == 'print':
            _print_original_only(df_display)
            return None
        elif out.lower() == 'html':
            # HTML 헤더는 오리지널 컬럼명만 출력
            df_copy = df_display.copy()
            # 실수형 값들을 포맷팅
            for col in df_copy.columns:
                df_copy[col] = df_copy[col].apply(_format_value)
            df_copy.columns = list(df_display.columns)
            from IPython.display import HTML
            return HTML(df_copy.to_html(escape=False))
        elif out.lower() in ['str', 'string']:
            # 문자열 형태로 오리지널 컬럼명만 출력
            column_widths = _calculate_column_widths(df_display, {})
            result = ""
            english_row = ""
            for i, col in enumerate(df_display.columns):
                english_row += _align_text(col, column_widths[i])
            result += english_row + "\n"
            for idx, row in df_display.iterrows():
                data_row = ""
                for i, val in enumerate(row):
                    if i == 0:
                        text = str(idx)
                        formatted_val = _format_value(val)
                        data_row += _align_text(text, column_widths[i] - _get_text_width(formatted_val))
                        data_row += formatted_val
                    else:
                        data_row += _align_text(_format_value(val), column_widths[i])
                result += data_row + "\n"
            return result.rstrip()
        else:
            raise ValueError("out 옵션은 'html', 'print', 'str', 'string' 중 하나여야 합니다.")
    else:
        # 기존 로직 (보조 컬럼명 일부만 비어 있으면 기존과 동일하게 처리)
        if out is None or out.lower() == 'print':
            return self._print_head_att(df_display, labels)
        elif out.lower() == 'html':
            return self._html_head_att(df_display, labels)
        elif out.lower() in ['str', 'string']:
            return self._string_head_att(df_display, labels)
        else:
            raise ValueError("out 옵션은 'html', 'print', 'str', 'string' 중 하나여야 합니다.")

def _print_head_att(self, df_display, labels):
    """print 형태로 출력 (pandas 기본 스타일)"""
    column_widths = _calculate_column_widths(df_display, labels)
    
    # 첫 번째 부분은 인덱스용
    index_width = column_widths[0]
    data_widths = column_widths[1:]
    
    # 한글 헤더 출력 (오른쪽 정렬)
    korean_parts = []
    korean_parts.append(_align_text('', index_width, 'right'))  # 인덱스 헤더는 빈공간
    for col, width in zip(df_display.columns, data_widths):
        korean_name = labels.get(col, col)
        korean_parts.append(_align_text(korean_name, width, 'right'))
    print(''.join(korean_parts))
    
    # 영문 헤더 출력 (오른쪽 정렬)
    english_parts = []
    english_parts.append(_align_text('', index_width, 'right'))  # 인덱스 헤더는 빈공간
    for col, width in zip(df_display.columns, data_widths):
        english_parts.append(_align_text(col, width, 'right'))
    print(''.join(english_parts))
    
    # 데이터 출력 (모두 오른쪽 정렬 - pandas 기본 스타일)
    for idx, row in df_display.iterrows():
        row_parts = []
        # 인덱스 출력 (오른쪽 정렬)
        row_parts.append(_align_text(str(idx), index_width, 'right'))
        # 데이터 출력 (오른쪽 정렬)
        for val, width in zip(row, data_widths):
            row_parts.append(_align_text(_format_value(val), width, 'right'))
        print(''.join(row_parts))

def _html_head_att(self, df_display, labels):
    """HTML 형태로 출력"""
    header = []
    for col in df_display.columns:
        if col in labels and labels[col]:
            header.append(f"{labels[col]}<br>{col}")
        else:
            header.append(col)
    
    df_copy = df_display.copy()
    # 실수형 값들을 포맷팅
    for col in df_copy.columns:
        df_copy[col] = df_copy[col].apply(_format_value)
    df_copy.columns = header
    
    from IPython.display import HTML
    return HTML(df_copy.to_html(escape=False))

def _string_head_att(self, df_display, labels):
    """문자열 형태로 출력"""
    column_widths = _calculate_column_widths(df_display, labels)
    
    result = ""
    
    # 한글 헤더 생성
    korean_row = ""
    for i, col in enumerate(df_display.columns):
        korean_name = labels.get(col, col)
        korean_row += _align_text(korean_name, column_widths[i])
    result += korean_row + "\n"
    
    # 영문 헤더 생성
    english_row = ""
    for i, col in enumerate(df_display.columns):
        english_row += _align_text(col, column_widths[i])
    result += english_row + "\n"
    
    # 데이터 생성
    for idx, row in df_display.iterrows():
        data_row = ""
        for i, val in enumerate(row):
            if i == 0:
                text = str(idx)
                formatted_val = _format_value(val)
                data_row += _align_text(text, column_widths[i] - _get_text_width(formatted_val))
                data_row += formatted_val
            else:
                data_row += _align_text(_format_value(val), column_widths[i])
        result += data_row + "\n"
    
    return result.rstrip()

def series_head_att(self, rows=5, out=None):
    """한글 컬럼 설명이 포함된 Series를 다양한 형태로 출력합니다."""
    labels = self.attrs.get("column_descriptions", {})
    
    # 출력할 데이터 결정
    if isinstance(rows, str) and rows.lower() == "all":
        series_display = self
    elif isinstance(rows, int):
        if rows == -1:
            series_display = self
        elif rows == 0:
            series_display = self.iloc[0:0]
        else:
            series_display = self.head(rows)
    else:
        series_display = self.head(5)
    
    series_name = self.name if self.name is not None else "Series"
    korean_name = labels.get(series_name, series_name)
    
    if out is None or out.lower() == 'print':
        # 인덱스 최대 폭 계산
        index_widths = [_get_text_width(str(idx)) for idx in series_display.index]
        max_index_width = max(index_widths) if index_widths else 0
        
        # 데이터 최대 폭 계산
        data_widths = [_get_text_width(_format_value(val)) for val in series_display]
        max_data_width = max(data_widths) if data_widths else 0
        
        # 헤더 폭 계산
        korean_header_width = _get_text_width(korean_name)
        english_header_width = _get_text_width(series_name)
        
        # 각 컬럼의 최대 폭 결정
        index_column_width = max(max_index_width, 5) + 2
        data_column_width = max(max_data_width, korean_header_width, english_header_width) + 2
        
        # 헤더 출력
        korean_header = _align_text("인덱스", index_column_width) + _align_text(korean_name, data_column_width)
        print(korean_header)
        
        english_header = _align_text("index", index_column_width) + _align_text(series_name, data_column_width)
        print(english_header)
        
        # 데이터 출력
        for idx, val in series_display.items():
            data_row = _align_text(str(idx), index_column_width) + _align_text(_format_value(val), data_column_width)
            print(data_row)
        
        return None
    
    elif out.lower() == 'html':
        df = series_display.to_frame()
        # 실수형 값들을 포맷팅
        df.iloc[:, 0] = df.iloc[:, 0].apply(_format_value)
        
        if series_name in labels and labels[series_name]:
            df.columns = [f"{labels[series_name]}<br>{series_name}"]
        else:
            df.columns = [series_name]
        
        from IPython.display import HTML
        return HTML(df.to_html(escape=False))
    
    elif out.lower() in ['str', 'string']:
        # 인덱스 최대 폭 계산
        index_widths = [_get_text_width(str(idx)) for idx in series_display.index]
        max_index_width = max(index_widths) if index_widths else 0
        
        # 데이터 최대 폭 계산
        data_widths = [_get_text_width(_format_value(val)) for val in series_display]
        max_data_width = max(data_widths) if data_widths else 0
        
        # 헤더 폭 계산
        korean_header_width = _get_text_width(korean_name)
        english_header_width = _get_text_width(series_name)
        
        # 각 컬럼의 최대 폭 결정
        index_column_width = max(max_index_width, _get_text_width("인덱스"), _get_text_width("index")) + 2
        data_column_width = max(max_data_width, korean_header_width, english_header_width) + 2
        
        result = ""
        
        # 한글 헤더 생성
        korean_header = _align_text("인덱스", index_column_width) + _align_text(korean_name, data_column_width)
        result += korean_header + "\n"
        
        # 영문 헤더 생성
        english_header = _align_text("index", index_column_width) + _align_text(series_name, data_column_width)
        result += english_header + "\n"
        
        # 데이터 생성
        for idx, val in series_display.items():
            data_row = _align_text(str(idx), index_column_width) + _align_text(_format_value(val), data_column_width)
            result += data_row + "\n"
        
        return result.rstrip()
    
    else:
        raise ValueError("out 옵션은 'html', 'print', 'str', 'string' 중 하나여야 합니다.")

def _init_column_attrs(self):
    """컬럼 속성 초기화"""
    if not hasattr(self, 'attrs'):
        self.attrs = {}
    if 'columns_extra' not in self.attrs:
        self.attrs['columns_extra'] = {
            'org': {'name': 'org', 'columns': {col: col for col in self.columns}}
        }
        self.attrs['current_column_set'] = 'org'

def set_head_ext(self, columns_name, columns_extra=None, column_value=None):
    """
    보조 컬럼명 세트를 설정합니다.
    
    사용법:
    1. 전체 세트 설정: set_head_ext('kr', {'id': 'ID', 'name': '이름'})
    2. 개별 컬럼 설정: set_head_ext('kr', 'name', '이름')
    
    Parameters:
    -----------
    columns_name : str
        컬럼 세트의 이름 (예: 'kr', 'desc', 'eng')
    columns_extra : dict or str
        방식1: 전체 매핑 딕셔너리 {"원본컬럼": "새컬럼명"}
        방식2: 개별 컬럼명 (키)
    column_value : str, optional
        방식2에서 사용할 컬럼 값
    
    Raises:
    -------
    TypeError : 잘못된 타입의 매개변수
    ValueError : 잘못된 값 (빈 문자열, 빈 딕셔너리, None 값, 중복값 등)
    KeyError : 존재하지 않는 컬럼명
    
    Examples:
    ---------
    >>> df.set_head_ext('kr', {'id': 'ID', 'name': '이름'})
    >>> df.set_head_ext('kr', 'score', '점수')  # 개별 추가
    >>> df.set_head_ext('desc', {'id': '식별자', 'name': '성명'})
    """
    # 입력 방식 판단
    if column_value is not None:
        # 방식 2: 개별 컬럼 설정
        return self._set_head_ext_individual(columns_name, columns_extra, column_value)
    else:
        # 방식 1: 전체 세트 설정
        return self._set_head_ext_bulk(columns_name, columns_extra)

def _set_head_ext_bulk(self, columns_name, columns_extra):
    """전체 세트 설정 (기존 방식)"""
    # 1. 입력 타입 검증
    if not isinstance(columns_name, str):
        raise TypeError(f"columns_name은 문자열이어야 합니다. 현재 타입: {type(columns_name)}")
    
    if not isinstance(columns_extra, dict):
        raise TypeError(f"columns_extra는 딕셔너리여야 합니다. 현재 타입: {type(columns_extra)}")
    
    # 2. 빈 이름 검증
    if not columns_name.strip():
        raise ValueError("columns_name은 비어있을 수 없습니다.")
    
    # 3. 빈 딕셔너리 검증
    if not columns_extra:
        raise ValueError("columns_extra는 최소 하나의 컬럼 매핑을 포함해야 합니다.")
    
    # 4. 현재 DataFrame의 컬럼 목록 가져오기
    current_columns = set(self.columns)
    
    # 5. 존재하지 않는 컬럼 검증
    missing_columns = set(columns_extra.keys()) - current_columns
    if missing_columns:
        raise KeyError(f"다음 컬럼들이 DataFrame에 존재하지 않습니다: {list(missing_columns)}")
    
    # 6. None 값 검증
    none_mappings = [k for k, v in columns_extra.items() if v is None]
    if none_mappings:
        raise ValueError(f"다음 컬럼들의 매핑 값이 None입니다: {none_mappings}")
    
    # 7. 중복된 새 컬럼명 검증
    new_column_names = list(columns_extra.values())
    duplicates = [name for name in new_column_names if new_column_names.count(name) > 1]
    if duplicates:
        unique_duplicates = list(set(duplicates))
        raise ValueError(f"중복된 새 컬럼명이 있습니다: {unique_duplicates}")
    
    # 8. 예약된 세트명 검증
    if columns_name == 'org':
        raise ValueError("'org'는 예약된 세트명입니다. 다른 이름을 사용하세요.")
    
    # 모든 검증을 통과하면 기존 로직 실행
    self._init_column_attrs()
    
    self.attrs['columns_extra'][columns_name] = {
        'name': columns_name,
        'columns': columns_extra.copy()
    }
    
    print(f"컬럼 세트 '{columns_name}' 설정 완료")
    print(f"{len(columns_extra)}개 컬럼 매핑됨")

def _set_head_ext_individual(self, columns_name, column_key, column_value):
    """개별 컬럼 설정 (새로운 방식)"""
    # 입력 검증
    if not isinstance(columns_name, str):
        raise TypeError(f"columns_name은 문자열이어야 합니다. 현재 타입: {type(columns_name)}")
    
    if not isinstance(column_key, str):
        raise TypeError(f"column_key는 문자열이어야 합니다. 현재 타입: {type(column_key)}")
    
    if column_value is None:
        raise ValueError("column_value는 None일 수 없습니다.")
    
    if not columns_name.strip():
        raise ValueError("columns_name은 비어있을 수 없습니다.")
    
    if columns_name == 'org':
        raise ValueError("'org'는 예약된 세트명입니다. 다른 이름을 사용하세요.")
    
    # 컬럼 존재 확인
    if column_key not in self.columns:
        raise KeyError(f"컬럼 '{column_key}'이 DataFrame에 존재하지 않습니다.")
    
    self._init_column_attrs()
    
    # 세트가 존재하지 않으면 생성
    if columns_name not in self.attrs['columns_extra']:
        self.attrs['columns_extra'][columns_name] = {
            'name': columns_name,
            'columns': {}
        }
    
    # 개별 컬럼 업데이트
    old_value = self.attrs['columns_extra'][columns_name]['columns'].get(column_key)
    self.attrs['columns_extra'][columns_name]['columns'][column_key] = column_value
    
    if old_value is None:
        print(f"컬럼 세트 '{columns_name}'에 '{column_key}' → '{column_value}' 추가")
    else:
        print(f" 컬럼 세트 '{columns_name}'에서 '{column_key}': '{old_value}' → '{column_value}' 수정")
    
    total_mappings = len(self.attrs['columns_extra'][columns_name]['columns'])
    print(f" 현재 '{columns_name}' 세트 총 매핑 수: {total_mappings}개")

def set_head_column(self, columns_name):
    """
    지정된 컬럼 세트로 DataFrame의 컬럼명을 변경합니다.
    
    Parameters:
    -----------
    columns_name : str
        사용할 컬럼 세트 이름 (예: 'kr', 'desc', 'org')
    
    Raises:
    -------
    TypeError : 잘못된 타입의 매개변수
    ValueError : 잘못된 값 (빈 문자열 등)
    KeyError : 존재하지 않는 컬럼 세트명
    
    Examples:
    ---------
    >>> df.set_head_column('kr')   # 한글 컬럼명으로 변경
    >>> df.set_head_column('org')  # 원본 컬럼명으로 복원
    """
    # 1. 입력 타입 검증
    if not isinstance(columns_name, str):
        raise TypeError(f"columns_name은 문자열이어야 합니다. 현재 타입: {type(columns_name)}")
    
    # 2. 빈 문자열 검증
    if not columns_name.strip():
        raise ValueError("columns_name은 비어있을 수 없습니다.")
    
    self._init_column_attrs()
    
    # 3. 컬럼 세트 존재 검증
    if columns_name not in self.attrs['columns_extra']:
        available = list(self.attrs['columns_extra'].keys())
        raise KeyError(f"'{columns_name}' 컬럼 세트를 찾을 수 없습니다. 사용 가능한 세트: {available}")
    
    current_set = self.get_current_column_set()
    target_columns = self.attrs['columns_extra'][columns_name]['columns']
    
    # 컬럼명 변경 로직
    new_columns = self._convert_columns(current_set, columns_name, target_columns)
    self.columns = new_columns
    self.attrs['current_column_set'] = columns_name
    
    self._update_column_descriptions(current_set, columns_name)
    
    print(f" 컬럼명 변경: '{current_set}' → '{columns_name}'")
    print(f" 현재 컬럼: {list(self.columns)}")

def _convert_columns(self, current_set, target_set, target_columns):
    """컬럼명 변환 로직"""
    current_columns = self.attrs['columns_extra'][current_set]['columns']
    current_to_org = {v: k for k, v in current_columns.items()}
    
    new_columns = []
    for current_col in self.columns:
        if current_col in current_to_org:
            org_col = current_to_org[current_col]
        else:
            org_col = current_col
        
        if org_col in target_columns:
            new_columns.append(target_columns[org_col])
        else:
            new_columns.append(org_col)
    
    return new_columns

def _update_column_descriptions(self, current_set, target_set):
    """컬럼 설명 업데이트"""
    if 'column_descriptions' not in self.attrs:
        return
    
    # 컬럼명 변경 전의 old_columns와 변경 후의 new_columns(self.columns) 매핑
    current_columns = self.attrs['columns_extra'][current_set]['columns']
    target_columns = self.attrs['columns_extra'][target_set]['columns']
    
    # 현재 컬럼명 → 원본 컬럼명 매핑
    current_to_org = {v: k for k, v in current_columns.items()}
    
    # 변경 전 컬럼명 목록 생성 (현재 self.columns는 이미 변경된 상태)
    old_columns = []
    for new_col in self.columns:  # new_col은 변경된 컬럼명
        # 새 컬럼명에서 원본 컬럼명 찾기
        target_to_org = {v: k for k, v in target_columns.items()}
        if new_col in target_to_org:
            org_col = target_to_org[new_col]
            # 원본 컬럼명에서 이전 컬럼명 찾기
            if org_col in current_columns:
                old_columns.append(current_columns[org_col])
            else:
                old_columns.append(org_col)
        else:
            old_columns.append(new_col)
    
    old_descriptions = self.attrs['column_descriptions'].copy()
    new_descriptions = {}
    
    # 변경 전 컬럼명과 변경 후 컬럼명을 매핑
    for old_col, new_col in zip(old_columns, self.columns):
        if old_col in old_descriptions:
            new_descriptions[new_col] = old_descriptions[old_col]
    
    self.attrs['column_descriptions'] = new_descriptions

def get_current_column_set(self):
    """
    현재 활성화된 컬럼 세트를 반환합니다.
    
    Returns:
    --------
    str : 현재 컬럼 세트 이름
    """
    if not hasattr(self, 'attrs'):
        return 'org'
    return self.attrs.get('current_column_set', 'org')

def get_head_ext(self, columns_name=None):
    """
    보조 컬럼명 세트를 반환합니다.
    
    Parameters:
    -----------
    columns_name : str, optional
        특정 컬럼 세트 이름. None이면 전체 반환
    
    Returns:
    --------
    dict : 컬럼 세트 정보
    """
    if not hasattr(self, 'attrs'):
        self.attrs = {}
    if 'columns_extra' not in self.attrs:
        self.attrs['columns_extra'] = {}
    
    if columns_name is None:
        return self.attrs['columns_extra']
    else:
        return self.attrs['columns_extra'].get(columns_name, {})

def list_head_ext(self):
    """등록된 모든 컬럼 세트 출력"""
    self._init_column_attrs()
    
    if not self.attrs['columns_extra']:
        print(" 등록된 컬럼 세트가 없습니다.")
        return
    
    current_set = self.get_current_column_set()
    max_name_length = max(len(name) for name in self.attrs['columns_extra'].keys())
    
    print(" 등록된 컬럼 세트:")
    for name, info in self.attrs['columns_extra'].items():
        columns_list = list(info['columns'].values() if name != 'org' else info['columns'].keys())
        status = " (현재)" if name == current_set else ""
        formatted_name = f"{name}{status}".rjust(max_name_length + 5)
        print(f"{formatted_name}: {columns_list}")

def clear_head_ext(self):
    """컬럼명을 원본으로 복원 및 컬럼 세트 초기화"""
    if not hasattr(self, 'attrs') or 'columns_extra' not in self.attrs:
        return
    
    if 'org' in self.attrs['columns_extra']:
        org_columns = list(self.attrs['columns_extra']['org']['columns'].keys())
        self.columns = org_columns
        self.attrs['current_column_set'] = 'org'
        print(" 컬럼명을 원본으로 복원했습니다.")
    
    # org 제외하고 모든 컬럼 세트 초기화
    org_backup = self.attrs['columns_extra'].get('org', {})
    self.attrs['columns_extra'] = {'org': org_backup}
    print(" 모든 컬럼 세트를 초기화했습니다.")

def remove_head_ext(self, columns_name):
    """
    특정 컬럼 세트 또는 컬럼 세트 리스트 삭제
    Parameters:
    -----------
    columns_name : str or list
        삭제할 컬럼 세트명 또는 세트명 리스트
    """
    if not hasattr(self, 'attrs') or 'columns_extra' not in self.attrs:
        return

    if isinstance(columns_name, str):
        columns_name = [columns_name]

    current_set = self.get_current_column_set()
    for name in columns_name:
        if name == 'org':
            print(" 'org' 세트는 삭제할 수 없습니다.")
            continue
        if name == current_set:
            print(f" 현재 활성화된 '{name}' 세트는 삭제할 수 없습니다.")
            print(" 먼저 다른 세트로 변경하거나 원본으로 복원하세요.")
            continue
        if name in self.attrs['columns_extra']:
            del self.attrs['columns_extra'][name]
            print(f" 컬럼 세트 '{name}' 삭제 완료")
        else:
            print(f" '{name}' 컬럼 세트를 찾을 수 없습니다.")

class DataCatch:
    _default_cache_file = "cache.json"
    _cache = None
    _cache_file = None
    
    @classmethod
    def _initialize_cache(cls, cache_file=None):
        """캐시 초기화 (한 번만 실행)"""
        if cls._cache is None:
            # 기본 캐시 파일 경로 결정
            if cache_file is None:
                if _in_colab():
                    # Colab 환경에서는 Google Drive 경로 사용
                    cls._cache_file = "/content/drive/MyDrive/cache.json"
                else:
                    # 로컬 환경에서는 현재 디렉토리 사용
                    cls._cache_file = cls._default_cache_file
            else:
                # 사용자가 경로를 지정한 경우
                if _in_colab() and not cache_file.startswith(('/', 'http://', 'https://')):
                    # Colab에서 상대 경로인 경우 Google Drive 경로로 변환
                    cls._cache_file = f"/content/drive/MyDrive/{cache_file}"
                else:
                    cls._cache_file = cache_file
            
            cls._cache = cls._load_cache()
    
    @staticmethod
    def key(*datas, **kwargs):
        """여러 데이터와 키워드 인자를 받아서 고유한 해시키 생성"""
        try:
            # 위치 인자들을 직렬화 가능한 형태로 변환
            serializable_data = []
            for d in datas:
                if isinstance(d, np.ndarray):
                    serializable_data.append(d.tolist())
                elif isinstance(d, pd.DataFrame):
                    serializable_data.append(d.to_dict())
                elif isinstance(d, pd.Series):
                    serializable_data.append(d.to_list())
                elif hasattr(d, '__iter__') and not isinstance(d, (str, bytes)):
                    # 리스트, 튜플 등 반복 가능한 객체
                    serializable_data.append(list(d))
                else:
                    serializable_data.append(d)
            
            # 키워드 인자들을 정렬된 딕셔너리로 추가
            if kwargs:
                serializable_data.append(dict(sorted(kwargs.items())))
            
            # JSON 문자열로 변환하여 해시 생성
            data_str = json.dumps(serializable_data, sort_keys=True, default=str)
            return hashlib.md5(data_str.encode()).hexdigest()
        except Exception as e:
            # 직렬화 실패 시 객체의 문자열 표현으로 폴백
            fallback_str = str(datas) + str(kwargs)
            return hashlib.md5(fallback_str.encode()).hexdigest()
        
    @classmethod
    def save(cls, key, value, cache_file=None):
        """값을 직렬화 가능한 형태로 변환하여 저장"""
        cls._initialize_cache(cache_file)
        
        try:
            # 큰 데이터 저장 시 진행 상황 표시
            import sys
            data_size = sys.getsizeof(value)
            if data_size > 10 * 1024 * 1024:  # 10MB 이상
                print(f"큰 데이터 저장 중... (크기: {data_size / 1024 / 1024:.1f}MB)")
            
            # 값을 직렬화 가능한 형태로 변환
            serializable_value = cls._make_serializable(value)
            cls._cache[key] = serializable_value
            cls._save_cache()
            
            if data_size > 10 * 1024 * 1024:
                print(f"저장 완료: 키 '{key[:30]}{'...' if len(key) > 30 else ''}'")
            
            return True
        except Exception as e:
            print(f"오류: 저장 실패: {e}")
            return False

    @classmethod
    def load(cls, key, cache_file=None):
        """저장된 값을 원래 형태로 복원하여 반환"""
        cls._initialize_cache(cache_file)
        
        cached_value = cls._cache.get(key, None)
        if cached_value is None:
            return None
        
        try:
            # 저장된 값을 원래 형태로 복원
            return cls._restore_value(cached_value)
        except Exception as e:
            print(f" 복원 실패: {e}")
            return cached_value  # 실패 시 원본 반환

    @classmethod
    def _make_serializable(cls, value):
        """값을 JSON 직렬화 가능한 형태로 변환"""
        if isinstance(value, np.ndarray):
            return {
                '_type': 'numpy_array',
                'data': value.tolist(),
                'dtype': str(value.dtype),
                'shape': value.shape
            }
        elif isinstance(value, pd.DataFrame):
            return {
                '_type': 'pandas_dataframe',
                'data': value.to_dict(),
                'columns': list(value.columns),
                'index': list(value.index)
            }
        elif isinstance(value, pd.Series):
            return {
                '_type': 'pandas_series',
                'data': value.to_dict(),
                'name': value.name,
                'index': list(value.index)
            }
        elif isinstance(value, (list, tuple)):
            return [cls._make_serializable(item) for item in value]
        elif isinstance(value, dict):
            return {k: cls._make_serializable(v) for k, v in value.items()}
        elif isinstance(value, (np.integer, np.floating)):
            return float(value)
        else:
            return value

    @classmethod
    def _restore_value(cls, cached_value):
        """캐시된 값을 원래 형태로 복원"""
        if isinstance(cached_value, dict) and '_type' in cached_value:
            if cached_value['_type'] == 'numpy_array':
                return np.array(cached_value['data'], dtype=cached_value['dtype']).reshape(cached_value['shape'])
            elif cached_value['_type'] == 'pandas_dataframe':
                return pd.DataFrame(cached_value['data'], columns=cached_value['columns'], index=cached_value['index'])
            elif cached_value['_type'] == 'pandas_series':
                return pd.Series(cached_value['data'], name=cached_value['name'], index=cached_value['index'])
        elif isinstance(cached_value, list):
            return [cls._restore_value(item) for item in cached_value]
        elif isinstance(cached_value, dict):
            return {k: cls._restore_value(v) for k, v in cached_value.items()}
        
        return cached_value

    @classmethod
    def _load_cache(cls):
        """캐시 파일 로드 (백업 시스템 적용)"""
        backup_file = cls._cache_file + ".bak"
        
        # 메인 캐시 파일 로드 시도
        if os.path.exists(cls._cache_file):
            try:
                # 파일 크기 확인
                file_size = os.path.getsize(cls._cache_file)
                if file_size > 100 * 1024 * 1024:  # 100MB 이상
                    print(f"경고: 캐시 파일이 매우 큽니다 ({file_size / 1024 / 1024:.1f}MB). 로딩에 시간이 걸릴 수 있습니다.")
                
                # 큰 파일을 위한 청크 단위 읽기
                with open(cls._cache_file, "r", encoding='utf-8', buffering=8192) as f:
                    # JSON 파일의 완전성 검증을 위해 끝까지 읽기
                    content = f.read()
                    if not content.strip():
                        print("캐시 파일이 비어있습니다.")
                        return {}
                    
                    # JSON 파싱
                    cache_data = json.loads(content)
                    print(f"캐시 로드 완료: {len(cache_data)}개 항목 ({file_size / 1024 / 1024:.2f}MB)")
                    return cache_data
                    
            except json.JSONDecodeError as e:
                print(f"오류: 캐시 파일이 손상되었습니다: {e}")
                return cls._load_from_backup()
            except MemoryError:
                print(f"오류: 메모리 부족으로 캐시 파일을 로드할 수 없습니다.")
                print(f"   파일 크기: {file_size / 1024 / 1024:.1f}MB")
                return cls._load_from_backup()
            except Exception as e:
                print(f"오류: 캐시 파일 로드 실패: {e}")
                return cls._load_from_backup()
        
        # 메인 파일이 없으면 백업 파일 확인
        elif os.path.exists(backup_file):
            print("메인 캐시 파일이 없습니다. 백업 파일에서 복원을 시도합니다.")
            return cls._load_from_backup()
        
        return {}
    
    @classmethod
    def _load_from_backup(cls):
        """백업 파일에서 캐시 로드"""
        backup_file = cls._cache_file + ".bak"
        
        if not os.path.exists(backup_file):
            print("백업 파일이 존재하지 않습니다.")
            return {}
        
        try:
            print("백업 파일에서 캐시를 복원하는 중...")
            
            with open(backup_file, "r", encoding='utf-8', buffering=8192) as f:
                content = f.read()
                if not content.strip():
                    print("백업 파일이 비어있습니다.")
                    return {}
                
                cache_data = json.loads(content)
            
            # 손상된 메인 파일 삭제
            if os.path.exists(cls._cache_file):
                corrupted_file = cls._cache_file + ".corrupted"
                try:
                    os.rename(cls._cache_file, corrupted_file)
                    print(f"손상된 캐시 파일을 {corrupted_file}로 이동했습니다.")
                except:
                    try:
                        os.remove(cls._cache_file)
                        print("손상된 캐시 파일을 삭제했습니다.")
                    except:
                        pass
            
            # 백업 파일을 메인 파일로 복사
            try:
                import shutil
                shutil.copy2(backup_file, cls._cache_file)
                print("백업 파일에서 메인 캐시 파일을 복원했습니다.")
                print("주의: 캐시가 이전 상태로 되돌려졌습니다. 일부 최근 데이터가 손실될 수 있습니다.")
            except Exception as e:
                print(f"백업 파일 복사 실패: {e}")
            
            backup_size = os.path.getsize(backup_file)
            print(f"백업에서 캐시 복원 완료: {len(cache_data)}개 항목 ({backup_size / 1024 / 1024:.2f}MB)")
            return cache_data
            
        except json.JSONDecodeError as e:
            print(f"오류: 백업 파일도 손상되었습니다: {e}")
            return {}
        except Exception as e:
            print(f"오류: 백업 파일 로드 실패: {e}")
            return {}
    
    @classmethod
    def _cleanup_temp_files(cls):
        """임시 파일들 정리"""
        temp_file = cls._cache_file + ".tmp"
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except:
                pass

    @classmethod
    def _save_cache(cls):
        """캐시를 파일에 저장 (백업 시스템 적용)"""
        try:
            # 디렉토리가 존재하지 않으면 생성
            cache_dir = os.path.dirname(cls._cache_file)
            if cache_dir and not os.path.exists(cache_dir):
                os.makedirs(cache_dir, exist_ok=True)
            
            # 파일 경로 설정
            temp_file = cls._cache_file + ".tmp"
            backup_file = cls._cache_file + ".bak"
            
            # 예상 파일 크기 추정
            cache_str = json.dumps(cls._cache, indent=2, ensure_ascii=False)
            estimated_size = len(cache_str.encode('utf-8'))
            
            if estimated_size > 50 * 1024 * 1024:  # 50MB 이상
                print(f"경고: 큰 캐시 파일 저장 중... (예상 크기: {estimated_size / 1024 / 1024:.1f}MB)")
            
            # 임시 파일에 저장
            with open(temp_file, "w", encoding='utf-8', buffering=8192) as f:
                # 대용량 JSON을 청크 단위로 작성
                if estimated_size > 10 * 1024 * 1024:  # 10MB 이상
                    # 스트리밍 방식으로 JSON 저장
                    f.write('{\n')
                    items = list(cls._cache.items())
                    for i, (key, value) in enumerate(items):
                        f.write(f'  {json.dumps(key, ensure_ascii=False)}: ')
                        f.write(json.dumps(value, indent=2, ensure_ascii=False).replace('\n', '\n  '))
                        if i < len(items) - 1:
                            f.write(',')
                        f.write('\n')
                        
                        # 주기적으로 플러시
                        if i % 100 == 0:
                            f.flush()
                    f.write('}')
                else:
                    # 일반적인 경우
                    f.write(cache_str)
                
                f.flush()  # 버퍼 강제 플러시
                os.fsync(f.fileno())  # 디스크에 강제 동기화
            
            # 임시 파일이 정상적으로 저장되었는지 검증
            try:
                with open(temp_file, "r", encoding='utf-8') as f:
                    json.load(f)  # JSON 파싱 테스트
            except:
                print("오류: 임시 파일 저장 중 오류가 발생했습니다.")
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                return False
            
            # 백업 시스템 적용
            # 1. 기존 백업 파일 삭제
            if os.path.exists(backup_file):
                os.remove(backup_file)
            
            # 2. 기존 캐시 파일을 백업으로 이동 (있는 경우)
            if os.path.exists(cls._cache_file):
                os.rename(cls._cache_file, backup_file)
            
            # 3. 임시 파일을 메인 캐시 파일로 이동
            os.rename(temp_file, cls._cache_file)
            
            # 저장 완료 확인
            actual_size = os.path.getsize(cls._cache_file)
            if estimated_size > 10 * 1024 * 1024:
                print(f"캐시 저장 완료: {len(cls._cache)}개 항목 ({actual_size / 1024 / 1024:.2f}MB)")
            
            return True
                
        except OSError as e:
            print(f"오류: 디스크 공간 부족 또는 권한 오류: {e}")
            print(f"경로: {cls._cache_file}")
            cls._cleanup_temp_files()
            return False
        except MemoryError:
            print(f"오류: 메모리 부족으로 캐시를 저장할 수 없습니다.")
            print(f"캐시 항목 수: {len(cls._cache)}")
            cls._cleanup_temp_files()
            return False
        except Exception as e:
            print(f"오류: 캐시 파일 저장 실패: {e}")
            print(f"경로: {cls._cache_file}")
            if _in_colab():
                print("Google Drive가 마운트되지 않았을 수 있습니다.")
            cls._cleanup_temp_files()
            return False

    @classmethod
    def clear_cache(cls, cache_file=None):
        """캐시 초기화"""
        cls._initialize_cache(cache_file)
        cls._cache = {}
        if os.path.exists(cls._cache_file):
            os.remove(cls._cache_file)

    @classmethod
    def cache_info(cls, cache_file=None):
        """캐시 정보 출력"""
        cls._initialize_cache(cache_file)
        env_name = "Colab" if _in_colab() else "로컬"
        print(f"캐시 정보 ({env_name} 환경):")
        print(f"   - 파일: {cls._cache_file}")
        print(f"   - 항목 수: {len(cls._cache):,}")
        
        if os.path.exists(cls._cache_file):
            file_size = os.path.getsize(cls._cache_file)
            size_mb = file_size / 1024 / 1024
            
            if size_mb >= 1:
                print(f"   - 파일 크기: {size_mb:.2f}MB ({file_size:,} bytes)")
            elif file_size >= 1024:
                print(f"   - 파일 크기: {file_size / 1024:.1f}KB ({file_size:,} bytes)")
            else:
                print(f"   - 파일 크기: {file_size:,} bytes")
            
            # 메모리 사용량 추정
            try:
                import sys
                cache_memory = sys.getsizeof(cls._cache)
                for key, value in cls._cache.items():
                    cache_memory += sys.getsizeof(key) + sys.getsizeof(value)
                
                memory_mb = cache_memory / 1024 / 1024
                if memory_mb >= 1:
                    print(f"   - 메모리 사용량: 약 {memory_mb:.2f}MB")
                else:
                    print(f"   - 메모리 사용량: 약 {cache_memory / 1024:.1f}KB")
            except:
                pass
            
            # 큰 파일에 대한 경고
            if size_mb > 50:
                print(f"   경고: 캐시 파일이 큽니다. 성능에 영향을 줄 수 있습니다.")
            elif size_mb > 10:
                print(f"   적당한 크기의 캐시 파일입니다.")
                
        else:
            print(f"   - 상태: 캐시 파일 없음")
        
        # 최근 수정 시간
        if os.path.exists(cls._cache_file):
            import time
            mtime = os.path.getmtime(cls._cache_file)
            mtime_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(mtime))
            print(f"   - 최근 수정: {mtime_str}")

    @classmethod
    def delete(cls, key, cache_file=None):
        """특정 키 삭제"""
        cls._initialize_cache(cache_file)
        
        if key in cls._cache:
            del cls._cache[key]
            cls._save_cache()
            print(f" 키 '{key}' 삭제 완료")
            return True
        else:
            print(f" 키 '{key}'를 찾을 수 없습니다")
            return False
    
    @classmethod
    def delete_keys(cls, *keys, cache_file=None):
        """여러 키를 한번에 삭제"""
        cls._initialize_cache(cache_file)
        
        deleted_count = 0
        for key in keys:
            if key in cls._cache:
                del cls._cache[key]
                deleted_count += 1
                print(f" 키 '{key}' 삭제")
            else:
                print(f" 키 '{key}' 없음")
        
        if deleted_count > 0:
            cls._save_cache()
            print(f" 총 {deleted_count}개 키 삭제 완료")
        
        return deleted_count
    
    @classmethod
    def list_keys(cls, cache_file=None):
        """저장된 모든 키 목록 조회"""
        cls._initialize_cache(cache_file)
        return list(cls._cache.keys())
    
    @classmethod
    def exists(cls, key, cache_file=None):
        """키 존재 여부 확인"""
        cls._initialize_cache(cache_file)
        return key in cls._cache
    
    @classmethod
    def size(cls, cache_file=None):
        """캐시 크기 반환"""
        cls._initialize_cache(cache_file)
        return len(cls._cache)
    
    @classmethod
    def compress_cache(cls, cache_file=None):
        """캐시 파일 압축하여 저장 공간 절약"""
        cls._initialize_cache(cache_file)
        
        if not os.path.exists(cls._cache_file):
            print("압축할 캐시 파일이 없습니다.")
            return False
        
        try:
            import gzip
            import shutil
            
            original_size = os.path.getsize(cls._cache_file)
            compressed_file = cls._cache_file + ".gz"
            
            print(f"캐시 파일 압축 중... (원본: {original_size / 1024 / 1024:.2f}MB)")
            
            with open(cls._cache_file, 'rb') as f_in:
                with gzip.open(compressed_file, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            compressed_size = os.path.getsize(compressed_file)
            compression_ratio = (1 - compressed_size / original_size) * 100
            
            print(f"압축 완료: {compressed_size / 1024 / 1024:.2f}MB")
            print(f"압축률: {compression_ratio:.1f}% 절약")
            print(f"압축 파일: {compressed_file}")
            
            return True
            
        except ImportError:
            print("오류: gzip 모듈을 사용할 수 없습니다.")
            return False
        except Exception as e:
            print(f"오류: 압축 실패: {e}")
            return False
    
    @classmethod
    def cleanup_cache(cls, days=30, cache_file=None):
        """캐시 정리 (현재는 수동 정리)"""
        cls._initialize_cache(cache_file)
        
        if not cls._cache:
            print("정리할 캐시가 없습니다.")
            return 0
        
        print(f"캐시 정리 도구 (현재 {len(cls._cache)}개 항목)")
        print("향후 업데이트에서 자동 정리 기능이 추가될 예정입니다.")
        print("현재는 수동으로 cache_clear() 또는 cache_delete() 를 사용하세요.")
        
        # 메모리 사용량이 큰 항목들 표시
        try:
            import sys
            large_items = []
            for key, value in cls._cache.items():
                item_size = sys.getsizeof(value)
                if item_size > 1024 * 1024:  # 1MB 이상
                    large_items.append((key, item_size))
            
            if large_items:
                large_items.sort(key=lambda x: x[1], reverse=True)
                print("\n큰 캐시 항목들 (1MB 이상):")
                for key, size in large_items[:5]:  # 상위 5개만
                    print(f"  - {key[:50]}{'...' if len(key) > 50 else ''}: {size / 1024 / 1024:.2f}MB")
                    
        except Exception:
            pass
        
        return len(cls._cache)
    
    @classmethod
    def optimize_cache(cls, cache_file=None):
        """캐시 최적화 (재저장으로 파일 크기 최적화)"""
        cls._initialize_cache(cache_file)
        
        if not os.path.exists(cls._cache_file):
            print("최적화할 캐시 파일이 없습니다.")
            return False
        
        try:
            original_size = os.path.getsize(cls._cache_file)
            print(f"캐시 파일 최적화 중... (현재: {original_size / 1024 / 1024:.2f}MB)")
            
            # 캐시를 다시 저장하여 파일 최적화
            cls._save_cache()
            
            new_size = os.path.getsize(cls._cache_file)
            if new_size < original_size:
                saved_size = original_size - new_size
                saved_percent = (saved_size / original_size) * 100
                print(f"최적화 완료: {saved_size / 1024 / 1024:.2f}MB 절약 ({saved_percent:.1f}%)")
            else:
                print("최적화 완료: 추가 절약 공간 없음")
            
            return True
            
        except Exception as e:
            print(f"오류: 최적화 실패: {e}")
            return False


def _generate_commit_hash(dt, msg):
    """커밋 해시를 생성합니다."""
    base = f"{dt.strftime('%Y%m%d_%H%M%S')}_{msg}"
    return hashlib.md5(base.encode("utf-8")).hexdigest()[:12]

def df_to_pickle(df, path):
    """
    DataFrame과 df.attrs(딕셔너리)까지 함께 pickle로 저장
    """
    obj = {
        "data": df,
        "attrs": getattr(df, 'attrs', {})
    }
    with open(path, "wb") as f:
        pickle.dump(obj, f)

def df_read_pickle(path):
    """
    DataFrame과 attrs(딕셔너리)까지 복원
    """
    with open(path, "rb") as f:
        obj = pickle.load(f)
    df = obj["data"]
    if "attrs" in obj:
        df.attrs = obj["attrs"]
    return df

def pd_commit(df, msg, commit_dir=None):
    """
    DataFrame의 현재 상태를 git처럼 커밋합니다.
    파일명: 해시키.pkl, 메타: pandas_df.json
    commit_dir: 저장할 폴더 지정 (None이면 기본)
    동일한 메시지가 있으면 기존 커밋을 새 커밋으로 대체(업데이트)합니다.
    """
    if df is None or not isinstance(df, pd.DataFrame):
        raise ValueError("df 인자가 None이거나 유효한 DataFrame이 아닙니다.")
    dt = datetime.datetime.now()
    dt_str = dt.strftime("%Y-%m-%d %H:%M:%S")  # ISO8601 포맷
    commit_hash = _generate_commit_hash(dt, msg)
    fname = f"{commit_hash}.pkl_helper"
    save_dir = os.path.join(pd_root(commit_dir), ".commit_pandas")
    os.makedirs(save_dir, exist_ok=True)

    meta = _load_commit_meta(commit_dir)
    # print(f"커밋 준비: {commit_hash} | {dt_str} | {msg}")
    # print(f"meta: {meta}")
    # 메타데이터 파일 경로
    
    # 동일한 메시지(msg)가 있으면 기존 파일 삭제 및 메타에서 제거
    old_idx = None
    for i, m in enumerate(meta):
        if m["msg"] == msg:
            old_file = os.path.join(save_dir, m["file"])
            if os.path.exists(old_file):
                os.remove(old_file)
            old_idx = i
            break
    if old_idx is not None:
        meta.pop(old_idx)

    # 새 커밋 저장
    df_to_pickle(df, os.path.join(save_dir, fname))
    meta.append({
        "hash": commit_hash,
        "datetime": dt_str,
        "msg": msg,
        "file": fname
    })
    _save_commit_meta(meta, commit_dir)
    print(f"✅ 커밋 완료: {commit_hash} | {dt_str} | {msg}")
    return df

import pandas as pd



def pd_commit_list(commit_dir=None):
    """
    커밋 리스트를 시간순으로 반환 (존재하는 파일만, 없으면 자동 삭제)
    commit_dir: 저장 폴더 지정
    반환값: pandas.DataFrame (순서, 해시, 시간, 메시지, 파일)
    """
    meta = _load_commit_meta(commit_dir)
    save_dir = os.path.join(pd_root(commit_dir), ".commit_pandas")
    new_meta = []
    removed_count = 0
    
    for m in meta:
        file_path = os.path.join(save_dir, m["file"])
        if os.path.exists(file_path):
            new_meta.append(m)
        else:
            print(f"경고: 누락된 파일 '{m['file']}' (메시지: {m['msg']}) 메타데이터에서 제거")
            removed_count += 1
    
    # 메타데이터 정리가 필요한 경우
    if removed_count > 0:
        _save_commit_meta(new_meta, commit_dir)
        print(f"✅ {removed_count}개의 누락된 커밋 항목을 정리했습니다.")
    
    new_meta.sort(key=lambda x: x["datetime"])
    # DataFrame 변환
    df = pd.DataFrame(new_meta)
    if not df.empty:
        # datetime 컬럼을 pandas datetime 타입으로 변환
        df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')
        df.insert(0, 'index', range(len(df)))
    else:
        print("커밋 내역이 없습니다.")
    return df

def pd_checkout(idx_or_hash, commit_dir=None):
    """
    커밋 해시, 시간정보, 메시지, 순서번호로 DataFrame 복원
    파일이 없는 경우 메타데이터에서 자동으로 정리하고 빈 DataFrame 반환
    commit_dir: 저장 폴더 지정
    """
    meta = _load_commit_meta(commit_dir)
    save_dir = os.path.join(pd_root(commit_dir), ".commit_pandas")
    
    # 메타데이터 정리 플래그
    meta_updated = False
    
    if isinstance(idx_or_hash, int):
        if idx_or_hash < 0 or idx_or_hash >= len(meta):
            print(f"오류: 순서번호 {idx_or_hash}가 범위를 벗어났습니다. (0-{len(meta)-1})")
            return pd.DataFrame()
        
        fname = meta[idx_or_hash]["file"]
        file_path = os.path.join(save_dir, fname)
        
        # 파일 존재 여부 확인
        if not os.path.exists(file_path):
            print(f"경고: 파일 '{fname}'이 존재하지 않습니다. 메타데이터에서 제거합니다.")
            meta.pop(idx_or_hash)
            _save_commit_meta(meta, commit_dir)
            return pd.DataFrame()
        
        try:
            return df_read_pickle(file_path)
        except Exception as e:
            print(f"오류: 파일 읽기 실패: {e}")
            # 손상된 파일 정보를 메타에서 제거
            meta.pop(idx_or_hash)
            _save_commit_meta(meta, commit_dir)
            return pd.DataFrame()
    
    # 해시, 날짜, 메시지로 검색
    for i, m in enumerate(meta):
        if idx_or_hash == m["hash"] or idx_or_hash == m["datetime"] or idx_or_hash == m["msg"]:
            fname = m["file"]
            file_path = os.path.join(save_dir, fname)
            
            # 파일 존재 여부 확인
            if not os.path.exists(file_path):
                print(f"경고: 파일 '{fname}'이 존재하지 않습니다. 메타데이터에서 제거합니다.")
                meta.pop(i)
                _save_commit_meta(meta, commit_dir)
                return pd.DataFrame()
            
            try:
                return df_read_pickle(file_path)
            except Exception as e:
                print(f"오류: 파일 읽기 실패: {e}")
                # 손상된 파일 정보를 메타에서 제거
                meta.pop(i)
                _save_commit_meta(meta, commit_dir)
                return pd.DataFrame()
    
    print(f"오류: 커밋 '{idx_or_hash}'을(를) 찾을 수 없습니다.")
    return pd.DataFrame()  # 빈 DataFrame 반환


def pd_commit_rm(idx_or_hash, commit_dir=None):
    """
    커밋을 삭제합니다.
    idx_or_hash: 삭제할 커밋의 인덱스, 해시, 날짜, 또는 메시지
    commit_dir: 저장 폴더 지정
    """
    meta = _load_commit_meta(commit_dir)
    save_dir = os.path.join(pd_root(commit_dir), ".commit_pandas")
    if isinstance(idx_or_hash, int):
        if idx_or_hash < 0 or idx_or_hash >= len(meta):
            print(f"오류: 순서번호 {idx_or_hash}가 범위를 벗어났습니다. (0-{len(meta)-1})")
            return False
        fname = meta[idx_or_hash]["file"]
        try:
            os.remove(os.path.join(save_dir, fname))
            meta.pop(idx_or_hash)  # 메타에서 삭제
            _save_commit_meta(meta, commit_dir)
            print(f"✅ 커밋 {idx_or_hash} 삭제 완료")
            return True
        except OSError as e:
            print(f"오류: 파일 삭제 실패: {e}")
            return False
    for i, m in enumerate(meta):
        if idx_or_hash == m["hash"] or idx_or_hash == m["datetime"] or idx_or_hash == m["msg"]:
            fname = m["file"]
            try:
                os.remove(os.path.join(save_dir, fname))
                meta.pop(i)  # 메타에서 삭제
                _save_commit_meta(meta, commit_dir)
                print(f"✅ 커밋 '{idx_or_hash}' 삭제 완료")
                return True
            except OSError as e:
                print(f"오류: 파일 삭제 실패: {e}")
                return False
    print(f"오류: 커밋 '{idx_or_hash}'을(를) 찾을 수 없습니다.")
    return False

def pd_commit_has(idx_or_hash, commit_dir=None):
    """
    커밋 index, hash, datetime, msg 중 하나를 입력받아
    해당 커밋 파일이 존재하면 True, 없으면 False 반환
    """
    meta = _load_commit_meta(commit_dir)
    save_dir = os.path.join(pd_root(commit_dir), ".commit_pandas")
    # index로 검사
    if isinstance(idx_or_hash, int):
        if 0 <= idx_or_hash < len(meta):
            fname = meta[idx_or_hash]["file"]
            if os.path.exists(os.path.join(save_dir, fname)):
                return True
        return False
    # hash, datetime, msg로 검사
    for m in meta:
        if idx_or_hash == m["hash"] or idx_or_hash == m["datetime"] or idx_or_hash == m["msg"]:
            fname = m["file"]
            if os.path.exists(os.path.join(save_dir, fname)):
                return True
    return False

# 모듈 import 시 자동으로 setup 실행
if __name__ != "__main__":
    setup()
    set_pd_root_base()
