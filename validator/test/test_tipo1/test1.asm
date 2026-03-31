#------------------------------------------------------------------------------------
#
# TRACCIA 1.
# Scrivi un programma in assembly RISC-V che dato un vetore di word (numeri) faccia
# accendere il led x della ESP per y + 1000ms tempo, dove x è il massimo valore
# nel vettore di word mentre y è il valore minimo nel vettore di word.
#
#------------------------------------------------------------------------------------

# Svolgimento

.globl main

.data

vettore:    .word 15, 20, 42, 90, 88, 10, 40

.text

main:

    la t0, vettore
    li t1, 7
    
    lw a0, 0(t0)
    lw a1, 0(t0)    
    
    addi t0, t0, 4    
    addi t1, t1, -1     

loop:
    blez t1, fine  
    
    lw t2, 0(t0)       
    
    ble t2, a0, check_min
    mv a0, t2        
    j skip_update    

check_min:

    bge t2, a1, skip_update 
    mv a1, t2              

skip_update:
    addi t0, t0, 4
    addi t1, t1, -1
    j loop                  # Ripeti il ciclo

fine:
    addi a0, a0, 1000