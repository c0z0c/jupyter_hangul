"""
Jupyter/Colab 한글 폰트 및 pandas 확장 모듈

🚀 기본 사용법:
    import helper.c0z0c.dev as helper
    helper.setup()  # 한번에 모든 설정 완료

🔧 개별 실행:
    helper.font_download()      # 폰트 다운로드
    helper.load_font()          # 폰트 로딩
    helper.set_pandas_extension()  # pandas 확장 기능

📁 파일 읽기:
    df = helper.pd_read_csv("파일명.csv")          # 문자열 경로 (자동 변환)
    df = helper.pd_read_csv(file_obj, encoding='utf-8')  # 파일 객체/URL 등

🔍 유틸리티:
    helper.dir_start(객체, "접두사")  # 메서드 검색
    df.head_att()  # 한글 컬럼 설명 출력

💡 Colab 사용 시 주의사항:
    - 세션 재시작 후 Google Drive 인증 오류 발생 시 런타임 재시작 필요
    - 문제가 지속되면 런타임 재시작 후 helper.setup() 다시 실행

작성자: 김명환
날짜: 2025.07.18
버전: 2.1.5
"""

import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# 전역 변수
__version__ = "2.1.5"
font_path = ""
is_colab = False

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

def font_download():
    """폰트를 다운로드하거나 설치합니다."""
    global font_path
    import urllib.request
    import subprocess
    
    if _in_colab():
        if os.system("dpkg -l | grep fonts-nanum") == 0:
            print("fonts-nanum이 이미 설치되어 있습니다.")
            return
        print("📥 install fonts-nanum")
        subprocess.run(['sudo', 'apt-get', 'install', '-y', 'fonts-nanum'], 
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("📥 프로세서가 종료 됩니다. 잠시후 다시 시도 하세요")
        subprocess.run(['sudo', 'fc-cache', '-fv'], 
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(['rm', '-rf', os.path.expanduser('~/.cache/matplotlib')], 
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        os.kill(os.getpid(), 9)
    else:
        font_url = "https://github.com/c0z0c/jupyter_hangul/raw/master/NanumGothic.ttf"
        font_dir = "fonts"
        os.makedirs(font_dir, exist_ok=True)
        font_path = os.path.join(font_dir, "NanumGothic.ttf")
        if not os.path.exists(font_path):
            print("📥 Downloading NanumGothic.ttf...")
            urllib.request.urlretrieve(font_url, font_path)
            print("✅ Download complete.")
        else:
            print("✔️ Font already exists.")
        print(f"font_path={font_path}")

def _colab_font_reinstall():
    """Colab에서 폰트 재설치"""
    import subprocess
    import time
    from IPython.display import display, Markdown
    
    print("📋 Colab 환경에서 폰트 재설치를 진행합니다...")
    try:
        # 기존 폰트 패키지 완전 제거
        print("🗑️  기존 fonts-nanum 패키지 제거 중...")
        subprocess.run(['sudo', 'apt-get', 'remove', '--purge', '-y', 'fonts-nanum'], 
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # 폰트 캐시 완전 정리
        print("🧹 폰트 캐시 완전 정리 중...")
        subprocess.run(['sudo', 'fc-cache', '-f', '-v'], 
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(['rm', '-rf', os.path.expanduser('~/.cache/matplotlib')], 
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(['rm', '-rf', os.path.expanduser('~/.fontconfig')], 
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # 패키지 목록 업데이트
        print("📦 패키지 목록 업데이트 중...")
        subprocess.run(['sudo', 'apt-get', 'update', '-qq'], 
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # 폰트 재설치
        print("📥 fonts-nanum 재설치 중...")
        subprocess.run(['sudo', 'apt-get', 'install', '-y', 'fonts-nanum'], 
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # 폰트 캐시 재구성
        print("🔧 폰트 캐시 재구성 중...")
        subprocess.run(['sudo', 'fc-cache', '-f', '-v'], 
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        restart_guide = """
# 🔄 폰트 재설치 완료

폰트 재설치가 완료되었습니다. **프로세서를 재시작**하고 다시 시도하세요.

## 🚀 재시작 방법
1. **메뉴 > 런타임 > 런타임 다시 시작** 클릭
2. 재시작 후 **helper.setup()** 다시 실행
"""
        display(Markdown(restart_guide))
        
        print("🔄 3초 후 프로세서를 재시작합니다...")
        time.sleep(3)
        os.kill(os.getpid(), 9)
        
    except Exception as reinstall_error:
        print(f"❌ 재설치 중 오류 발생: {str(reinstall_error)}")
        print("🔄 수동으로 런타임을 재시작하고 다시 시도하세요.")

def load_font():
    """폰트를 로딩하고 설정합니다."""
    global font_path, is_colab
    import matplotlib.font_manager as fm
    from IPython.display import display, Markdown

    try:
        if _in_colab():
            print("🔍 Colab 환경에서 폰트 설정 중...")
            is_colab = True
            
            # Google Drive 마운트 시도 (선택적)
            try:
                print("📁 Google Drive 연결 시도 중...")
                from google.colab import drive
                drive.mount("/content/drive", force_remount=True)
                print("✅ Google Drive 연결 성공")
            except Exception as drive_error:
                print(f"⚠️  Google Drive 연결 실패: {str(drive_error)}")
                print("� Google Drive 없이 계속 진행합니다...")
            
            plt.rc("font", family="NanumBarunGothic")
            plt.rcParams['axes.unicode_minus'] = False
            display(Markdown("**💻 실행 환경**: Colab\n✅ 한글 폰트가 성공적으로 설정되었습니다."))
        else:
            is_colab = False
            if plt.rcParams["font.family"] == "NanumGothic":
                print("✔️ 한글 폰트가 설치 되어 있습니다.\n추가 작업을 하지 않습니다.")
                return

            try:
                fm.fontManager.addfont(font_path)
                plt.rcParams["font.family"] = "NanumGothic"
                plt.rcParams['axes.unicode_minus'] = False
                display(Markdown("**💻 실행 환경**: 로컬\n✅ 한글 폰트가 성공적으로 설정되었습니다."))
            except Exception as e:
                display(Markdown(f"**❌ 오류 발생**: {str(e)}\n폰트 설정에 실패했습니다."))
    except Exception as e:
        display(Markdown(f"**❌ 오류 발생**: {str(e)}\n폰트 설정에 실패했습니다."))   
        print("🔄 폰트 관련 오류 발생 - 재설치를 시도합니다...")
        
        if _in_colab():
            _colab_font_reinstall()
        else:
            print("💻 로컬 환경에서는 폰트 파일을 다시 다운로드하세요.")
            print("helper.font_download()를 다시 실행해보세요.")

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
        if is_colab:
            full_path = f"/content/drive/MyDrive/{filepath_or_buffer}"
            print(f"🔍 Colab 환경 - 파일 경로: {full_path}")
        else:
            full_path = filepath_or_buffer
            print(f"🔍 로컬 환경 - 파일 경로: {full_path}")
        
        try:
            if not os.path.exists(full_path):
                print(f"❌ 파일을 찾을 수 없습니다: {full_path}")
                if is_colab:
                    print("💡 Google Drive가 마운트되지 않았거나 파일 경로를 확인하세요.")
                else:
                    print("💡 현재 디렉토리 기준으로 파일 경로를 확인하세요.")
                return None
            
            df = pd.read_csv(full_path, **kwargs)
            file_size = os.path.getsize(full_path)
            print(f"✅ 파일 읽기 성공: {full_path}")
            print(f"📊 데이터 크기: {df.shape[0]}행 × {df.shape[1]}열 ({file_size:,} bytes)")
            return df
            
        except Exception as e:
            print(f"❌ 파일 읽기 실패: {str(e)}")
            return None
    else:
        # 문자열이 아니거나 URL인 경우 (파일 객체, URL 등) 그대로 전달
        try:
            if isinstance(filepath_or_buffer, str):
                print(f"🔍 URL로 직접 읽기: {filepath_or_buffer}")
            else:
                print(f"🔍 파일 객체 등으로 직접 읽기: {type(filepath_or_buffer)}")
            df = pd.read_csv(filepath_or_buffer, **kwargs)
            print(f"✅ 파일 읽기 성공")
            print(f"📊 데이터 크기: {df.shape[0]}행 × {df.shape[1]}열")
            return df
            
        except Exception as e:
            print(f"❌ 파일 읽기 실패: {str(e)}")
            return None

def dir_start(object, cmd):
    """라이브러리 도움말을 검색합니다."""
    for c in [att for att in dir(object) if att.startswith(cmd)]:
        print(f"{c}")

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
    
    print("✅ pandas 확장 기능이 성공적으로 설정되었습니다.")

def setup():
    """한번에 모든 설정 완료"""
    print("🚀 Jupyter/Colab 한글 환경 설정을 시작합니다...")
    
    try:
        font_download()
        load_font()
        set_pandas_extension()
        
        print("🎉 모든 설정이 완료되었습니다!")
        print("✅ 사용 가능한 기능:")
        print("   - 한글 폰트 지원")
        print("   - helper.pd_read_csv(): 파일 읽기")
        print("   - DataFrame.head_att(): 한글 컬럼 설명")
        
    except Exception as e:
        print(f"❌ 설정 중 오류: {str(e)}")

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
        available_keys = list(self.attrs["column_descriptions"].keys())
        raise KeyError(f"컬럼 '{key}'에 대한 설명이 없습니다. 사용 가능한 컬럼: {available_keys}")
    
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
            print(f"✅ 컬럼 설명 '{k}' 삭제 완료")
        else:
            print(f"❌ '{k}' 컬럼 설명을 찾을 수 없습니다.")

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
            max_data_width = max(_get_text_width(str(val)) for val in df_display[col])
        
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
    
    # 출력 방식 결정 (기본값: print)
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
            row_parts.append(_align_text(str(val), width, 'right'))
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
                data_row += _align_text(text, column_widths[i] - _get_text_width(str(val)))
                data_row += str(val)
            else:
                data_row += _align_text(str(val), column_widths[i])
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
        data_widths = [_get_text_width(str(val)) for val in series_display]
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
            data_row = _align_text(str(idx), index_column_width) + _align_text(str(val), data_column_width)
            print(data_row)
        
        return None
    
    elif out.lower() == 'html':
        df = series_display.to_frame()
        
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
        data_widths = [_get_text_width(str(val)) for val in series_display]
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
            data_row = _align_text(str(idx), index_column_width) + _align_text(str(val), data_column_width)
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
    
    print(f"✅ 컬럼 세트 '{columns_name}' 설정 완료")
    print(f"📊 {len(columns_extra)}개 컬럼 매핑됨")

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
        print(f"✅ 컬럼 세트 '{columns_name}'에 '{column_key}' → '{column_value}' 추가")
    else:
        print(f"✅ 컬럼 세트 '{columns_name}'에서 '{column_key}': '{old_value}' → '{column_value}' 수정")
    
    total_mappings = len(self.attrs['columns_extra'][columns_name]['columns'])
    print(f"📊 현재 '{columns_name}' 세트 총 매핑 수: {total_mappings}개")

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
    
    print(f"✅ 컬럼명 변경: '{current_set}' → '{columns_name}'")
    print(f"📋 현재 컬럼: {list(self.columns)}")

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
        print("📋 등록된 컬럼 세트가 없습니다.")
        return
    
    current_set = self.get_current_column_set()
    max_name_length = max(len(name) for name in self.attrs['columns_extra'].keys())
    
    print("📋 등록된 컬럼 세트:")
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
        print("✅ 컬럼명을 원본으로 복원했습니다.")
    
    # org 제외하고 모든 컬럼 세트 초기화
    org_backup = self.attrs['columns_extra'].get('org', {})
    self.attrs['columns_extra'] = {'org': org_backup}
    print("🧹 모든 컬럼 세트를 초기화했습니다.")

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
            print("❌ 'org' 세트는 삭제할 수 없습니다.")
            continue
        if name == current_set:
            print(f"❌ 현재 활성화된 '{name}' 세트는 삭제할 수 없습니다.")
            print("💡 먼저 다른 세트로 변경하거나 원본으로 복원하세요.")
            continue
        if name in self.attrs['columns_extra']:
            del self.attrs['columns_extra'][name]
            print(f"✅ 컬럼 세트 '{name}' 삭제 완료")
        else:
            print(f"❌ '{name}' 컬럼 세트를 찾을 수 없습니다.")