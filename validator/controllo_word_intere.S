#include <soc/gpio_reg.h>

.globl controllo_word_intere

.section .data
	testo: .asciz "fail_word_intere\n"

.text
	controllo_word_intere:
	    sub t2, s0, t0                  # t2 = lunghezza in byte del programma
	    li t4, 8
	    rem t3, t2, t4   
	    beqz t3, ok 
	
 # se la lunghezza non è multipla di 8
	    j errore
	
        # Segnalazione errore

errore:
    jal ra, vuota_registri
    li a0,2
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