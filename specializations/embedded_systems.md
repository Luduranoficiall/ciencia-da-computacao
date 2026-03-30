# Especialização: Sistemas embarcados e IoT

## Pré-requisitos mínimos

- Circuitos digitais, arquitetura de computadores I–II, programação em C ou Rust.

## Trilha sugerida

1. **Microcontrolador** — GPIO, timers, interrupções, sem bloquear loop principal à toa.
2. **Comunicação** — UART, I2C/SPI; protocolos em camadas.
3. **Consumo e tempo real** — latências, watchdog, RTOS introdutório (FreeRTOS ou Zephyr).
4. **Toolchain** — build, flash, debug com GDB/OpenOCD ou IDE mínima.
5. **Segurança** — updates OTA (conceito), chaves, superfície de ataque de firmware.

## Recursos

- Datasheets e manuais de referência do chip (habilidade central).
- *Making Embedded Systems* (White) — visão prática.

## Capstone

- **A:** Firmware que lê sensor, filtra ruído e publica em protocolo documentado (MQTT serial mock, etc.).
- **B:** PCB simples ou shield + firmware com testes em hardware-in-the-loop simulado (QEMU quando aplicável).

## Prova de nível

Diagrama de estados do firmware + log de decisões de projeto (por que esse clock, esse sleep mode).
