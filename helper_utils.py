import os
import sys

try:
    # Colab 환경 여부 확인
    import google.colab
    IS_COLAB = True
except ImportError:
    IS_COLAB = False

# --- PyTorch: 딥러닝 관련 ---
import torch

# --- 기타 ---
import requests
import tarfile
import shutil
import json
from datetime import datetime
from pathlib import Path
import re
from tqdm.notebook import tqdm
import numpy as np  # 수치 연산
import logging
import pytz
from typing import Union, List
import zipfile
import unicodedata

################################################################################################################

__version__ = "2.6.0"

################################################################################################################

class ShortLevelFormatter(logging.Formatter):
    """로그 레벨을 1글자로 축약 (DEBUG→D, INFO→I, WARNING→W, ERROR→E, CRITICAL→C)"""

    LEVEL_MAP = {
        'DEBUG': 'D',
        'INFO': 'I',
        'WARNING': 'W',
        'ERROR': 'E',
        'CRITICAL': 'C'
    }
    kst = pytz.timezone('Asia/Seoul')

    def format(self, record):
        # 원본 레벨명을 약자로 교체
        record.levelname = self.LEVEL_MAP.get(record.levelname, record.levelname)
        return super().format(record)

    def formatTime(self, record, datefmt=None):
        """record.created를 KST로 변환해 포맷된 문자열 반환"""
        ct = datetime.fromtimestamp(record.created, tz=self.kst)
        if datefmt:
            return ct.strftime(datefmt)
        return ct.strftime('%Y-%m-%d %H:%M:%S')
    
