#include <soc/gpio_reg.h>

.section .text
.global controller_led

controller_led:

    li t1, 1
    beq a0, t1, errore_opcode
    li t1, 2
    beq a0, t1, errore_word_intere
    li t1, 3
    beq a0, t1, errore_sintassi
    li t1, 4
    beq a0, t1, errore_salti
    li t1, 5
    beq a0, t1, errore_registro_zero
    li t1, 6
    beq a0, t1, errore_registri_critici
    li t1, 7
    beq a0, t1, errore_memoria
    ret 

errore_opcode:
    li a1, 1          # Numero di lampeggi lenti
    j esegui_sequenza

errore_word_intere:
    li a1, 2          # 2 lampeggi lenti
    j esegui_sequenza

errore_sintassi:
    li a1, 3          # 3 lampeggi lenti
    j esegui_sequenza

errore_salti:
    li a1, 4          # 4 lampeggi lenti
    j esegui_sequenza

errore_registro_zero:
    li a1, 5          # 5 lampeggi lenti
    j esegui_sequenza

errore_registri_critici:
    li a1, 6          # 6 lampeggi lenti
    j esegui_sequenza

errore_memoria:
    li a1, 7          # 7 lampeggi lenti
    j esegui_sequenza

esegui_sequenza:
    li a4, 0x60004000      # Base GPIO ESP32-C3
    li a5, (1 << 8)        # Maschera Pin 8 (GPIO8)
    mv s1, a1              # Salviamo il numero di lampeggi in s1

ciclo_lento:
    sw zero, 0x0004(a4)    # LED ON (Logica negata solitamente su ESP32: 0=ON)
    li a6, 8000000         
    jal ra, delay_custom
    sw a5, 0x0004(a4)      # LED OFF
    li a6, 8000000         
    jal ra, delay_custom
    
    addi s1, s1, -1        # Decrementa il numero di lampeggi rimasti
    bnez s1, ciclo_lento

    li t0, 20              # Moltiplicatore pausa
pausa_lunga_loop:
    li a6, 5000000         
    jal ra, delay_custom
    addi t0, t0, -1
    bnez t0, pausa_lunga_loop

blink_loop_infinito:
    sw zero, 0x0004(a4)    # LED ON
    li a6, 1500000         
    jal ra, delay_custom
    sw a5, 0x0004(a4)      # LED OFF
    li a6, 1500000
    jal ra, delay_custom
    j blink_loop_infinito

delay_custom:
    addi a6, a6, -1
    bnez a6, delay_custom