import os
import uuid
import io
import zipfile
from flask import Flask, render_template, request, send_file
import qrcode
from qrcode.constants import ERROR_CORRECT_M 

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_batch', methods=['POST'])
def generate_batch():
    try:
        data = request.form.get('data', '')
        box_size = int(request.form.get('size', 10))
        border = int(request.form.get('border', 2))
        fg_color = request.form.get('fg_color', '#000000')
        bg_color = request.form.get('bg_color', '#FFFFFF')
        quantity = int(request.form.get('quantity', 1))
        gen_type = request.form.get('gen_type', 'single') 

        if quantity > 500:
            quantity = 500
        
        if gen_type != 'random' and not data:
            return "Veri veya link boş olamaz!", 400

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_archive:
            for i in range(quantity):
                
                if gen_type == 'random':
                    qr_data = str(uuid.uuid4())
                    filename = f"random_qr_{i+1}_{qr_data[:8]}.png"
                else: 
                    qr_data = data
                    filename = f"qr_code_{i+1}.png"
                
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=ERROR_CORRECT_M, 
                    box_size=box_size,
                    border=border,
                )
                qr.add_data(qr_data)
                qr.make(fit=True)
                
                img = qr.make_image(fill_color=fg_color, back_color=bg_color)
                img_buffer = io.BytesIO()
                img.save(img_buffer, format='PNG')
                img_buffer.seek(0)
                
                zip_archive.writestr(filename, img_buffer.read())

        zip_buffer.seek(0)
        
        zip_filename = "QR_Kod_Arsivi.zip"
        if gen_type == 'single' and quantity == 1:
            zip_filename = "qrcode.png"
            with zipfile.ZipFile(zip_buffer, 'r') as zf:
                png_data = zf.read(zf.infolist()[0].filename)
            return send_file(
                io.BytesIO(png_data),
                mimetype='image/png',
                as_attachment=True,
                download_name=zip_filename
            )

        return send_file(
            zip_buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name=zip_filename
        )

    except Exception as e:
        print(f"Hata oluştu: {e}")
        return "QR kod oluşturulurken bir hata oluştu.", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)