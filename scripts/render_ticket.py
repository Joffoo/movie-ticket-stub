import sys
import os
import json
import base64
import argparse
import subprocess
import tempfile
import shutil
from pathlib import Path

# Try importing config_manager from same folder
try:
    from config_manager import load_config, resolve_ticket_path, resolve_output_dir
except ImportError:
    try:
        from scripts.config_manager import load_config, resolve_ticket_path, resolve_output_dir
    except ImportError:
        def load_config(): return {}, None
        def resolve_ticket_path(name, custom=None): return Path(custom or ".") / name
        def resolve_output_dir(custom=None): return Path(custom or ".")

def find_browser():
    # 1. Custom environment variable override
    env_browser = os.environ.get("CHROME_PATH") or os.environ.get("BROWSER_PATH")
    if env_browser and os.path.exists(env_browser):
        return env_browser

    # 2. Windows paths
    if sys.platform == "win32":
        candidates = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\Application\msedge.exe"),
        ]
        for p in candidates:
            if os.path.exists(p):
                return p

    # 3. macOS paths
    elif sys.platform == "darwin":
        candidates = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
            "/Applications/Chromium.app/Contents/MacOS/Chromium",
            "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
        ]
        for p in candidates:
            if os.path.exists(p):
                return p

    # 4. Linux / Unix
    else:
        candidates = [
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "/usr/bin/chromium",
            "/usr/bin/chromium-browser",
            "/snap/bin/chromium",
        ]
        for p in candidates:
            if os.path.exists(p):
                return p

    # 5. Fallback via PATH
    for name in ["google-chrome", "chrome", "msedge", "chromium", "chromium-browser"]:
        found = shutil.which(name)
        if found:
            return found

    return None

def autocrop_borders(img_path):
    """
    Detects and crops pseudo-borders/white margins added by diffusion models,
    returning path to a clean 1:1 square image.
    """
    if not img_path or not os.path.exists(img_path):
        return img_path

    try:
        from PIL import Image
        import numpy as np

        img = Image.open(img_path).convert("RGB")
        w, h = img.size
        arr = np.array(img)

        # Check corners to see if there is a uniform border
        corners = [arr[0, 0], arr[0, w - 1], arr[h - 1, 0], arr[h - 1, w - 1]]
        # If corners are near-white (> 235 on all channels) or near-black (< 20)
        is_light_border = all(np.all(c > 235) for c in corners)
        is_dark_border = all(np.all(c < 20) for c in corners)

        if is_light_border or is_dark_border:
            if is_light_border:
                mask = np.any(arr < 235, axis=2)
            else:
                mask = np.any(arr > 25, axis=2)

            coords = np.argwhere(mask)
            if coords.size > 0:
                y0, x0 = coords.min(axis=0)
                y1, x1 = coords.max(axis=0) + 1
                # If border is noticeable (> 1% of canvas)
                if x0 > 4 or y0 > 4 or (w - x1) > 4 or (h - y1) > 4:
                    cropped = img.crop((x0, y0, x1, y1))
                    # Resize back to clean square 1024x1024
                    clean_sq = cropped.resize((1024, 1024), Image.Resampling.LANCZOS)
                    clean_path = str(Path(img_path).with_name(f"{Path(img_path).stem}_clean.png"))
                    clean_sq.save(clean_path, "PNG")
                    return clean_path
    except Exception as e:
        # If PIL/numpy not available or error, gracefully fallback to original
        pass

    return img_path

def image_to_base64_or_uri(img_path):
    if not img_path or not os.path.exists(img_path):
        return None
    # For local Chrome rendering, convert to standard file URI for maximum performance
    clean_p = autocrop_borders(img_path)
    ext = os.path.splitext(clean_p)[1].lower().replace('.', '')
    mime = "image/png" if ext == "png" else ("image/jpeg" if ext in ["jpg", "jpeg"] else "image/webp")
    with open(clean_p, "rb") as f:
        data = base64.b64encode(f.read()).decode('utf-8')
    return f"data:{mime};base64,{data}"

def parse_input_data(data_arg, data_b64_arg):
    if data_b64_arg:
        decoded = base64.b64decode(data_b64_arg).decode('utf-8')
        return json.loads(decoded)
    
    if not data_arg:
        raise ValueError("Either --data or --data-b64 must be provided.")

    if data_arg == "-":
        content = sys.stdin.read()
        return json.loads(content)

    if os.path.exists(data_arg):
        with open(data_arg, "r", encoding="utf-8-sig") as f:
            return json.load(f)
            
    try:
        return json.loads(data_arg)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON data. Provide a valid JSON string or file path: {e}")

