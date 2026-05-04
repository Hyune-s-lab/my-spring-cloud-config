package dev.hyunec.commonconfig.config

import org.springframework.cloud.config.server.environment.EnvironmentRepository
import org.springframework.cloud.config.server.environment.VaultEnvironmentProperties
import org.springframework.cloud.config.server.environment.vault.SpringVaultEnvironmentRepositoryFactory
import org.springframework.context.annotation.Bean
import org.springframework.context.annotation.Configuration

@Configuration
class ApplicationBootstrap {
    @Bean
    fun environmentRepository(
        factory: SpringVaultEnvironmentRepositoryFactory,
        properties: VaultEnvironmentProperties,
    ): EnvironmentRepository = factory.build(properties)
}
