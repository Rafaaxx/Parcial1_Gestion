# mp-checkout-frontend Specification

## Purpose

Frontend integration for MercadoPago Checkout using SDK React. Handles tokenization of card data (PCI-compliant) and payment status display.

## Requirements

### Requirement: Payment Store — Zustand State Management

El sistema SHALL usar Zustand para gestionar el estado del pago en el frontend con status, mpPaymentId, statusDetail y error.

#### Scenario: paymentStore inicializa en idle
- **GIVEN** usuario navega a checkout
- **WHEN** paymentStore se inicializa
- **THEN** status="idle", mpPaymentId=null, statusDetail=null, error=null

#### Scenario: paymentStore actualiza a processing
- **GIVEN** usuario inicia pago
- **WHEN** paymentStore.setStatus("processing")
- **THEN** status="processing", UI muestra spinner

#### Scenario: paymentStore actualiza a approved
- **GIVEN** pago aprobado recibido del backend
- **WHEN** paymentStore.setPaymentApproved(mpPaymentId)
- **THEN** status="approved", mpPaymentId="123456", error=null
- **AND** UI muestra success

#### Scenario: paymentStore actualiza a rejected
- **GIVEN** pago rechazado recibido del backend
- **WHEN** paymentStore.setPaymentRejected(statusDetail)
- **THEN** status="rejected", error=statusDetail

#### Scenario: paymentStore actualiza a error
- **GIVEN** error de red o excepción
- **WHEN** paymentStore.setError(errorMessage)
- **THEN** status="error", error=errorMessage

### Requirement: Checkout Form — SDK React Integration

El sistema SHALL usar @mercadopago/sdk-react para tokenizar datos de tarjeta, asegurando que datos sensibles nunca viajen al servidor del backend.

#### Scenario: Tokenización exitosa
- **GIVEN** usuario ingresa datos de tarjeta válidos
- **WHEN** Checkout form procesa payment
- **THEN** token se genera via SDK de MP
- **AND** token se envía al backend (NO datos de tarjeta)

#### Scenario: Datos de tarjeta NO van al backend
- **GIVEN** request POST a backend
- **WHEN** inspeccionar payload
- **THEN** NO contiene número de tarjeta, CVV, o fecha de expiración
- **AND** solo contiene token generado por SDK MP

#### Scenario: Tokenización falla muestra error
- **GIVEN** datos de tarjeta inválidos
- **WHEN** Checkout intenta tokenizar
- **THEN** SDK retorna error de validación
- **AND** UI muestra mensaje de error de MP

### Requirement: Payment Status Display — User Feedback

El sistema SHALL mostrar estados de pago claramente al usuario con feedback visual apropiado.

#### Scenario: Mostrar estado pending
- **GIVEN** pago creado con status "pending"
- **WHEN** componente PaymentStatus renderiza
- **THEN** muestra "Pago en proceso" + spinner

#### Scenario: Mostrar estado approved
- **GIVEN** paymentStore.status="approved"
- **WHEN** componente PaymentStatus renderiza
- **THEN** muestra check verde + "Pago aprobado"
- **AND** botón para ver pedido

#### Scenario: Mostrar estado rejected
- **GIVEN** paymentStore.status="rejected"
- **WHEN** componente PaymentStatus renderiza
- **THEN** muestra X rojo + "Pago rechazado"
- **AND** mensaje de error detallado

#### Scenario: Mostrar estado error
- **GIVEN** paymentStore.status="error"
- **WHEN** componente PaymentStatus renderiza
- **THEN** muestra icono de alerta + mensaje de error

### Requirement: Redirección a MP — Init Point

El sistema SHALL redirigir al usuario al init_point de MercadoPago cuando el pago no se procese directamente via SDK.

#### Scenario: Redireccionar a URL de MP
- **GIVEN** backend retorna init_point en respuesta
- **WHEN** paymentStore recibe init_point
- **THEN** window.location.href = init_point

### Requirement: PCI Compliance — SAQ-A

El sistema SHALL cumplir con PCI SAQ-A asegurando que datos de tarjeta nunca sean almacenados ni transmitidos por el servidor del comercio.

#### Scenario: Sin logging de datos sensibles
- **GIVEN** pago en proceso
- **WHEN** revisar logs del browser
- **THEN** NO aparecen números de tarjeta, CVV, o datos sensibles

#### Scenario: SDK usa iframes seguros
- **GIVEN** Checkout form renderiza
- **WHEN** inspeccionar DOM
- **THEN** campos sensibles están en iframes de MP