if IS_COLAB:
    # Colab: 기존 핸들러 제거 후 재설정
    logger = logging.getLogger()
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    handler = logging.StreamHandler()
    handler.setFormatter(ShortLevelFormatter(
        '%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    ))
    logger.addHandler(handler)
else:
    logging.basicConfig(
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logger = logging.getLogger()
    
    # 기존 핸들러의 Formatter 교체
    for handler in logging.getLogger().handlers:
        handler.setFormatter(ShortLevelFormatter(
            '%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))

# logger.setLevel(logging.DEBUG)

################################################################################################################

class AIHubShell:
    def __init__(self, DEBUG=False, download_dir=None):
        self.BASE_URL = "https://api.aihub.or.kr"
        self.LOGIN_URL = f"{self.BASE_URL}/api/keyValidate.do"
        self.BASE_DOWNLOAD_URL = f"{self.BASE_URL}/down/0.5"
        self.MANUAL_URL = f"{self.BASE_URL}/info/api.do"
        self.BASE_FILETREE_URL = f"{self.BASE_URL}/info"
        self.DATASET_URL = f"{self.BASE_URL}/info/dataset.do"
        self.DEBUG = DEBUG
        self.download_dir = download_dir if download_dir else "."
                
    def help(self):
        """AIHubShell 클래스 사용법 출력"""
        print("=" * 80)
        print("                        AIHubShell 클래스 사용 가이드")
        print("=" * 80)
        print()
        
        print("🔧 초기화")
        print("  AIHubShell(DEBUG=False, download_dir=None)")
        print("    DEBUG: True로 설정하면 상세 로그 출력")
        print("    download_dir: 다운로드 경로 지정 (기본값: 현재 경로)")
        print()
        
        print("📋 데이터셋 조회")
        print("  .dataset_info()                    # 전체 데이터셋 목록 조회")
        print("  .dataset_search('검색어')          # 특정 이름 포함 데이터셋 검색")
        print("  .dataset_search('검색어', tree=True) # 검색 + 파일 트리 조회")
        print("  .list_info(datasetkey=576)         # 특정 데이터셋의 파일 목록")
        print("  .json_info(datasetkey=576)         # JSON 형태로 파일 구조 반환")
        print()
        
        print("💾 다운로드")
        print("  .download_dataset(apikey, datasetkey, filekeys='all')")
        print("    apikey: AI Hub API 키")
        print("    datasetkey: 데이터셋 번호")
        print("    filekeys: 파일키 ('all' 또는 '66065,66083' 형태)")
        print("    overwrite: 기존 파일 덮어쓰기 여부 (기본값: False)")
        print()
        
        print("📖 기타 기능")
        print("  .print_usage()                     # AI Hub API 상세 사용법")
        print("  .help()                            # 이 도움말")
        print()
        
        print("💡 사용 예시")
        print("  # 1. 인스턴스 생성")
        print("  aihub = AIHubShell(DEBUG=True, download_dir='./data')")
        print()
        print("  # 2. 경구약제 데이터셋 검색")
        print("  aihub.dataset_search('경구약제')")
        print()
        print("  # 3. 데이터셋 576의 파일 목록 확인")
        print("  aihub.list_info(datasetkey=576)")
        print()
        print("  # 4. 특정 파일들만 다운로드")
        print("  aihub.download_dataset(")
        print("      apikey='YOUR_API_KEY',")
        print("      datasetkey=576,")
        print("      filekeys='66065,66083'")
        print("  )")
        print()
        print("  # 5. 전체 데이터셋 다운로드")
        print("  aihub.download_dataset(")
        print("      apikey='YOUR_API_KEY',")
        print("      datasetkey=576,")
        print("      filekeys='all'")
        print("  )")
        print()
        
        print("⚠️  주의사항")
        print("  - API 키는 AI Hub에서 발급받아야 합니다")
        print("  - 대용량 파일 다운로드 시 충분한 저장 공간을 확보하세요")
        print("  - overwrite=False일 때 기존 파일은 자동으로 건너뜁니다")
        print("  - 네트워크 상태에 따라 다운로드 시간이 달라질 수 있습니다")
        print()
        
        print("🔍 추가 정보")
        print("  AI Hub API 공식 문서: https://aihub.or.kr")
        print("  문제 발생 시 DEBUG=True로 설정하여 상세 로그를 확인하세요")
        print("=" * 80)
                        
    def print_usage(self):
        """사용법 출력"""
        try:
            response = requests.get(self.MANUAL_URL)
            manual = response.text
            
            if self.DEBUG:
                print("API 원본 응답:")
                print(manual)            
            
            # JSON 파싱하여 데이터 추출
            try:
                manual = re.sub(r'("FRST_RGST_PNTTM":)([0-9\- :\.]+)', r'\1"\2"', manual)
                manual_data = json.loads(manual)
                if self.DEBUG:
                    print("JSON 파싱 성공")
                    
                if 'result' in manual_data and len(manual_data['result']) > 0:
                    print(manual_data['result'][0].get('SJ', ''))
                    print()
                    print("ENGL_CMGG\t KOREAN_CMGG\t\t\t DETAIL_CN")
                    print("-" * 80)
                    
                    for item in manual_data['result']:
                        engl = item.get('ENGL_CMGG', '')
                        korean = item.get('KOREAN_CMGG', '')
                        detail = item.get('DETAIL_CN', '').replace('\\n', '\n').replace('\\t', '\t')
                        print(f"{engl:<10}\t {korean:<15}\t|\t {detail}\n")
            except json.JSONDecodeError:
                if self.DEBUG:
                    print("JSON 파싱 오류:", e)
                else:
                    print("API 응답 파싱 오류")
        except requests.RequestException as e:
            print(f"API 요청 오류: {e}")
    
    def _merge_parts(self, target_dir):
        """part 파일들을 병합"""
        target_path = Path(target_dir)
        part_files = list(target_path.glob("*.part*"))
        
        if not part_files:
            return
            
        # prefix별로 그룹화
        prefixes = {}
        for part_file in part_files:
            match = re.match(r'(.+)\.part(\d+)$', part_file.name)
            if match:
                prefix = match.group(1)
                part_num = int(match.group(2))
                if prefix not in prefixes:
                    prefixes[prefix] = []
                prefixes[prefix].append((part_num, part_file))
        
        # 각 prefix별로 병합
        for prefix, parts in prefixes.items():
            print(f"Merging {prefix} in {target_dir}")
            parts.sort(key=lambda x: x[0])  # part 번호로 정렬
            
            output_path = target_path / prefix
            with open(output_path, 'wb') as output_file:
                for _, part_file in parts:
                    with open(part_file, 'rb') as input_file:
                        shutil.copyfileobj(input_file, output_file)
            
            # part 파일들 삭제
            for _, part_file in parts:
                part_file.unlink()
                
    def _merge_parts_all(self, base_path="."):
        """모든 하위 폴더의 part 파일들을 병합"""
        if self.DEBUG:
            print("병합 중입니다...")
        for root, dirs, files in os.walk(base_path):
            part_files = [f for f in files if '.part' in f]
            if part_files:
                self._merge_parts(root)
        if self.DEBUG:
            print("병합이 완료되었습니다.")
    
    def download_dataset(self, apikey, datasetkey, filekeys="all", overwrite=False):
        """데이터셋 다운로드 (옵션: 덮어쓰기)"""
        def _parse_size(size_str):
            """'92 GB', '8 MB' 등 문자열을 바이트 단위로 변환"""
            size_str = size_str.strip().upper()
            if 'GB' in size_str:
                return float(size_str.replace('GB', '').strip()) * 1024**3
            elif 'MB' in size_str:
                return float(size_str.replace('MB', '').strip()) * 1024**2
            elif 'KB' in size_str:
                return float(size_str.replace('KB', '').strip()) * 1024
            elif 'B' in size_str:
                return float(size_str.replace('B', '').strip())
            return 0
        
        download_path = Path(self.download_dir)
        download_tar_path = download_path / "download.tar"
        
        download_list = self.list_info(datasetkey=datasetkey, filekeys=filekeys, print_out=False)
        
        # 이미 존재하는 파일은 제외
        keys_to_download = []
        for key, info in download_list.items():
            extracted_file_path = os.path.join(self.download_dir, info.path)
            if not overwrite and os.path.exists(extracted_file_path):
                print(f"파일 발견: {extracted_file_path}")
                if self.DEBUG:
                    print("다운로드를 생략합니다.")
                continue
            
            # 압축 해지 하고 용량 이슈로 인하여 zip파일은 삭제 되었다.
            if not overwrite and os.path.exists(extracted_file_path + ".unzip"):
                print(f"파일 발견 unzip: {extracted_file_path}.unzip")
                if self.DEBUG:
                    print("다운로드를 생략합니다.")
                continue
            
            keys_to_download.append(str(key))

        # 다운로드할 filekeys가 없으면 종료
        if not keys_to_download:
            print("모든 파일이 이미 존재합니다.")
            extracted_files = []
            for key, info in download_list.items():
                file_path = os.path.join(self.download_dir, info.path)
                if os.path.exists(file_path):
                    extracted_files.append(file_path)
            print("다운로드 파일 목록:", extracted_files)
            return extracted_files            

        # 헤더와 파라미터 기본 설정
        headers = {"apikey": apikey}
        params = {"fileSn": ",".join(keys_to_download)}
        
        mode = "wb"
        existing_size = 0
        response_head = requests.head(f"{self.BASE_DOWNLOAD_URL}/{datasetkey}.do", headers=headers, params=params)
        if "content-length" in response_head.headers:
            total_size = int(response_head.headers.get('content-length', 0))
        else:
            total_size = 0
            if self.DEBUG:
                print("content-length 헤더가 없습니다. 전체 크기 알 수 없음.")
                print("HEAD 응답 헤더:", response_head.headers)

        if total_size == 0:
            total_size = int(sum(_parse_size(info.size) for info in download_list.values()))
            if self.DEBUG:
                print(f"download_list 기반 추정 total_size: {total_size / (1024**3):.2f} GB")
                
        # 실제 다운로드
        if self.DEBUG:
            print("다운로드 시작...")
            
        os.makedirs(download_path, exist_ok=True)
        response = requests.get(
            f"{self.BASE_DOWNLOAD_URL}/{datasetkey}.do",
            headers=headers,
            params=params,
            stream=True
        )

        if response.status_code in [200, 206]:
            
            with open(download_tar_path, mode) as f, tqdm(
                total=total_size, 
                unit='B', 
                unit_scale=True, 
                desc="Downloading", 
                mininterval=3.0,  # 3초마다 갱신
                initial=(existing_size if mode == "ab" else 0)
            ) as pbar:
                update_count = 1000
                downloaded = existing_size if mode == "ab" else 0
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    #f.flush()
                    downloaded += len(chunk)
                    pbar.update(len(chunk))
                    if update_count <= 0:
                        pbar.set_postfix_str(f"{downloaded / (1024**2):.2f}MB / {total_size / (1024**2):.2f}MB")
                        update_count = 1000
                    update_count -= 1
                f.flush()
            
            if self.DEBUG:
                print("압축 해제 중...")
            with tarfile.open(download_tar_path, "r") as tar:
                tar.extractall(path=download_path)
            self._merge_parts_all(download_path)
            download_tar_path.unlink()
            
            print("다운로드 완료!")
        else:
            print(f"Download failed with HTTP status {response.status_code}.")
            print("Error msg:")
            print(response.text)
            if download_tar_path.exists():
                download_tar_path.unlink()
                
        extracted_files = []
        for key, info in download_list.items():
            file_path = os.path.join(self.download_dir, info.path)
            if os.path.exists(file_path):
                extracted_files.append(file_path)
        print("다운로드 파일 목록:", extracted_files)
        return extracted_files            
                
    def list_info(self, datasetkey=None, filekeys="all", print_out=True):
        """데이터셋 파일 정보 조회 (filekeys, 파일명, 사이즈 출력 및 딕셔너리 반환)"""
        resjson = self.json_info(datasetkey=datasetkey)
        
        # 파일 정보를 담을 딕셔너리
        file_info_dict = {}
        
        def extract_files(structure):
            """재귀적으로 파일 정보 추출"""
            for item in structure:
                if item["type"] == "file" and "filekey" in item:
                    filekey = int(item["filekey"])
                    file_info_dict[filekey] = {
                        "filekey": item["filekey"],
                        "filename": item["name"],
                        "size": item["size"],
                        "path": item["path"],
                        "deep": item["deep"]
                    }
                elif item["type"] == "directory" and "children" in item:
                    extract_files(item["children"])
        
        # JSON 구조에서 파일 정보 추출
        extract_files(resjson["structure"])
        
        # filekeys 처리
        if filekeys == "all":
            filtered_files = file_info_dict
        else:
            # 쉼표로 구분된 filekeys 파싱
            requested_keys = []
            for key in filekeys.split(','):
                try:
                    requested_keys.append(int(key.strip()))
                except ValueError:
                    continue
            
            # 요청된 filekey만 필터링
            filtered_files = {k: v for k, v in file_info_dict.items() if k in requested_keys}
        
        # 출력
        if print_out:
            print(f"Dataset: {datasetkey}")
            print("=" * 80)
            print(f"{'FileKey':<8} {'Filename':<30} {'Size':<10} {'Path'}")
            print("-" * 80)
            
            for filekey, info in sorted(filtered_files.items()):
                print(f"{info['filekey']:<8} {info['filename']:<30} {info['size']:<10} {info['path']}")
            
            print(f"\n총 {len(filtered_files)}개 파일")
        
        # 딕셔너리 반환 (FileInfo 객체 형태로)
        class FileInfo:
            def __init__(self, filekey, filename, size, path, deep):
                self.filekey = filekey
                self.filename = filename
                self.size = size
                self.path = path
                self.deep = deep
            
            def __str__(self):
                return f"FileInfo(filekey={self.filekey}, filename='{self.filename}', size='{self.size}' , path='{self.path}', deep={self.deep})"
            
            def __repr__(self):
                return self.__str__()
        
        result_dict = {}
        for filekey, info in filtered_files.items():
            result_dict[filekey] = FileInfo(
                filekey=info["filekey"],
                filename=info["filename"],
                size=info["size"],
                path=info["path"],
                deep=info["deep"]
            )
        
        return result_dict
        
    # filepath: [경구약제_이미지_데이터.ipynb](http://_vscodecontentref_/0)
    def dataset_info(self, datasetkey=None, datasetname=None):
        """데이터셋 목록 또는 파일 트리 조회"""
        if datasetkey:
            filetree_url = f"{self.BASE_FILETREE_URL}/{datasetkey}.do"
            print("Fetching file tree structure...")
            try:
                response = requests.get(filetree_url)
                # 인코딩 자동 감지
                response.encoding = response.apparent_encoding
                print(response.text)
            except requests.RequestException as e:
                print(f"API 요청 오류: {e}")
        else:
            print("Fetching dataset information...")
            try:
                response = requests.get(self.DATASET_URL)
                response.encoding = 'utf-8'
                #response.encoding = 'euc-kr'
                print(response.text)
            except requests.RequestException as e:
                print(f"API 요청 오류: {e}")

    def dataset_search(self, datasetname=None, tree=False):
        """
        데이터셋 목록 또는 특정 이름이 포함된 데이터셋의 파일 트리 조회
        datasetname: 검색할 데이터셋 이름 (부분 일치)
        tree: True이면 해당 데이터셋의 파일 트리도 조회        
        """
        print("Fetching dataset information...")
        try:
            response = requests.get(self.DATASET_URL)
            response.encoding = 'utf-8'
            text = response.text
            if datasetname:
                # datasetname이 포함된 부분만 출력
                lines = text.splitlines()
                for line in lines:
                    if datasetname in line:
                        #print(line)
                        # 576, 경구약제 이미지 데이터
                        num, name = line.split(',', 1)
                        # 해당 데이터셋의 파일 트리 조회
                        if tree:
                            self.dataset_info(datasetkey=num.strip())
                        else:
                            print(line)
            else:
                print(text)
        except requests.RequestException as e:
            print(f"API 요청 오류: {e}")

    def _get_depth_from_star_count(self, star_count, depth_mapping):
        """star_count 값을 깊이(deep)로 변환"""
        if star_count not in depth_mapping:
            # 새로운 star_count 값이면 배열에 추가
            depth_mapping.append(star_count)
            # 오름차순 정렬
            depth_mapping.sort()
        
        # 배열에서의 인덱스가 깊이
        return depth_mapping.index(star_count)

    def _json_line(self, line, json_obj, depth_mapping, path_stack, weight=0, deep=0):
        """파일 트리의 한 줄을 JSON 구조에 맞게 파싱하여 추가"""
        # 트리 구조 기호를 모두 *로 변경
        line = line.replace("├─", "└─")
        line = line.replace("│ ", "└─")
        while "    └─" in line:
            line = line.replace("    └─", "└─└─")
        while " └─" in line:
            line = line.replace(" └─", "└─")
        
        while "└─" in line:
            line = line.replace("└─", "*")
        
        # 앞부분의 * 개수와 문자열 추출
        star_count = 0
        for char in line:
            if char == '*':
                star_count += 1
            else:
                break
        clean_str = line.replace('*', '').strip()
        
        # star_count를 deep로 동적 변환
        deep = self._get_depth_from_star_count(star_count, depth_mapping)
        
        has_pipe = "|" in line
        
        # 파일/폴더 정보 추출
        if has_pipe:
            parts = clean_str.split('|')
            if len(parts) >= 3:
                filename = parts[0].strip()
                size = parts[1].strip()
                filekey = parts[2].strip()
                item_type = "file"
            else:
                filename = clean_str
                size = ""
                filekey = ""
                item_type = "directory"
        else:
            filename = clean_str
            size = ""
            filekey = ""
            item_type = "directory"
        
        # path_stack 조정 (현재 깊이에 맞게)
        while len(path_stack) > deep:
            path_stack.pop()
        
        # 현재 아이템 정보
        current_item = {
            "name": filename,
            "type": item_type,
            "deep": deep,
            "weight": star_count,
            "path": str(Path(*path_stack, filename)).replace(' ', '_')  # 공백을 언더스코어로 변경
        }
        
        if item_type == "file":
            current_item["size"] = size
            current_item["filekey"] = filekey
        else:
            current_item["children"] = []
        
        # JSON 구조에 추가 (배열 구조)
        current_array = json_obj
        for path_name in path_stack:
            # 해당 이름의 디렉토리를 찾아서 그 children 배열로 이동
            found = None
            for item in current_array:
                if item["name"] == path_name and item["type"] == "directory":
                    found = item
                    break
            if found:
                current_array = found["children"]
        
        # 현재 배열에 아이템 추가
        current_array.append(current_item)
        
        # 디렉토리인 경우 path_stack에 추가
        if item_type == "directory":
            path_stack.append(filename)
        
        # if self.DEBUG:
        #     print(f"[deep={deep}] [weight={star_count}] {item_type[0].upper()} {filename}" + 
        #         (f" , {size} , {filekey}" if item_type == "file" else " , , "))
        
        return current_item

    def json_info(self, datasetkey=None):
        """데이터셋 목록 또는 파일 트리를 JSON 형태로 반환"""
        filetree_url = f"{self.BASE_FILETREE_URL}/{datasetkey}.do"        
        response = requests.get(filetree_url)
        response.encoding = response.apparent_encoding
        text = response.text
        
        # JSON 구조를 위한 딕셔너리
        result = {
            "datasetkey": datasetkey,
            "structure": []  # 배열로 변경
        }
        
        lines = text.splitlines()
        
        is_notify = True
        json_obj = []  # 루트 배열
        depth_mapping = []  # 각 파싱 세션마다 새로운 depth_mapping
        path_stack = []     # 현재 경로를 추적하는 스택

        # if self.DEBUG:
        #     test_count = 10

        for line in lines:
            if not line.strip() or '공지사항' in line or '=' in line:
                is_notify = False
                continue
            if is_notify:
                continue

            self._json_line(line, json_obj, depth_mapping, path_stack, weight=0, deep=0)

            # if self.DEBUG:
            #     test_count -= 1
            #     if test_count <= 0:
            #         break
        
        result["structure"] = json_obj
        
        return result
################################################################################################################

def get_tqdm_kwargs():
    """Widget 오류를 방지하는 안전한 tqdm 설정"""
    return {
        'disable': False,
        'leave': True,
        'file': sys.stdout,
        'ascii': True,  # ASCII 문자만 사용
        'dynamic_ncols': False,
#        'ncols': 80  # 고정 폭
    }

def drive_root():
    root_path = os.path.join("D:\\", "GoogleDrive")
    if IS_COLAB:
        root_path = os.path.join("/content/drive/MyDrive")
    return root_path

def get_path_modeling(add_path = None):
    modeling_path = "modeling"
    path = os.path.join(drive_root(),modeling_path)
    if add_path is not None:
        path = os.path.join(path,add_path)
    return path

def get_path_modeling_release(add_path = None):
    modeling_path = "modeling_release"
    path = os.path.join(drive_root(),modeling_path)
    if add_path is not None:
        path = os.path.join(path,add_path)
    return path
    
def get_path_temp(add_path = None):
    """임시 경로를 가져옵니다.

    Args:
        add_path (str, optional): 추가 경로를 지정합니다. Defaults to None.

    Returns:
        str: 임시 경로 문자열
    """
    if IS_COLAB:
        temp_path = r"/content/temp"
    else:
        drive = os.path.splitdrive(os.getcwd())[0]  # ex: 'D:'
        temp_path = os.path.join(drive + os.sep, 'temp')
    if add_path is not None:
        temp_path = os.path.join(temp_path,add_path)
    return temp_path

################################################################################################################
def download_gdrive_file(url : str, output_path: str, ignore=True):
    try:
        import gdown
    except ImportError:
        raise ImportError("gdown 모듈이 필요합니다. 'pip install gdown'으로 설치하세요.")

    """Google Drive 파일 다운로드 함수

    Args:
        url (str): Google Drive 공유 링크
        output_path (str): 다운로드할 파일 경로
        ignore (bool, optional): True면 기존 파일 삭제 후 다운로드, False면 파일 있으면 건너뜀. Defaults to True.

    Raises:
        ValueError: Google Drive 파일 ID를 찾을 수 없습니다.
    """
    # 공유 링크에서 파일 ID 추출
    if os.path.exists(output_path):
        if ignore:
            os.remove(output_path)
        else:
            return

    file_id_match = re.search(r'/d/([a-zA-Z0-9_-]+)', url)
    if not file_id_match:
        raise ValueError("Google Drive 파일 ID를 찾을 수 없습니다.")
    file_id = file_id_match.group(1)

    gdown.download(f"https://drive.google.com/uc?id={file_id}", output_path, quiet=False)

def download_http(url: str, output_path: str, ignore=True):
    """
    HTTP 파일 다운로드 함수 (진행률 표시)
    url: 다운로드할 파일 URL
    output_path: 저장할 파일 경로
    ignore: True면 기존 파일 삭제 후 다운로드, False면 파일 있으면 건너뜀
    """
    if os.path.exists(output_path):
        if ignore:
            os.remove(output_path)
        else:
            print(f"이미 파일이 존재합니다: {output_path}")
            return output_path

    response = requests.get(url, stream=True)
    total = int(response.headers.get('content-length', 0))
    with open(output_path, 'wb') as file, tqdm(
        desc=f"Downloading {os.path.basename(output_path)}",
        total=total,
        unit='B',
        unit_scale=True,
        unit_divisor=1024,
        ascii=True
    ) as bar:
        for data in response.iter_content(chunk_size=1024):
            size = file.write(data)
            bar.update(size)
    print(f"다운로드 완료: {output_path}")
    return output_path

################################################################################################################

def print_dir_tree(root, indent=""):
    """디렉토리 트리를 출력합니다.

    Args:
        root (str): 시작 디렉토리 경로
        max_depth (int, optional): 최대 깊이. Defaults to 2.
        indent (str, optional): 들여쓰기 문자열. Defaults to "".
    """
    import os
    try:
        items = os.listdir(root)
    except Exception as e:
        print(indent + f"[Error] {e}")
        return

    img_count = len([f for f in os.listdir(root)])
    for item in items:
        path = os.path.join(root, item)
        if os.path.isdir(path):
            print(indent + "|-- "+ item)
            # 이미지 파일 개수만 출력
            img_count = len([f for f in os.listdir(path)])
            print(indent + "   "+ f"[데이터파일: {img_count}개]")
            print_dir_tree(root=path, indent=indent + "   ")
        else:
            print(indent + "|-- "+ item)
            

def print_json_tree(data, indent="", max_depth=4, _depth=0, list_count=2, print_value=True, limit_value_text=100):
    """
    JSON 객체를 지정한 단계(max_depth)까지 트리 형태로 출력
    - list 타입은 3개 이상일 때 개수만 출력
    - 하위 노드가 값일 경우 key(type) 형태로 출력
    - print_value=True일 때 key(type): 값 형태로 출력
    """
    if _depth > max_depth:
        return
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                print(f"{indent}|-- {key}")
                print_json_tree(value, indent + "    ", max_depth, _depth + 1, list_count, print_value)
            else:
                if print_value:
                    print(f"{indent}|-- {key}({type(value).__name__}): {value if len(str(value)) < limit_value_text else f'{str(value)[:30]}...'}")
                else:
                    print(f"{indent}|-- {key}({type(value).__name__})")
    elif isinstance(data, list):
        if len(data) > list_count:
            print(f"{indent}|-- [list] ({len(data)} items)")
        else:
            for i, item in enumerate(data):
                if isinstance(item, (dict, list)):
                    print(f"{indent}|-- [{i}]")
                    print_json_tree(item, indent + "    ", max_depth, _depth + 1, list_count, print_value)
                else:
                    if print_value:
                        print(f"{indent}|-- [{i}]({type(item).__name__}): {item if len(str(item)) < limit_value_text else f'{str(item)[:30]}...'}")
                    else:
                        print(f"{indent}|-- [{i}]({type(item).__name__})")
    else:
        if print_value:
            print(f"{indent}{type(data).__name__}: {data if len(str(data)) < limit_value_text else f'{str(data)[:30]}...'}")
        else:
            print(f"{indent}{type(data).__name__}")

def print_dic_tree(dic_data, indent="", max_depth=3, _depth=0):
    """
    PyTorch tensor/딕셔너리/리스트를 git tree 스타일로 출력
    """
    import torch
    import numpy as np

    if _depth > max_depth:
        return
    if isinstance(dic_data, dict):
        for key, value in dic_data.items():
            print(f"{indent}├─ {key} [{type(value).__name__}]")
            print_dic_tree(value, indent + "│  ", max_depth, _depth + 1)
    elif isinstance(dic_data, (list, tuple)):
        for i, item in enumerate(dic_data):
            print(f"{indent}├─ [{i}] [{type(item).__name__}]")
            print_dic_tree(item, indent + "│  ", max_depth, _depth + 1)
    elif torch.is_tensor(dic_data):
        shape = tuple(dic_data.shape)
        dtype = str(dic_data.dtype)
        preview = str(dic_data)
        preview_str = preview[:80] + ("..." if len(preview) > 80 else "")
        print(f"{indent}└─ Tensor shape={shape} dtype={dtype} preview={preview_str}")
    elif isinstance(dic_data, np.ndarray):
        shape = dic_data.shape
        dtype = dic_data.dtype
        preview = str(dic_data)
        preview_str = preview[:80] + ("..." if len(preview) > 80 else "")
        print(f"{indent}└─ ndarray shape={shape} dtype={dtype} preview={preview_str}")
    else:
        val_str = str(dic_data)
        print(f"{indent}└─ {type(dic_data).__name__}: {val_str[:80]}{'...' if len(val_str)>80 else ''}")

################################################################################################################

def save_model_dict(model, path, pth_name, kwargs=None):
    """
    모델 state_dict와 추가 정보를 저장
    """
    def safe_makedirs(path):
        """안전한 디렉토리 생성"""
        if os.path.exists(path) and not os.path.isdir(path):
            os.remove(path)  # 파일이면 삭제
        os.makedirs(path, exist_ok=True)

    # 디렉토리 생성
    safe_makedirs(path)

    # 모델 구조 정보 추출
    model_info = {
        'class_name': model.__class__.__name__,
        'init_args': {},
        'str': str(model),
        'repr': repr(model),
        'modules': [m.__class__.__name__ for m in model.modules()],
    }

    # 생성자 인자 자동 추출(가능한 경우)
    if hasattr(model, '__dict__'):
        for key in ['in_ch', 'base_ch', 'num_classes', 'out_ch']:
            if hasattr(model, key):
                model_info['init_args'][key] = getattr(model, key)

    # kwargs 처리
    extra_info = {}
    if kwargs is not None:
        if isinstance(kwargs, str):
            extra_info = json.loads(kwargs)
        elif isinstance(kwargs, dict):
            extra_info = kwargs

    model_info.update(extra_info)

    # 저장할 dict 구성
    save_dict = {
        'model_state': model.state_dict(),
        'class_name': model.__class__.__name__,
        'model_info': model_info,
    }

    save_path = os.path.join(path, f"{pth_name}.pth")
    torch.save(save_dict, save_path)
    return save_path

def load_model_dict(path, pth_name=None):
    """
    save_model_dict로 저장한 모델을 불러오는 함수
    반환값: (model_state, model_info)
    """
    import torch
    load_path = path
    if pth_name is not None:
        load_path = os.path.join(path, f"{pth_name}.pth")
    checkpoint = torch.load(load_path, map_location='cpu', weights_only=False)  # <-- 여기 추가
    model_state = checkpoint.get('model_state')
    model_info = checkpoint.get('model_info')
    model_info['file_name'] = os.path.basename(load_path)
    return model_state, model_info

################################################################################################################

def search_pth_files(base_path):
    """
    입력된 경로의 하위 폴더들에서 pth 파일들을 검색
    """
    pth_files = []

    if not os.path.exists(base_path):
        print(f"경로가 존재하지 않습니다: {base_path}")
        return pth_files

    print(f"pth 파일 검색 시작: {base_path}")

    # 하위 폴더들을 순회하며 pth 파일 검색
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith('.pth'):
                pth_path = os.path.join(root, file)
                pth_files.append(pth_path)

    # 결과 정리 및 출력
    if pth_files:
        print(f"\n발견된 pth 파일들 ({len(pth_files)}개):")
        for i, pth_file in enumerate(pth_files, 1):
            # 상대 경로로 표시 (base_path 기준)
            rel_path = os.path.relpath(pth_file, base_path)
            print(f" {i:2d}. {rel_path}")
    else:
        print("pth 파일을 찾을 수 없습니다.")

    return pth_files


def save_datasets_as_json(save_datasets, dataset_path):
    """데이터셋을 JSON 형태로 저장"""
    print(f"JSON 형태로 데이터셋 저장 중: {dataset_path}")
    
    # numpy array를 list로 변환
    json_data = {}
    for split in ['train', 'validation', 'test']:
        json_data[split] = {
            'text': save_datasets[split]['text'].tolist() if isinstance(save_datasets[split]['text'], np.ndarray) else list(save_datasets[split]['text']),
            'target': save_datasets[split]['target'].tolist() if isinstance(save_datasets[split]['target'], np.ndarray) else list(save_datasets[split]['target'])
        }
    
    json_data['target_names'] = list(save_datasets['target_names'])
    
    # JSON으로 저장
    with open(dataset_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    
    print(f"저장 완료: {dataset_path}")

def load_datasets_from_json(dataset_path):
    """JSON에서 데이터셋 로드"""
    print(f"JSON에서 데이터셋 로드: {dataset_path}")
    
    with open(dataset_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    
    # numpy array로 변환
    load_datasets = {}
    for split in ['train', 'validation', 'test']:
        load_datasets[split] = {
            'text': np.array(json_data[split]['text']),
            'target': np.array(json_data[split]['target'])
        }
    
    load_datasets['target_names'] = json_data['target_names']
    
    print("로드 완료")
    return load_datasets

################################################################################################################
def create_tqdm(iterable=None, total=None, desc="Progress", **kwargs):
    """
    tqdm 진행률 표시줄을 생성하거나 재사용하는 함수

    Args:
        iterable: 반복 가능한 객체 (range, list 등)
        total: 전체 개수 (iterable이 None일 때 사용)
        desc: 설명 텍스트
        **kwargs: 추가 tqdm 옵션

    Returns:
        tqdm 객체
    """
    # 기본 옵션 설정
    default_kwargs = get_tqdm_kwargs() if 'get_tqdm_kwargs' in globals() else {}
    default_kwargs.update(kwargs)

    if iterable is not None:
        # iterable이 있으면 직접 사용
        return tqdm(iterable, desc=desc, **default_kwargs)
    else:
        # manual update용 tqdm
        return tqdm(total=total, desc=desc, **default_kwargs)


def reset_tqdm(pbar, iterable=None, total=None, desc=None, **kwargs):
    """
    기존 tqdm 객체를 재설정하는 함수

    Args:
        pbar: 기존 tqdm 객체
        iterable: 새로운 반복 가능한 객체
        total: 새로운 전체 개수
        desc: 새로운 설명 텍스트
        **kwargs: 추가 옵션

    Returns:
        재설정된 tqdm 객체
    """
    if pbar is None:
        return create_tqdm(iterable, total, desc, **kwargs)

    # 기존 pbar 재설정
    if total is not None:
        pbar.reset(total=total)
    else:
        pbar.reset()

    if desc is not None:
        pbar.set_description(desc)

    # 내부 상태 초기화
    pbar.n = 0
    pbar.last_print_n = 0
    pbar.start_t = pbar._time()
    pbar.last_print_t = pbar.start_t

    # 추가 옵션 적용
    default_kwargs = get_tqdm_kwargs() if 'get_tqdm_kwargs' in globals() else {}
    default_kwargs.update(kwargs)

    for key, value in default_kwargs.items():
        if hasattr(pbar, key):
            setattr(pbar, key, value)

    pbar.refresh()
    return pbar

def create_or_reset_tqdm(pbar=None, iterable=None, total=None, desc="Progress", **kwargs):
    """
    기존 create_tqdm과 reset_tqdm을 활용한 통합 함수

    Args:
        pbar: 기존 tqdm 객체 (None이면 새로 생성)
        iterable: 반복 가능한 객체
        total: 전체 개수
        desc: 설명 텍스트
        **kwargs: 추가 tqdm 옵션

    Returns:
        tqdm 객체 (새로 생성되거나 재설정된)
    """
    if pbar is None:
        # 새로 생성
        return create_tqdm(iterable=iterable, total=total, desc=desc, **kwargs)
    else:
        # 기존 것 재설정
        return reset_tqdm(pbar, iterable=iterable, total=total, desc=desc, **kwargs)

##########################################################################################################

def unzip(zipfile_list, remove_zip=False, skip_root=False, normalize_nfc: bool = True, force_utf8: bool = False):
    def _try_force_utf8(name: str) -> str:
        """CP437→UTF-8/CP949 재해석 (개선)"""
        candidates = [
            ('utf-8', 'strict'),      # UTF-8 ZIP
            ('cp949', 'ignore'),      # 한국 레거시
            ('euc_kr', 'ignore'),     # 구형 리눅스
            ('cp437', 'replace'),     # DOS 폴백
        ]
        for enc, errors in candidates:
            try:
                return name.encode('latin1').decode(enc, errors=errors)
            except (UnicodeDecodeError, UnicodeEncodeError):
                continue
        return name  # 실패 시 원본 반환

    unzip_paths = []

    for zip_path in zipfile_list:
        if not (os.path.exists(zip_path) and os.path.isfile(zip_path)):
            print(f"존재하지 않은 파일: {zip_path}")
            continue

        extract_dir = zip_path + ".unzip"
        unzip_paths.append(extract_dir)

        if os.path.exists(extract_dir):
            print(f"이미 압축 해제됨: {extract_dir}")
            continue

        os.makedirs(extract_dir, exist_ok=True)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            members = zip_ref.namelist()

            # ========== skip_root 로직 (수정) ==========
            skip_prefix = ""

            if skip_root and members:
                # ZIP 내부 경로는 항상 POSIX 형식('/')이므로 '/'로 분할
                # __MACOSX 같은 메타파일 제외하고 최상위 디렉토리 추출
                top_level_dirs = set()
                for m in members:
                    if m.startswith('__MACOSX') or m.startswith('.'):
                        continue
                    parts = m.split('/', 1)  # POSIX 구분자 사용
                    if len(parts) > 0 and parts[0]:
                        top_level_dirs.add(parts[0])

                # 최상위 디렉토리가 1개만 존재하면 스킵 대상
                if len(top_level_dirs) == 1:
                    skip_prefix = list(top_level_dirs)[0] + '/'
                    print(f"최상위 디렉토리 스킵: {skip_prefix.rstrip('/')}")

            # ========== 압축 해제 ==========
            for member_name_orig in tqdm(members, desc=f"압축 해제 중: {os.path.basename(zip_path)}", unit="file"):

                # 메타파일 건너뛰기
                if member_name_orig.startswith('__MACOSX') or member_name_orig.startswith('.'):
                    continue

                member_name_to_use = member_name_orig

                # 1. force_utf8 옵션이 켜져있으면 재해석 시도
                if force_utf8:
                    member_name_to_use = _try_force_utf8(member_name_orig)

                # 2. NFD → NFC 변환 (옵션)
                if normalize_nfc:
                    member_name_nfc = unicodedata.normalize('NFC', member_name_to_use)
                else:
                    member_name_nfc = member_name_to_use

                # 3. 최상위 디렉토리 스킵 (skip_prefix는 원본 멤버 기준)
                if skip_prefix and member_name_orig.startswith(skip_prefix):
                    relative_path = member_name_orig[len(skip_prefix):]
                    if not relative_path:
                        continue
                    if force_utf8:
                        relative_path = _try_force_utf8(relative_path)
                    relative_path_nfc = unicodedata.normalize('NFC', relative_path) if normalize_nfc else relative_path
                else:
                    relative_path_nfc = member_name_nfc

                # 4. 추출 경로 (OS 구분자로 변환)
                target_path = os.path.join(extract_dir, relative_path_nfc.replace('/', os.sep))

                # 5. 파일/디렉토리 추출
                info = zip_ref.getinfo(member_name_orig)

                if info.is_dir():
                    os.makedirs(target_path, exist_ok=True)
                else:
                    # 상위 디렉토리 생성
                    parent_dir = os.path.dirname(target_path)
                    if parent_dir:
                        os.makedirs(parent_dir, exist_ok=True)

                    # 파일 추출
                    with zip_ref.open(member_name_orig) as source, open(target_path, 'wb') as target:
                        target.write(source.read())


            print(f"\n압축 해제 완료: {extract_dir}")
        # 원본 zip 삭제
        if remove_zip:
            os.remove(zip_path)
    return unzip_paths


def zip_progress(input_path: Union[str, Path], zip_path: str, compression=None) -> str:
    """
    파일 또는 폴더를 ZIP으로 압축하면서 tqdm 프로그레스바를 표시합니다.
    압축 파일 내에 상대 경로를 유지합니다.

    Args:
        input_path (Union[str, Path]): 압축할 파일 또는 폴더 경로.
        zip_path (str): 생성할 ZIP 파일 경로.
        compression (int, optional): 압축 방식. 기본값은 `zipfile.ZIP_STORED`이며, 
                                      `zipfile.ZIP_DEFLATED`를 사용할 수 있습니다.

    Returns:
        str: 생성된 ZIP 파일 경로. 실패 시 None을 반환합니다.

    Raises:
        Exception: 압축 중 오류가 발생하면 예외 메시지를 출력합니다.

    Example:
        >>> zip_progress3("my_folder", "archive.zip")
        Zipping: 100%|█████████████████████████████████████████████████████████████| 10/10 [00:00<00:00, 100.00file/s]
        'archive.zip'
    """
    input_path = Path(input_path)
    if not input_path.exists():
        print(f"압축할 대상이 존재하지 않습니다: {input_path}")
        return None

    if compression is None:
        compression = zipfile.ZIP_DEFLATED

    # 압축 대상 파일 목록 생성
    if input_path.is_dir():
        files = [f for f in input_path.rglob('*') if f.is_file()]
    else:
        files = [input_path]

    if not files:
        print("압축할 파일이 없습니다.")
        return None

    # ZIP 파일 생성
    with zipfile.ZipFile(zip_path, 'w', compression) as zf:
        with tqdm(total=len(files), desc="Zipping", unit="file") as pbar:
            for file in files:
                # 압축 파일 내 상대 경로 계산
                arcname = file.relative_to(input_path.parent if input_path.is_file() else input_path)
                zf.write(file, arcname)
                pbar.update(1)

    return zip_path


##########################################################################################################

print('helper_utils.py loaded')
