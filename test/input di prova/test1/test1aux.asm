.global x

.text
x:
    # Incrementa t5 di 1500
    addi t5, t5, 1500
    
    # Somma t5 a s7
    add  s7, s7, t5
    
    # Salva il risultato nello stack
    sw   s7, 0(sp)
    
    # Ritorna al chiamante 
    jr   ra
