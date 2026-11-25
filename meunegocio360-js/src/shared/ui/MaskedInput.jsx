import Form from 'react-bootstrap/Form'

/**
 * Campo com máscara para uso com `Controller` do React Hook Form: o valor guardado já vem
 * mascarado e só dígitos são mantidos ao digitar ou colar (letras são descartadas).
 */
export default function MaskedInput({
  mascara,
  inputRef,
  value,
  onChange,
  onBlur,
  name,
  ...props
}) {
  return (
    <Form.Control
      {...props}
      ref={inputRef}
      name={name}
      value={value}
      onBlur={onBlur}
      onChange={(evento) => onChange(mascara(evento.target.value))}
    />
  )
}
