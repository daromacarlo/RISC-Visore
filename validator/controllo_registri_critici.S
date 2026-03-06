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
    jal ra, vuota_registri
    li a0,6
    lw ra, 44(sp)
    lw s0, 40(sp)
    lw s1, 36(sp)
    lw s2, 32(sp)
    lw s3, 28(sp)
    lw s4, 24(sp)
    lw s9, 20(sp)
    lw s10, 16(sp)
    lw s11, 12(sp)
    addi sp, sp, 48
    ret


            # se tutto va bene invece:

ok:
    li a0, 0                # Opcode valido 
    jr ra
