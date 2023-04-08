import random
from flask import Flask, render_template, request, flash, redirect, url_for
import os
from werkzeug.utils import send_from_directory, secure_filename
import secrets
from PIL import Image, ImageDraw, ImageFont


secret_key = secrets.token_hex(16)
UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = secret_key


# Check if extension is valid for file upload
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=['GET', 'POST'])
def home():
    if request.method == 'POST':

        # Handle the image upload/check if file is valid
        if 'file' not in request.files:
            flash('No file part.')
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            flash('No selected file.')
            return redirect(request.url)

        # Check if file extension is allowed
        if not allowed_file(file.filename):
            flash('Invalid file extension. Only JPG, PNG, and GIF files are allowed.')
            return redirect(request.url)

        # File valid, handle the image watermark manipulation then save for download
        filename = secure_filename(file.filename)

        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        # Open image with Pillow
        with Image.open(os.path.join(app.config['UPLOAD_FOLDER'], filename)) as img:
            watermark_text = request.form['watermark_text']

            # Draw image object and set font size
            draw = ImageDraw.Draw(img)
            font = ImageFont.truetype("arial.ttf", 36)

            # Calculate text size and position
            textbbox = draw.textbbox((0, 0), watermark_text, font)
            text_width = textbbox[2] - textbbox[0]
            text_height = textbbox[3] - textbbox[1]

            alpha = random.randint(0, 255)

            # Draw the text multiple times with increasing y values
            y = 0
            while y < img.height:
                x = img.width - text_width - 10
                draw.text((x, y), watermark_text, font=font, fill=(50, 50, 50, 50))
                y += text_height + 10

            # Save to file
            watermarked_filename = 'watermarked_' + filename
            img.save(os.path.join(app.config['UPLOAD_FOLDER'], watermarked_filename))

        return redirect(url_for('download_file', img_name=watermarked_filename))

    else:
        return render_template('home.html')


@app.route("/download")
def download_file():
    watermarked_filename = request.args.get('img_name')
    return render_template('download.html', img_name=watermarked_filename)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True, environ=request.environ)


if __name__ == "__main__":
    app.run(debug=True, port=80)


