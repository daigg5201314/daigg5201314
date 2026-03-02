## **UPD!!!** **A demo of Manga Colorization v2.5 is now available [link](https://mangacol.com). Feel free to check it out!**


# Automatic colorization

1. Download [generator](https://drive.google.com/file/d/1qmxUEKADkEM4iYLp1fpPLLKnfZ6tcF-t/view?usp=sharing) and [denoiser](https://drive.google.com/file/d/161oyQcYpdkVdw8gKz_MA8RD-Wtg9XDp3/view?usp=sharing) weights. Put generator and extractor weights in `networks` and denoiser weights in `denoising/models`.
2. To colorize image or folder of images with CLI, use:
```
$ python inference.py -p "path to file or folder"
```

## Web UI (recommended)

A user-friendly interface is provided via Gradio:

```bash
$ pip install -r requirements.txt
$ python app.py
```

Then open: `http://127.0.0.1:7860`

UI features:
- Upload image and one-click colorization.
- Adjustable inference size (step=32).
- Optional denoising and denoiser sigma control.
- Optional GPU toggle.
- Result preview and PNG download.

| Original      | Colorization      |
|------------|-------------|
| <img src="figures/bw1.jpg" width="512"> | <img src="figures/color1.png" width="512"> |
| <img src="figures/bw2.jpg" width="512"> | <img src="figures/color2.png" width="512"> |
| <img src="figures/bw3.jpg" width="512"> | <img src="figures/color3.png" width="512"> |
| <img src="figures/bw4.jpg" width="512"> | <img src="figures/color4.png" width="512"> |
| <img src="figures/bw5.jpg" width="512"> | <img src="figures/color5.png" width="512"> |
| <img src="figures/bw6.jpg" width="512"> | <img src="figures/color6.png" width="512"> |
