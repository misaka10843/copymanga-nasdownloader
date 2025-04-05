import logging
import os
import shutil
from pathlib import Path

from cbz.comic import ComicInfo
from cbz.constants import PageType, YesNo, Manga, AgeRating, Format
from cbz.page import PageInfo
from natsort import natsorted

from utils import config
from utils.request import get

log = logging.getLogger(__name__)


def downloader(url: str, filename: str, overwrite: bool = False) -> bool:
    # 检查文件是否已存在
    if os.path.exists(filename):
        if overwrite:
            log.warning(f"文件已存在，强制覆盖: {filename}")
        else:
            log.info(f"文件已存在，跳过下载: {filename}")
            return True

    try:
        # 发起HTTP请求
        response = get(url)

        if response is None:
            log.error(f"无法获取图片响应，URL: {url}")
            return False

        if not response.content:
            log.error(f"获取到空内容，URL: {url}")
            return False

        # 创建目录路径
        directory = os.path.dirname(filename)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            log.debug(f"创建目录: {directory}")

        # 保存文件
        with open(filename, 'wb') as f:
            f.write(response.content)

        log.info(f"图片下载成功: {filename}")
        return True

    except IOError as e:
        log.error(f"文件写入失败: {e}，路径: {filename}")
    except Exception as e:
        log.error(f"未知错误: {e}，URL: {url}")

    return False


def postprocess(series_name: str, chapter_name: str, chapter_filename: str, chapter_number: float | int, file_path: str,
                specials: bool = False):
    source_dir = Path(file_path)
    if not source_dir.is_dir():
        log.error(f"无效目录: {file_path}")
        raise ValueError(f"无效目录: {file_path}")

    # 获取并排序文件列表（自然排序）
    paths = natsorted(source_dir.iterdir(), key=lambda x: x.name)
    if not paths:
        log.error(f"没有在 {file_path} 中找到图片")
        raise RuntimeError(f"没有在 {file_path} 中找到图片")

    # 构建页面信息(关于尾页因为推测大部分尾页都是汉化组的图所以就直接打标了)
    pages = [
        PageInfo.load(
            path=path,
            type=PageType.FRONT_COVER if i == 0 else
            PageType.BACK_COVER if i == len(paths) - 1 else
            PageType.STORY
        )
        for i, path in enumerate(paths)
    ]

    # 构建漫画元数据
    comic = ComicInfo.from_pages(
        pages=pages,
        title=chapter_name,
        series=series_name,
        number=chapter_number,
        language_iso='zh',
        format=Format.WEB_COMIC,
        black_white=YesNo.NO,
        manga=Manga.YES,
        age_rating=AgeRating.PENDING
    )

    base_dir = Path(config.CBZ_PATH) / series_name
    if specials:
        base_dir /= "Specials"

    # 确保目录存在
    base_dir.mkdir(parents=True, exist_ok=True)
    cbz_path = base_dir / f"{chapter_filename}.cbz"
    cbz_path.write_bytes(comic.pack())
    log.info(f"cbz打包成功: {cbz_path}")
    shutil.rmtree(file_path, ignore_errors=True)
    log.info(f"图片删除成功: {file_path}")
