"""MercadoPago client utilities for webhook validation and API queries"""
import hashlib
import hmac
import logging
from typing import Optional

import mercadopago

from app.config import settings

logger = logging.getLogger(__name__)


def validar_firma_webhook(
    mp_payment_id: str,
    x_signature: Optional[str],
    x_request_id: Optional[str] = None,
) -> bool:
    """
    Validate the X-Signature header from MercadoPago webhook.

    MercadoPago firma las notificaciones usando SHA256:
    1. Concatenar: "v1" + "{payment_id}" + "{access_token}"
    2. Generar hash SHA256

    Args:
        mp_payment_id: The MP payment ID from the webhook
        x_signature: The X-Signature header value from MP
        x_request_id: Optional X-Request-Id header

    Returns:
        True if signature is valid, False otherwise
    """
    if not x_signature:
        logger.warning("Webhook received without X-Signature header")
        return False

    if not settings.mp_access_token:
        logger.warning("MP_ACCESS_TOKEN not configured, skipping signature validation")
        return True  # En desarrollo, permitir sin validación

    # Generar la firma esperada
    # Formato: v1>{payment_id}>{access_token}
    payload = f"v1>{mp_payment_id}>{settings.mp_access_token}"
    expected_signature = hmac.new(
        settings.mp_access_token.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    # Comparar signatures (MercadoPago puede enviar múltiples firmas separadas por coma)
    valid_signatures = x_signature.split(",")
    for sig in valid_signatures:
        sig = sig.strip()
        if hmac.compare_digest(sig, expected_signature):
            logger.info(f"Webhook signature validated for payment {mp_payment_id}")
            return True

    logger.warning(
        f"Invalid webhook signature for payment {mp_payment_id}. "
        f"Expected: {expected_signature[:20]}..., Got: {x_signature[:40]}..."
    )
    return False


def get_mp_client() -> mercadopago.SDK:
    """
    Get a configured MercadoPago SDK instance.

    Returns:
        Configured mercadopago.SDK instance
    """
    access_token = settings.mp_access_token
    if not access_token:
        raise ValueError("MP_ACCESS_TOKEN not configured")
    return mercadopago.SDK(access_token)


def consultar_estado_pago(mp_payment_id: str) -> dict:
    """
    Consultar el estado real de un pago en MercadoPago.

    IMPORTANTE: Siempre usar este método en lugar de confiar ciegamente
    en los datos del webhook. Consultamos la API de MP para confirmar.

    Args:
        mp_payment_id: ID del pago en MercadoPago

    Returns:
        Dict con:
        - status: Código de estado MP (approved, pending, rejected, etc.)
        - status_detail: Detalle del estado (cc_approved, cc_rejected, etc.)
        - external_reference: Referencia externa (UUID del pedido)
        - response: Respuesta completa de la API (para debugging)

    Raises:
        MPConnectionError: Si no se puede conectar a la API de MP
    """
    client = get_mp_client()

    try:
        result = client.payment().get(mp_payment_id)

        if result["status"] != 200:
            logger.error(f"MP API returned status {result['status']}: {result}")
            return {
                "status": "error",
                "status_detail": None,
                "external_reference": None,
                "response": result,
            }

        payment_info = result["response"]
        return {
            "status": payment_info.get("status", "unknown"),
            "status_detail": payment_info.get("status_detail", ""),
            "external_reference": payment_info.get("external_reference"),
            "response": payment_info,
        }

    except Exception as e:
        logger.error(f"Error consulting MP API for payment {mp_payment_id}: {e}")
        raise