# Watermark helpers (added). Video: ffmpeg drawtext. PDF: pypdf + reportlab overlay.
import os, io, asyncio, tempfile

FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
]
def _font():
    for f in FONT_CANDIDATES:
        if os.path.exists(f):
            return f
    return None

async def watermark_video(path, text, out=None):
    """Burn text into the video (bottom-right, semi-transparent). Returns new path or None."""
    out = out or (os.path.splitext(path)[0] + "_wm.mp4")
    tf = tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8")
    tf.write(text); tf.close()
    font = _font()
    dt = f"textfile='{tf.name}':fontcolor=white@0.55:fontsize=h/22:box=1:boxcolor=black@0.25:boxborderw=8:x=w-tw-20:y=h-th-20"
    if font:
        dt += f":fontfile='{font}'"
    cmd = ["ffmpeg", "-y", "-i", path, "-vf", f"drawtext={dt}",
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
           "-c:a", "copy", "-movflags", "+faststart", out]
    try:
        proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        _, err = await proc.communicate()
        if proc.returncode == 0 and os.path.isfile(out) and os.path.getsize(out) > 0:
            return out
        print("ffmpeg watermark error:", err.decode(errors="ignore")[-400:])
        if os.path.exists(out): os.remove(out)
        return None
    finally:
        try: os.remove(tf.name)
        except OSError: pass

def _watermark_pdf_sync(path, text, out):
    from pypdf import PdfReader, PdfWriter
    from reportlab.pdfgen import canvas
    reader = PdfReader(path)
    if reader.is_encrypted:
        reader.decrypt("")
    writer = PdfWriter()
    for page in reader.pages:
        w = float(page.mediabox.width); h = float(page.mediabox.height)
        buf = io.BytesIO()
        c = canvas.Canvas(buf, pagesize=(w, h))
        c.saveState()
        c.setFillGray(0.5, alpha=0.25)
        c.setFont("Helvetica-Bold", max(24, min(w, h) / 12))
        c.translate(w / 2, h / 2); c.rotate(45)
        c.drawCentredString(0, 0, text)
        c.restoreState()
        c.setFillGray(0.3, alpha=0.6); c.setFont("Helvetica", 9)
        c.drawRightString(w - 12, 10, text)
        c.save(); buf.seek(0)
        page.merge_page(PdfReader(buf).pages[0])
        writer.add_page(page)
    with open(out, "wb") as f:
        writer.write(f)
    return out

async def watermark_pdf(path, text, out=None):
    out = out or (os.path.splitext(path)[0] + "_wm.pdf")
    try:
        return await asyncio.get_event_loop().run_in_executor(None, _watermark_pdf_sync, path, text, out)
    except Exception as e:
        print("pdf watermark error:", e)
        if os.path.exists(out): os.remove(out)
        return None
