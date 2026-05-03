# 코드 컨벤션

이 문서는 common-config 서버 구현 시 지킬 Kotlin 코드 작성 규칙입니다. 목적은 도메인 모델을 단순하게 유지하고, 저장소/파이프라인/어댑터를 나중에 교체하기 쉽게 만드는 것입니다.

## 필수: MUST

- 불변 모델을 기본으로 합니다. 모델 타입은 `data class`로 만들고, 변경은 `copy()`로 표현합니다. 모델 클래스에 `var`를 쓰지 않습니다.
- 타입 안전 union에는 `sealed interface` 또는 `sealed class`를 사용합니다. 예: `ConfigResource`, `ConfigCommand`, `ConfigParseException`.
- nullable보다 non-null 기본값을 우선합니다. 값이 없다는 의미가 필요한 경우에만 `?`를 사용하고, 목록과 map은 `emptyList()`, `emptyMap()`을 기본으로 둡니다.
- public API 경계를 명확히 합니다. public은 entry point, model, config, output, language, pipeline interface/implementation에 한정합니다.
- 내부 유틸은 `internal`로 둡니다. 예: `storage/file`, `serialization`, `clock`, `validation`, `http/internal` 같은 구현 세부사항.
- 파이프라인 단계는 `pipeline/` 패키지의 interface로 정의합니다. 구현체는 `pipeline/impl/`에 둡니다.
- 파이프라인 interface와 기본 구현체는 public으로 둡니다. 사용자가 커스텀 파이프라인 조합을 만들 수 있어야 합니다.
- 도메인 특화 로직을 범용 계층에 넣지 않습니다. 예를 들어 특정 팀, 특정 고객, 특정 서비스명에만 맞는 로직은 parser, storage, projection 공통 계층에 넣지 않습니다.
- 휴리스틱은 구조적 기준만 사용합니다. 예: key pattern, environment map, gap 감지, version 비교, 스키마 유효성.
- 파이프라인 구현체는 parse/process 호출 간 mutable state를 보유하지 않습니다. per-call 상태는 지역 변수나 메서드 파라미터로만 둡니다.

## 권장: RECOMMENDED

- public 클래스, 함수, 프로퍼티에는 KDoc을 작성합니다. 가능하면 짧은 사용 예시를 포함합니다.
- 상태 없는 유틸은 `object`로 둡니다. 예: `JsonWriter`, `MarkdownWriter`, `LanguageDetector`.
- 설정 가능한 구현체는 `class`로 만들고 생성자 파라미터로 설정을 받습니다. 예: `FileConfigRepository`, `VersionedConfigProjector`.
- 구현체 이름은 알고리즘이나 책임을 설명하게 짓습니다. 예: `JsonLineAuditRepository`, `EnvironmentConfigProjector`, `MergeAwareConfigLoader`.
- 상수는 `companion object`에 `UPPER_SNAKE_CASE`로 둡니다. 의미가 애매한 값에는 짧은 주석을 남깁니다.
- 로깅은 `KotlinLogging.logger {}`를 사용합니다.
- 라이브러리/코어 계층 로그는 `debug`와 `warn`만 제한적으로 사용합니다. `info`는 되도록 애플리케이션 경계에서만 사용하고, `error`는 호출부가 판단하게 예외로 반환합니다.
- 테스트명은 서술적으로 작성합니다. 예: `test("FileConfigRepository가 audit event를 append한 뒤 current state를 교체합니다")`.
- 파일당 하나의 top-level 클래스 또는 인터페이스를 둡니다. 예외는 유틸 확장 함수와 nested/inner class입니다.

## 금지: DO NOT

- 모델 클래스에 `var`를 사용하지 않습니다.
- 공통 파이프라인에 포맷/고객/서비스 특화 로직을 추가하지 않습니다.
- 이유 주석 없이 `@Suppress`를 추가하지 않습니다.
- public API를 편의상 넓히지 않습니다. 외부 확장 지점이 아니면 `internal`을 우선합니다.
- 파이프라인 구현체에 parse/process 호출 사이에 남는 mutable cache나 임시 상태를 두지 않습니다.
