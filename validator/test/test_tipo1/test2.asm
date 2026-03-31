#------------------------------------------------------------------------------------
#
# TRACCIA 2.
# Scrivere un programma in assembly RISC-V che
# data una matrice 3x3 di word (interi),
# 1. Ricerchi il valore MASSIMO (M) e il valore MINIMO (m) all'interno della matrice.
# 2. Calcoli la differenza D = M - m.
# 3. 
#    - Accendi il LED x + 2 della ESP, dove x è il valore MINIMO (m).
#    - Mantieni il LED acceso per un tempo y = D * 10 ms.
#
#------------------------------------------------------------------------------------

# Svolgimento

.globl main

.data

matrice:    .word 12, 45, 67
            .word 8,  90, 23
            .word 34, 11, 56

dim:        .word 9      # non serve
soglia:     .word 50     # non serve   

.text

main:
    la   t0, matrice        
    lw   t1, dim           
    
    lw   t2, 0(t0)        
    lw   t3, 0(t0)         
    

    addi t0, t0, 4
    addi t1, t1, -1

loop:
    blez t1, verifica     
    lw   t4, 0(t0)         
    
    ble  t4, t2, check_min  
    mv   t2, t4            
    j    next_step

check_min:
    bge  t4, t3, next_step
    mv   t3, t4

next_step:
    addi t0, t0, 4
    addi t1, t1, -1
    j    loop

verifica:
    sub  t5, t2, t3
    mv   a1, t3
    addi a1, a1, 2
    li   t6, 10
    mul  a0, t5, t6

fine: