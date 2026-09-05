from flask import Flask, render_template, request, send_from_directory
from pathlib import Path
import re

app = Flask(__name__)

# Folder containing QR images
QR_FOLDER = Path(__file__).resolve().parent / "qr_images"

# Allowed image extensions
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}


def find_qr_image(emp_id):
    """
    Find an image whose filename starts with the employee ID.

    Example:
    103_Nagarajan_Durai.png
    Employee ID = 103
    """

    emp_id = emp_id.strip()

    # Only allow numbers as employee ID
    if not re.fullmatch(r"\d+", emp_id):
        return None

    for file in QR_FOLDER.iterdir():

        if not file.is_file():
            continue

        if file.suffix.lower() not in ALLOWED_EXTENSIONS:
            continue

        # Match:
        # 103_Nagarajan_Durai.png
        # 103_Rajaprabhu_M.jpg
        pattern = rf"^{re.escape(emp_id)}(?:_|$)"

        if re.match(pattern, file.name, re.IGNORECASE):
            return file

    return None


@app.route("/", methods=["GET", "POST"])
def index():

    if request.method == "POST":

        emp_id = request.form.get("emp_id", "").strip()

        if not emp_id:
            return render_template(
                "index.html",
                error="Please enter your Employee ID."
            )

        qr_file = find_qr_image(emp_id)

        if qr_file is None:
            return render_template(
                "index.html",
                error=f"No QR code found for Employee ID {emp_id}."
            )

        return render_template(
            "result.html",
            emp_id=emp_id,
            filename=qr_file.name
        )

    return render_template("index.html")


@app.route("/qr/<filename>")
def qr_image(filename):

    # Security: prevent path traversal
    safe_filename = Path(filename).name

    return send_from_directory(
        QR_FOLDER,
        safe_filename
    )


@app.route("/download/<filename>")
def download(filename):

    # Security: prevent path traversal
    safe_filename = Path(filename).name

    return send_from_directory(
        QR_FOLDER,
        safe_filename,
        as_attachment=True
    )


if __name__ == "__main__":

    # Make sure QR folder exists
    QR_FOLDER.mkdir(parents=True, exist_ok=True)

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )