"""
Helper utilities for Jupyter Notebook environments.

This module provides various utility functions for:
- AI Hub dataset download and management
- File operations (zip/unzip with progress bars)
- Model saving/loading
- Directory tree visualization
- Logging configuration
"""

import json
import logging
import os
import re
import shutil
import sys
import tarfile
import unicodedata
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pytz
import requests
import torch
from tqdm.notebook import tqdm

try:
    # Colab 환경 여부 확인
    import google.colab
    IS_COLAB: bool = True
except ImportError:
    IS_COLAB: bool = False


__version__: str = "2.6.0"


class ShortLevelFormatter(logging.Formatter):
    """
    Custom logging formatter that abbreviates log levels to single characters.

    This formatter converts log level names to single-character abbreviations:
    DEBUG→D, INFO→I, WARNING→W, ERROR→E, CRITICAL→C

    It also formats timestamps in Korean Standard Time (KST/Asia/Seoul).

    Attributes:
        LEVEL_MAP (Dict[str, str]): Mapping of full level names to abbreviations.
        kst (pytz.timezone): Korean Standard Time timezone object.
    """

    LEVEL_MAP: Dict[str, str] = {
        'DEBUG': 'D',
        'INFO': 'I',
        'WARNING': 'W',
        'ERROR': 'E',
        'CRITICAL': 'C'
    }
    kst: pytz.tzinfo.BaseTzInfo = pytz.timezone('Asia/Seoul')

    def format(self, record: logging.LogRecord) -> str:
        """
        Format the log record with abbreviated level name.

        Args:
            record (logging.LogRecord): The log record to format.

        Returns:
            str: Formatted log message string.
        """
        record.levelname = self.LEVEL_MAP.get(record.levelname, record.levelname)
        return super().format(record)

    def formatTime(
        self,
        record: logging.LogRecord,
        datefmt: Optional[str] = None
    ) -> str:
        """
        Convert record.created timestamp to KST and return formatted string.

        Args:
            record (logging.LogRecord): The log record containing timestamp.
            datefmt (Optional[str]): Custom date format string.

        Returns:
            str: Formatted timestamp in KST.
        """
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


