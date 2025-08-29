---
layout: default
title: 테스트 리포트 히스토리
description: Helper Module 테스트 리포트 모음
date: 2025-08-29
cache-control: no-cache
expires: 0
pragma: no-cache
---

# 🧪 테스트 리포트 히스토리

<script>

{%- assign cur_dir = "/reports/" -%}
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

      // basename 추출 - 정규식 사용 안함
      let basename = page.name ? page.name.substring(0, page.name.lastIndexOf('.')) || page.name : '';

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

  // test_report_ 파일만 필터링하고 날짜순 정렬
  curFiles = curFiles.filter(file => 
    file.name && file.name.startsWith('test_report_') && file.extname === '.md'
  );

  curFiles.sort((a, b) => {
    // 파일명에서 날짜/시간 추출하여 최신순 정렬
    if (!a.name || !b.name) return 0;
    return b.name.localeCompare(a.name);
  });

  console.log('테스트 리포트 파일 수:', curFiles.length);
  console.log('리포트 목록:', curFiles);

  var project_path = site.baseurl || '';
  var site_url = 'https://c0z0c.github.io' + project_path + curDir;
  var raw_url = 'https://raw.githubusercontent.com/c0z0c' + project_path + '/master' + curDir;
  var git_url = 'https://github.com/c0z0c' + project_path + '/blob/master' + curDir;
  
  console.log('site_url:', site_url);
  console.log('raw_url:', raw_url);
  console.log('git_url:', git_url);

  // 파일명에서 날짜/시간 파싱 함수
  function parseReportDate(filename) {
    // test_report_20250803_142530.md 형식에서 날짜/시간 추출
    // 정규 표현식 대신 문자열 처리 방식 사용
    if (!filename || !filename.includes('test_report_')) {
      return { date: '', time: '', formatted: '날짜 미상' };
    }
    
    // test_report_ 이후 부분 추출
    const parts = filename.replace('test_report_', '').replace('.md', '').split('_');
    if (parts.length !== 2) {
      return { date: '', time: '', formatted: '날짜 미상' };
    }
    
    const dateStr = parts[0]; // 20250803
    const timeStr = parts[1]; // 142530
    
    if (dateStr.length !== 8 || timeStr.length !== 6) {
      return { date: '', time: '', formatted: '날짜 미상' };
    }
    
    const year = dateStr.substring(0, 4);
    const month = dateStr.substring(4, 6);
    const day = dateStr.substring(6, 8);
    const hour = timeStr.substring(0, 2);
    const minute = timeStr.substring(2, 4);
    
    return {
      date: dateStr,
      time: timeStr,
      formatted: year + '년 ' + month + '월 ' + day + '일 ' + hour + ':' + minute
    };
  }

  // 리포트 설명 생성 함수
  function getReportDescription(index, total) {
    if (index === 0) {
      return 'v2.3.0 완전 테스트 - 37개 테스트 모두 통과';
    } else if (index === 1) {
      return '캐시 기능 및 DataFrame 커밋 시스템 검증';
    } else if (index === 2) {
      return 'DataCatch 클래스 및 캐시 관리 기능 검증';
    } else if (index === 3) {
      return '한글 컬럼 설명 및 출력 형식 검증';
    } else if (index === 4) {
      return 'Colab, 로컬 환경 호환성 검증';
    } else {
      return '기본 기능 및 한글 폰트 설정 검증';
    }
  }

  // DOM이 로드된 후 리포트 목록 렌더링
  document.addEventListener('DOMContentLoaded', function() {
    const reportGrid = document.querySelector('.report-grid');
    
    if (curFiles.length === 0) {
      reportGrid.innerHTML = '<div class="empty-message">' +
        '<span class="empty-icon">🔍</span>' +
        '<h3>테스트 리포트가 없습니다</h3>' +
        '<p>현재 이 위치에는 테스트 리포트가 없습니다.</p>' +
        '</div>';
      return;
    }

    // 요약 정보 업데이트
    const summaryElement = document.querySelector('.summary');
    if (summaryElement) {
      summaryElement.innerHTML = '<h3><span class="emoji">📊</span> 테스트 요약</h3>' +
        '<p>Helper Module v2.3.0의 안정성과 신뢰성을 보장하기 위한 지속적인 테스트 결과입니다.</p>' +
        '<ul>' +
        '<li><strong>총 리포트 수:</strong> ' + curFiles.length + '개</li>' +
        '<li><strong>최신 테스트:</strong> 37개 테스트 모두 통과 (100% 성공률)</li>' +
        '<li><strong>테스트 범위:</strong> 캐시 기능, pandas 확장, DataFrame 커밋, 파일 처리, 에러 핸들링</li>' +
        '<li><strong>플랫폼 지원:</strong> Windows, Ubuntu, Mac 크로스 플랫폼 검증</li>' +
        '</ul>';
    }

    // 리포트 테이블 생성
    let html = '<table class="report-table">' +
      '<thead>' +
      '<tr>' +
      '<th>리포트 제목</th>' +
      '<th>테스트 날짜</th>' +
      '<th>설명</th>' +
      '<th>상태</th>' +
      '</tr>' +
      '</thead>' +
      '<tbody>';
    
    curFiles.forEach((file, index) => {
      if (file.name === 'index.md') return;

      const dateInfo = parseReportDate(file.name);
      const description = getReportDescription(index, curFiles.length);
      const reportUrl = site_url + file.path.replace('.md', '');
      const isLatest = index === 0;
      const reportIcon = isLatest ? '🆕' : (index <= 2 ? '🔧' : '🚀');
      const reportTitle = isLatest ? '최신 테스트 리포트' : '테스트 리포트 #' + (curFiles.length - index);
      
      html += '<tr>' +
        '<td>' +
        '<a href="' + reportUrl + '" class="report-link">' +
        '<span class="emoji">' + reportIcon + '</span>' +
        reportTitle +
        '</a>' +
        (isLatest ? '<span class="latest-badge">NEW</span>' : '') +
        '</td>' +
        '<td>' + dateInfo.formatted + '</td>' +
        '<td>' + description + '</td>' +
        '<td>' +
        '<span class="status-badge">✅ ' + (isLatest ? '100% 통과' : '통과') + '</span>' +
        '</td>' +
        '</tr>';
    });
    
    html += '</tbody></table>';
    
    reportGrid.innerHTML = html;
  });
