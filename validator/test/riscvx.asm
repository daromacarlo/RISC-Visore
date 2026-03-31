.globl main

.data
    # Spazio per memorizzare 10 numeri (4 byte ciascuno)
    array:      .space 40       
    dimensione: .word 10
    msg_ris:    .asciz "La somma dei primi 10 numeri di Fibonacci è: "

.text
main:
    # --- Inizializzazione ---

    la   t0, array          # t0 = indirizzo base dell'array
    li   t1, 10     # t1 = contatore (n = 10)
    
    li   t2, 0              # F(0) = 0
    li   t3, 1              # F(1) = 1
    
    # Memorizziamo i primi due valori manualmente
    sw   t2, 0(t0)          # array[0] = 0
    sw   t3, 4(t0)          # array[1] = 1
    
    # Prepariamo il loop (partiamo dall'indice 2)
    li   t4, 2              # t4 = indice corrente i

loop_fib:
    bge  t4, t1, fine_fib   # Se i >= dimensione, esci
    
    add  t5, t2, t3         # F(i) = F(i-1) + F(i-2)
    
    # Calcolo indirizzo: t0 + (t4 * 4)
    slli t6, t4, 2          # t6 = i * 4 (shift a sinistra di 2)
    add  t6, t6, t0         # t6 = indirizzo di array[i]
    sw   t5, 0(t6)          # Memorizza F(i)
    
    # Aggiorna i valori per il prossimo ciclo
    mv   t2, t3             # F(i-2) diventa F(i-1)
    mv   t3, t5             # F(i-1) diventa F(i)
    
    addi t4, t4, 1          # i++
    j    loop_fib

fine_fib:
    # --- Calcolo della Somma ---
    li   a0, 0              # a0 userà come accumulatore per la somma
    li   t4, 0              # Reset indice i = 0

loop_somma:
    bge  t4, t1, stampa_ris # Se i >= dimensione, fine
    
    slli t6, t4, 2
    add  t6, t6, t0
    lw   t5, 0(t6)          # Carica array[i]
    
    add  a0, a0, t5         # Somma += array[i]
    
    addi t4, t4, 1
    j    loop_somma

stampa_ris:
    mv   s1, a0             # Salva la somma in s1 (a0 serve per i syscall)
    
    # Stampa messaggio stringa
    li   a7, 4              # Syscall 4: print string
    la   a0, msg_ris
	li a0,1000
	li a1,10
    j fine
    
    # Stampa il risultato numerico
    li   a7, 1              # Syscall 1: print integer
    mv   a0, s1
	li a0,1000
	li a1,10
    j fine

    # --- Uscita ---
    li   a7, 10             # Syscall 10: exit
	li a0,1000
	li a1,10
    j fine
fine:
