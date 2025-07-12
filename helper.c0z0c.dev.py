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
# google의 driver와 local 파일을 읽어오는 함수
def pd_read_csv(path):
    """
    Colab/로컬 환경에 맞춰 CSV 파일을 읽어옵니다.
    
    Parameters:
    -----------
    path : str
        읽어올 파일 경로
    
    Returns:
    --------
    pandas.DataFrame : 읽어온 데이터프레임
    """
    import os
    df = None
    
    if is_colab:
        # Colab 환경에서 여러 경로 시도
        possible_paths = [
            f"/content/drive/MyDrive/codeit/online/{path}",
            f"/content/drive/MyDrive/{path}",
            f"/content/{path}",
            f"{path}"
        ]
        
        for try_path in possible_paths:
            try:
                if os.path.exists(try_path):
                    df = pd.read_csv(try_path)
                    print(f"✅ 파일 읽기 성공: {try_path}")
                    break
            except Exception as e:
                continue
        
        if df is None:
            print(f"❌ 파일을 찾을 수 없습니다: {path}")
            print("🔍 시도한 경로들:")
            for try_path in possible_paths:
                print(f"  - {try_path}")
            print("💡 Google Drive가 마운트되지 않았거나 파일 경로를 확인하세요.")
    else:
        # 로컬 환경
        try:
            df = pd.read_csv(path)
            print(f"✅ 파일 읽기 성공: {path}")
        except Exception as e:
            print(f"❌ 파일 읽기 실패: {str(e)}")
            print(f"🔍 확인할 경로: {path}")
    
    return df


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
    
    # 이미 설정되어 있는지 확인
    if hasattr(pd.DataFrame, 'head_att'):
        print("📊 pandas 확장 기능이 이미 설정되어 있습니다.")
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

# 사용자 편의 함수들
def reset_colab_fonts():
    """
    Colab에서 폰트 관련 문제가 발생했을 때 완전히 리셋하는 함수
    """
    def in_colab():
        try:
            import google.colab
            return True
        except ImportError:
            return False
    
    if not in_colab():
        print("❌ 이 함수는 Colab 전용입니다.")
        return
    
    print("🔄 Colab 폰트 완전 리셋을 시작합니다...")
    
    try:
        import subprocess
        import os
        from IPython.display import display, Markdown
        
        # 1. 모든 폰트 패키지 제거
        print("🗑️  모든 폰트 패키지 제거 중...")
        subprocess.run(['sudo', 'apt-get', 'remove', '--purge', '-y', 'fonts-*'], 
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # 2. 캐시 완전 정리
        print("🧹 모든 캐시 정리 중...")
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
        
        # 4. 필수 폰트 재설치
        print("📥 필수 폰트 재설치 중...")
        subprocess.run(['sudo', 'apt-get', 'install', '-y', 'fonts-nanum', 'fonts-nanum-coding'], 
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # 5. 캐시 재구성
        print("🔧 폰트 캐시 재구성 중...")
        subprocess.run(['sudo', 'fc-cache', '-f', '-v'], 
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        print("✅ 폰트 리셋 완료!")
        print("🔄 런타임을 재시작하고 helper.setup()을 다시 실행하세요.")
        
        # 재시작 안내
        reset_guide = """
# 🔄 폰트 리셋 완료

## 📌 다음 단계
1. **메뉴 > 런타임 > 런타임 다시 시작** 클릭
2. 재시작 후 **helper.setup()** 실행

## 💡 이제 정상적으로 작동할 것입니다!
"""
        display(Markdown(reset_guide))
        
    except Exception as e:
        print(f"❌ 리셋 중 오류 발생: {str(e)}")
        print("🔄 수동으로 런타임을 재시작하고 다시 시도하세요.")

def check_font_status():
    """
    현재 폰트 설정 상태를 확인하는 함수
    """
    print("🔍 폰트 설정 상태 확인 중...")
    
    def in_colab():
        try:
            import google.colab
            return True
        except ImportError:
            return False
    
    import matplotlib.pyplot as plt
    import matplotlib.font_manager as fm
    
    print(f"💻 실행 환경: {'Colab' if in_colab() else '로컬'}")
    print(f"📝 현재 폰트 패밀리: {plt.rcParams['font.family']}")
    
    # 사용 가능한 한글 폰트 목록
    fonts = [f.name for f in fm.fontManager.ttflist]
    korean_fonts = [f for f in fonts if any(keyword in f for keyword in ['Nanum', 'Gothic', 'Malgun', 'Dotum', 'Batang'])]
    
    if korean_fonts:
        print("✅ 사용 가능한 한글 폰트:")
        for font in korean_fonts:
            print(f"  - {font}")
    else:
        print("❌ 한글 폰트를 찾을 수 없습니다.")
    
    # Colab에서 폰트 패키지 확인
    if in_colab():
        import os
        fonts_installed = os.system("dpkg -l | grep fonts-nanum") == 0
        print(f"📦 fonts-nanum 패키지: {'✅ 설치됨' if fonts_installed else '❌ 미설치'}")
    
    # 간단한 테스트
    try:
        import matplotlib.pyplot as plt
        import numpy as np
        
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.text(0.5, 0.5, '한글 폰트 테스트', ha='center', va='center', fontsize=16)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_title('폰트 테스트')
        plt.tight_layout()
        plt.show()
        
        print("🎨 폰트 테스트 완료!")
        
    except Exception as e:
        print(f"❌ 폰트 테스트 실패: {str(e)}")