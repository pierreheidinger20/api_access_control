
import phonenumbers
from phonenumbers import NumberParseException, PhoneNumberType


ALLOWED_COUNTRIES = {
    "BR": "Brasil",
    "PE": "Perú",
}


def normalize_phone_number(phone_number: str) -> str:
    """
    Normaliza un número de teléfono eliminando espacios en blanco y caracteres no numéricos.
    y validando que sea un numero valido 5511965797746 br / 51970211874 pe
    """
    phone_number = phone_number.strip()
    phone_number = ''.join(filter(str.isdigit, phone_number))
    return phone_number 

def validate_phone(phone: str) -> dict:
    """
    Valida teléfonos móviles de Brasil y Perú.

    Acepta ejemplos como:
        +5511999999999
        5511999999999
        +51999999999
    """

    if not phone:
        return {
            "valid": False,
            "message": "Número de teléfono requerido",
        }

    phone = phone.strip()

    try:
        # Si viene sin +, asumimos que contiene el código internacional.
        if not phone.startswith("+"):
            phone = "+" + phone

        parsed = phonenumbers.parse(phone, None)

    except NumberParseException:
        return {
            "valid": False,
            "message": "Formato de teléfono inválido",
        }

    # Código de país
    country_code = phonenumbers.region_code_for_number(parsed)

    if country_code not in ALLOWED_COUNTRIES:
        return {
            "valid": False,
            "message": "Solo se permiten números de Brasil y Perú",
        }

    # Validación estructural
    if not phonenumbers.is_valid_number(parsed):
        return {
            "valid": False,
            "message": "Número de teléfono inválido",
        }

    # Verificar que sea celular
    number_type = phonenumbers.number_type(parsed)

    if number_type not in (
        PhoneNumberType.MOBILE,
        PhoneNumberType.FIXED_LINE_OR_MOBILE,
    ):
        return {
            "valid": False,
            "message": "El número debe ser un celular",
        }

    return {
        "valid": True,
        "country": country_code,
        "country_name": ALLOWED_COUNTRIES[country_code],
        "international": phonenumbers.format_number(
            parsed,
            phonenumbers.PhoneNumberFormat.E164,
        ),
    }