def render_ticket(data, output_path, html_output_path=None, scale=None):
    cfg, _ = load_config()
    if scale is None:
        scale = float(cfg.get("scale", 4.0))

    script_dir = Path(__file__).resolve().parent
    template_path = script_dir.parent / "templates" / "ticket_template.html"
    
    if not template_path.exists():
        raise FileNotFoundError(f"Template not found at: {template_path}")
        
    with open(template_path, "r", encoding="utf-8-sig") as f:
        html = f.read()

    # Pre-process image with border autocrop and Data URI
    artwork_path = data.get("artwork_path") or data.get("generatedImageUrl")
    if artwork_path and os.path.exists(artwork_path):
        data["artwork_data_uri"] = image_to_base64_or_uri(artwork_path)
    elif artwork_path and artwork_path.startswith("data:"):
        data["artwork_data_uri"] = artwork_path

    # Inject data into JSON placeholder
    json_str = json.dumps(data, ensure_ascii=False)
    html = html.replace('/* __TICKET_DATA_PLACEHOLDER__ */', json_str)

    if html_output_path:
        os.makedirs(os.path.dirname(os.path.abspath(html_output_path)), exist_ok=True)
        with open(html_output_path, "w", encoding="utf-8-sig") as f:
            f.write(html)
        print(f"[EverStub] Saved populated HTML to: {html_output_path}")

    browser_exe = find_browser()
    if not browser_exe:
        raise RuntimeError("No compatible Chromium-based browser (Chrome, Edge, Chromium) was found on this system. Please install Google Chrome or Microsoft Edge, or specify CHROME_PATH environment variable.")

    temp_html = tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w", encoding="utf-8-sig")
    temp_html.write(html)
    temp_html.close()

    try:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        # 100% offline match with original EverStub:
        # Width: 384px (max-w-sm), Height: 683px (9/16 ratio)
        # Scale: 4 (Retina pixelRatio: 4, exactly 1536 x 2732 px)
        cmd = [
            browser_exe,
            "--headless=new",
            "--disable-gpu",
            f"--force-device-scale-factor={scale}",
            "--window-size=384,683",
            "--hide-scrollbars",
            "--virtual-time-budget=1000",
            "--run-all-compositor-stages-before-draw",
            f"--screenshot={os.path.abspath(output_path)}",
            f"file:///{os.path.abspath(temp_html.name).replace(os.sep, '/')}"
        ]
        
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30)
        if proc.returncode != 0:
            print(f"[Warning] Browser returned code {proc.returncode}: {proc.stderr.decode('utf-8', errors='ignore')}")
            
        if os.path.exists(output_path):
            print(f"[EverStub] Successfully generated ticket PNG: {output_path}")
            return output_path
        else:
            raise RuntimeError(f"Screenshot file was not generated: {proc.stderr.decode('utf-8', errors='ignore')}")
    finally:
        if os.path.exists(temp_html.name):
            try:
                os.remove(temp_html.name)
            except OSError:
                pass

def main():
    parser = argparse.ArgumentParser(description="Render EverStub Swiss Style Ticket Stub (Cross-platform, Offline & Autocrop)")
    parser.add_argument("--data", help="JSON string, path to JSON file, or '-' for stdin")
    parser.add_argument("--data-b64", help="Base64-encoded JSON string (immune to shell escaping)")
    parser.add_argument("--output", help="Path to output PNG image (defaults to auto resolution via config)")
    parser.add_argument("--html-output", help="Optional path to output populated HTML")
    parser.add_argument("--scale", type=float, default=None, help="Device scale factor (default: from config or 4.0 for Retina 1536x2732)")
    args = parser.parse_args()

    data = parse_input_data(args.data, args.data_b64)

    output_path = args.output
    if not output_path or output_path == "auto":
        # Format naming as [[The_Odyssey_Ticket.png]] or [[Resident_Evil_Ticket.png]]
        movie_en = data.get("movie_en", "").strip()
        if movie_en:
            # Title Case and replace spaces with underscore
            words = [w.capitalize() for w in movie_en.replace("-", " ").replace("_", " ").split()]
            safe_en = "_".join(words)
            filename = f"{safe_en}_Ticket.png"
        else:
            movie_cn = data.get("movie_cn", "").strip() or "Movie"
            safe_cn = "_".join(movie_cn.split())
            filename = f"{safe_cn}_Ticket.png"
        output_path = resolve_ticket_path(filename)

    render_ticket(data, output_path, args.html_output, scale=args.scale)

if __name__ == "__main__":
    main()
