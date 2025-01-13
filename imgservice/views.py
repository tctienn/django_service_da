from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse  # Thêm dòng này cho việc lấy dữ liệu từ các request

from imgservice.function import analyze_and_predict
from imgservice.function import extract_and_count_products

import base64


@api_view(['POST'])
def get_data(request):
    name = request.GET.get('name')  # Lấy 'name' từ query parameters
    
    if not name:
        return Response({'error': 'Thiếu giá trị name : '}, status=400)
    # Gọi hàm để phân tích và dự đoán cho sản phẩm "Winter Zipper"
    try:
        img, slope,product_data = analyze_and_predict(request.data,name)
        
        # Tạo một HttpResponse để trả về ảnh trực tiếp
        # response = HttpResponse(img, content_type='image/png')
        # response['Content-Disposition'] = 'attachment; filename="chart.png"'
        # return response
        #trả về dạng base64
        img_base64 = base64.b64encode(img.getvalue()).decode('utf-8')
        return Response({
        'image': img_base64,
        'data': product_data,
        'nameProduct':name
    })
    except Exception as e:
        return Response({'error': str(e)}, status=500)


# đếm số lượng sản phẩm trong danh sách hóa đơn
@api_view(['POST'])
def post_count_product(request):
    try:

        body_data = request.data
        # body_data = json.loads(request.body)
        arr_data_coutn = extract_and_count_products(body_data)
        
        return JsonResponse({
            # 'message': 'Success',
         
            'data': arr_data_coutn
        })
    except Exception as e:
        return Response({'error': str(e)}, status=500)
    





# ///// demo chức năng thanh toán với momo 
# ------ Phần Momo QR Payment Integration ------
import json
import uuid
import requests
import hmac
import hashlib

# Các thông tin cấu hình
endpoint = "https://test-payment.momo.vn/v2/gateway/api/create"
partnerCode = "MOMO"
accessKey = "F8BBA842ECF85"
secretKey = "K951B6PE1waDMi640xX08PD3vg6EkVlz"
orderInfo = "Thanh toán qua MoMo QR"
redirectUrl = "https://your-redirect-url.com"  # URL sau khi thanh toán xong
ipnUrl = "https://your-ipn-url.com"  # URL để nhận thông báo giao dịch
amount = "50000"  # Số tiền cần thanh toán (đơn vị VND)

def create_momo_payment():
    # Tạo thông tin đơn hàng
    orderId = str(uuid.uuid4())
    requestId = str(uuid.uuid4())
    # phương thức thanh toán captureWallet
    requestType = "payWithATM" 
    extraData = ""  # Có thể truyền thêm dữ liệu tùy chọn
    # otp = otp
    # Tạo chữ ký (signature)
    rawSignature = f"accessKey={accessKey}&amount={amount}&extraData={extraData}&ipnUrl={ipnUrl}&orderId={orderId}&orderInfo={orderInfo}&partnerCode={partnerCode}&redirectUrl={redirectUrl}&requestId={requestId}&requestType={requestType}"
    
    # h = hmac.new(bytes(secretKey, 'ascii'), bytes(rawSignature, 'ascii'), hashlib.sha256)
    # signature = h.hexdigest()
    h = hmac.new(bytes(secretKey, 'utf-8'), bytes(rawSignature, 'utf-8'), hashlib.sha256)
    signature = h.hexdigest()

    # Tạo đối tượng dữ liệu để gửi đến MoMo
    data = {
        'partnerCode': partnerCode,
        'partnerName': "MoMo Payment",
        'storeId': "YourStoreID",
        'requestId': requestId,
        'amount': amount,
        'orderId': orderId,
        'orderInfo': orderInfo,
        'redirectUrl': redirectUrl,
        'ipnUrl': ipnUrl,
        'lang': "vi",
        'extraData': extraData,
        'requestType': requestType,
        'signature': signature
    }

    # Gửi yêu cầu POST đến API MoMo

    response = requests.post(endpoint, data=json.dumps(data), headers={'Content-Type': 'application/json; charset=UTF-8'})
    response_data = response.json()

    # Kiểm tra kết quả trả về và lấy URL thanh toán
    if response_data['resultCode'] == 0:
        payUrl = response_data['payUrl']
        return payUrl
    else:
        raise Exception(response_data['message'])

# ------ Phần thêm vào cho thanh toán bằng MoMo QR ------
@api_view(['POST'])
def momo_payment(request):
    try:
        # Tạo thanh toán MoMo và lấy URL mã QR
        payment_url = create_momo_payment()
        return JsonResponse({
            'message': 'Tạo thanh toán thành công',
            'payment_url': payment_url
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
# ------ Kết thúc phần thêm vào cho thanh toán bằng MoMo QR ------

# ------ Kết thúc phần Momo QR Payment Integration ------
