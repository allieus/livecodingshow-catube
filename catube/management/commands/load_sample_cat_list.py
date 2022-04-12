import json
import shutil
from pathlib import Path
from typing import List

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import BaseCommand, CommandError
from yt_dlp import YoutubeDL

from catube.models import Video, Tag


sample_json_path = settings.BASE_DIR / "assets" / "sample-cat-url-list.json"

ydl_opts = {"outtmpl": "temp/%(id)s.%(ext)s"}


def get_width_from_thumbnail(image):
    return image.get("width", 0)


class Command(BaseCommand):
    def handle(self, *args, **options):
        with sample_json_path.open("rt", encoding="utf-8") as f:
            cat_url_list: List[str] = json.load(f)

        ydl = YoutubeDL(ydl_opts)

        superuser = (
            get_user_model().objects.filter(is_superuser=True).order_by("pk").first()
        )
        if superuser is None:
            raise CommandError("슈퍼유저 계정을 먼저 생성해주세요.")

        with ydl:
            for cat_url in cat_url_list:
                info = ydl.extract_info(cat_url, download=True)

                thumbnail_list = (
                    thumb
                    for thumb in info["thumbnails"]
                    if thumb["url"].endswith(".jpg")
                )
                thumbnail_url = max(thumbnail_list, key=get_width_from_thumbnail)["url"]

                res = requests.get(thumbnail_url, stream=True)
                res.raise_for_status()
                thumbnail_f = res.raw

                video = Video(
                    title=info["title"],
                    description=info["description"],
                )

                video.photo.save(
                    Path(thumbnail_url).name,
                    thumbnail_f,
                    save=False,
                )

                # 다른 확장자로 비디오 파일이 다운로드 될 수 있습니다.
                video_path = next(Path("./temp").glob("%(id)s.*" % info))
                with video_path.open("rb") as video_f:
                    video.file.save(video_path.name, video_f, save=False)

                video.author = superuser

                video.save()

                tag_list = []
                for tag_name in info["tags"]:
                    tag, __ = Tag.objects.get_or_create(name=tag_name)
                    tag_list.append(tag)

                video.tag_set.set(tag_list)

        line = input("다운받은 비디오 임시 폴더를 삭제하시겠습니까? (Y/n)").lower()
        if line == "" or line.startswith("y"):
            shutil.rmtree("./temp")
            print("임시폴더를 삭제했습니다.")
