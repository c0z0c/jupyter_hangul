"""
Jupyter/Colab 한글 폰트 및 pandas 확장 모듈

🚀 기본 사용법:
    import helper.c0z0c.dev as helper
    helper.setup()  # 한번에 모든 설정 완료

🔧 개별 실행:
    helper.font_download()      # 폰트 다운로드
    helper.load_font()          # 폰트 로딩
    helper.set_pandas_extension()  # pandas 확장 기능

🆘 문제 해결:
    helper.reset_colab_fonts()  # Colab 폰트 완전 리셋
    helper.check_font_status()  # 폰트 상태 확인

📁 파일 읽기:
    df = helper.pd_read_csv("파일명.csv")  # Colab/로컬 자동 감지

🔍 유틸리티:
    helper.dir_start(객체, "접두사")  # 메서드 검색
    df.head_att()  # 한글 컬럼 설명 출력

💡 Colab 사용 시 주의사항:
    - 세션 재시작 후 Google Drive 인증 오류 발생 시 helper.reset_colab_fonts() 실행
    - 문제가 지속되면 런타임 재시작 후 helper.setup() 다시 실행

작성자: 김명환
날짜: 2025.07.12
버전: 2.1 (Google Drive 인증 오류 해결 + 폰트 리셋 기능 추가)
"""

