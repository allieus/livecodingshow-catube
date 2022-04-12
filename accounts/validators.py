from django.core.validators import RegexValidator


phone_number_validator = RegexValidator(
    r"^010-?\d{4}-?\d{4}$", message="휴대폰 번호를 입력해주세요."
)
