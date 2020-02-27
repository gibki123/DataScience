DEFAULT                 rel
%include                "asm/python.inc"
GLOBAL                  PyInit_asm:function


;; ---------------------------------------------------------------------------
SECTION			.bss
;; ---------------------------------------------------------------------------
bytes1:			resb 100000000
bytes2:			resb 100000000
arr_to_return:		resb 100000000
size_of_bytes:		resb 4


;; ---------------------------------------------------------------------------
SECTION                 .rodata
;; ---------------------------------------------------------------------------
l_converter_name            db "convert_image", 0
l_simpleconverter_name      db "simpleconvert_image", 0
l_converter_doc             db "This method converts two bytes arrays from image to monochromatic anaglyph", 0
l_simpleconverter_doc       db "This method converts two bytes arrays from image to monochromatic anaglyph", 0
l_module_name           db "asm", 0
parameter_list          db "y*y*i"


;; ---------------------------------------------------------------------------
SECTION                 .data
;; ---------------------------------------------------------------------------
align 16
Dubois1: dq 0.4561
align 16
Dubois2: dq 0.500484
align 16
Dubois3: dq 0.176381
align 16
Dubois4: dq 0.0434706
align 16
Dubois5: dq 0.0879388
align 16
Dubois6: dq 0.00155529
align 16
Dubois7: dq 0.0400822
align 16
Dubois8: dq 0.0378246
align 16
Dubois9: dq 0.0157589
align 16
Dubois10: dq 0.378476
align 16
Dubois11: dq 0.73364
align 16
Dubois12: dq 0.0184503
align 16
Dubois13: dq 0.0152161
align 16
Dubois14: dq 0.0205971
align 16
Dubois15: dq 0.00546856
align 16
Dubois16: dq 0.0721527
align 16
Dubois17: dq 0.112961
align 16
Dubois18: dq 1.2264
align 16
Casual1: dq 0.299
align 16
Casual2: dq 0.587
align 16
Casual3: dq 0.114
align 16
return_string: db "y*"
align 16
const: dq 1.1
align 16
const_zero: dq 0

l_asm_methods:              ;; struct PyMethodDef[] *
ISTRUC PyMethodDef
  at PyMethodDef.ml_name    , dq l_converter_name
  at PyMethodDef.ml_meth    , dq asm_converter
  at PyMethodDef.ml_flags   , dq METH_VARARGS
  at PyMethodDef.ml_doc     , dq l_converter_doc
IEND

ISTRUC PyMethodDef
  at PyMethodDef.ml_name    , dq l_simpleconverter_name
  at PyMethodDef.ml_meth    , dq asm_simpleconverter
  at PyMethodDef.ml_flags   , dq METH_VARARGS
  at PyMethodDef.ml_doc     , dq l_simpleconverter_doc
IEND
NullMethodDef

l_asm_module:                ;; struct PyModuleDef *
ISTRUC PyModuleDef
  at PyModuleDef.m_base     , PyModuleDef_HEAD_INIT
  at PyModuleDef.m_name     , dq l_module_name
  at PyModuleDef.m_doc      , dq NULL
  at PyModuleDef.m_size     , dq -1
  at PyModuleDef.m_methods  , dq l_asm_methods
  at PyModuleDef.m_slots    , dq NULL
  at PyModuleDef.m_traverse , dq NULL
  at PyModuleDef.m_clear    , dq 0
  at PyModuleDef.m_free     , dq NULL
IEND


;; ---------------------------------------------------------------------------
SECTION                 .text
;; ---------------------------------------------------------------------------

asm_simpleconverter:

	push  rbp
        mov   rbp, rsp

	;Parsing arguments
	mov   rdi, rsi  
	mov   rsi, parameter_list
	mov   rdx, bytes1
	mov   rcx, bytes2
	mov   r8,  size_of_bytes
	call	PyArg_ParseTuple WRT ..plt

	mov   r8, [size_of_bytes]
	mov   r9, [size_of_bytes]
	mov   r10, 0

r_byte_cas:
	movq xmm0, [const_zero]
	;Conversion byte to floating-point number and multiply operation
	;1st byte	
	mov rsi, [bytes1]
	movzx rsi, BYTE	[rsi+r9-2]
	cvtsi2sd xmm0, rsi
	movapd xmm1, [Casual1]
	mulsd xmm0, xmm1

	;2nd byte and addition to 1st byte
	mov rsi, [bytes1]
	movzx rsi, BYTE	[rsi-1+r9]
	cvtsi2sd xmm2, rsi
	movapd xmm3, [Casual2]	
	mulsd xmm2, xmm3
	addsd xmm0, xmm2

	;3rd byte and addition
	mov rsi, [bytes1]
	movzx rsi, BYTE	[rsi+r9]
	cvtsi2sd xmm2, rsi
	movapd xmm3, [Casual3]
	mulsd xmm2, xmm3
	addsd xmm0, xmm2
	
	;conversion back to byte
	cvtsd2si rsi,xmm0

	mov   rdi,arr_to_return
	cmp   sil, 0
	jne   r_byte_no_zero_cas
	mov   BYTE sil, 1

