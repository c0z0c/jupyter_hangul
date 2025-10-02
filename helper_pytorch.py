def show_image(data, idx, row_count=1, col_count=1, zoom=True):
    """
    데이터셋에서 이미지를 행렬 형태(여러 행, 여러 열)로 시각화합니다.
    
    data: 이미지와 레이블이 포함된 데이터셋
    idx: 시작 인덱스
    row_count: 행 개수 (기본값 1)
    col_count: 열 개수 (기본값 1)
    zoom: 확대 여부 (기본값 True)
    """

    if zoom:
        col_size = 2 * col_count
        row_size = 2 * row_count
    else:
        img, _ = data[0]
        width, height = img.size
        col_size = math.ceil(col_count * width / 100)  # 1인치=100픽셀로 가정
        row_size = math.ceil(row_count * height / 100)  # 1인치=100픽셀로 가정

    fig, axes = plt.subplots(row_count, col_count, figsize=(col_size, row_size), dpi=100)
    axes = axes.flatten() if hasattr(axes, 'flatten') else [axes]

    labels = []
    for i in range(row_count * col_count):
        if (i + idx) >= len(data):
            break
        img, label = data[i + idx]
        
        eng = data.classes[label]
        labels.append(f"{eng}")
        
        paxes = axes if row_count * col_count == 1 else axes[i]
        paxes.imshow(img)
        if zoom:
            paxes.set_title(f'{eng}')
        paxes.set_xticks([])
        paxes.set_yticks([])
        paxes.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
        paxes.axis('on')  # 테두리

    if zoom is False:
        grid = [labels[i*col_count:(i+1)*col_count] for i in range(row_count)]
        df = pd.DataFrame(grid)
        df.head_att(row_count)
        
    plt.tight_layout()
    plt.show()