class AIHubShell:
    """
    AI Hub API wrapper for dataset download and management.

    This class provides convenient methods to interact with the AI Hub API,
    including searching datasets, viewing file structures, and downloading datasets.

    Attributes:
        BASE_URL (str): Base URL for AI Hub API.
        LOGIN_URL (str): API key validation endpoint.
        BASE_DOWNLOAD_URL (str): Download endpoint base URL.
        MANUAL_URL (str): API manual documentation URL.
        BASE_FILETREE_URL (str): File tree structure endpoint base URL.
        DATASET_URL (str): Dataset information endpoint.
        DEBUG (bool): Enable debug output if True.
        download_dir (str): Directory path for downloaded files.
    """

    def __init__(self, DEBUG: bool = False, download_dir: Optional[str] = None) -> None:
        """
        Initialize AIHubShell instance.

        Args:
            DEBUG (bool, optional): Enable debug output. Defaults to False.
            download_dir (Optional[str], optional): Download directory path.
                Defaults to current directory (".").
        """
        self.BASE_URL: str = "https://api.aihub.or.kr"
        self.LOGIN_URL: str = f"{self.BASE_URL}/api/keyValidate.do"
        self.BASE_DOWNLOAD_URL: str = f"{self.BASE_URL}/down/0.5"
        self.MANUAL_URL: str = f"{self.BASE_URL}/info/api.do"
        self.BASE_FILETREE_URL: str = f"{self.BASE_URL}/info"
        self.DATASET_URL: str = f"{self.BASE_URL}/info/dataset.do"
        self.DEBUG: bool = DEBUG
        self.download_dir: str = download_dir if download_dir else "."

    def help(self) -> None:
        """
        Print usage guide for AIHubShell class.

        Displays comprehensive information about available methods,
        parameters, usage examples, and precautions.
        """
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

    def print_usage(self) -> None:
        """
        Print AI Hub API usage documentation.

        Fetches and displays the API manual from AI Hub, including
        command descriptions in English and Korean.

        Raises:
            requests.RequestException: If API request fails.
        """
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
            except json.JSONDecodeError as e:
                if self.DEBUG:
                    print("JSON 파싱 오류:", e)
                else:
                    print("API 응답 파싱 오류")
        except requests.RequestException as e:
            print(f"API 요청 오류: {e}")

    def _merge_parts(self, target_dir: str) -> None:
        """
        Merge split part files in the target directory.

        Finds files matching pattern '*.part*', groups them by prefix,
        and merges them into single files.

        Args:
            target_dir (str): Directory containing part files to merge.
        """
        target_path = Path(target_dir)
        part_files = list(target_path.glob("*.part*"))

        if not part_files:
            return

        # prefix별로 그룹화
        prefixes: Dict[str, List[Tuple[int, Path]]] = {}
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

    def _merge_parts_all(self, base_path: str = ".") -> None:
        """
        Recursively merge all part files in subdirectories.

        Walks through directory tree from base_path and merges
        any split part files found.

        Args:
            base_path (str, optional): Root directory to start search.
                Defaults to ".".
        """
        if self.DEBUG:
            print("병합 중입니다...")
        for root, dirs, files in os.walk(base_path):
            part_files = [f for f in files if '.part' in f]
            if part_files:
                self._merge_parts(root)
        if self.DEBUG:
            print("병합이 완료되었습니다.")

    def download_dataset(
        self,
        apikey: str,
        datasetkey: int,
        filekeys: str = "all",
        overwrite: bool = False
    ) -> List[str]:
        """
        Download dataset from AI Hub.

        Args:
            apikey (str): AI Hub API key for authentication.
            datasetkey (int): Dataset identifier number.
            filekeys (str, optional): File keys to download. Use 'all' for
                all files or comma-separated keys like '66065,66083'.
                Defaults to "all".
            overwrite (bool, optional): If True, overwrite existing files.
                Defaults to False.

        Returns:
            List[str]: List of extracted file paths.

        Raises:
            requests.RequestException: If download request fails.
        """
        def _parse_size(size_str: str) -> float:
            """
            Convert size string to bytes.

            Args:
                size_str (str): Size string like '92 GB', '8 MB', etc.

            Returns:
                float: Size in bytes.
            """
            size_str = size_str.strip().upper()
            if 'GB' in size_str:
                return float(size_str.replace('GB', '').strip()) * 1024**3
            elif 'MB' in size_str:
                return float(size_str.replace('MB', '').strip()) * 1024**2
            elif 'KB' in size_str:
                return float(size_str.replace('KB', '').strip()) * 1024
            elif 'B' in size_str:
                return float(size_str.replace('B', '').strip())
            return 0.0

        download_path = Path(self.download_dir)
        download_tar_path = download_path / "download.tar"

        download_list = self.list_info(
            datasetkey=datasetkey,
            filekeys=filekeys,
            print_out=False
        )

        # 이미 존재하는 파일은 제외
        keys_to_download: List[str] = []
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
            extracted_files: List[str] = []
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
        response_head = requests.head(
            f"{self.BASE_DOWNLOAD_URL}/{datasetkey}.do",
            headers=headers,
            params=params
        )
        if "content-length" in response_head.headers:
            total_size = int(response_head.headers.get('content-length', 0))
        else:
            total_size = 0
            if self.DEBUG:
                print("content-length 헤더가 없습니다. 전체 크기 알 수 없음.")
                print("HEAD 응답 헤더:", response_head.headers)

        if total_size == 0:
            total_size = int(sum(
                _parse_size(info.size) for info in download_list.values()
            ))
            if self.DEBUG:
                print(f"download_list 기반 추정 total_size: "
                      f"{total_size / (1024**3):.2f} GB")

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
                        pbar.set_postfix_str(
                            f"{downloaded / (1024**2):.2f}MB / "
                            f"{total_size / (1024**2):.2f}MB"
                        )
                        update_count = 1000
                    update_count -= 1
                f.flush()

            if self.DEBUG:
                print("압축 해제 중...")
            with tarfile.open(download_tar_path, "r") as tar:
                tar.extractall(path=download_path)
            self._merge_parts_all(str(download_path))
            download_tar_path.unlink()

            print("다운로드 완료!")
        else:
            print(f"Download failed with HTTP status {response.status_code}.")
            print("Error msg:")
            print(response.text)
            if download_tar_path.exists():
                download_tar_path.unlink()

        extracted_files: List[str] = []
        for key, info in download_list.items():
            file_path = os.path.join(self.download_dir, info.path)
            if os.path.exists(file_path):
                extracted_files.append(file_path)
        print("다운로드 파일 목록:", extracted_files)
        return extracted_files

    def list_info(
        self,
        datasetkey: Optional[int] = None,
        filekeys: str = "all",
        print_out: bool = True
    ) -> Dict[int, Any]:
        """
        Retrieve and display dataset file information.

        Args:
            datasetkey (Optional[int], optional): Dataset key to query.
                Defaults to None.
            filekeys (str, optional): File keys to filter. Use 'all' for all files
                or comma-separated keys. Defaults to "all".
            print_out (bool, optional): If True, print file information table.
                Defaults to True.

        Returns:
            Dict[int, Any]: Dictionary mapping filekey to FileInfo objects.
        """
        resjson = self.json_info(datasetkey=datasetkey)

        # 파일 정보를 담을 딕셔너리
        file_info_dict: Dict[int, Dict[str, Any]] = {}

        def extract_files(structure: List[Dict[str, Any]]) -> None:
            """
            Recursively extract file information from structure.

            Args:
                structure (List[Dict[str, Any]]): Nested file/directory structure.
            """
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
        filtered_files: Dict[int, Dict[str, Any]]
        if filekeys == "all":
            filtered_files = file_info_dict
        else:
            # 쉼표로 구분된 filekeys 파싱
            requested_keys: List[int] = []
            for key in filekeys.split(','):
                try:
                    requested_keys.append(int(key.strip()))
                except ValueError:
                    continue

            # 요청된 filekey만 필터링
            filtered_files = {
                k: v for k, v in file_info_dict.items()
                if k in requested_keys
            }

        # 출력
        if print_out:
            print(f"Dataset: {datasetkey}")
            print("=" * 80)
            print(f"{'FileKey':<8} {'Filename':<30} {'Size':<10} {'Path'}")
            print("-" * 80)

            for filekey, info in sorted(filtered_files.items()):
                print(f"{info['filekey']:<8} {info['filename']:<30} "
                      f"{info['size']:<10} {info['path']}")

            print(f"\n총 {len(filtered_files)}개 파일")

        # 딕셔너리 반환 (FileInfo 객체 형태로)
        class FileInfo:
            """File information container."""

            def __init__(
                self,
                filekey: str,
                filename: str,
                size: str,
                path: str,
                deep: int
            ) -> None:
                """
                Initialize FileInfo.

                Args:
                    filekey (str): File key identifier.
                    filename (str): Name of the file.
                    size (str): File size string.
                    path (str): File path.
                    deep (int): Directory depth level.
                """
                self.filekey = filekey
                self.filename = filename
                self.size = size
                self.path = path
                self.deep = deep

            def __str__(self) -> str:
                return (f"FileInfo(filekey={self.filekey}, "
                        f"filename='{self.filename}', size='{self.size}', "
                        f"path='{self.path}', deep={self.deep})")

            def __repr__(self) -> str:
                return self.__str__()

        result_dict: Dict[int, FileInfo] = {}
        for filekey, info in filtered_files.items():
            result_dict[filekey] = FileInfo(
                filekey=info["filekey"],
                filename=info["filename"],
                size=info["size"],
                path=info["path"],
                deep=info["deep"]
            )

        return result_dict

    def dataset_info(
        self,
        datasetkey: Optional[int] = None,
        datasetname: Optional[str] = None
    ) -> None:
        """
        Fetch and display dataset list or file tree structure.

        Args:
            datasetkey (Optional[int], optional): Dataset key for file tree.
                Defaults to None.
            datasetname (Optional[str], optional): Dataset name (unused).
                Defaults to None.

        Raises:
            requests.RequestException: If API request fails.
        """
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
                print(response.text)
            except requests.RequestException as e:
                print(f"API 요청 오류: {e}")

    def dataset_search(
        self,
        datasetname: Optional[str] = None,
        tree: bool = False
    ) -> None:
        """
        Search datasets by name and optionally show file tree.

        Args:
            datasetname (Optional[str], optional): Dataset name to search for
                (partial match). Defaults to None.
            tree (bool, optional): If True, also display file tree for matches.
                Defaults to False.

        Raises:
            requests.RequestException: If API request fails.
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
                        # 576, 경구약제 이미지 데이터
                        num, name = line.split(',', 1)
                        # 해당 데이터셋의 파일 트리 조회
                        if tree:
                            self.dataset_info(datasetkey=int(num.strip()))
                        else:
                            print(line)
            else:
                print(text)
        except requests.RequestException as e:
            print(f"API 요청 오류: {e}")

    def _get_depth_from_star_count(
        self,
        star_count: int,
        depth_mapping: List[int]
    ) -> int:
        """
        Convert star_count to depth level.

        Maintains a sorted mapping of star counts to depth levels.

        Args:
            star_count (int): Number of stars/indentation level.
            depth_mapping (List[int]): List of known star counts.

        Returns:
            int: Depth level (index in sorted mapping).
        """
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


def get_tqdm_kwargs() -> Dict[str, Any]:
    """
    Get safe tqdm configuration to prevent widget errors.

    Returns:
        Dict[str, Any]: Configuration dictionary for tqdm.
    """
    return {
        'disable': False,
        'leave': True,
        'file': sys.stdout,
        'ascii': True,  # ASCII 문자만 사용
        'dynamic_ncols': False,
    }


def drive_root() -> str:
    """
    Get Google Drive root path.

    Returns:
        str: Path to Google Drive root directory.
            - Colab: '/content/drive/MyDrive'
            - Windows: 'D:\\GoogleDrive'
    """
    root_path = os.path.join("D:\\", "GoogleDrive")
    if IS_COLAB:
        root_path = os.path.join("/content/drive/MyDrive")
    return root_path


def get_path_modeling(add_path: Optional[str] = None) -> str:
    """
    Get modeling directory path.

    Args:
        add_path (Optional[str], optional): Additional path to append.
            Defaults to None.

    Returns:
        str: Full path to modeling directory.
    """
    modeling_path = "modeling"
    path = os.path.join(drive_root(), modeling_path)
    if add_path is not None:
        path = os.path.join(path, add_path)
    return path


def get_path_modeling_release(add_path: Optional[str] = None) -> str:
    """
    Get modeling release directory path.

    Args:
        add_path (Optional[str], optional): Additional path to append.
            Defaults to None.

    Returns:
        str: Full path to modeling_release directory.
    """
    modeling_path = "modeling_release"
    path = os.path.join(drive_root(), modeling_path)
    if add_path is not None:
        path = os.path.join(path, add_path)
    return path


def get_path_temp(add_path: Optional[str] = None) -> str:
    """
    Get temporary directory path.

    Args:
        add_path (Optional[str], optional): Additional path to append.
            Defaults to None.

    Returns:
        str: Full path to temporary directory.
            - Colab: '/content/temp'
            - Windows: 'D:\\temp' (or current drive)
    """
    if IS_COLAB:
        temp_path = r"/content/temp"
    else:
        drive = os.path.splitdrive(os.getcwd())[0]  # ex: 'D:'
        temp_path = os.path.join(drive + os.sep, 'temp')
    if add_path is not None:
        temp_path = os.path.join(temp_path, add_path)
    return temp_path


def download_gdrive_file(url: str, output_path: str, ignore: bool = True) -> None:
    """
    Download file from Google Drive.

    Args:
        url (str): Google Drive share link.
        output_path (str): Output file path.
        ignore (bool, optional): If True, delete existing file before download.
            If False, skip download if file exists. Defaults to True.

    Raises:
        ImportError: If gdown module is not installed.
        ValueError: If Google Drive file ID cannot be found in URL.
    """
    try:
        import gdown
    except ImportError:
        raise ImportError("gdown 모듈이 필요합니다. 'pip install gdown'으로 설치하세요.")

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


def download_http(url: str, output_path: str, ignore: bool = True) -> str:
    """
    Download file via HTTP with progress bar.

    Args:
        url (str): URL of file to download.
        output_path (str): Output file path.
        ignore (bool, optional): If True, delete existing file before download.
            If False, skip download if file exists. Defaults to True.

    Returns:
        str: Path to downloaded file.

    Raises:
        requests.RequestException: If download request fails.
    """
    if os.path.exists(output_path):
        if ignore:
            os.remove(output_path)
        else:
            print(f"이미 파일이 존재합니다: {output_path}")
            return output_path

    # 폴더 생성
    output_dir = os.path.dirname(output_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

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


def print_dir_tree(
    root: str,
    indent: str = "",
    max_file_list: Optional[int] = None,
    max_dir_list: Optional[int] = None
) -> None:
    """
    Print directory tree structure.

    Args:
        root (str): Root directory path.
        indent (str, optional): Indentation string. Defaults to "".
        max_file_list (Optional[int], optional): Maximum number of files to
            display per directory. None means show all. Defaults to None.
        max_dir_list (Optional[int], optional): Maximum number of subdirectories
            to display per directory. None means show all. Defaults to None.
    """
    try:
        entries = sorted(os.listdir(root))
    except Exception as e:
        print(indent + f"[Error] {e}")
        return

    # 디렉토리 / 파일 분리
    dirs = [e for e in entries if os.path.isdir(os.path.join(root, e))]
    files = [e for e in entries if not os.path.isdir(os.path.join(root, e))]

    total_dirs = len(dirs)
    total_files = len(files)

    display_dirs = dirs if max_dir_list is None else dirs[:max_dir_list]
    display_files = files if max_file_list is None else files[:max_file_list]

    allowed_dirs = set(display_dirs)
    allowed_files = set(display_files)

    has_more_dirs = (max_dir_list is not None) and (total_dirs > max_dir_list)
    has_more_files = (max_file_list is not None) and (total_files > max_file_list)

    for entry in entries:
        path = os.path.join(root, entry)
        if os.path.isdir(path):
            if entry not in allowed_dirs:
                continue
            print(indent + "|-- " + entry)
            # 디렉토리 내 파일 개수 출력
            try:
                file_count = len([f for f in os.listdir(path)])
            except Exception:
                file_count = 0
            print(indent + "   " + f"[데이터파일: {file_count}개]")
            # 재귀 호출 시 동일한 제한 전달
            print_dir_tree(
                root=path,
                indent=indent + "   ",
                max_file_list=max_file_list,
                max_dir_list=max_dir_list
            )
        else:
            if entry not in allowed_files:
                continue
            print(indent + "|-- " + entry)

    # 생략된 항목이 있으면 표시
    if has_more_dirs:
        print(indent + "   " + "... dirs")
    if has_more_files:
        print(indent + "   " + "... files")
            

def print_json_tree(data, indent="", max_depth=4, _depth=0, list_count=1, print_value=True, limit_value_text=100):
    """
    JSON 객체를 지정한 단계(max_depth)까지 트리 형태로 출력
    - list 타입은 앞/뒤 list_count개수 만큼 출력하고 중간은 "..."로 생략 처리
    - 하위 노드가 값일 경우 key(type) 형태로 출력
    - print_value=True일 때 key(type): 값 형태로 출력
    """
    if _depth > max_depth:
        return

    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                print(f"{indent}|-- {key}")
                print_json_tree(value, indent + "    ", max_depth, _depth + 1, list_count, print_value, limit_value_text)
            else:
                if print_value:
                    vstr = str(value)
                    short = vstr if len(vstr) < limit_value_text else f"{vstr[:30]}..."
                    print(f"{indent}|-- {key}({type(value).__name__}): {short}")
                else:
                    print(f"{indent}|-- {key}({type(value).__name__})")

    elif isinstance(data, list):
        n = int(list_count) if list_count is not None else 0
        L = len(data)

        if L == 0:
            print(f"{indent}|-- [list] (0 items)")
            return

        # 리스트가 충분히 길면 앞/뒤 n개만 보여주고 중간 생략
        if n > 0 and L > 2 * n:
            print(f"{indent}|-- [list] ({L} items)")
            # 앞쪽 n개
            for i in range(0, n):
                item = data[i]
                if isinstance(item, (dict, list)):
                    print(f"{indent}    |-- [{i}]")
                    print_json_tree(item, indent + "        ", max_depth, _depth + 1, list_count, print_value, limit_value_text)
                else:
                    if print_value:
                        vstr = str(item)
                        short = vstr if len(vstr) < limit_value_text else f"{vstr[:30]}..."
                        print(f"{indent}    |-- [{i}]({type(item).__name__}): {short}")
                    else:
                        print(f"{indent}    |-- [{i}]({type(item).__name__})")

            # 생략 표시
            omitted = L - 2 * n
            print(f"{indent}    |-- ... ({omitted} items omitted)")

            # 뒤쪽 n개
            for j in range(L - n, L):
                item = data[j]
                if isinstance(item, (dict, list)):
                    print(f"{indent}    |-- [{j}]")
                    print_json_tree(item, indent + "        ", max_depth, _depth + 1, list_count, print_value, limit_value_text)
                else:
                    if print_value:
                        vstr = str(item)
                        short = vstr if len(vstr) < limit_value_text else f"{vstr[:30]}..."
                        print(f"{indent}    |-- [{j}]({type(item).__name__}): {short}")
                    else:
                        print(f"{indent}    |-- [{j}]({type(item).__name__})")

        else:
            # 전체 출력 (list_count가 0 이거나 리스트가 짧은 경우)
            print(f"{indent}|-- [list] ({L} items)")
            for i, item in enumerate(data):
                if isinstance(item, (dict, list)):
                    print(f"{indent}    |-- [{i}]")
                    print_json_tree(item, indent + "        ", max_depth, _depth + 1, list_count, print_value, limit_value_text)
                else:
                    if print_value:
                        vstr = str(item)
                        short = vstr if len(vstr) < limit_value_text else f"{vstr[:30]}..."
                        print(f"{indent}    |-- [{i}]({type(item).__name__}): {short}")
                    else:
                        print(f"{indent}    |-- [{i}]({type(item).__name__})")
    else:
        if print_value:
            vstr = str(data)
            short = vstr if len(vstr) < limit_value_text else f"{vstr[:30]}..."
            print(f"{indent}{type(data).__name__}: {short}")
        else:
            print(f"{indent}{type(data).__name__}")

def print_dic_tree(dic_data, indent="", max_depth=3, _depth=0, list_count=1, print_value=True, limit_value_text=100):
    """
    PyTorch tensor/딕셔너리/리스트를 git tree 스타일로 출력
    - max_depth: 출력할 최대 깊이
    - list_count: 리스트 앞/뒤로 출력할 항목 수 (중간 생략)
    - print_value: True이면 값도 출력, False이면 타입만 출력
    - limit_value_text: 값 출력 시 최대 텍스트 길이
    """

    if _depth > max_depth:
        return
    
    if isinstance(dic_data, dict):
        for key, value in dic_data.items():
            if isinstance(value, (dict, list, tuple)):
                print(f"{indent}├─ {key} [{type(value).__name__}]")
                print_dic_tree(value, indent + "│  ", max_depth, _depth + 1, list_count, print_value, limit_value_text)
            elif torch.is_tensor(value):
                shape = tuple(value.shape)
                dtype = str(value.dtype)
                if print_value:
                    preview = str(value)
                    preview_str = preview[:limit_value_text] + ("..." if len(preview) > limit_value_text else "")
                    print(f"{indent}├─ {key} [Tensor] shape={shape} dtype={dtype}")
                    print(f"{indent}│  └─ {preview_str}")
                else:
                    print(f"{indent}├─ {key} [Tensor] shape={shape} dtype={dtype}")
            elif isinstance(value, np.ndarray):
                shape = value.shape
                dtype = value.dtype
                if print_value:
                    preview = str(value)
                    preview_str = preview[:limit_value_text] + ("..." if len(preview) > limit_value_text else "")
                    print(f"{indent}├─ {key} [ndarray] shape={shape} dtype={dtype}")
                    print(f"{indent}│  └─ {preview_str}")
                else:
                    print(f"{indent}├─ {key} [ndarray] shape={shape} dtype={dtype}")
            else:
                if print_value:
                    val_str = str(value)
                    short = val_str[:limit_value_text] + ("..." if len(val_str) > limit_value_text else "")
                    print(f"{indent}├─ {key} [{type(value).__name__}]: {short}")
                else:
                    print(f"{indent}├─ {key} [{type(value).__name__}]")
    
    elif isinstance(dic_data, (list, tuple)):
        n = int(list_count) if list_count is not None else 0
        L = len(dic_data)
        
        if L == 0:
            print(f"{indent}└─ [{type(dic_data).__name__}] (0 items)")
            return
        
        # 리스트가 충분히 길면 앞/뒤 n개만 보여주고 중간 생략
        if n > 0 and L > 2 * n:
            # 앞쪽 n개
            for i in range(0, n):
                item = dic_data[i]
                if isinstance(item, (dict, list, tuple)):
                    print(f"{indent}├─ [{i}] [{type(item).__name__}]")
                    print_dic_tree(item, indent + "│  ", max_depth, _depth + 1, list_count, print_value, limit_value_text)
                elif torch.is_tensor(item):
                    shape = tuple(item.shape)
                    dtype = str(item.dtype)
                    if print_value:
                        preview = str(item)
                        preview_str = preview[:limit_value_text] + ("..." if len(preview) > limit_value_text else "")
                        print(f"{indent}├─ [{i}] [Tensor] shape={shape} dtype={dtype}: {preview_str}")
                    else:
                        print(f"{indent}├─ [{i}] [Tensor] shape={shape} dtype={dtype}")
                elif isinstance(item, np.ndarray):
                    shape = item.shape
                    dtype = item.dtype
                    if print_value:
                        preview = str(item)
                        preview_str = preview[:limit_value_text] + ("..." if len(preview) > limit_value_text else "")
                        print(f"{indent}├─ [{i}] [ndarray] shape={shape} dtype={dtype}: {preview_str}")
                    else:
                        print(f"{indent}├─ [{i}] [ndarray] shape={shape} dtype={dtype}")
                else:
                    if print_value:
                        val_str = str(item)
                        short = val_str[:limit_value_text] + ("..." if len(val_str) > limit_value_text else "")
                        print(f"{indent}├─ [{i}] [{type(item).__name__}]: {short}")
                    else:
                        print(f"{indent}├─ [{i}] [{type(item).__name__}]")
            
            # 생략 표시
            omitted = L - 2 * n
            print(f"{indent}├─ ... ({omitted} items omitted)")
            
            # 뒤쪽 n개
            for j in range(L - n, L):
                item = dic_data[j]
                if isinstance(item, (dict, list, tuple)):
                    print(f"{indent}├─ [{j}] [{type(item).__name__}]")
                    print_dic_tree(item, indent + "│  ", max_depth, _depth + 1, list_count, print_value, limit_value_text)
                elif torch.is_tensor(item):
                    shape = tuple(item.shape)
                    dtype = str(item.dtype)
                    if print_value:
                        preview = str(item)
                        preview_str = preview[:limit_value_text] + ("..." if len(preview) > limit_value_text else "")
                        print(f"{indent}├─ [{j}] [Tensor] shape={shape} dtype={dtype}: {preview_str}")
                    else:
                        print(f"{indent}├─ [{j}] [Tensor] shape={shape} dtype={dtype}")
                elif isinstance(item, np.ndarray):
                    shape = item.shape
                    dtype = item.dtype
                    if print_value:
                        preview = str(item)
                        preview_str = preview[:limit_value_text] + ("..." if len(preview) > limit_value_text else "")
                        print(f"{indent}├─ [{j}] [ndarray] shape={shape} dtype={dtype}: {preview_str}")
                    else:
                        print(f"{indent}├─ [{j}] [ndarray] shape={shape} dtype={dtype}")
                else:
                    if print_value:
                        val_str = str(item)
                        short = val_str[:limit_value_text] + ("..." if len(val_str) > limit_value_text else "")
                        print(f"{indent}├─ [{j}] [{type(item).__name__}]: {short}")
                    else:
                        print(f"{indent}├─ [{j}] [{type(item).__name__}]")
        else:
            # 전체 출력
            for i, item in enumerate(dic_data):
                if isinstance(item, (dict, list, tuple)):
                    print(f"{indent}├─ [{i}] [{type(item).__name__}]")
                    print_dic_tree(item, indent + "│  ", max_depth, _depth + 1, list_count, print_value, limit_value_text)
                elif torch.is_tensor(item):
                    shape = tuple(item.shape)
                    dtype = str(item.dtype)
                    if print_value:
                        preview = str(item)
                        preview_str = preview[:limit_value_text] + ("..." if len(preview) > limit_value_text else "")
                        print(f"{indent}├─ [{i}] [Tensor] shape={shape} dtype={dtype}: {preview_str}")
                    else:
                        print(f"{indent}├─ [{i}] [Tensor] shape={shape} dtype={dtype}")
                elif isinstance(item, np.ndarray):
                    shape = item.shape
                    dtype = item.dtype
                    if print_value:
                        preview = str(item)
                        preview_str = preview[:limit_value_text] + ("..." if len(preview) > limit_value_text else "")
                        print(f"{indent}├─ [{i}] [ndarray] shape={shape} dtype={dtype}: {preview_str}")
                    else:
                        print(f"{indent}├─ [{i}] [ndarray] shape={shape} dtype={dtype}")
                else:
                    if print_value:
                        val_str = str(item)
                        short = val_str[:limit_value_text] + ("..." if len(val_str) > limit_value_text else "")
                        print(f"{indent}├─ [{i}] [{type(item).__name__}]: {short}")
                    else:
                        print(f"{indent}├─ [{i}] [{type(item).__name__}]")
    
    elif torch.is_tensor(dic_data):
        shape = tuple(dic_data.shape)
        dtype = str(dic_data.dtype)
        if print_value:
            preview = str(dic_data)
            preview_str = preview[:limit_value_text] + ("..." if len(preview) > limit_value_text else "")
            print(f"{indent}└─ Tensor shape={shape} dtype={dtype}")
            print(f"{indent}   {preview_str}")
        else:
            print(f"{indent}└─ Tensor shape={shape} dtype={dtype}")
    
    elif isinstance(dic_data, np.ndarray):
        shape = dic_data.shape
        dtype = dic_data.dtype
        if print_value:
            preview = str(dic_data)
            preview_str = preview[:limit_value_text] + ("..." if len(preview) > limit_value_text else "")
            print(f"{indent}└─ ndarray shape={shape} dtype={dtype}")
            print(f"{indent}   {preview_str}")
        else:
            print(f"{indent}└─ ndarray shape={shape} dtype={dtype}")
    
    else:
        if print_value:
            val_str = str(dic_data)
            short = val_str[:limit_value_text] + ("..." if len(val_str) > limit_value_text else "")
            print(f"{indent}└─ {type(dic_data).__name__}: {short}")
        else:
            print(f"{indent}└─ {type(dic_data).__name__}")

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

def create_tqdm(
    iterable: Optional[Any] = None,
    total: Optional[int] = None,
    desc: str = "Progress",
    **kwargs: Any
) -> tqdm:
    """
    Create tqdm progress bar with safe configuration.

    Args:
        iterable (Optional[Any], optional): Iterable object to track.
            Defaults to None.
        total (Optional[int], optional): Total count for manual updates.
            Used when iterable is None. Defaults to None.
        desc (str, optional): Description text. Defaults to "Progress".
        **kwargs (Any): Additional tqdm options.

    Returns:
        tqdm: Configured tqdm progress bar object.
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


