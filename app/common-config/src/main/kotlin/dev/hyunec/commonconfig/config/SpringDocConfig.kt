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
    fun configLookupOpenApiCustomizer(): OpenApiCustomizer = OpenApiCustomizer { openApi ->
        val paths = Paths()
        openApi.paths
            .filterKeys { path -> path in CONFIG_LOOKUP_PATHS }
            .forEach { (path, pathItem) -> paths.addPathItem(path, pathItem) }
        openApi.paths(paths)
    }

    @Bean
    fun openApi(): OpenAPI = OpenAPI()
        .info(
            Info()
                .title("Common Config API")
                .version("0.0.1")
                .description("Spring Cloud Config standard lookup API"),
        )
        .tags(
            listOf(
                Tag()
                    .name("environment-controller")
                    .description("Spring Cloud Config standard lookup API"),
            ),
        )

    private companion object {
        val CONFIG_LOOKUP_PATHS = setOf(
            "/config/{name}/{profiles}",
            "/config/{name}-{profiles}.yaml",
            "/config/{name}-{profiles}.yml",
            "/config/{name}-{profiles}.properties",
            "/config/{name}-{profiles}.json",
        )
    }
}
