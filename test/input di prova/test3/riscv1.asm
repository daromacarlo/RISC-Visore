
.globl start
.text
start:
    # Alloca spazio sullo stack
    addi sp, sp, -16

    # Carica valori immediati
    li t0, 5
    li t1, 10

    # Somma
    add t2, t0, t1      # t2 = 15

    # Salva nello stack
    sw t2, 0(sp)

    # Carica dalla memoria
    lw t3, 0(sp)

    # Altra operazione
    addi t3, t3, 3      # t3 = 18

    # Salva ancora
    sw t3, 4(sp)

    # Carica per confronto
    lw t4, 4(sp)

    # Salto condizionato
    li t5, 20
    blt t4, t5, less_than

greater_equal:
    addi t6, zero, 1
    j end

less_than:
    addi t6, zero, 0

end:
    # Libera lo stack
    addi sp, sp, 16

    