def reset_tqdm(
    pbar: Optional[tqdm],
    iterable: Optional[Any] = None,
    total: Optional[int] = None,
    desc: Optional[str] = None,
    **kwargs: Any
) -> tqdm:
    """
    Reset existing tqdm object or create new one if None.

    Args:
        pbar (Optional[tqdm]): Existing tqdm object to reset.
        iterable (Optional[Any], optional): New iterable object. Defaults to None.
        total (Optional[int], optional): New total count. Defaults to None.
        desc (Optional[str], optional): New description text. Defaults to None.
        **kwargs (Any): Additional options.

    Returns:
        tqdm: Reset tqdm object.
    """
    if pbar is None:
        return create_tqdm(iterable, total, desc or "Progress", **kwargs)

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
    # _time은 protected이므로 직접 접근 대신 다른 방법 사용
    pbar.last_print_t = pbar.start_t

    # 추가 옵션 적용
    default_kwargs = get_tqdm_kwargs() if 'get_tqdm_kwargs' in globals() else {}
    default_kwargs.update(kwargs)

    for key, value in default_kwargs.items():
        if hasattr(pbar, key):
            setattr(pbar, key, value)

    pbar.refresh()
    return pbar


def create_or_reset_tqdm(
    pbar: Optional[tqdm] = None,
    iterable: Optional[Any] = None,
    total: Optional[int] = None,
    desc: str = "Progress",
    **kwargs: Any
) -> tqdm:
    """
    Create or reset tqdm progress bar (unified function).

    Args:
        pbar (Optional[tqdm], optional): Existing tqdm object. If None,
            create new one. Defaults to None.
        iterable (Optional[Any], optional): Iterable object. Defaults to None.
        total (Optional[int], optional): Total count. Defaults to None.
        desc (str, optional): Description text. Defaults to "Progress".
        **kwargs (Any): Additional tqdm options.

    Returns:
        tqdm: New or reset tqdm object.
    """
    if pbar is None:
        # 새로 생성
        return create_tqdm(iterable=iterable, total=total, desc=desc, **kwargs)
    else:
        # 기존 것 재설정
        return reset_tqdm(pbar, iterable=iterable, total=total, desc=desc, **kwargs)

