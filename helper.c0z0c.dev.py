"""
Jupyter/Colab 한글 폰트 및 pandas 확장 모듈

사용법:
    import helper.c0z0c.dev as helper
    helper.setup()  # 폰트 다운로드 + 로딩 + pandas 확장 한번에 설정
    
    # 또는 개별 실행
    helper.font_download()
    helper.load_font()
    helper.set_pandas_extension()

작성자: 김명환
날짜: 2025.07.12
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
    if in_colab():
        from google.colab import drive

        is_colab = True
        drive.mount("/content/drive")
        plt.rc("font", family="NanumBarunGothic")
        md = """
**💻 실행 환경**: Colab
✅ 한글 폰트가 성공적으로 설정되었습니다.
# colab에서 연결된 google drive 경로 입니다.
- /content/drive/MyDrive
- import matplotlib.pyplot as plt 되어 있습니다. (한글 폰트 적용됨)
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


# load_font()

#  step3 pandas 주로 사용하는 라이브러리 로딩
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

pd.set_option("display.max_rows", 100)
pd.set_option("display.max_columns", 100)


# by 김명환 25.07.12
# google의 driver와 local 파일을 읽어오는 함수
def pd_read_csv(path):
    df = None
    if is_colab:
        df = pd.read_csv(f"/content/drive/MyDrive/codeit/online/{path}")
    else:
        df = pd.read_csv(f"{path}")
    return df


# by 김명환 25.07.12
# 라이브러리 도움말을 검색 하기 위하여 추가
def dir_start(object, cmd):
    for c in [att for att in dir(object) if att.startswith(cmd)]:
        print(f"{c}")

# by 김명환 25.07.12
# DataFrame / Series 출력시 한글 컬럼 설명 기능 추가

def set_pandas_extension():
    """
    pandas DataFrame/Series에 한글 컬럼 설명 기능을 추가합니다.
    """
    print("📊 pandas 확장 기능을 설정합니다...")
    
    # pandas 옵션 설정
    pd.set_option("display.max_rows", 100)
    pd.set_option("display.max_columns", 100)
    
    # 이미 설정되어 있는지 확인
    if hasattr(pd.DataFrame, 'head_att'):
        print("✔️ pandas 확장 기능이 이미 설정되어 있습니다.")
        return
    
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
        print("- pd_read_csv(): Colab/로컬 파일 읽기")
        print("- dir_start(): 라이브러리 도움말 검색")
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

def pd_head_att(self, rows=5):
    """
    한글 컬럼 설명이 포함된 DataFrame을 HTML로 출력합니다.
    
    Parameters:
    -----------
    rows : int or str, default 5
        - int: 출력할 행 수
        - "all" or -1: 모든 행 출력
        - 0: 헤더만 출력
        
    Returns:
    --------
    IPython.display.HTML : HTML 형식의 테이블
    
    Examples:
    ---------
    >>> df.set_head_att({"id": "ID", "name": "이름"})
    >>> df.head_att(10)  # 10행 출력
    >>> df.head_att("all")  # 모든 행 출력
    """
    from IPython.display import HTML
    
    labels = self.attrs.get("column_descriptions", {})
    
    # 헤더 생성 (한글 설명이 있으면 추가)
    header = []
    for col in self.columns:
        if col in labels and labels[col]:
            header.append(f"{col}<br><small>({labels[col]})</small>")
        else:
            header.append(col)
    
    # 데이터 복사 및 컬럼명 변경
    df_copy = self.copy()
    df_copy.columns = header
    
    # 출력할 데이터 결정
    if isinstance(rows, str) and rows.lower() == "all":
        df_display = df_copy
    elif isinstance(rows, int):
        if rows == -1:
            df_display = df_copy
        elif rows == 0:
            df_display = df_copy.iloc[0:0]  # 헤더만
        else:
            df_display = df_copy.head(rows)
    else:
        df_display = df_copy.head(5)
    
    return HTML(df_display.to_html(escape=False))

def series_head_att(self, rows=5):
    """
    한글 컬럼 설명이 포함된 Series를 HTML로 출력합니다.
    
    Parameters:
    -----------
    rows : int, default 5
        출력할 행 수
        
    Returns:
    --------
    IPython.display.HTML : HTML 형식의 테이블
    
    Examples:
    ---------
    >>> s.set_head_att({"value": "값"})
    >>> s.head_att(10)
    """
    from IPython.display import HTML
    
    df = self.to_frame()
    labels = self.attrs.get("column_descriptions", {})
    
    if labels:
        col_name = df.columns[0]
        if col_name in labels and labels[col_name]:
            header = f"{col_name}<br><small>({labels[col_name]})</small>"
            df.columns = [header]
    
    return HTML(df.head(rows).to_html(escape=False))

# 모듈 직접 실행시 setup 함수 호출
if __name__ == "__main__":
    setup()