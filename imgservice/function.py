import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import io
# import base64

# Dữ liệu mẫu
# data = [
#     {"id": 5, "sp": "name:tên 2,quantity:2,price:20000.0\nname:tên them2,quantity:1,price:40300.0\n", "ngaytao": "20240422161742"},
#     {"id": 6, "sp": "name:tên 2,quantity:2,price:20000.0\nname:tên them2,quantity:1,price:40300.0\n", "ngaytao": "20240428161742"},
#     {"id": 8, "sp": "name:tên them7,quantity:1,price:40300.0\nname:tên 1,quantity:1,price:10000.0\nname:tên 2,quantity:1,price:20000.0\nname:sản phẩm id 22aa,quantity:1,price:401111.0\nname:tên them 23,quantity:1,price:40.0\nname:tên them 24,quantity:1,price:40.0\n", "ngaytao": "20240430161742"},
#     {"id": 11, "sp": "name:Winter Zipper,quantity:1,price:400000.0\n", "ngaytao": "20240503063452"},
#     {"id": 12, "sp": "name:Trench Winter Coat,quantity:1,price:120000.0\nname:sản phẩm id 22aa,quantity:1,price:400000.0\nname:tên 1,quantity:2,price:100000.0\n", "ngaytao": "20240503063803"},
#     {"id": 13, "sp": "name:The Trench Winter Coa,quantity:2,price:100000.0\nname:Winter Zipper,quantity:1,price:400000.0\n", "ngaytao": "20240504151537"},
#     {"id": 14, "sp": "name:Winter Zipper,quantity:10,price:400000.0\nname:The Trench Winter Coa,quantity:1,price:100000.0\n", "ngaytao": "20240504152031"},
#     {"id": 15, "sp": "name:The Trench Winter Coa,quantity:3,price:100000.0\nname:Winter Zipper,quantity:2,price:400000.0\n", "ngaytao": "20240907011824"}
# ]

# Hàm phân tích xu hướng sản phẩm và thực hiện tìm đường hồi quy
def analyze_and_predict(data,product_name):
    product_data = []

    # Trích xuất chi tiết sản phẩm và lọc theo tên sản phẩm
    for record in data:
        date = datetime.strptime(record["ngaytao"], "%Y%m%d%H%M%S")  # Chuyển đổi chuỗi ngày giờ thành đối tượng datetime
        items = record["sp"].split("|")  # Tách các sản phẩm

        for item in items:
            if item:
                # Phân tích chi tiết sản phẩm
                details = {kv.split(":")[0]: kv.split(":")[1] for kv in item.split(",")}
                if details["name"] == product_name:
                    product_data.append({"date": date, "quantity": int(details["quantity"])})

    # Kiểm tra nếu không có dữ liệu
    if not product_data:
        # print(f"Không có dữ liệu cho sản phẩm '{product_name}'")
        
        # Tạo hình ảnh trắng trả về
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, 'No Data Available', horizontalalignment='center', verticalalignment='center', fontsize=15)
        ax.axis('off')  # Tắt trục
        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plt.close(fig)
        
        return img, None  # Trả về ảnh trắng và None cho hệ số góc

    # Chuyển đổi dữ liệu thành DataFrame
    df = pd.DataFrame(product_data)
    
    # Sắp xếp theo ngày
    df = df.sort_values(by="date")
    
    if df.empty:
        print(f"Không có dữ liệu cho sản phẩm '{product_name}'")
        return None, None

    # Hồi quy tuyến tính
    x = np.array([date.timestamp() for date in df["date"]])  # Chuyển ngày thành giá trị số
    y = df["quantity"].values

    # Tính toán hệ số góc (m) và điểm cắt (b)
    N = x.shape[0]
    m = (N * np.sum(x * y) - np.sum(x) * np.sum(y)) / (N * np.sum(x ** 2) - (np.sum(x) ** 2))
    b = (np.sum(y) - m * np.sum(x)) / N

    # print(f"Hệ số góc (m): {m}, Điểm cắt (b): {b}")

    # so sánh mức độ tăng trưởng trong tương lai
    threshold = 1e-6
    status = {"text": "null", "color": "yellow"}
    if m > threshold:
        status["text"] = "tăng nhanh."
        status["color"] = "green"
    elif m > 0:
        status["text"] = "tăng chậm."
        status["color"] = "green"
    elif m < -threshold:
        status["text"] = "giảm nhanh."
        status["color"] = "red"
    elif m < 0:
        status["text"] = "giảm chậm."
        status["color"] = "red"
    else:
        status["text"] = "Không có sự thay đổi rõ rệt."

    # Vẽ đường hồi quy
    x_min = np.min(x)
    y_min = m * x_min + b
    x_max = np.max(x)
    y_max = m * x_max + b

    fig, ax = plt.subplots()
    sns.scatterplot(data=df, x="date", y="quantity", ax=ax, alpha=0.4)
    sns.lineplot(x=[datetime.fromtimestamp(x_min), datetime.fromtimestamp(x_max)],
                 y=[y_min, y_max], linewidth=1.5, color=status["color"])
    



    # Hiển thị giá trị độ dốc và điểm cắt trên biểu đồ
    plt.text(datetime.fromtimestamp(x_min), (y_min+1), f'Slope (m): {m:.10f} ', fontsize=12, ha='left', color=status["color"])
    # plt.text(datetime.fromtimestamp(x_max), y_max, f'Intercept (b): {b:.2f}', fontsize=12, ha='right', color='red')

    # Đổi tên trục X và Y
    plt.xlabel('Thời gian ', fontsize=8)  
    plt.ylabel('Số lượng', fontsize=8) 

    plt.title(f"Đường hồi quy cho sản phẩm '{product_name}' \n có xu hướng {status["text"]} trong tương lai", fontsize=8)
    plt.xticks(rotation=45,fontsize=8)
    plt.tight_layout()
   

    # Lưu biểu đồ vào một đối tượng BytesIO
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    
    # Chuyển đổi hình ảnh thành chuỗi base64
    # img_base64 = base64.b64encode(img.getvalue()).decode('utf-8')
    
    # Đóng biểu đồ để giải phóng bộ nhớ
    plt.close(fig)
    
    return img, m 

# # Gọi hàm để phân tích và dự đoán cho sản phẩm "Winter Zipper"
# img_base64, slope = analyze_and_predict("Winter Zipper")

# # Ví dụ in ra giá trị độ dốc và ảnh biểu đồ
# print(f"Slope: {slope}")
# print(f"Image (Base64): {img_base64}")


###########
# hàm đếm lọc và đếm số lượng từng sản phẩm
import re
from collections import defaultdict


def extract_and_count_products(data):
    product_counts = defaultdict(int)
    
    # Duyệt qua từng phần tử trong data
    for entry in data:
        sp_data = entry["sp"]
        
        # Sử dụng regex để lấy tên sản phẩm và số lượng
        products = re.findall(r'name:(.*?),quantity:(\d+),', sp_data)
        
        # Cộng dồn số lượng từng sản phẩm
        for product in products:
            product_name = product[0].strip()
            quantity = int(product[1])
            product_counts[product_name] += quantity
    
    # Chuyển từ defaultdict thành danh sách các đối tượng
    result = [{"name": name, "total_quantity": total_quantity} for name, total_quantity in product_counts.items()]
    
    return result


# output = extract_and_count_products(data)
# print(output)
