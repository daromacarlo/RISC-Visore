#include <soc/gpio_reg.h>

.section .text
.global main_validator

main_validator:
    addi sp, sp, -48        
    sw ra, 44(sp)           
    sw s0, 40(sp)           
    sw s1, 36(sp)
    sw s2, 32(sp)
    sw s3, 28(sp)
    sw s4, 24(sp)
    sw s9, 20(sp)
    sw s10, 16(sp)
    sw s11, 12(sp)

    mv t0, a0 
    mv s4, a0         
    mv s0, a1
    li s1, 15

    jal ra, controllo_word_intere

while:
    bge t0, s0, tutto_ok    # Scansione byte per byte
    
    lbu t1, (t0)
    addi t1, t1, -48
    ble t1, s1, continua1
    addi t1, t1, -39
continua1:
    lbu t2, 1(t0)
    addi t2, t2, -48
    ble t2, s1, continua2
    addi t2, t2, -39
continua2:
    lbu t3, 2(t0)
    addi t3, t3, -48
    ble t3, s1, continua3
    addi t3, t3, -39
continua3:
    lbu t4, 3(t0)
    addi t4, t4, -48
    ble t4, s1, continua4
    addi t4, t4, -39
continua4:
    lbu t5, 4(t0)
    addi t5, t5, -48
    ble t5, s1, continua5
    addi t5, t5, -39
continua5:
    lbu s9, 5(t0)
    addi s9, s9, -48
    ble s9, s1, continua6
    addi s9, s9, -39
continua6:
    lbu s10, 6(t0)
    addi s10, s10, -48
    ble s10, s1, continua7
    addi s10, s10, -39
continua7:
    lbu s11, 7(t0)
    addi s11, s11, -48
    ble s11, s1, continua8
    addi s11, s11, -39
continua8:

    # Ricostruzione Word in t6
    li t6, 0
    add t6, t6, s10
    slli t6, t6, 4
    add t6, t6, s11
    slli t6, t6, 4
    add t6, t6, t5
    slli t6, t6, 4
    add t6, t6, s9
    slli t6, t6, 4
    add t6, t6, t3
    slli t6, t6, 4
    add t6, t6, t4
    slli t6, t6, 4
    add t6, t6, t1
    slli t6, t6, 4
    add t6, t6, t2

    # Chiamata ai validatori
    jal ra, controllo_opcode
    jal ra, controllo_memoria
    jal ra, controllo_registro_zero
    jal ra, controllo_registri_critici
    jal ra, controllo_sintassi

    # Controllo Salti
    andi s3, t6, 127 
    li s2, 99                # Opcode Branch
    beq s2, s3, vai_controllo_salti
    li s2, 111               # Opcode JAL
    beq s2, s3, vai_controllo_salti
    li s2, 103               # Opcode JALR
    beq s2, s3, vai_controllo_salti
    j NO_vai_controllo_salti

vai_controllo_salti:
    jal ra, controllo_salti

NO_vai_controllo_salti:
    li t6, 0
    addi t0, t0, 8           # Prossima word
    j while

tutto_ok:
    li a0, 0                 # Successo
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