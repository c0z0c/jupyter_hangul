---
layout: default
title: Jupyter 한글 환경 설정 모듈
description: Jupyter Notebook과 Google Colab에서 한글 폰트 설정, pandas 확장 기능, 데이터 캐시를 제공하는 모듈
date: 2025-08-29
cache-control: no-cache
expires: 0
pragma: no-cache
---

<script>
{%- assign cur_dir = "/docs/" -%}
{%- include cur_files.liquid -%}

  var curDir = '{{- cur_file_dir -}}';
  var curFiles = {{- cur_files_json -}};
  var curPages = {{- cur_pages_json -}};
  
  console.log('curDir:', curDir);
  console.log('curFiles:', curFiles);
  console.log('curPages:', curPages);

  curPages.forEach(page => {
    // curFiles에 같은 name과 path가 있는지 확인
    const exists = curFiles.some(file => file.name === page.name && file.path === page.path);

    if (!exists) {
      // 확장자 추출
      let extname = '';
      if (page.name && page.name.includes('.')) {
        extname = '.' + page.name.split('.').pop();
      }

      // basename 추출
      let basename = page.name ? page.name.replace(/\.[^/.]+$/, '') : '';

      // modified_time 처리 (page.date가 없으면 빈 문자열)
      let modified_time = page.date || '';

      // curFiles 포맷에 맞게 변환해서 추가
      curFiles.push({
        name: page.name || '',
        path: page.path || '',
        extname: extname,
        modified_time: modified_time,
        basename: basename,
        url: page.url || ''
      });
    }
  });

  var project_path = site.baseurl || '';
  var site_url = `https://c0z0c.github.io${project_path}`;
  var git_url = `https://github.com/c0z0c${project_path}`;
  
  console.log('site_url:', site_url);
  console.log('git_url:', git_url);

  // 최신 테스트 리포트 찾기
  function getLatestTestReport() {
    const testReports = curFiles.filter(file => 
      file.name && file.name.startsWith('test_report_') && file.extname === '.md'
    );
    
    if (testReports.length === 0) return null;
    
    testReports.sort((a, b) => b.name.localeCompare(a.name));
    return testReports[0];
  }

  // DOM이 로드된 후 동적 콘텐츠 업데이트
  document.addEventListener('DOMContentLoaded', function() {
    // 메인 호스팅 페이지 링크 업데이트
    const mainLink = document.querySelector('.main-link');
    if (mainLink) {
      mainLink.href = 'https://c0z0c.github.io/';
    }

    // GitHub 저장소 링크 업데이트
    const githubLink = document.querySelector('.github-link');
    if (githubLink) {
      githubLink.href = git_url;
    }

    // 네비게이션 링크들 업데이트
    const navLinks = {
      '.readme-link': `${site_url}/md/README`,
      '.cheatsheet-link': `${site_url}/md/CHEATSHEET`,
      '.colab-link': `${site_url}/md/COLAB_USAGE`,
      '.reports-link': `${site_url}/reports/`
    };

    Object.entries(navLinks).forEach(([selector, url]) => {
      const element = document.querySelector(selector);
      if (element) {
        element.href = url;
      }
    });

    // 최신 테스트 리포트 정보 업데이트
    const latestReport = getLatestTestReport();
    const reportItems = document.querySelectorAll('.report-item a');
    
    if (latestReport && reportItems.length > 0) {
      // 첫 번째 리포트 아이템 업데이트
      const firstReportLink = reportItems[0];
      if (firstReportLink) {
        firstReportLink.href = latestReport.url || latestReport.path.replace('.md', '');
      }
    }

    // 리소스 링크들 업데이트
    const resourceLinks = {
      '.tutorial-link': 'https://youtu.be/C6XRhqoKBc4',
      '.repository-link': git_url,
      '.docs-link': `${site_url}/md/README`,
      '.reference-link': `${site_url}/md/CHEATSHEET`
    };

    Object.entries(resourceLinks).forEach(([selector, url]) => {
      const element = document.querySelector(selector);
      if (element) {
        element.href = url;
      }
    });
  });
</script>

<div style="text-align: center; margin-bottom: 20px;">
    <a href="https://c0z0c.github.io/" class="main-link" style="color: #87ceeb; text-decoration: none; font-weight: bold;">
        🏠 c0z0c 메인 호스팅 페이지
    </a>
    |
    <a href="https://github.com/c0z0c{{ site.baseurl }}" class="github-link" style="color: #87ceeb; text-decoration: none;">
        📂 GitHub 저장소
    </a>
</div>

# <span class="emoji">🚀</span> Jupyter 한글 환경 설정 모듈 v2.4.0

<div class="highlight">
    <strong><span class="emoji">🎯</span> 빠른 사용법:</strong> <code>helper.setup()</code> 한 번으로 모든 설정 완료!
</div>

Jupyter Notebook과 Google Colab에서 한글 폰트 설정, pandas 확장 기능, 데이터 캐시를 제공하는 모듈입니다.

