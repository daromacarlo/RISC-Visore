.global main

.text
main:
    # Alloca spazio sullo stack (es. 16 byte)
    addi sp, sp, -16
    
    # Inizializza s10 a 900
    addi s10, zero, 900
    
    # Salva s10 nello stack (offset 8 per non sovrapporre x)
    sw   s10, 8(sp)
    
    # Salta alla funzione x e salva l'indirizzo di ritorno in ra
    jal  ra, x
    
    # Ripristina lo stack prima di uscire
    addi sp, sp, 16

    # Fine programma (Simulazione uscita)
    li a6, 10
    li a7, 10
    beq a6,a7,fine
    fine:
    ecall
