## ADDED Requirements

### Requirement: BaseRepository debe tener tests unitarios para operaciones CRUD

El sistema SHALL tener tests unitarios para el BaseRepository que verifiquen las operaciones básicas de CRUD.

#### Scenario: Test save con nuevo registro
- **GIVEN** una instancia de BaseRepository configurada con un modelo SQLModel
- **WHEN** se llama a save() con un objeto nuevo (sin id)
- **THEN** debe llamar a session.add() y session.commit()

#### Scenario: Test save con registro existente
- **GIVEN** una instancia de BaseRepository con un objeto que tiene id
- **WHEN** se llama a save()
- **THEN** debe llamar solo a session.commit() (sin add)

#### Scenario: Test find_by_id retorna resultado
- **GIVEN** un registro en la base de datos
- **WHEN** se llama a find_by_id() con el id del registro
- **THEN** debe retornar el objeto

#### Scenario: Test find_by_id retorna None cuando no existe
- **GIVEN** una base de datos vacía
- **WHEN** se llama a find_by_id() con un id que no existe
- **THEN** debe retornar None

### Requirement: Auth Service debe tener tests unitarios para registro

El sistema SHALL tener tests unitarios para el AuthService que verifiquen el flujo de registro de usuarios.

#### Scenario: Registro exitoso
- **GIVEN** datos válidos de registro (email, password, nombre)
- **WHEN** auth_service.register() es llamado
- **THEN** debe crear el usuario, hashear la password, y retornar el usuario creado

#### Scenario: Registro con email duplicado
- **GIVEN** un email que ya existe en la base de datos
- **WHEN** auth_service.register() es llamado
- **THEN** debe lanzar una excepción de conflicto (ConflictError)

#### Scenario: Registro con password inválida
- **GIVEN** una password que no cumple los requisitos (< 8 caracteres)
- **WHEN** auth_service.register() es llamado
- **THEN** debe lanzar una excepción de validación

### Requirement: Auth Service debe tener tests unitarios para login

El sistema SHALL tener tests unitarios para el flujo de login.

#### Scenario: Login exitoso
- **GIVEN** un usuario existente con password correcta
- **WHEN** auth_service.login() es llamado con credenciales válidas
- **THEN** debe retornar tokens de acceso y refresh

#### Scenario: Login con password incorrecta
- **GIVEN** un usuario existente con password incorrecta
- **WHEN** auth_service.login() es llamado
- **THEN** debe lanzar UnauthorizedError

#### Scenario: Login con usuario inexistente
- **GIVEN** un email que no existe en la base de datos
- **WHEN** auth_service.login() es llamado
- **THEN** debe lanzar UnauthorizedError

### Requirement: Pydantic Schemas deben tener tests de validación

El sistema SHALL tener tests unitarios que verifiquen la validación de schemas Pydantic.

#### Scenario: UserCreate con email válido
- **GIVEN** un UserCreate con email válido (formato email)
- **WHEN** se valida el schema
- **THEN** no debe lanzar excepción

#### Scenario: UserCreate con email inválido
- **GIVEN** un UserCreate con email sin formato válido
- **WHEN** se valida el schema
- **THEN** debe lanzar ValidationError

#### Scenario: Password con longitud mínima
- **GIVEN** una password con menos de 8 caracteres
- **WHEN** se valida UserCreate
- **THEN** debe lanzar ValidationError