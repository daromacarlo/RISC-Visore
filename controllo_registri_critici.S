#include <soc/gpio_reg.h>

.section .data
    .align 4
    msg_sp: .asciz "Modifica dello Stack Pointer.\n"
    msg_gp: .asciz "Modifica del Global Pointer\n"
    msg_tp: .asciz "Modifica del Thread Pointer\n"

.section .text
.globl controllo_registri_critici

controllo_registri_critici:
    
    # Cerchiamo le istruzioni che hanno il registro di ritorno con la solita maschera
    andi t1, t6, 0x7F
    
    # Opcodes che usano rd: 51(R), 19(I), 3(Load), 103(jalr), 55(LUI), 23(AUIPC), 111(JAL)
    li t2, 51
    beq t1, t2, verifica_rd_critico
    li t2, 19
    beq t1, t2, verifica_rd_critico
    li t2, 3
    beq t1, t2, verifica_rd_critico
    li t2, 103
    beq t1, t2, verifica_rd_critico
    li t2, 55
    beq t1, t2, verifica_rd_critico
    li t2, 23
    beq t1, t2, verifica_rd_critico
    li t2, 111
    beq t1, t2, verifica_rd_critico
    
    j ok

verifica_rd_critico:
    # Estraiamo il campo rd (bit 7-11)
    srli t1, t6, 7
    andi t1, t1, 0x1F
    
    # Controllo se rd è uno dei registri riservati (x2, x3, x4)
    li t2, 2                # x2 = sp 
    beq t1, t2, errore
    
    li t2, 3                # x3 = gp 
    beq t1, t2, errore
    
    li t2, 4                # x4 = tp 
    beq t1, t2, errore
    
    j ok

        # Segnala errore

errore:
    li a4, 0x60004000           # Base GPIO ESP32-C3
    li a5, (1 << 8)             # Maschera Pin 8

blink_loop:
    sw a5, 0x0004(a4)           # LED OFF
    jal ra, delay
    sw zero, 0x0004(a4)         # LED ON
    jal ra, delay
    j blink_loop

        # Invece se tutto va bene

ok:
    li a0, 0                # valido 
    jr ra

delay:
    li a6, 2500000
1:  addi a6, a6, -1
    bnez a6, 1b
    ret
