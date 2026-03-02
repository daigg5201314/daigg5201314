## **UPD!!!** **A demo of Manga Colorization v2.5 is now available [link](https://mangacol.com). Feel free to check it out!**

# Automatic colorization

1. Download [generator](https://drive.google.com/file/d/1qmxUEKADkEM4iYLp1fpPLLKnfZ6tcF-t/view?usp=sharing) and [denoiser](https://drive.google.com/file/d/161oyQcYpdkVdw8gKz_MA8RD-Wtg9XDp3/view?usp=sharing) weights.
2. Put generator and extractor weights in `networks` and denoiser weights in `denoising/models`.

## CLI usage

```bash
python inference.py -p "path to file or folder"
```

## Web UI (recommended)

```bash
pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:7860`.

UI features:
- Upload image and one-click colorization.
- Adjustable inference size (step=32).
- Optional denoising and denoiser sigma control.
- Optional GPU toggle.
- Result preview and PNG download.

### Windows support

Yes, the UI can run on Windows.

1. Install Python 3.10+.
2. Install dependencies and run:
   ```powershell
   pip install -r requirements.txt
   python app.py --host 127.0.0.1 --port 7860
   ```
3. If OpenCV reports missing runtime DLLs, install **Microsoft Visual C++ Redistributable (x64)**.

### Build EXE on Windows

This repository includes `build_windows_exe.bat` for one-click packaging with PyInstaller:

```powershell
build_windows_exe.bat
```

After building, executable path is:

```text
dist\MangaColorizationUI.exe
```

> Note: Windows EXE must be built on Windows. Building in Linux produces Linux binaries, not `.exe`.

| Original      | Colorization      |
|------------|-------------|
| <img src="figures/bw1.jpg" width="512"> | <img src="figures/color1.png" width="512"> |
| <img src="figures/bw2.jpg" width="512"> | <img src="figures/color2.png" width="512"> |
| <img src="figures/bw3.jpg" width="512"> | <img src="figures/color3.png" width="512"> |
| <img src="figures/bw4.jpg" width="512"> | <img src="figures/color4.png" width="512"> |
| <img src="figures/bw5.jpg" width="512"> | <img src="figures/color5.png" width="512"> |
| <img src="figures/bw6.jpg" width="512"> | <img src="figures/color6.png" width="512"> |
