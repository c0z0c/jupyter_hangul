---
layout: default
title: 테스트 리포트 히스토리
cache-control: no-cache
expires: 0
pragma: no-cache
---

<style>
/* 리포트 페이지 전용 스타일 */
.reports-grid {
    margin: 30px 0;
}
.report-table {
    width: 100%;
    border-collapse: collapse;
    margin: 20px 0;
    background: white;
    border-radius: 10px;
    overflow: hidden;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}
.report-table th {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 15px;
    text-align: left;
    font-weight: bold;
}
.report-table td {
    padding: 15px;
    border-bottom: 1px solid #eee;
    vertical-align: top;
}
.report-table tr:hover {
    background-color: #f8f9fa;
}
.report-table tr:last-child td {
    border-bottom: none;
}
.report-link {
    color: #3498db;
    text-decoration: none;
    font-weight: bold;
    transition: color 0.3s;
}
.report-link:hover {
    color: #2980b9;
    text-decoration: underline;
}
.status-badge {
    background: #27ae60;
    color: white;
    padding: 4px 8px;
    border-radius: 12px;
    font-size: 0.8em;
    font-weight: bold;
}
.latest-badge {
    background: #e74c3c;
    color: white;
    padding: 4px 8px;
    border-radius: 12px;
    font-size: 0.8em;
    font-weight: bold;
    margin-left: 10px;
}
.summary {
    background: #e8f5e8;
    padding: 20px;
    border-radius: 10px;
    border-left: 5px solid #27ae60;
    margin: 20px 0;
}
</style>

<div class="container">

    <h1 style="text-align: center;"><span class="emoji">🧪</span> 테스트 리포트 히스토리</h1>
    
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
    
    <div class="reports-grid">
        {% assign all_files = site.static_files | where: "extname", ".md" %}
        {% assign reports = all_files | where_exp: "item", "item.path contains '/reports/test_report_'" | sort: "name" %}
        {% if reports.size == 0 %}
            {% comment %} Fallback: GitHub Pages 빌드 시 static_files를 못 찾는 경우 {% endcomment %}
            {% assign reports = site.pages | where_exp: "page", "page.path contains 'reports/test_report_'" | sort: "path" %}
        {% endif %}
        
        {% if reports.size > 0 %}
            <table class="report-table">
                <thead>
                    <tr>
                        <th>리포트 제목</th>
                        <th>테스트 날짜</th>
                        <th>설명</th>
                        <th>상태</th>
                    </tr>
                </thead>
                <tbody>
                    {% for report in reports %}
                        {% assign filename = report.path | split: "/" | last %}
                        {% if filename contains "test_report_" %}
                            {% assign name_parts = filename | replace: ".md", "" | split: "_" %}
                            {% assign date_part = name_parts[2] %}
                            {% assign time_part = name_parts[3] %}
                            
                            {% assign year = date_part | slice: 0, 4 %}
                            {% assign month = date_part | slice: 4, 2 %}
                            {% assign day = date_part | slice: 6, 2 %}
                            {% assign hour = time_part | slice: 0, 2 %}
                            {% assign minute = time_part | slice: 2, 2 %}
                            {% assign second = time_part | slice: 4, 2 %}
                            
                            {% assign formatted_date = year | append: "년 " | append: month | append: "월 " | append: day | append: "일 " | append: hour | append: ":" | append: minute %}
                            
                            <tr>
                                <td>
                                    <a href="{{ report.path | replace: '.md', '' | relative_url }}" class="report-link">
                                        <span class="emoji">{% if forloop.first %}🆕{% elsif forloop.index <= 3 %}🔧{% else %}🚀{% endif %}</span>
                                        {% if forloop.first %}최신 테스트 리포트{% else %}테스트 리포트 #{{ forloop.rindex }}{% endif %}
                                    </a>
                                    {% if forloop.first %}<span class="latest-badge">NEW</span>{% endif %}
                                </td>
                                <td>{{ formatted_date }}</td>
                                <td>
                                    {% if forloop.first %}
                                        v2.3.0 완전 테스트 - 37개 테스트 모두 통과
                                    {% elsif forloop.index == 2 %}
                                        캐시 기능 및 DataFrame 커밋 시스템 검증
                                    {% elsif forloop.index == 3 %}
                                        DataCatch 클래스 및 캐시 관리 기능 검증
                                    {% elsif forloop.index == 4 %}
                                        한글 컬럼 설명 및 출력 형식 검증
                                    {% elsif forloop.index == 5 %}
                                        Colab, 로컬 환경 호환성 검증
                                    {% else %}
                                        기본 기능 및 한글 폰트 설정 검증
                                    {% endif %}
                                </td>
                                <td>
                                    <span class="status-badge">✅ {% if forloop.first %}100% 통과{% else %}통과{% endif %}</span>
                                </td>
                            </tr>
                        {% endif %}
                    {% endfor %}
                </tbody>
            </table>
        {% else %}
            <div style="text-align: center; padding: 40px; color: #666;">
                <p>🔍 테스트 리포트를 찾을 수 없습니다.</p>
                <p>Jekyll 빌드 중이거나 파일이 아직 처리되지 않았을 수 있습니다.</p>
            </div>
        {% endif %}
    </div>

    <h2><span class="emoji">📈</span> 테스트 발전 과정</h2>
    
    <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0;">
        <h4>2025년 8월 3일 - v2.3.0 최종 검증</h4>
        <ul>
            <li>37개 전체 테스트 항목 완성</li>
            <li>DataFrame 커밋 시스템 완전 검증</li>
            <li>크로스 플랫폼 지원 확인</li>
            <li>100% 테스트 통과율 달성</li>
        </ul>
    </div>
    
    <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0;">
        <h4>2025년 7월 25일 - 캐시 시스템 강화</h4>
        <ul>
            <li>DataCatch 클래스 도입</li>
            <li>JSON 직렬화 기반 안정적 캐시</li>
            <li>복잡한 객체 저장 지원</li>
            <li>환경별 캐시 경로 최적화</li>
        </ul>
    </div>
    
    <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0;">
        <h4>2025년 7월 22일 - 기초 안정성 확립</h4>
        <ul>
            <li>기본 환경 설정 검증</li>
            <li>한글 폰트 자동 설치</li>
            <li>pandas 확장 기능 구현</li>
            <li>파일 읽기 유틸리티 완성</li>
        </ul>
    </div>

    <footer style="text-align: center; margin-top: 50px; padding-top: 20px; border-top: 1px solid #eee; color: #7f8c8d;">
        <p>© 2025 Helper Module Test Reports</p>
        <p><a href="{{ site.baseurl }}/">홈으로 돌아가기</a></p>
    </footer>
</div>
