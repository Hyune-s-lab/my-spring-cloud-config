package dev.hyunec.commonconfig

import org.springframework.boot.autoconfigure.SpringBootApplication
import org.springframework.boot.runApplication
import org.springframework.cloud.config.server.EnableConfigServer

@EnableConfigServer
@SpringBootApplication
class CommonConfigApplication

fun main(args: Array<String>) {
    runApplication<CommonConfigApplication>(*args)
}
