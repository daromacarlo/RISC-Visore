#------------------------------------------------------------------------------------
#
# TRACCIA 3.
# Scrivere un programma in assembly RISC-V che:
# 1. Calcola Somma Totale e Massimo (M) di una matrice 3x3.
# 2. Calcola Media = Somma / 9.
# 3. Accendi LED pin Media per (M * 10) ms.
#
#------------------------------------------------------------------------------------

# Svolgimento

.globl main

.data
matrice:    .word 1, 3, 3
            .word 4, 8, 15
            .word 5, 2, 11

dim:        .word 9  # non serve

.text
main:
    la t0, matrice
    li t1, 9
    li t2, 0
    li t3, 0
    
    lw t2, 0(t0)

loop:
    blez t1, calcola
    lw t4, 0(t0)
    
    add t3, t3, t4
    
    ble t4, t2, skip
    mv t2, t4
    
skip:
    addi t0, t0, 4
    addi t1, t1, -1
    j loop

calcola:
    li t5, 9
    div t6, t3, t5
    
    sub t5, t2, t6

    mv a1, t6
    li t4, 10
    mul a0, t2, t4
    j fine


fine:

