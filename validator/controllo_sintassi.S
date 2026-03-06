#include <soc/gpio_reg.h>

.globl controllo_sintassi

.section .data
    scritta: .asciz "errore_sintassi\n"

.section .text             
controllo_sintassi:
    andi s3, t6, 127         # Estraiamo l'opcode (bit 0-6)
    
    # verifichiamo che l'istruzione sia di TIPO R
    li s2, 51                # Opcode 0110011
    beq s2, s3, Rcheck
    
    # verifichiamo che l'istruzione sia di TIPO I
    li s2, 19                # Opcode 0010011 (Arimetica imm)
    beq s2, s3, Icheck
    li s2, 3                 # Opcode 0000011 (Load)
    beq s2, s3, Icheck
    li s2, 103               # Opcode 1100111 (JALR)
    beq s2, s3, Icheck
    li s2, 115               # Opcode 1110011 (System: ecall/ebreak)
    beq s2, s3, Icheck
    
    # verifichiamo che l'istruzione sia di TIPO S
    li s2, 35                # Opcode 0100011 (Store)
    beq s2, s3, Scheck
    
    # verifichiamo che l'istruzione sia di TIPO B 
    li s2, 99                # Opcode 1100011 (Branch)
    beq s2, s3, Bcheck
    
    # verifichiamo che l'istruzione sia di TIPO U
    li s2, 55                # Opcode 0110111 (LUI)
    beq s2, s3, Ucheck
    li s2, 23                # Opcode 0010111 (AUIPC)
    beq s2, s3, Ucheck
    
    # verifichiamo che l'istruzione sia di TIPO J
    li s2, 111               # Opcode 1101111 (JAL)
    beq s2, s3, Jcheck
    
fail:
    j errore

Rcheck:
    srli s4, t6, 12
    andi s4, s4, 7           # s4 = funct3
    srli s5, t6, 25          # s5 = funct7
    
    li s2, 0x01              # Estensione M
    beq s5, s2, ok
    li s2, 0x00              # Standard
    beq s5, s2, ok
    
    li s2, 0x20              # SUB / SRA
    bne s5, s2, fail
    li s2, 0                 # funct3 per SUB
    beq s4, s2, ok
    li s2, 5                 # funct3 per SRA
    beq s4, s2, ok
    j fail

Icheck:
    srli s4, t6, 12
    andi s4, s4, 7           # s4 = funct3
    andi s3, t6, 127         # ricarico opcode
    
    li s2, 3                 # Load
    beq s3, s2, check_load
    li s2, 19                # Op-Imm
    beq s3, s2, check_imm
    li s2, 103               # JALR
    beq s3, s2, check_jalr
    j ok                # System call

check_load:
    li s2, 5
    bgt s4, s2, fail
    li s2, 3
    beq s4, s2, fail
    j ok

check_imm:
    li s2, 1
    beq s4, s2, check_shift
    li s2, 5
    beq s4, s2, check_shift
    j ok

check_shift:
    srli s5, t6, 31          # Bit 31 deve essere 0
    bne s5, zero, fail
    j ok

check_jalr:
    bne s4, zero, fail
    j ok

Scheck:
    srli s4, t6, 12
    andi s4, s4, 7
    li s2, 2
    bgt s4, s2, fail
    j ok
    
Bcheck:
    srli s4, t6, 12
    andi s4, s4, 7
    li s2, 2
    beq s4, s2, fail
    li s2, 3
    beq s4, s2, fail
    j ok
    
Ucheck: j ok

Jcheck: j ok

        # Segnalazione errore

errore:
    jal ra, vuota_registri
    li a0,3
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