r_byte_no_zero_cas:
	mov   [rdi+r10],sil	

g_byte_cas:
	movq xmm0, [const_zero]

	mov rsi, [bytes2]
	movzx rsi, BYTE	[rsi+r9-2]
	cvtsi2sd xmm2, rsi
	movapd xmm3, [Casual1]
	mulsd xmm2, xmm3
	addsd xmm0, xmm2

	mov rsi, [bytes2]
	movzx rsi, BYTE	[rsi-1+r9]
	cvtsi2sd xmm2, rsi
	movapd xmm3, [Casual2]
	mulsd xmm2, xmm3
	addsd xmm0, xmm2

	mov rsi, [bytes2]
	movzx rsi, BYTE	[rsi+r9]
	cvtsi2sd xmm2, rsi
	movapd xmm3, [Casual3]
	mulsd xmm2, xmm3
	addsd xmm0, xmm2

	cvtsd2si rsi,xmm0

	mov   rdi,arr_to_return
	cmp   sil, 0
	jne   g_byte_no_zero_cas
	mov   BYTE sil, 1

g_byte_no_zero_cas:
	mov   [rdi+r10+1], sil

b_byte_cas:
	movq xmm0, [const_zero]
	
	mov rsi, [bytes2]
	movzx rsi, BYTE	[rsi+r9-2]
	cvtsi2sd xmm2, rsi
	movapd xmm3, [Casual1]
	mulsd xmm2, xmm3
	addsd xmm0, xmm2

	mov rsi, [bytes2]
	movzx rsi, BYTE	[rsi-1+r9]
	cvtsi2sd xmm2, rsi
	movapd xmm3, [Casual2]
	mulsd xmm2, xmm3
	addsd xmm0, xmm2

	mov rsi, [bytes2]
	movzx rsi, BYTE	[rsi+r9]
	cvtsi2sd xmm2, rsi
	movapd xmm3, [Casual3]
	mulsd xmm2, xmm3
	addsd xmm0, xmm2

	cvtsd2si rsi,xmm0

	mov   rdi,arr_to_return
	cmp   sil, 0
	jne   b_byte_no_zero_cas
	mov   BYTE sil, 1	

b_byte_no_zero_cas:
	mov   [rdi+r10+2], sil

; End of converting first pixel

	sub   r9, 3
	add   r10, 3	
	cmp   r10, r8
	jne   r_byte_cas

	mov   rax, 0
	mov   rdi, arr_to_return
	call  PyBytes_FromString WRT ..plt

	inc   QWORD [rax + PyObject.ob_refcnt]

        pop   rbp
        ret	

asm_converter: ;; ----------------------------------------------------------------

	push  rbp
        mov   rbp, rsp

	;Parsing arguments
	mov   rdi, rsi  
	mov   rsi, parameter_list
	mov   rdx, bytes1
	mov   rcx, bytes2
	mov   r8,  size_of_bytes
	call	PyArg_ParseTuple WRT ..plt

	mov   r8, [size_of_bytes]
	mov   r9, [size_of_bytes]
	mov   r10, 0

r_byte:
	movq xmm0, [const_zero]
	;Conversion byte to floating-point number and multiply operation
	;1st byte	
	mov rsi, [bytes1]
	movzx rsi, BYTE	[rsi+r9-2]
	cvtsi2sd xmm0, rsi
	movapd xmm1, [Dubois1]
	mulsd xmm0, xmm1

	;2nd byte and addition to 1st byte
	mov rsi, [bytes1]
	movzx rsi, BYTE	[rsi-1+r9]
	cvtsi2sd xmm2, rsi
	movapd xmm3, [Dubois2]	
	mulsd xmm2, xmm3
	addsd xmm0, xmm2

	;3rd byte and addition
	mov rsi, [bytes1]
	movzx rsi, BYTE	[rsi+r9]
	cvtsi2sd xmm2, rsi
	movapd xmm3, [Dubois3]
	mulsd xmm2, xmm3
	addsd xmm0, xmm2

	;4th byte and subtraction
	mov rsi, [bytes2]
	movzx rsi, BYTE	[rsi+r9-2]
	cvtsi2sd xmm2, rsi
	movapd xmm3, [Dubois4]
	mulsd xmm2, xmm3
	subsd xmm0, xmm2

	;5th byte and subtraction
	mov rsi, [bytes2]
	movzx rsi, BYTE	[rsi-1+r9]
	cvtsi2sd xmm2, rsi
	movapd xmm3, [Dubois5]
	mulsd xmm2, xmm3
	subsd xmm0, xmm2
	
	;6th byte and subtraction
	mov rsi, [bytes2]
	movzx rsi, BYTE	[rsi+r9]
	cvtsi2sd xmm2, rsi
	movapd xmm3, [Dubois6]
	mulsd xmm2, xmm3
	subsd xmm0, xmm2
	
	;conversion back to byte
	cvtsd2si rsi,xmm0


	mov   rdi,arr_to_return
	cmp   sil, 0
	jne   r_byte_no_zero
	mov   sil, 1