# step1 폰트 다운로드
# colab 에서는 폰트 다운로드 이후 프로세서 재시작 됩니다.
# jupyter는 폰트 다운로드만 진행 됩니다.
font_path = ""
def font_download():
    global font_path
    import os
    import urllib.request
    def in_colab():
        try:
            import google.colab
            return True
        except ImportError:
            return False
    if in_colab():
        if os.system("dpkg -l | grep fonts-nanum") == 0:
            print("fonts-nanum이 이미 설치되어 있습니다.")
            return
        print("📥 install fonts-nanum")
        import subprocess
        subprocess.run(['sudo', 'apt-get', 'install', '-y', 'fonts-nanum'], 
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("📥 프로세서가 종료 됩니다. 장시후 힌번 더 시도 하세요")
        subprocess.run(['sudo', 'fc-cache', '-fv'], 
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(['rm', '-rf', os.path.expanduser('~/.cache/matplotlib')], 
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        os.kill(os.getpid(), 9)
    else:
        # 1. 다운로드 경로 설정
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
# font_download()

# step2 폰트 로딩 matplotlib.pyplot
import matplotlib.pyplot as plt

is_colab = False


def load_font():
    global font_path
    global is_colab
    import os
    import matplotlib.font_manager as fm
    from IPython.display import display, Markdown

    def in_colab():
        try:
            import google.colab

            return True
        except ImportError:
            return False

    # matplotlib 라이브 러리 자동 로딩
    try:
        if in_colab():
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
                print("📍 Google Drive 없이 계속 진행합니다...")
            
            # 폰트 설정
            plt.rc("font", family="NanumBarunGothic")
            md = """
**💻 실행 환경**: Colab
✅ 한글 폰트가 성공적으로 설정되었습니다.
"""
            display(Markdown(md))
        else:
            is_colab = False
            if plt.rcParams["font.family"] == "NanumGothic":
                print("✔️ 한글 폰트가 설치 되어 있습니다.\n추가 작업을 하지 않습니다.")
                return

            try:
                fm.fontManager.addfont(font_path)
                plt.rcParams["font.family"] = "NanumGothic"
                md = """
**💻 실행 환경**: 로컬
✅ 한글 폰트가 성공적으로 설정되었습니다.
    - import matplotlib.pyplot as plt 되어 있습니다. (한글 폰트 적용됨)
"""
                display(Markdown(md))
            except Exception as e:
                md = f"""
**❌ 오류 발생**: {str(e)}
폰트 설정에 실패했습니다. 폰트 파일이 존재하는지 확인하세요.
font_path={font_path}
    """
                display(Markdown(md))
    except Exception as e:
        md = f"""
**❌ 오류 발생**: {str(e)}
폰트 설정에 실패했습니다. 폰트 파일이 존재하는지 확인하세요.
"""
        display(Markdown(md))   
        # 폰트를 삭제 하고 다시 설치 하자
        print("🔄 폰트 관련 오류 발생 - 재설치를 시도합니다...")
        
        # Colab에서 Google Drive 인증 오류 해결
        def in_colab():
            try:
                import google.colab
                return True
            except ImportError:
                return False
        
        if in_colab():
            print("📋 Colab 환경에서 폰트 재설치를 진행합니다...")
            try:
                import subprocess
                import os
                from IPython.display import display, Markdown
                
                # 1. 기존 폰트 패키지 완전 제거
                print("🗑️  기존 fonts-nanum 패키지 제거 중...")
                subprocess.run(['sudo', 'apt-get', 'remove', '--purge', '-y', 'fonts-nanum'], 
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
                # 2. 폰트 캐시 완전 정리
                print("🧹 폰트 캐시 완전 정리 중...")
                subprocess.run(['sudo', 'fc-cache', '-f', '-v'], 
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                subprocess.run(['rm', '-rf', os.path.expanduser('~/.cache/matplotlib')], 
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                subprocess.run(['rm', '-rf', os.path.expanduser('~/.fontconfig')], 
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
                # 3. 패키지 목록 업데이트
                print("📦 패키지 목록 업데이트 중...")
                subprocess.run(['sudo', 'apt-get', 'update', '-qq'], 
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
                # 4. 폰트 재설치
                print("📥 fonts-nanum 재설치 중...")
                subprocess.run(['sudo', 'apt-get', 'install', '-y', 'fonts-nanum'], 
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
                # 5. 폰트 캐시 재구성
                print("🔧 폰트 캐시 재구성 중...")
                subprocess.run(['sudo', 'fc-cache', '-f', '-v'], 
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
                # 사용자에게 재시도 안내
                restart_guide = """
# 🔄 폰트 재설치 완료

## 📌 다음 단계
폰트 재설치가 완료되었습니다. **프로세서를 재시작**하고 다시 시도하세요.

## 🚀 재시작 방법
1. **메뉴 > 런타임 > 런타임 다시 시작** 클릭
2. 재시작 후 **helper.setup()** 다시 실행

## 💡 참고사항
- Google Drive 인증 오류가 해결되었습니다
- 재시작 후에는 Google Drive 마운트가 다시 필요할 수 있습니다
- 폰트 설정이 정상적으로 작동할 것입니다

## ⚠️ 문제가 지속되면
새로운 노트북을 만들어 다시 시도하세요.
"""
                
                display(Markdown(restart_guide))
                
                print("🔄 3초 후 프로세서를 재시작합니다...")
                print("재시작 후 다시 helper.setup()을 실행하세요!")
                
                # 잠시 대기 후 재시작
                import time
                time.sleep(3)
                os.kill(os.getpid(), 9)
                
            except Exception as reinstall_error:
                print(f"❌ 재설치 중 오류 발생: {str(reinstall_error)}")
                print("🔄 수동으로 런타임을 재시작하고 다시 시도하세요.")
                print("메뉴 > 런타임 > 런타임 다시 시작")
        else:
            print("💻 로컬 환경에서는 폰트 파일을 다시 다운로드하세요.")
            print("helper.font_download()를 다시 실행해보세요.")


# load_font()

#  step3 pandas 주로 사용하는 라이브러리 로딩
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

pd.set_option("display.max_rows", 100)
pd.set_option("display.max_columns", 100)


# by 김명환 25.07.12
# google의 drive와 local 파일을 읽어오는 함수
def pd_read_csv(path):
    """
    Colab/로컬 환경에 맞춰 CSV 파일을 읽어옵니다.
    
    Parameters:
    -----------
    path : str
        읽어올 파일 경로
        예: "data/test.csv"
    
    Returns:
    --------
    pandas.DataFrame : 읽어온 데이터프레임
    
    Examples:
    ---------
    >>> df = helper.pd_read_csv("data/test.csv")
    # Jupyter: ./data/test.csv
    # Colab: /content/drive/MyDrive/data/test.csv
    """
    import os
    
    if is_colab:
        # Colab 환경: Google Drive 경로 사용
        full_path = f"/content/drive/MyDrive/{path}"
        print(f"🔍 Colab 환경 - 파일 경로: {full_path}")
    else:
        # Jupyter 로컬 환경: 현재 디렉토리 기준
        full_path = path
        print(f"🔍 로컬 환경 - 파일 경로: {full_path}")
    
    try:
        # 파일 존재 여부 확인
        if not os.path.exists(full_path):
            print(f"❌ 파일을 찾을 수 없습니다: {full_path}")
            if is_colab:
                print("💡 Google Drive가 마운트되지 않았거나 파일 경로를 확인하세요.")
                print("   Google Drive 경로: /content/drive/MyDrive/")
            else:
                print("💡 현재 디렉토리 기준으로 파일 경로를 확인하세요.")
            return None
        
        # CSV 파일 읽기
        df = pd.read_csv(full_path)
        file_size = os.path.getsize(full_path)
        print(f"✅ 파일 읽기 성공: {full_path}")
        print(f"� 데이터 크기: {df.shape[0]}행 × {df.shape[1]}열 ({file_size:,} bytes)")
        
        return df
        
    except Exception as e:
        print(f"❌ 파일 읽기 실패: {str(e)}")
        print(f"🔍 확인할 경로: {full_path}")
        return None


# by 김명환 25.07.12
# 라이브러리 도움말을 검색 하기 위하여 추가
def dir_start(object, cmd):
    for c in [att for att in dir(object) if att.startswith(cmd)]:
        print(f"{c}")

# by 김명환 25.07.12
# DataFrame / Series 출력시 한글 컬럼 설명 기능 추가

def set_pandas_extension():
    # """
    # pandas DataFrame/Series에 한글 컬럼 설명 기능을 추가합니다.
    # """
    # print("📊 pandas 확장 기능을 설정합니다...")
    
    # pandas 옵션 설정
    pd.set_option("display.max_rows", 100)
    pd.set_option("display.max_columns", 100)
    
    # 속도 얼마 안걸린다 무조거 다시 읽자
    # # 이미 설정되어 있는지 확인
    # if hasattr(pd.DataFrame, 'head_att'):
    #     print("📊 pandas 확장 기능이 이미 설정되어 있습니다.")
    #     return
    
    # 메서드들을 pandas DataFrame/Series에 추가
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
    
    print("✅ pandas 확장 기능이 성공적으로 설정되었습니다.")

def setup():
    """
    한번에 모든 설정을 완료합니다.
    - 폰트 다운로드
    - 폰트 로딩
    - pandas 확장 기능 설정
    """
    print("🚀 Jupyter/Colab 한글 환경 설정을 시작합니다...")
    
    try:
        # 1. 폰트 다운로드
        font_download()
        
        # 2. 폰트 로딩
        load_font()
        
        # 3. pandas 확장 기능 설정
        set_pandas_extension()
        
        print("🎉 모든 설정이 완료되었습니다!")
        print("사용 가능한 기능:")
        print("- 한글 폰트 지원 (matplotlib)")
        print("- helper.pd_read_csv(): Colab/로컬 파일 읽기")
        print("- helper.dir_start(): 라이브러리 도움말 검색")
        print("- DataFrame.head_att(): 한글 컬럼 설명")
        
    except Exception as e:
        print(f"❌ 설정 중 오류가 발생했습니다: {str(e)}")

# by 김명환 25.07.12
# DataFrame / Series 출력시 한글 컬럼 설명 기능 추가

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
    """
    모든 컬럼 설명을 초기화합니다.
    
    Examples:
    ---------
    >>> df.clear_head_att()
    """
    if not hasattr(self, 'attrs'):
        self.attrs = {}
    self.attrs["column_descriptions"] = {}

# DataFrame과 Series에 메서드 추가
setattr(pd.DataFrame, "set_head_att", set_head_att)
setattr(pd.Series, "set_head_att", set_head_att)
setattr(pd.DataFrame, "get_head_att", get_head_att)
setattr(pd.Series, "get_head_att", get_head_att)
setattr(pd.DataFrame, "remove_head_att", remove_head_att)
setattr(pd.Series, "remove_head_att", remove_head_att)
setattr(pd.DataFrame, "clear_head_att", clear_head_att)
setattr(pd.Series, "clear_head_att", clear_head_att)

def pd_head_att(self, rows=5, out=None):
    """
    한글 컬럼 설명이 포함된 DataFrame을 다양한 형태로 출력합니다.
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
        def get_display_width(text):
            if text is None:
                return 0
            width = 0
            for char in str(text):
                if ord(char) > 127:
                    width += 2
                else:
                    width += 1
            return width
        
        def pad_text(text, width):
            text_str = str(text)
            text_width = get_display_width(text_str)
            padding = width - text_width
            return ' ' * padding + text_str
        
        # 컬럼 정보 준비
        columns_info = []
        for col in df_display.columns:
            korean_name = labels.get(col, col)
            english_name = col
            
            data_widths = []
            for val in df_display[col]:
                data_widths.append(get_display_width(str(val)))
            max_data_width = max(data_widths) if data_widths else 0
            
            index_width = max(get_display_width(str(idx)) for idx in df_display.index) if not df_display.empty else 0
            
            max_width = max(
                get_display_width(korean_name),
                get_display_width(english_name),
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
            korean_parts.append(pad_text(info['korean'], info['width']))
        print(''.join(korean_parts))
        
        # 영문 헤더 출력
        english_parts = []
        for info in columns_info:
            english_parts.append(pad_text(info['english'], info['width']))
        print(''.join(english_parts))
        
        # 데이터 출력
        for idx, row in df_display.iterrows():
            row_parts = []
            first_val = str(row.iloc[0])
            first_text = str(idx) + first_val
            row_parts.append(pad_text(first_text, columns_info[0]['width']))
            
            for i, val in enumerate(row.iloc[1:], 1):
                row_parts.append(pad_text(str(val), columns_info[i]['width']))
            
            print(''.join(row_parts))
        
        return None
    
    elif out.lower() == 'html':
        header = []
        for col in df_display.columns:
            if col in labels and labels[col]:
                header.append(f"{col}<br><small>({labels[col]})</small>")
            else:
                header.append(col)
        
        df_copy = df_display.copy()
        df_copy.columns = header
        
        from IPython.display import HTML
        return HTML(df_copy.to_html(escape=False))
    
    elif out.lower() in ['str', 'string']:
        def get_char_width(char):
            return 2 if ord(char) >= 0x1100 else 1
        
        def get_text_width(text):
            return sum(get_char_width(char) for char in str(text))
        
        def align_text(text, width):
            text_str = str(text)
            current_width = get_text_width(text_str)
            padding = max(0, width - current_width)
            return ' ' * padding + text_str
        
        column_widths = []
        
        for i, col in enumerate(df_display.columns):
            korean_name = labels.get(col, col)
            english_name = col
            
            max_data_width = max(get_text_width(str(val)) for val in df_display[col])
            
            if i == 0:
                max_index_width = max(get_text_width(str(idx)) for idx in df_display.index)
                max_data_width = max(max_data_width, max_index_width)
            
            max_width = max(
                get_text_width(korean_name),
                get_text_width(english_name),
                max_data_width
            )
            
            column_widths.append(max_width + 2)
        
        result = ""
        
        # 한글 헤더 생성
        korean_row = ""
        for i, col in enumerate(df_display.columns):
            korean_name = labels.get(col, col)
            korean_row += align_text(korean_name, column_widths[i])
        result += korean_row + "\n"
        
        # 영문 헤더 생성
        english_row = ""
        for i, col in enumerate(df_display.columns):
            english_row += align_text(col, column_widths[i])
        result += english_row + "\n"
        
        # 데이터 생성
        for idx, row in df_display.iterrows():
            data_row = ""
            for i, val in enumerate(row):
                if i == 0:
                    text = str(idx)
                    data_row += align_text(text, column_widths[i] - get_text_width(str(val)))
                    data_row += str(val)
                else:
                    data_row += align_text(str(val), column_widths[i])
            result += data_row + "\n"
        
        return result.rstrip()
    
    else:
        raise ValueError("out 옵션은 'html', 'print', 'str', 'string' 중 하나여야 합니다.")

def series_head_att(self, rows=5, out=None):
    """
    한글 컬럼 설명이 포함된 Series를 다양한 형태로 출력합니다.
    
    Parameters:
    -----------
    rows : int or str, default 5
        - int: 출력할 행 수
        - "all" or -1: 모든 행 출력
        - 0: 헤더만 출력
    out : str, optional
        - None or 'print': print 문으로 출력 (기본값)
        - 'html': HTML 형식으로 출력
        - 'str' or 'string': 문자열로 반환
        
    Returns:
    --------
    IPython.display.HTML or str or None : 출력 방식에 따라 다름
    """
    
    labels = self.attrs.get("column_descriptions", {})
    
    # 출력할 데이터 결정
    if isinstance(rows, str) and rows.lower() == "all":
        series_display = self
    elif isinstance(rows, int):
        if rows == -1:
            series_display = self
        elif rows == 0:
            series_display = self.iloc[0:0]  # 헤더만
        else:
            series_display = self.head(rows)
    else:
        series_display = self.head(5)
    
    # Series 이름 (컬럼명)
    series_name = self.name if self.name is not None else "Series"
    korean_name = labels.get(series_name, series_name)
    
    # 출력 방식 결정 (기본값: print)
    if out is None or out.lower() == 'print':
        def get_display_width(text):
            if text is None:
                return 0
            width = 0
            for char in str(text):
                if ord(char) > 127:
                    width += 2
                else:
                    width += 1
            return width
        
        def pad_text(text, width):
            text_str = str(text)
            text_width = get_display_width(text_str)
            padding = width - text_width
            return ' ' * padding + text_str
        
        # 인덱스 최대 폭 계산
        index_widths = [get_display_width(str(idx)) for idx in series_display.index]
        max_index_width = max(index_widths) if index_widths else 0
        
        # 데이터 최대 폭 계산
        data_widths = [get_display_width(str(val)) for val in series_display]
        max_data_width = max(data_widths) if data_widths else 0
        
        # 헤더 폭 계산
        korean_header_width = get_display_width(korean_name)
        english_header_width = get_display_width(series_name)
        
        # 각 컬럼의 최대 폭 결정
        index_column_width = max(max_index_width, 5) + 2  # 'index' 최소 폭
        data_column_width = max(max_data_width, korean_header_width, english_header_width) + 2
        
        # 한글 헤더 출력
        korean_header = pad_text("인덱스", index_column_width) + pad_text(korean_name, data_column_width)
        print(korean_header)
        
        # 영문 헤더 출력
        english_header = pad_text("index", index_column_width) + pad_text(series_name, data_column_width)
        print(english_header)
        
        # 데이터 출력
        for idx, val in series_display.items():
            data_row = pad_text(str(idx), index_column_width) + pad_text(str(val), data_column_width)
            print(data_row)
        
        return None
    
    elif out.lower() == 'html':
        # Series를 DataFrame으로 변환하여 HTML 출력
        df = series_display.to_frame()
        
        # 컬럼명 설정
        if series_name in labels and labels[series_name]:
            df.columns = [f"{series_name}<br><small>({labels[series_name]})</small>"]
        else:
            df.columns = [series_name]
        
        from IPython.display import HTML
        return HTML(df.to_html(escape=False))
    
    elif out.lower() in ['str', 'string']:
        def get_char_width(char):
            return 2 if ord(char) >= 0x1100 else 1
        
        def get_text_width(text):
            return sum(get_char_width(char) for char in str(text))
        
        def align_text(text, width):
            text_str = str(text)
            current_width = get_text_width(text_str)
            padding = max(0, width - current_width)
            return ' ' * padding + text_str
        
        # 인덱스 최대 폭 계산
        index_widths = [get_text_width(str(idx)) for idx in series_display.index]
        max_index_width = max(index_widths) if index_widths else 0
        
        # 데이터 최대 폭 계산
        data_widths = [get_text_width(str(val)) for val in series_display]
        max_data_width = max(data_widths) if data_widths else 0
        
        # 헤더 폭 계산
        korean_header_width = get_text_width(korean_name)
        english_header_width = get_text_width(series_name)
        
        # 각 컬럼의 최대 폭 결정
        index_column_width = max(max_index_width, get_text_width("인덱스"), get_text_width("index")) + 2
        data_column_width = max(max_data_width, korean_header_width, english_header_width) + 2
        
        result = ""
        
        # 한글 헤더 생성
        korean_header = align_text("인덱스", index_column_width) + align_text(korean_name, data_column_width)
        result += korean_header + "\n"
        
        # 영문 헤더 생성
        english_header = align_text("index", index_column_width) + align_text(series_name, data_column_width)
        result += english_header + "\n"
        
        # 데이터 생성
        for idx, val in series_display.items():
            data_row = align_text(str(idx), index_column_width) + align_text(str(val), data_column_width)
            result += data_row + "\n"
        
        return result.rstrip()
    
    else:
        raise ValueError("out 옵션은 'html', 'print', 'str', 'string' 중 하나여야 합니다.")