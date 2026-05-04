package dev.hyunec.commonconfig.config

import io.swagger.v3.oas.models.OpenAPI
import io.swagger.v3.oas.models.Paths
import io.swagger.v3.oas.models.info.Info
import io.swagger.v3.oas.models.tags.Tag
import org.springdoc.core.customizers.OpenApiCustomizer
import org.springframework.context.annotation.Bean
import org.springframework.context.annotation.Configuration

@Configuration
class SpringDocConfig {

    @Bean
    fun phase1OpenApiCustomizer(): OpenApiCustomizer = OpenApiCustomizer { openApi ->
        val paths = Paths()
        openApi.paths
            .filterKeys { path -> path in PHASE_1_PATHS }
            .forEach { (path, pathItem) -> paths.addPathItem(path, pathItem) }
        openApi.paths(paths)
    }

    @Bean
    fun openApi(): OpenAPI = OpenAPI()
        .info(
            Info()
                .title("Common Config API")
                .version("0.0.1")
                .description("OpenBao backed Spring Cloud Config API"),
        )
        .tags(
            listOf(
                Tag()
                    .name("environment-controller")
                    .description("Spring Cloud Config standard lookup API"),
            ),
        )

    private companion object {
        val PHASE_1_PATHS = setOf(
            "/config/{name}/{profiles}",
            "/config/{name}-{profiles}.yaml",
            "/config/{name}-{profiles}.yml",
            "/config/{name}-{profiles}.properties",
            "/config/{name}-{profiles}.json",
        )
    }
}
