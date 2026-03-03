#include <soc/gpio_reg.h>

.section .data
	testo: .asciz "fail_memoria\n"

.section .text
.globl controllo_memoria

controllo_memoria:
    
    # Capiamo se è un'istruzione di tipo Load o Store tramite l'opcode
    andi t1, t6, 127         
    li t2, 3                
    beq t1, t2, verifica_allineamento
    li t2, 35               
    beq t1, t2, verifica_allineamento
    
    j ok               # Se non è un'istruzione di memoria, esci 

verifica_allineamento:
    # Controlliamo se è una Word (funct3 deve essere 2 per LW/SW)
    srli t3, t6, 12
    andi t3, t3, 7           # Isoliamo funct3
    li t4, 2                 # Valore 2 = Word
    bne t3, t4, ok           # Se è un byte (0) o half-word (1), l'allineamento a 4 non è richiesto

    # Estraiamo l'immediato per verificare l'allineamento dell'offset
    # Per LOAD (I-type): immediato è nei bit 20-31
    # Per STORE (S-type): immediato è diviso, ma i bit 0-1 dell'offset sono comunque nei bit 7-8 dell'istruzione
    # Per semplicità di convalida statica, controlliamo i bit che determinano l'allineamento a 4 (ultimi 2 bit dell'offset)
    
    andi t1, t6, 127         # Ricarica opcode
    li t2, 3
    beq t1, t2, imm_load     # Altrimenti continui su imm_store

imm_store:
    # In Store (S-type), l'offset basso (bit 0-4) è nei bit 7-11 dell'istruzione
    srli t1, t6, 7           
    j check_bits

imm_load:
    # In Load (I-type), l'offset è nei bit 20-31
    srli t1, t6, 20

check_bits:
    andi t1, t1, 3           # Verifica i bit 0 e 1 dell'offset
    beqz t1, ok              # Se sono 00, l'offset è multiplo di 4 

        # Segnalazione errore


errore:
    jal ra, vuota_registri
    li a0,7
    j controller_led

ok:
    li a0, 0                # valido 
    jr ra

