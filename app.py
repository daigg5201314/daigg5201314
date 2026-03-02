import argparse
import tempfile
import webbrowser
from pathlib import Path

import gradio as gr
import numpy as np
from PIL import Image


class ColorizeService:
    def __init__(self):
        self._cache = {}

    def get_colorizator(self, device: str, generator_path: str, extractor_path: str):
        # Lazy import to avoid importing heavy deps (e.g., cv2) before first inference.
        from colorizator import MangaColorizator

        key = (device, generator_path, extractor_path)
        if key not in self._cache:
            self._cache[key] = MangaColorizator(device, generator_path, extractor_path)
        return self._cache[key]


def save_result_png(result: np.ndarray) -> str:
    result = np.asarray(result)
    if result.dtype != np.uint8:
        result = np.clip(result, 0, 1)
        result = (result * 255).astype(np.uint8)

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        output_path = Path(tmp.name)

    Image.fromarray(result).save(output_path)
    return str(output_path)


service = ColorizeService()


def colorize_image(
    image,
    size,
    denoise,
    denoiser_sigma,
    use_gpu,
    generator_path,
    extractor_path,
):
    if image is None:
        raise gr.Error("请先上传一张图片。")

    device = "cpu"
    if use_gpu:
        import torch

        if not torch.cuda.is_available():
            raise gr.Error("当前环境未检测到可用 CUDA GPU，请关闭 GPU 选项或检查驱动。")
        device = "cuda"

    try:
        colorizator = service.get_colorizator(device, generator_path, extractor_path)
        colorizator.set_image(image, size=size, apply_denoise=denoise, denoise_sigma=denoiser_sigma)
        result = colorizator.colorize()
    except FileNotFoundError as exc:
        raise gr.Error(f"模型权重不存在：{exc}")
    except Exception as exc:
        raise gr.Error(f"处理失败：{exc}")

    output_path = save_result_png(result)
    return result, output_path


with gr.Blocks(title="Manga Colorization UI") as demo:
    gr.Markdown(
        """
        # 🎨 Manga Automatic Colorization
        上传黑白漫画图，一键上色。

        > 首次推理会加载模型，速度会稍慢。
        """
    )

    with gr.Row():
        with gr.Column(scale=1):
            input_image = gr.Image(label="输入图", type="numpy")
            size = gr.Slider(256, 1536, value=576, step=32, label="推理尺寸 (必须 32 的倍数)")
            denoise = gr.Checkbox(value=True, label="启用去噪")
            denoiser_sigma = gr.Slider(0, 75, value=25, step=1, label="去噪强度 sigma")
            use_gpu = gr.Checkbox(value=False, label="使用 GPU (CUDA)")

            with gr.Accordion("高级设置", open=False):
                generator_path = gr.Textbox(value="networks/generator.zip", label="Generator 权重路径")
                extractor_path = gr.Textbox(value="networks/extractor.pth", label="Extractor 权重路径")

            run_button = gr.Button("开始上色", variant="primary")

        with gr.Column(scale=1):
            output_image = gr.Image(label="上色结果", type="numpy")
            download_file = gr.File(label="下载 PNG")

    run_button.click(
        fn=colorize_image,
        inputs=[
            input_image,
            size,
            denoise,
            denoiser_sigma,
            use_gpu,
            generator_path,
            extractor_path,
        ],
        outputs=[output_image, download_file],
    )


def parse_args():
    parser = argparse.ArgumentParser(description="Manga colorization web UI")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=7860)
    parser.add_argument("--share", action="store_true")
    parser.add_argument("--no-open-browser", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if not args.no_open_browser:
        webbrowser.open(f"http://{args.host}:{args.port}")
    demo.launch(server_name=args.host, server_port=args.port, share=args.share, theme=gr.themes.Soft())