r_byte_no_zero:
	mov   BYTE [rdi+r10],sil	

g_byte:
	movq xmm0, [const_zero]
	mov rsi, [bytes1]
	movzx rsi, BYTE	[rsi+r9-2]
	cvtsi2sd xmm2, rsi
	movapd xmm3, [Dubois7]
	mulsd xmm2, xmm3
	subsd xmm0, xmm2

	mov rsi, [bytes1]
	movzx rsi, BYTE	[rsi-1+r9]
	cvtsi2sd xmm2, rsi
	movapd xmm3, [Dubois8]	
	mulsd xmm2, xmm3
	subsd xmm0, xmm2

	mov rsi, [bytes1]
	movzx rsi, BYTE	[rsi+r9]
	cvtsi2sd xmm2, rsi
	movapd xmm3, [Dubois9]
	mulsd xmm2, xmm3
	subsd xmm0, xmm2

	mov rsi, [bytes2]
	movzx rsi, BYTE	[rsi+r9-2]
	cvtsi2sd xmm2, rsi
	movapd xmm3, [Dubois10]
	mulsd xmm2, xmm3
	addsd xmm0, xmm2

	mov rsi, [bytes2]
	movzx rsi, BYTE	[rsi-1+r9]
	cvtsi2sd xmm2, rsi
	movapd xmm3, [Dubois11]
	mulsd xmm2, xmm3
	addsd xmm0, xmm2

	mov rsi, [bytes2]
	movzx rsi, BYTE	[rsi+r9]
	cvtsi2sd xmm2, rsi
	movapd xmm3, [Dubois12]
	mulsd xmm2, xmm3
	subsd xmm0, xmm2

	cvtsd2si rsi,xmm0

	mov   rdi,arr_to_return
	cmp   sil, 0
	jne   g_byte_no_zero
	mov   sil, 1

g_byte_no_zero:
	mov   BYTE [rdi+r10+1], sil

b_byte:
	movq xmm0, [const_zero]
	mov rsi, [bytes1]
	movzx rsi, BYTE	[rsi-2+r9]
	cvtsi2sd xmm2, rsi
	movapd xmm3, [Dubois13]
	mulsd xmm2, xmm3
	subsd xmm0, xmm2

	mov rsi, [bytes1]
	movzx rsi, BYTE	[rsi-1+r9]
	cvtsi2sd xmm2, rsi
	movapd xmm3, [Dubois14]	
	mulsd xmm2, xmm3
	subsd xmm0, xmm2

	mov rsi, [bytes1]
	movzx rsi, BYTE	[rsi+r9]
	cvtsi2sd xmm2, rsi
	movapd xmm3, [Dubois15]
	mulsd xmm2, xmm3
	subsd xmm0, xmm2

	mov rsi, [bytes2]
	movzx rsi, BYTE	[rsi+r9-2]
	cvtsi2sd xmm2, rsi
	movapd xmm3, [Dubois16]
	mulsd xmm2, xmm3
	subsd xmm0, xmm2

	mov rsi, [bytes2]
	movzx rsi, BYTE	[rsi-1+r9]
	cvtsi2sd xmm2, rsi
	movapd xmm3, [Dubois17]
	mulsd xmm2, xmm3
	subsd xmm0, xmm2

	mov rsi, [bytes2]
	movzx rsi, BYTE	[rsi+r9]
	cvtsi2sd xmm2, rsi
	movapd xmm3, [Dubois18]
	mulsd xmm2, xmm3
	addsd xmm0, xmm2

	cvtsd2si rsi,xmm0

	mov   rdi,arr_to_return
	cmp   sil, 0
	jne   b_byte_no_zero
	mov   sil, 1
b_byte_no_zero:
	mov   BYTE [rdi+r10+2], sil

; End of converting first pixel

	sub   r9, 3
	add   r10, 3	
	cmp   r10, r8
	jne   r_byte

	mov   rax, 0
	mov   rdi, arr_to_return
	call  PyBytes_FromString WRT ..plt

	inc   QWORD [rax + PyObject.ob_refcnt]

	pop rbp
        ret


PyInit_asm: ;; --------------------------------------------------------------
        push  rbp
        mov   rbp, rsp

        mov   rsi, PYTHON_API_VERSION
        mov   rdi, l_asm_module
        call  PyModule_Create2 WRT ..plt

        pop   rbp
        ret
