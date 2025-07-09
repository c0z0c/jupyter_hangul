1. notebook_template.ipynb을 참고하세요
2. matplotlib.pyplot 에서 한글을 사용할 수 있도록 해주는 로직입니다.
   - colab은 프로세서 재시작이 있습니다.
   - jupyter는 다른 폴더마다 font를 다운로드 받을 수 있습니다.
     = 다운로드 및 폰트 경로를 수정하세요

3. colab, jupyter 구분 할 수 있는 변수 추가
- 예)
<pre>
if is_colab:
    df = pd.read_csv(r'/content/drive/MyDrive/codeit/data/body.csv')
else:
    df = pd.read_csv(r'data\body.csv')
</pre>
