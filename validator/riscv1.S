#------------------------------------------------------------------------------------
#
# TRACCIA 0.
# Scrivere un programma in assembly RISC-V che fa accendere il led 10 della ESP per 
# 6 secondi. 
#
#------------------------------------------------------------------------------------

# Svolgimento

.globl riscvprg

.text

	riscvprg:
	li a0, 6000
	li a1,10