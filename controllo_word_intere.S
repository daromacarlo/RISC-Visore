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
    j controller_led


            # se tutto va bene invece:

ok:
    li a0, 0                # Opcode valido 
    jr ra