</script>

<!-- 나머지 HTML 내용은 그대로 유지 -->
<div class="summary">
  <h3><span class="emoji">📊</span> 테스트 요약</h3>
  <p>Helper Module v2.3.0의 안정성과 신뢰성을 보장하기 위한 지속적인 테스트 결과입니다.</p>
  <ul>
    <li><strong>최신 테스트:</strong> 37개 테스트 모두 통과 (100% 성공률)</li>
    <li><strong>테스트 범위:</strong> 캐시 기능, pandas 확장, DataFrame 커밋, 파일 처리, 에러 핸들링</li>
    <li><strong>플랫폼 지원:</strong> Windows, Ubuntu, Mac 크로스 플랫폼 검증</li>
  </ul>
</div>

<h2><span class="emoji">📅</span> 테스트 리포트 목록</h2>

<div class="report-grid">
  <!-- 리포트 목록이 JavaScript로 동적 생성됩니다 -->
</div>

<h2><span class="emoji">📈</span> 테스트 발전 과정</h2>

<div style="background: #404040; padding: 20px; border-radius: 10px; margin: 20px 0; border: 1px solid #555;">
  <h4>2025년 8월 3일 - v2.3.0 최종 검증</h4>
  <ul>
    <li>37개 전체 테스트 항목 완성</li>
    <li>DataFrame 커밋 시스템 완전 검증</li>
    <li>크로스 플랫폼 지원 확인</li>
    <li>100% 테스트 통과율 달성</li>
  </ul>
</div>

<div style="background: #404040; padding: 20px; border-radius: 10px; margin: 20px 0; border: 1px solid #555;">
  <h4>2025년 7월 25일 - 캐시 시스템 강화</h4>
  <ul>
    <li>DataCatch 클래스 도입</li>
    <li>JSON 직렬화 기반 안정적 캐시</li>
    <li>복잡한 객체 저장 지원</li>
    <li>환경별 캐시 경로 최적화</li>
  </ul>
</div>

<div style="background: #404040; padding: 20px; border-radius: 10px; margin: 20px 0; border: 1px solid #555;">
  <h4>2025년 7월 22일 - 기초 안정성 확립</h4>
  <ul>
    <li>기본 환경 설정 검증</li>
    <li>한글 폰트 자동 설치</li>
    <li>pandas 확장 기능 구현</li>
    <li>파일 읽기 유틸리티 완성</li>
  </ul>
</div>

---

<div class="navigation-footer">
  <a href="{{- site.baseurl -}}/" class="nav-button home">
    <span class="nav-icon">🏠</span> 홈으로
  </a>
</div>