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
    df = helper.pd_read_csv("파일명.csv")  # Colab/로컬 자동 감지

🔍 유틸리티:
    helper.dir_start(객체, "접두사")  # 메서드 검색
    df.head_att()  # 한글 컬럼 설명 출력

💡 Colab 사용 시 주의사항:
    - 세션 재시작 후 Google Drive 인증 오류 발생 시 런타임 재시작 필요
    - 문제가 지속되면 런타임 재시작 후 helper.setup() 다시 실행

작성자: 김명환
날짜: 2025.07.12
버전: 2.1
"""

import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# 전역 변수
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

def _get_display_width(text):
    """텍스트의 화면 표시 폭 계산 (한글 2칸, 영문 1칸)"""
    if text is None:
        return 0
    width = 0
    for char in str(text):
        if ord(char) > 127:
            width += 2
        else:
            width += 1
    return width

def _get_char_width(char):
    """문자 하나의 폭 계산 (한글 2칸, 영문 1칸)"""
    return 2 if ord(char) >= 0x1100 else 1

def _get_text_width(text):
    """텍스트 전체 폭 계산"""
    return sum(_get_char_width(char) for char in str(text))

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
            display(Markdown("**💻 실행 환경**: Colab\n✅ 한글 폰트가 성공적으로 설정되었습니다."))
        else:
            is_colab = False
            if plt.rcParams["font.family"] == "NanumGothic":
                print("✔️ 한글 폰트가 설치 되어 있습니다.\n추가 작업을 하지 않습니다.")
                return

            try:
                fm.fontManager.addfont(font_path)
                plt.rcParams["font.family"] = "NanumGothic"
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
pd.set_option("display.max_rows", 100)
pd.set_option("display.max_columns", 100)

def pd_read_csv(path):
    """
    Colab/로컬 환경에 맞춰 CSV 파일을 읽어옵니다.
    
    Parameters:
    -----------
    path : str
        읽어올 파일 경로 (예: "data/test.csv")
    
    Returns:
    --------
    pandas.DataFrame : 읽어온 데이터프레임
    """
    if is_colab:
        full_path = f"/content/drive/MyDrive/{path}"
        print(f"🔍 Colab 환경 - 파일 경로: {full_path}")
    else:
        full_path = path
        print(f"🔍 로컬 환경 - 파일 경로: {full_path}")
    
    try:
        if not os.path.exists(full_path):
            print(f"❌ 파일을 찾을 수 없습니다: {full_path}")
            if is_colab:
                print("💡 Google Drive가 마운트되지 않았거나 파일 경로를 확인하세요.")
            else:
                print("💡 현재 디렉토리 기준으로 파일 경로를 확인하세요.")
            return None
        
        df = pd.read_csv(full_path)
        file_size = os.path.getsize(full_path)
        print(f"✅ 파일 읽기 성공: {full_path}")
        print(f"📊 데이터 크기: {df.shape[0]}행 × {df.shape[1]}열 ({file_size:,} bytes)")
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
    setattr(pd.DataFrame, "set_head_att", set_head_att)
    setattr(pd.Series, "set_head_att", set_head_att)
    setattr(pd.DataFrame, "get_head_att", get_head_att)
    setattr(pd.Series, "get_head_att", get_head_att)
    setattr(pd.DataFrame, "remove_head_att", remove_head_att)
    setattr(pd.Series, "remove_head_att", remove_head_att)
    setattr(pd.DataFrame, "clear_head_att", clear_head_att)
    setattr(pd.Series, "clear_head_att", clear_head_att)
    setattr(pd.DataFrame, "head_att", pd_head_att)
    setattr(pd.Series, "head_att", series_head_att)
    setattr(pd.DataFrame, "set_head_ext", set_head_ext)
    setattr(pd.Series, "set_head_ext", set_head_ext)
    setattr(pd.DataFrame, "set_head_column", set_head_column)
    setattr(pd.Series, "set_head_column", set_head_column)
    setattr(pd.DataFrame, "get_current_column_set", get_current_column_set)
    setattr(pd.Series, "get_current_column_set", get_current_column_set)
    setattr(pd.DataFrame, "get_head_ext", get_head_ext)
    setattr(pd.Series, "get_head_ext", get_head_ext)
    setattr(pd.DataFrame, "list_head_ext", list_head_ext)
    setattr(pd.Series, "list_head_ext", list_head_ext)
    setattr(pd.DataFrame, "reset_head_column", reset_head_column)
    setattr(pd.Series, "reset_head_column", reset_head_column)
    setattr(pd.DataFrame, "remove_head_ext", remove_head_ext)
    setattr(pd.Series, "remove_head_ext", remove_head_ext)
    print("✅ pandas 확장 기능이 성공적으로 설정되었습니다.")

def setup():
    """한번에 모든 설정을 완료합니다."""
    print("🚀 Jupyter/Colab 한글 환경 설정을 시작합니다...")
    
    try:
        font_download()
        load_font()
        set_pandas_extension()
        
        print("🎉 모든 설정이 완료되었습니다!")
        print("사용 가능한 기능:")
        print("- 한글 폰트 지원 (matplotlib)")
        print("- helper.pd_read_csv(): Colab/로컬 파일 읽기")
        print("- helper.dir_start(): 라이브러리 도움말 검색")
        print("- DataFrame.head_att(): 한글 컬럼 설명")
        
    except Exception as e:
        print(f"❌ 설정 중 오류가 발생했습니다: {str(e)}")

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

def get_head_att(self):
    """
    컬럼 설명을 반환합니다.
    
    Returns:
    --------
    dict : 컬럼 설명 딕셔너리 (직접 수정 가능)
    
    Examples:
    ---------
    >>> descriptions = df.get_head_att()
    >>> descriptions['new_col'] = '새로운 설명'
    """
    if not hasattr(self, 'attrs'):
        self.attrs = {}
    if 'column_descriptions' not in self.attrs:
        self.attrs["column_descriptions"] = {}
    return self.attrs["column_descriptions"]

def remove_head_att(self, key):
    """
    특정 컬럼 설명을 삭제합니다.
    
    Parameters:
    -----------
    key : str
        삭제할 컬럼명
        
    Examples:
    ---------
    >>> df.remove_head_att("id")
    """
    if hasattr(self, 'attrs') and 'column_descriptions' in self.attrs:
        self.attrs["column_descriptions"].pop(key, None)

def clear_head_att(self):
    """모든 컬럼 설명을 초기화합니다."""
    if not hasattr(self, 'attrs'):
        self.attrs = {}
    self.attrs["column_descriptions"] = {}

def _pad_text(text, width):
    """텍스트를 지정된 폭에 맞춰 패딩합니다."""
    text_str = str(text)
    text_width = _get_display_width(text_str)
    padding = width - text_width
    return ' ' * padding + text_str

def _align_text(text, width):
    """텍스트를 지정된 폭에 맞춰 정렬합니다."""
    text_str = str(text)
    current_width = _get_text_width(text_str)
    padding = max(0, width - current_width)
    return ' ' * padding + text_str

def pd_head_att(self, rows=5, out=None):
    """한글 컬럼 설명이 포함된 DataFrame을 다양한 형태로 출력합니다."""
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
        # 컬럼 정보 준비
        columns_info = []
        for col in df_display.columns:
            korean_name = labels.get(col, col)
            english_name = col
            
            data_widths = []
            for val in df_display[col]:
                data_widths.append(_get_display_width(str(val)))
            max_data_width = max(data_widths) if data_widths else 0
            
            index_width = max(_get_display_width(str(idx)) for idx in df_display.index) if not df_display.empty else 0
            
            max_width = max(
                _get_display_width(korean_name),
                _get_display_width(english_name),
                max_data_width,
                index_width
            )
            
            columns_info.append({
                'korean': korean_name,
                'english': english_name,
                'width': max_width + 2
            })
        
        # 한글 헤더 출력
        korean_parts = []
        for info in columns_info:
            korean_parts.append(_pad_text(info['korean'], info['width']))
        print(''.join(korean_parts))
        
        # 영문 헤더 출력
        english_parts = []
        for info in columns_info:
            english_parts.append(_pad_text(info['english'], info['width']))
        print(''.join(english_parts))
        
        # 데이터 출력
        for idx, row in df_display.iterrows():
            row_parts = []
            first_val = str(row.iloc[0])
            first_text = str(idx) + first_val
            row_parts.append(_pad_text(first_text, columns_info[0]['width']))
            
            for i, val in enumerate(row.iloc[1:], 1):
                row_parts.append(_pad_text(str(val), columns_info[i]['width']))
            
            print(''.join(row_parts))
        
        return None
    
    elif out.lower() == 'html':
        header = []
        for col in df_display.columns:
            if col in labels and labels[col]:
                header.append(f"{labels[col]}<br><small>{col}</small>")
            else:
                header.append(col)
        
        df_copy = df_display.copy()
        df_copy.columns = header
        
        from IPython.display import HTML
        return HTML(df_copy.to_html(escape=False))
    
    elif out.lower() in ['str', 'string']:
        column_widths = []
        
        for i, col in enumerate(df_display.columns):
            korean_name = labels.get(col, col)
            english_name = col
            
            max_data_width = max(_get_text_width(str(val)) for val in df_display[col])
            
            if i == 0:
                max_index_width = max(_get_text_width(str(idx)) for idx in df_display.index)
                max_data_width = max(max_data_width, max_index_width)
            
            max_width = max(
                _get_text_width(korean_name),
                _get_text_width(english_name),
                max_data_width
            )
            
            column_widths.append(max_width + 2)
        
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
    
    else:
        raise ValueError("out 옵션은 'html', 'print', 'str', 'string' 중 하나여야 합니다.")

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
        index_widths = [_get_display_width(str(idx)) for idx in series_display.index]
        max_index_width = max(index_widths) if index_widths else 0
        
        # 데이터 최대 폭 계산
        data_widths = [_get_display_width(str(val)) for val in series_display]
        max_data_width = max(data_widths) if data_widths else 0
        
        # 헤더 폭 계산
        korean_header_width = _get_display_width(korean_name)
        english_header_width = _get_display_width(series_name)
        
        # 각 컬럼의 최대 폭 결정
        index_column_width = max(max_index_width, 5) + 2
        data_column_width = max(max_data_width, korean_header_width, english_header_width) + 2
        
        # 헤더 출력
        korean_header = _pad_text("인덱스", index_column_width) + _pad_text(korean_name, data_column_width)
        print(korean_header)
        
        english_header = _pad_text("index", index_column_width) + _pad_text(series_name, data_column_width)
        print(english_header)
        
        # 데이터 출력
        for idx, val in series_display.items():
            data_row = _pad_text(str(idx), index_column_width) + _pad_text(str(val), data_column_width)
            print(data_row)
        
        return None
    
    elif out.lower() == 'html':
        df = series_display.to_frame()
        
        if series_name in labels and labels[series_name]:
            df.columns = [f"{labels[series_name]}<br><small>{series_name}</small>"]
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

# 확장 컬럼 시스템 함수들
def set_head_ext(self, columns_name, columns_extra):
    """
    보조 컬럼명 세트를 설정합니다.
    
    Parameters:
    -----------
    columns_name : str
        컬럼 세트의 이름 (예: 'kr', 'desc', 'eng')
    columns_extra : dict
        컬럼 매핑 딕셔너리 {"원본컬럼": "새컬럼명"}
    
    Examples:
    ---------
    >>> df.set_head_ext('kr', {'id': 'ID', 'name': '이름'})
    >>> df.set_head_ext('desc', {'id': '식별자', 'name': '성명'})
    """
    # attrs 초기화
    if not hasattr(self, 'attrs'):
        self.attrs = {}
    if 'columns_extra' not in self.attrs:
        self.attrs['columns_extra'] = {}
        # 원본 컬럼 저장 (처음 한 번만)
        self.attrs['columns_extra']['org'] = {
            'name': 'org',
            'columns': {col: col for col in self.columns}
        }
        # 현재 활성화된 컬럼 세트 추적
        self.attrs['current_column_set'] = 'org'
    
    # 새로운 컬럼 세트 추가
    self.attrs['columns_extra'][columns_name] = {
        'name': columns_name,
        'columns': columns_extra.copy()
    }
    
    print(f"✅ 컬럼 세트 '{columns_name}' 설정 완료")
    
    # 원본과 새 컬럼을 나란히 표시
    org_columns = list(columns_extra.keys())
    new_columns = list(columns_extra.values())
    
    print("📋 컬럼 매핑:")
    print(f"    org: {org_columns}")
    print(f" {columns_name:>6}: {new_columns}")
    print(f"📊 총 {len(columns_extra)}개 컬럼 매핑됨")

def set_head_column(self, columns_name):
    """
    지정된 컬럼 세트로 DataFrame의 컬럼명을 변경합니다.
    원본 컬럼명을 기준으로 매칭합니다.
    
    Parameters:
    -----------
    columns_name : str
        사용할 컬럼 세트 이름 (예: 'kr', 'desc', 'org')
    
    Examples:
    ---------
    >>> df.set_head_column('kr')   # 한글 컬럼명으로 변경
    >>> df.set_head_column('org')  # 원본 컬럼명으로 복원
    """
    if not hasattr(self, 'attrs'):
        self.attrs = {}
    if 'columns_extra' not in self.attrs:
        print("❌ 등록된 컬럼 세트가 없습니다.")
        print("💡 먼저 set_head_ext()로 컬럼 세트를 등록하세요.")
        return
    
    if columns_name not in self.attrs['columns_extra']:
        available = list(self.attrs['columns_extra'].keys())
        print(f"❌ '{columns_name}' 컬럼 세트를 찾을 수 없습니다.")
        print(f"💡 사용 가능한 세트: {available}")
        return
    
    # 원본 컬럼 정보 가져오기
    org_columns = self.attrs['columns_extra']['org']['columns']
    target_columns = self.attrs['columns_extra'][columns_name]['columns']
    
    # 현재 컬럼 세트 정보 가져오기
    current_set = self.attrs.get('current_column_set', 'org')
    current_columns = self.attrs['columns_extra'][current_set]['columns']
    
    # 현재 컬럼 → 원본 컬럼 매핑 (역방향 매핑)
    current_to_org = {v: k for k, v in current_columns.items()}
    
    # 새로운 컬럼명 리스트 생성
    new_columns = []
    for current_col in self.columns:
        # 1. 현재 컬럼 → 원본 컬럼 변환
        if current_col in current_to_org:
            org_col = current_to_org[current_col]
        else:
            org_col = current_col  # 매핑되지 않은 컬럼은 원본으로 가정
        
        # 2. 원본 컬럼 → 타겟 컬럼 변환
        if org_col in target_columns:
            new_columns.append(target_columns[org_col])
        else:
            new_columns.append(org_col)  # 매핑되지 않은 컬럼은 원본 유지
    
    # _head_att (column_descriptions) 업데이트
    if 'column_descriptions' in self.attrs:
        old_descriptions = self.attrs['column_descriptions'].copy()
        new_descriptions = {}
        
        for old_col, new_col in zip(self.columns, new_columns):
            # 현재 컬럼 → 원본 컬럼 변환 (이미 계산됨)
            if old_col in current_to_org:
                org_col = current_to_org[old_col]
            else:
                org_col = old_col
            
            # 원본 컬럼을 키로 하는 설명이 있다면 새 컬럼을 키로 매핑
            if org_col in old_descriptions:
                new_descriptions[new_col] = old_descriptions[org_col]
            elif old_col in old_descriptions:
                new_descriptions[new_col] = old_descriptions[old_col]
        
        self.attrs['column_descriptions'] = new_descriptions
    
    # 컬럼명 변경
    self.columns = new_columns
    
    # 현재 활성화된 컬럼 세트 업데이트
    self.attrs['current_column_set'] = columns_name
    
    print(f"✅ 컬럼명을 '{current_set}' → '{columns_name}' 세트로 변경했습니다.")
    
    # head_att 설명도 함께 업데이트되었음을 알림
    if 'column_descriptions' in self.attrs and self.attrs['column_descriptions']:
        print(f"📝 컬럼 설명도 새로운 컬럼명에 맞게 업데이트되었습니다.")
    print(f"📋 현재 컬럼: {list(self.columns)}")

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
    """
    등록된 모든 컬럼 세트를 출력합니다.
    """
    if not hasattr(self, 'attrs'):
        self.attrs = {}
    if 'columns_extra' not in self.attrs:
        print("📋 등록된 컬럼 세트가 없습니다.")
        return
    
    current_set = self.get_current_column_set()
    
    print("📋 등록된 컬럼 세트:")
    
    # 모든 컬럼 세트의 이름 중 가장 긴 이름의 길이 계산 (정렬용)
    max_name_length = max(len(name) for name in self.attrs['columns_extra'].keys())
    
    for name, info in self.attrs['columns_extra'].items():
        columns_list = list(info['columns'].values()) if name != 'org' else list(info['columns'].keys())
        status = " (현재)" if name == current_set else ""
        
        # 이름을 오른쪽 정렬로 출력
        formatted_name = f"{name}{status}".rjust(max_name_length + 5)
        print(f"{formatted_name}: {columns_list}")

def reset_head_column(self):
    """
    컬럼명을 원본으로 복원하고 모든 컬럼 세트를 초기화합니다.
    """
    if not hasattr(self, 'attrs'):
        return
    if 'columns_extra' not in self.attrs:
        return
    
    # 원본 컬럼으로 복원
    if 'org' in self.attrs['columns_extra']:
        org_columns = list(self.attrs['columns_extra']['org']['columns'].keys())
        self.columns = org_columns
        self.attrs['current_column_set'] = 'org'
        print("✅ 컬럼명을 원본으로 복원했습니다.")
    
    # 모든 컬럼 세트 초기화 (org 제외)
    org_backup = self.attrs['columns_extra'].get('org', {})
    self.attrs['columns_extra'] = {'org': org_backup}
    
    print("🧹 모든 컬럼 세트를 초기화했습니다.")

def remove_head_ext(self, columns_name):
    """
    특정 컬럼 세트를 삭제합니다.
    
    Parameters:
    -----------
    columns_name : str
        삭제할 컬럼 세트 이름
    """
    if not hasattr(self, 'attrs'):
        return
    if 'columns_extra' not in self.attrs:
        return
    
    if columns_name == 'org':
        print("❌ 'org' 세트는 삭제할 수 없습니다.")
        return
    
    current_set = self.get_current_column_set()
    if columns_name == current_set:
        print(f"❌ 현재 활성화된 '{columns_name}' 세트는 삭제할 수 없습니다.")
        print("💡 먼저 다른 세트로 변경하거나 원본으로 복원하세요.")
        return
    
    if columns_name in self.attrs['columns_extra']:
        del self.attrs['columns_extra'][columns_name]
        print(f"✅ 컬럼 세트 '{columns_name}' 삭제 완료")
    else:
        print(f"❌ '{columns_name}' 컬럼 세트를 찾을 수 없습니다.")