<div class="nav-links">
    <a href="{{ site.baseurl }}/md/README" class="nav-card readme-link">
        <h3><span class="emoji">📖</span> 전체 문서</h3>
        <p>상세한 사용법과 API 문서</p>
    </a>
    <a href="{{ site.baseurl }}/md/CHEATSHEET" class="nav-card cheatsheet-link">
        <h3><span class="emoji">📋</span> 치트시트</h3>
        <p>빠른 참조 가이드</p>
    </a>
    <a href="{{ site.baseurl }}/md/COLAB_USAGE" class="nav-card colab-link">
        <h3><span class="emoji">🌐</span> Colab 가이드</h3>
        <p>Google Colab 전용 사용법</p>
    </a>
    <a href="{{ site.baseurl }}/reports/" class="nav-card reports-link">
        <h3><span class="emoji">🧪</span> 테스트 리포트</h3>
        <p>모듈 안정성 검증 결과</p>
    </a>
</div>

## <span class="emoji">🆕</span> v2.4.0 주요 업데이트 <span class="update-badge">NEW</span>

<div class="features">
    <div class="feature">
        <div class="feature-icon">💾</div>
        <h3>캐시 기능</h3>
        <p>데이터/모델 저장으로 재실행 시간 단축</p>
    </div>
    <div class="feature">
        <div class="feature-icon">🌐</div>
        <h3>크로스 플랫폼</h3>
        <p>Windows, Ubuntu, Mac 모든 환경 지원</p>
    </div>
    <div class="feature">
        <div class="feature-icon">🧪</div>
        <h3>37개 유닛 테스트</h3>
        <p>100% 통과로 안정성 보장</p>
    </div>
    <div class="feature">
        <div class="feature-icon">📊</div>
        <h3>pandas 확장</h3>
        <p>DataFrame.head_att() 등 한글 지원</p>
    </div>
</div>

## <span class="emoji">⚡</span> 빠른 시작

```python
# 모듈 다운로드 및 import (한 번에 모든 설정 완료)
from urllib.request import urlretrieve; urlretrieve("https://raw.githubusercontent.com/c0z0c/jupyter_hangul/refs/heads/beta/helper_c0z0c_dev.py", "helper_c0z0c_dev.py")
import helper_c0z0c_dev as helper

# 출력 예시:
# 🚀 Jupyter/Colab 한글 환경 설정 중... (helper v2.4.0)
# ✅ 한글 폰트 및 pandas 확장 기능 설정 완료
# 🎉 사용 가능: 한글 폰트, CSV 읽기, DataFrame.head_att(), 캐시 기능
```

## <span class="emoji">💡</span> 주요 기능

- **🎨 한글 폰트 자동 설정:** NanumGothic 폰트를 자동으로 다운로드하고 matplotlib에 적용
- **📊 pandas 확장 기능:** DataFrame/Series에 한글 컬럼 설명 기능 추가
- **💾 캐시 기능:** ML 모델 및 데이터 캐싱 시스템
- **📝 DataFrame 커밋:** git처럼 DataFrame 버전 관리
- **🔧 편의 함수들:** 파일 읽기, 라이브러리 도움말 검색 등

## <span class="emoji">🧪</span> 테스트 리포트

<div class="reports-section">
    <p>모듈의 안정성과 신뢰성을 보장하기 위한 지속적인 테스트 결과입니다.</p>
    
    <div class="report-list">
        <div class="report-item">
            <h4><a href="{{ site.baseurl }}/reports/">최신 테스트 리포트</a></h4>
            <p class="report-date">자동 업데이트</p>
            <p><strong>37개 테스트 모두 통과</strong> - v2.4.0 안정성 검증</p>
        </div>
        <div class="report-item">
            <h4><a href="{{ site.baseurl }}/reports/">전체 테스트 히스토리</a></h4>
            <p class="report-date">2025년 7월 ~ 8월</p>
            <p>모든 버전별 테스트 결과 및 개선 과정</p>
        </div>
    </div>
</div>

## <span class="emoji">🌍</span> 환경 지원

- ✅ Google Colab (자동 감지)
- ✅ Windows (UTF-8 설정 자동 적용)
- ✅ Ubuntu/Linux (호환성 보장)
- ✅ macOS (호환성 보장)

## <span class="emoji">📚</span> 리소스

- <a href="https://youtu.be/C6XRhqoKBc4" class="tutorial-link">YouTube 튜토리얼</a>
- <a href="https://github.com/c0z0c/jupyter_hangul" class="repository-link">GitHub 저장소</a>
- <a href="{{ site.baseurl }}/md/README" class="docs-link">상세 문서</a>
- <a href="{{ site.baseurl }}/md/CHEATSHEET" class="reference-link">빠른 참조</a>

---

<div class="footer-info">
    <p>© 2025 Helper Module v2.4.0 | 감사 인사: 조하나 강사님</p>
    <p>Last updated: 2025년 8월 29일</p>
</div>