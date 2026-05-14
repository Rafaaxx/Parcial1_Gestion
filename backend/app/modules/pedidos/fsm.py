"""FSM (Finite State Machine) for Order State Transitions

This module defines the state transition map for the pedido lifecycle.
Validates transitions based on origin state, target state, and user roles.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Callable, Dict, List, Optional


class EstadoPedido(str, Enum):
    """Valid order states."""

    PENDIENTE = "PENDIENTE"
    CONFIRMADO = "CONFIRMADO"
    EN_PREP = "EN_PREP"
    EN_CAMINO = "EN_CAMINO"
    ENTREGADO = "ENTREGADO"
    CANCELADO = "CANCELADO"

    @property
    def es_terminal(self) -> bool:
        """Check if this state is terminal (no further transitions allowed)."""
        return self in (EstadoPedido.ENTREGADO, EstadoPedido.CANCELADO)


# Role constants
class RolUsuario(str, Enum):
    """Valid user roles for FSM transitions."""

    CLIENT = "CLIENT"
    ADMIN = "ADMIN"
    PEDIDOS = "PEDIDOS"
    SISTEMA = "SISTEMA"


@dataclass(frozen=True)
class Transition:
    """
    Represents a valid state transition.

    Attributes:
        target: The destination state after transition
        allowed_roles: Roles that can trigger this transition
        requires_motivo: Whether this transition requires a 'motivo' explanation
        stock_action: Optional function to execute on stock (decrement/restore)
        is_system: Whether this is a system-only transition (no manual trigger)
    """

    target: str
    allowed_roles: frozenset
    requires_motivo: bool = False
    stock_action: Optional[Callable] = None
    is_system: bool = False


# Terminal states (no transitions allowed)
TERMINAL_STATES = frozenset({EstadoPedido.ENTREGADO.value, EstadoPedido.CANCELADO.value})

# FSM Transition Map: {origin_state: [Transition, ...]}
# Based on specs: FSM-TRANS-01 (valid transitions), FSM-TRANS-02 (terminal), FSM-TRANS-03 (roles)
FSM_TRANSITION_MAP: Dict[str, List[Transition]] = {
    # PENDIENTE can transition to CONFIRMADO (system or admin for testing) or CANCELADO (any role)
    EstadoPedido.PENDIENTE.value: [
        Transition(
            target=EstadoPedido.CONFIRMADO.value,
            allowed_roles=frozenset({RolUsuario.SISTEMA.value, RolUsuario.ADMIN.value}),
            is_system=True,
        ),
        Transition(
            target=EstadoPedido.CANCELADO.value,
            allowed_roles=frozenset(
                {
                    RolUsuario.CLIENT.value,
                    RolUsuario.ADMIN.value,
                    RolUsuario.PEDIDOS.value,
                }
            ),
            requires_motivo=True,
        ),
    ],
    # CONFIRMADO can transition to EN_PREP or CANCELADO
    EstadoPedido.CONFIRMADO.value: [
        Transition(
            target=EstadoPedido.EN_PREP.value,
            allowed_roles=frozenset({RolUsuario.ADMIN.value, RolUsuario.PEDIDOS.value}),
        ),
        Transition(
            target=EstadoPedido.CANCELADO.value,
            allowed_roles=frozenset({RolUsuario.ADMIN.value, RolUsuario.PEDIDOS.value}),
            requires_motivo=True,
            stock_action="restore",  # Restore stock on cancel
        ),
    ],
    # EN_PREP can transition to EN_CAMINO or CANCELADO (admin only)
    EstadoPedido.EN_PREP.value: [
        Transition(
            target=EstadoPedido.EN_CAMINO.value,
            allowed_roles=frozenset({RolUsuario.ADMIN.value, RolUsuario.PEDIDOS.value}),
        ),
        Transition(
            target=EstadoPedido.CANCELADO.value,
            allowed_roles=frozenset({RolUsuario.ADMIN.value}),
            requires_motivo=True,
            stock_action="restore",
        ),
    ],
    # EN_CAMINO can only transition to ENTREGADO
    EstadoPedido.EN_CAMINO.value: [
        Transition(
            target=EstadoPedido.ENTREGADO.value,
            allowed_roles=frozenset({RolUsuario.ADMIN.value, RolUsuario.PEDIDOS.value}),
        ),
    ],
    # Terminal states: no transitions allowed
    EstadoPedido.ENTREGADO.value: [],
    EstadoPedido.CANCELADO.value: [],
}


def get_valid_transitions(estado_actual: str) -> List[Transition]:
    """
    Get valid transitions from a given state.

    Args:
        estado_actual: Current state code

    Returns:
        List of valid Transition objects
    """
    return FSM_TRANSITION_MAP.get(estado_actual, [])


def is_valid_state(estado: str) -> bool:
    """Check if a state code is valid."""
    return estado in FSM_TRANSITION_MAP


def es_estado_terminal(estado: str) -> bool:
    """Check if a state is terminal (ENTREGADO or CANCELADO)."""
    return estado in TERMINAL_STATES
