from django.core.exceptions import ValidationError


class FileSizeValidator:
    def __init__(self):
        """
        self.max_size: MB単位
        """
        self.max_size = 20

    def __call__(self, new_file):
        if new_file.size > self.max_size * 1024 * 1024:
            message = f"ファイルサイズは{self.max_size}MB以下である必要があります。"
            raise ValidationError(message)
