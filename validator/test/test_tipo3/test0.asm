# Traccia1.
# Si consideri il seguente programma in assembly RISC-V:

.globl main

.text
main:
j step1
	
END:
    j REAL_END
    j step1
    j step2

step1:
    j step2

step2:
    j check
    j END 

step3:
    j check

step4:

check:
    beq zero, zero, loop

loop:
    j again

again:
    j step1

REAL_END:


# Il programma attualmente entra in un loop infinito a causa della struttura dei salti.

# Modificare il programma in maniera minimale, cioè aggiungendo, rimuovendo o modificando il minor numero di operazioni possibili e in modo tale che:

#    - Il flusso venga eseguito una sola volta passando attraverso le varie etichette step1, step2, step3, check
#    - Il programma termini correttamente all’etichetta REAL_END
#    - Non venga utilizzato alcun loop infinito o salto ciclico


#    - È consentito modificare, aggiungere o rimuovere solo le istruzioni di salto j, beq
#    - Non è consentito aggiungere istruzioni di memoria o modificare la logica aritmetica
#    - Il numero di etichette deve rimanere invariato

#    IL NUMERO MASSIMO DI MODIFICHE CHE PUOI EFFETTUARE E' 5