##########################################################################################################

def unzip(
    zipfile_list: List[str],
    remove_zip: bool = False,
    skip_root: bool = False,
    normalize_nfc: bool = True,
    force_utf8: bool = False
) -> List[str]:
    """
    한글 파일명을 안전하게 압축 해제.
    
    Args:
        zipfile_list: ZIP 파일 경로 리스트
        remove_zip: 압축 해제 후 원본 ZIP 삭제 여부
        skip_root: 최상위 디렉토리 1개일 때 스킵 여부
        normalize_nfc: NFD → NFC 정규화 (macOS 호환)
        force_utf8: 인코딩 재해석 강제 (CP437/CP949/UTF-8)
    
    Returns:
        압축 해제된 디렉토리 경로 리스트
    """
    import unicodedata
    
    def _decode_filename(zip_info: zipfile.ZipInfo, name: str) -> str:
        """ZIP 파일명 인코딩 감지 및 디코딩."""
        # 1. UTF-8 플래그 확인
        if zip_info.flag_bits & 0x800:
            try:
                return name.encode('cp437').decode('utf-8')
            except (UnicodeDecodeError, UnicodeEncodeError):
                pass
        
        # 2. force_utf8 옵션: 다중 인코딩 시도
        if force_utf8:
            candidates = [
                ('utf-8', 'strict'),
                ('cp949', 'ignore'),
                ('euc_kr', 'ignore'),
                ('cp437', 'replace'),
            ]
            for enc, errors in candidates:
                try:
                    decoded = name.encode('cp437').decode(enc, errors=errors)
                    # 한글 범위 검증 (U+AC00 ~ U+D7A3)
                    if any('\uAC00' <= c <= '\uD7A3' for c in decoded):
                        return decoded
                except (UnicodeDecodeError, UnicodeEncodeError):
                    continue
        
        return name  # 실패 시 원본 반환

    unzip_paths = []

    for zip_path in zipfile_list:
        if not (os.path.exists(zip_path) and os.path.isfile(zip_path)):
            logger.warning(f"존재하지 않은 파일: {zip_path}")
            continue

        extract_dir = zip_path + ".unzip"
        unzip_paths.append(extract_dir)

        if os.path.exists(extract_dir):
            logger.info(f"이미 압축 해제됨: {extract_dir}")
            continue

        os.makedirs(extract_dir, exist_ok=True)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            members = zip_ref.infolist()

            # ========== skip_root 로직 ==========
            skip_prefix = ""
            if skip_root:
                top_level_dirs = set()
                for info in members:
                    name = info.filename
                    if name.startswith('__MACOSX') or name.startswith('.'):
                        continue
                    parts = name.split('/', 1)
                    if len(parts) > 0 and parts[0]:
                        top_level_dirs.add(parts[0])

                if len(top_level_dirs) == 1:
                    skip_prefix = list(top_level_dirs)[0] + '/'
                    logger.debug(f"최상위 디렉토리 스킵: {skip_prefix.rstrip('/')}")

            # ========== 압축 해제 ==========
            with tqdm(total=len(members), desc=f"압축 해제: {os.path.basename(zip_path)}", unit="file") as pbar:
                for info in members:
                    member_name_orig = info.filename

                    # 메타파일 건너뛰기
                    if member_name_orig.startswith('__MACOSX') or member_name_orig.startswith('.'):
                        pbar.update(1)
                        continue

                    # 1. 파일명 디코딩
                    member_name = _decode_filename(info, member_name_orig)

                    # 2. NFD → NFC 정규화
                    if normalize_nfc:
                        member_name = unicodedata.normalize('NFC', member_name)

                    # 3. 최상위 디렉토리 스킵
                    if skip_prefix and member_name_orig.startswith(skip_prefix):
                        relative_path = member_name_orig[len(skip_prefix):]
                        if not relative_path:
                            pbar.update(1)
                            continue
                        # 스킵된 경로도 디코딩/정규화
                        relative_path = _decode_filename(info, relative_path)
                        if normalize_nfc:
                            relative_path = unicodedata.normalize('NFC', relative_path)
                        member_name = relative_path

                    # 4. 추출 경로 (OS 구분자로 변환)
                    target_path = os.path.join(extract_dir, member_name.replace('/', os.sep))

                    # 5. 파일/디렉토리 추출
                    if info.is_dir():
                        os.makedirs(target_path, exist_ok=True)
                    else:
                        parent_dir = os.path.dirname(target_path)
                        if parent_dir:
                            os.makedirs(parent_dir, exist_ok=True)

                        with zip_ref.open(info) as source, open(target_path, 'wb') as target:
                            target.write(source.read())
                        
                        # logger.debug(f"추출: {member_name}")
                    
                    pbar.update(1)

            logger.info(f"압축 해제 완료: {extract_dir}")
        
        # 원본 zip 삭제
        if remove_zip:
            os.remove(zip_path)
            logger.info(f"원본 ZIP 삭제: {zip_path}")
    
    return unzip_paths

