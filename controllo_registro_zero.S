#include <soc/gpio_reg.h>

.section .data
    testo: .asciz "errore, scrittura su registro 0\n"

.section .text
.globl controllo_registro_zero

controllo_registro_zero:
    andi t1, t6, 0x7F               # Isoliamo l'opcode con una maschera
    
    # Opcode che hanno il campo RD 
    li t2, 51               # R-type 
    beq t1, t2, verifica_rd
    li t2, 19               # I-type arithmetic 
    beq t1, t2, verifica_rd
    li t2, 3                # Load 
    beq t1, t2, verifica_rd
    li t2, 55               # LUI
    beq t1, t2, verifica_rd
    li t2, 23               # AUIPC
    beq t1, t2, verifica_rd
    
    # JAL (111) e JALR (103) li ignoriamo dato che spesso usano X0 per i salti.

    # se l'operazione non è di questi tipi saltiamo alla prossima (se c'è)

    j ok

verifica_rd:
    srli t1, t6, 7               # Sposta RD (bit 7-11) in posizione 0
    andi t1, t1, 0x1F            # Maschera per ottenere solo i 5 bit di RD
    bnez t1, ok                  # Se RD != 0, va tutto bene, altrimenti 
                                 # il programma sta tentando di scrivere
                                 # sul registro zero e non va bene.
    

    # Escludiamo il NOP standard (addi x0, x0, 0)
    li t2, 0x00000013
    beq t6, t2, ok

    # IL NOP è una operaziozione che consuma un ciclo di clock, è una word a 32 bit di tutti zeri tranne per l'opcode (13)

    # Se RD è 0 e non è un NOP, segnala errore RGZ
    j errore

        # Segnala errore

errore:
    li a4, 0x60004000           # Base GPIO ESP32-C3
    li a5, (1 << 8)             # Maschera Pin 8

blink_loop:
    sw a5, 0x0004(a4)           # LED OFF
    jal ra, delay
    sw zero, 0x0004(a4)         # LED ON
    jal ra, delay
    j blink_loop

        # Invece se tutto va bene

ok:
    li a0, 0                # valido 
    jr ra

delay:
    li a6, 2500000
1:  addi a6, a6, -1
    bnez a6, 1b
    ret
