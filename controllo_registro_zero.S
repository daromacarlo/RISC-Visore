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
    jal ra, vuota_registri
    li a0,5
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