def zip_progress(
    input_path: Union[str, Path],
    zip_path: str,
    compression: Optional[int] = None
) -> Optional[str]:
    """
    한글 파일명을 UTF-8로 안전하게 압축 (ZIP with progress bar).

    NFC 정규화 및 UTF-8 플래그 설정으로 크로스 플랫폼 호환성 보장.

    Args:
        input_path (Union[str, Path]): 압축할 파일 또는 폴더 경로
        zip_path (str): 생성할 ZIP 파일 경로
        compression (Optional[int], optional): 압축 방식
            Defaults to zipfile.ZIP_DEFLATED.

    Returns:
        Optional[str]: 생성된 ZIP 파일 경로, 실패 시 None

    Example:
        >>> zip_progress("my_folder", "archive.zip")
        Zipping: 100%|████████████| 10/10 [00:00<00:00, 100.00file/s]
        'archive.zip'
    """
    import unicodedata
    
    input_path = Path(input_path)
    if not input_path.exists():
        logger.error(f"압축할 대상이 존재하지 않습니다: {input_path}")
        return None

    if compression is None:
        compression = zipfile.ZIP_DEFLATED

    # 압축 대상 파일 목록 생성
    if input_path.is_dir():
        files = [f for f in input_path.rglob('*') if f.is_file()]
    else:
        files = [input_path]

    if not files:
        logger.warning("압축할 파일이 없습니다.")
        return None

    # ZIP 파일 생성 (UTF-8 안전 압축)
    with zipfile.ZipFile(zip_path, 'w', compression, allowZip64=True) as zf:
        with tqdm(total=len(files), desc="Zipping", unit="file") as pbar:
            for file in files:
                # 압축 파일 내 상대 경로 계산
                arcname = str(file.relative_to(
                    input_path.parent if input_path.is_file() else input_path
                ))
                
                # NFC 정규화 (macOS NFD → Windows NFC)
                arcname = unicodedata.normalize('NFC', arcname)
                
                # ZipInfo 생성 및 UTF-8 플래그 설정
                info = zipfile.ZipInfo(arcname)
                info.flag_bits |= 0x800  # UTF-8 파일명 플래그
                
                # 파일 내용 읽어 압축
                with open(file, 'rb') as f:
                    zf.writestr(info, f.read(), compression)
                
                pbar.update(1)

    logger.info(f"UTF-8 안전 압축 완료: {zip_path}")
    return zip_path


##########################################################################################################

print('helper_utils.py loaded')
