# patterns/management/commands/import_system_patterns.py
from django.core.management.base import BaseCommand
from patterns.models import SystemPattern

class Command(BaseCommand):
    help = '导入系统推荐纹样'

    def handle(self, *args, **kwargs):
        system_patterns = [
            {'image': '马纹.png', 'name': '纹一', 'meaning': '策马奔腾', 'source': 'system'},
            {'image': '锦鲤纹.png', 'name': '纹二', 'meaning': '好运连连', 'source': 'system'},
            {'image': '菊花纹.png', 'name': '纹三', 'meaning': '淡泊', 'source': 'system'},
            {'image': '山水纹.png', 'name': '纹四', 'meaning': '吉祥云意', 'source': 'system'}
        ]

        # 将每个纹样数据存入数据库
        for pattern in system_patterns:
            SystemPattern.objects.create(
                name=pattern['name'],
                meaning=pattern['meaning'],
                image=f"designs/thumbnails/{pattern['image']}",  # 存储图片路径
                source=pattern['source']
            )

        self.stdout.write(self.style.SUCCESS('系统推荐纹样已导入成功！'))